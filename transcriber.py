import logging
import sys # Import sys
from pathlib import Path
from typing import Optional
from config import Config

# --- Dependency Checks ---
try:
    import openai
    from openai import OpenAI, APIError, AuthenticationError, RateLimitError
except ImportError:
    print("ERROR: 'openai' library not found. Install using: pip install openai", file=sys.stderr)
    sys.exit(1)

# --- Core Function ---
def transcribe_audio(audio_filepath: str) -> Optional[str]:
    """
    Transcribes an audio file using OpenAI Whisper.

    Args:
        audio_filepath: Path to the audio file (e.g., .mp3).

    Returns:
        The transcribed text as a string, or None if transcription fails.
    """
    audio_path = Path(audio_filepath)
    logging.info(f"Attempting transcription for: {audio_path}")

    if not audio_path.is_file():
        logging.error(f"Audio file not found or is not a file: {audio_path}")
        return None

    # Check file size (Whisper API has a 25MB limit)
    try:
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            logging.warning(
                f"Audio file size ({file_size_mb:.2f} MB) exceeds 25MB limit. "
                "Transcription may fail or be incomplete via standard API. "
                "Consider using a library that handles chunking for large files."
            )
            # Proceed anyway, but warn the user.
    except OSError as e:
        logging.warning(f"Could not determine file size for {audio_path}: {e}")

    try:
        # Ensure API key is loaded via Config or environment
        if not Config.OPENAI_API_KEY:
             raise AuthenticationError("OpenAI API key not configured.") # Should be caught by Config.validate

        client = OpenAI(api_key=Config.OPENAI_API_KEY) # Explicitly pass key

        with open(audio_path, "rb") as audio_file:
            logging.info(f"Sending {audio_path.name} to Whisper API (model: {Config.WHISPER_MODEL})...")
            transcript_response = client.audio.transcriptions.create(
                model=Config.WHISPER_MODEL,
                file=audio_file,
                response_format="text" # Request plain text output
            )
        logging.info("Transcription successful.")
        # The response for "text" format is directly the string
        return str(transcript_response)

    except AuthenticationError:
        logging.error("OpenAI Authentication Failed. Check your API key.")
        return None
    except RateLimitError:
        logging.error("OpenAI Rate Limit Exceeded. Please wait and try again, or check your usage limits.")
        return None
    except APIError as e:
        logging.error(f"OpenAI API error occurred during transcription: {e}")
        # You could log e.status_code or e.body for more details if needed
        return None
    except FileNotFoundError:
         # This check is redundant due to the check at the start, but good practice
         logging.error(f"Audio file could not be opened at {audio_path}")
         return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during transcription: {e}", exc_info=True)
        return None