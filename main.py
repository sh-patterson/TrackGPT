import argparse
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime

# --- Initialize logging ---
# Moved logging setup to the top to capture logs from module imports if needed
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)-8s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Set logger name for main script
log = logging.getLogger(__name__)

# --- Import project modules AFTER logging is set up ---
try:
    from config import Config # Already validated on import
    from downloader import download_audio
    from transcriber import transcribe_audio
    from analyzer import analyze_transcript
    from output import save_transcript, save_analysis
except ImportError as e:
    log.critical(f"Failed to import necessary module: {e}. Please ensure all files exist and dependencies are installed.", exc_info=True)
    sys.exit(1)
except Exception as e:
    log.critical(f"An unexpected error occurred during initial imports: {e}", exc_info=True)
    sys.exit(1)


# --- Main Orchestration ---
def main():
    """Main function to orchestrate the download, transcription, and analysis."""
    log.info("--- Starting Process ---")

    parser = argparse.ArgumentParser(
        description="Download audio, transcribe, and analyze statements by a target.",
        epilog="Example: python main.py \"<URL>\" \"<Target Name>\" -o results"
    )
    parser.add_argument(
        "url",
        help="URL of the video/audio source (use quotes if needed)."
    )
    parser.add_argument(
        "target_name",
        help="Name of the research target (person/entity)."
    )
    parser.add_argument(
        "-o", "--output_dir",
        default=Config.DEFAULT_OUTPUT_DIR,
        help=f"Output directory for results (default: {Config.DEFAULT_OUTPUT_DIR})."
    )
    parser.add_argument(
        "--skip_download",
        action="store_true",
        help="Skip download step (requires existing audio file)."
    )
    parser.add_argument(
        "--skip_transcription",
        action="store_true",
        help="Skip transcription step (requires existing transcript file)."
    )
    parser.add_argument(
        "--skip_analysis",
        action="store_true",
        help="Skip analysis step."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging for more detailed output."
    )


    args = parser.parse_args()

    # --- Setup Logging Level ---
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.info("Verbose logging enabled.")

    # --- Prepare Paths ---
    output_dir = Path(args.output_dir).resolve() # Use absolute path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize target name for filename
    safe_target_name = "".join(c if c.isalnum() else "_" for c in args.target_name)
    base_filename = f"{safe_target_name}_{timestamp}"

    audio_path = output_dir / f"{base_filename}.{Config.AUDIO_FORMAT}"
    transcript_path = output_dir / f"{base_filename}_transcript.txt"
    analysis_path = output_dir / f"{base_filename}_analysis.txt"

    log.info(f"Processing URL: {args.url}")
    log.info(f"Target Name: {args.target_name}")
    log.info(f"Output Directory: {output_dir}")
    log.info(f"Audio File: {audio_path.name}")
    log.info(f"Transcript File: {transcript_path.name}")
    log.info(f"Analysis File: {analysis_path.name}")
    log.info(f"Skip Download: {args.skip_download}")
    log.info(f"Skip Transcription: {args.skip_transcription}")
    log.info(f"Skip Analysis: {args.skip_analysis}")

    # --- Execution Pipeline ---
    current_audio_path_str: str | None = None
    transcript_text: str | None = None
    analysis_text: str | None = None
    exit_code = 0

    try:
        # --- Step 1: Download Audio ---
        if not args.skip_download:
            log.info("--- Step 1: Downloading Audio ---")
            current_audio_path_str = download_audio(args.url, output_dir, base_filename)
            if not current_audio_path_str:
                log.error("Audio download failed. Cannot proceed.")
                raise RuntimeError("Audio download failed.") # Raise to exit
        else:
            log.info("--- Step 1: Skipping Audio Download ---")
            if audio_path.is_file():
                log.info(f"Using existing audio file: {audio_path}")
                current_audio_path_str = str(audio_path)
            else:
                log.error(f"Skip download requested, but audio file not found: {audio_path}")
                raise FileNotFoundError(f"Required audio file missing for skipped download: {audio_path}")

        # --- Step 2: Transcribe Audio ---
        if not args.skip_transcription:
            log.info("--- Step 2: Transcribing Audio ---")
            if not current_audio_path_str:
                 log.error("Cannot transcribe because audio path is not available.")
                 raise RuntimeError("Audio path missing for transcription.")

            transcript_text = transcribe_audio(current_audio_path_str)
            if transcript_text:
                if not save_transcript(transcript_text, transcript_path):
                    log.warning("Failed to save transcript file, but continuing analysis.")
            else:
                log.error("Transcription failed. Cannot proceed with analysis.")
                raise RuntimeError("Transcription failed.")
        else:
            log.info("--- Step 2: Skipping Transcription ---")
            if transcript_path.is_file():
                log.info(f"Loading existing transcript from: {transcript_path}")
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                    if not transcript_text or not transcript_text.strip():
                         log.warning(f"Loaded transcript file is empty: {transcript_path}")
                         # Decide whether to proceed or fail based on empty transcript
                         # raise RuntimeError("Cannot analyze empty transcript.") # Option to fail
                except Exception as e:
                    log.error(f"Failed to read existing transcript file {transcript_path}: {e}", exc_info=True)
                    raise # Re-raise file read error
            else:
                log.error(f"Skip transcription requested, but transcript file not found: {transcript_path}")
                raise FileNotFoundError(f"Required transcript file missing for skipped transcription: {transcript_path}")


        # --- Step 3: Analyze Transcript ---
        if not args.skip_analysis:
            log.info("--- Step 3: Analyzing Transcript ---")
            if not transcript_text:
                 log.error("Cannot analyze because transcript text is not available.")
                 # Don't raise here if an empty transcript is acceptable (e.g., maybe the LLM handles it)
                 # log.warning("Proceeding to save analysis step, but analysis will likely be empty.")
                 analysis_text = "Analysis skipped due to empty transcript." # Provide a default message
            else:
                 try:
                      analysis_text = analyze_transcript(transcript_text, args.target_name)
                 except Exception as e:
                     log.error(f"Analysis step failed: {e}", exc_info=True)
                     analysis_text = f"Analysis failed: {e}" # Provide failure message


            if analysis_text:
                if not save_analysis(analysis_text, analysis_path):
                     log.error("Failed to save analysis file.")
                     exit_code = 1 # Mark process as failed if saving analysis fails
            else:
                 log.warning("Analysis did not produce any text to save.")
                 # Optionally save an empty file or a file indicating no analysis result
                 # save_analysis("Analysis returned no content.", analysis_path)

        else:
            log.info("--- Step 3: Skipping Analysis ---")
            # Optionally load existing analysis if skipping
            if analysis_path.is_file():
                 log.info(f"Loading existing analysis from: {analysis_path}")
                 try:
                      with open(analysis_path, 'r', encoding='utf-8') as f:
                           analysis_text = f.read()
                 except Exception as e:
                      log.error(f"Failed to read existing analysis file {analysis_path}: {e}", exc_info=True)
                      # Decide if failure here is critical
                      # raise # Re-raise file read error


    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        exit_code = 1
    except RuntimeError as e:
        log.error(f"Process halted due to error: {e}")
        exit_code = 1
    except Exception as e:
        log.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        # Log the full traceback for unexpected errors
        traceback.print_exc()
        exit_code = 1
    finally:
        log.info("--- Process Finished ---")
        if exit_code == 0:
            log.info("Process completed successfully.")
            if transcript_path.exists():
                log.info(f"Transcript saved to: {transcript_path}")
            if analysis_path.exists():
                log.info(f"Analysis saved to: {analysis_path}")
        else:
            log.warning(f"Process finished with errors (exit code {exit_code}). Check logs above.")

        sys.exit(exit_code)


if __name__ == "__main__":
    main()
