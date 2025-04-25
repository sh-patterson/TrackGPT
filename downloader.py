import subprocess
import logging
import sys
from pathlib import Path
from typing import Optional
from config import Config

# --- Dependency Checks ---
try:
    import yt_dlp
except ImportError:
    print("ERROR: 'yt-dlp' library not found. Install using: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)

def find_yt_dlp_executable() -> Optional[str]:
    """Tries to find the yt-dlp executable."""
    try:
        return yt_dlp.utils.exe_path()
    except AttributeError:
        import shutil
        return shutil.which("yt-dlp")

def find_ffmpeg_executable() -> Optional[str]:
    """Tries to find the ffmpeg executable."""
    import shutil
    return shutil.which("ffmpeg")

YT_DLP_PATH = find_yt_dlp_executable()
if not YT_DLP_PATH:
    print("ERROR: 'yt-dlp' command not found in system PATH or via library helper.", file=sys.stderr)
    print("Please ensure yt-dlp is installed and accessible.", file=sys.stderr)

FFMPEG_PATH = find_ffmpeg_executable()
if not FFMPEG_PATH:
    print("ERROR: 'ffmpeg' command not found in system PATH.", file=sys.stderr)
    print("Please ensure ffmpeg is installed and accessible.", file=sys.stderr)
    sys.exit(1) # Exit if ffmpeg is not found

# --- Core Function ---
def download_audio(url: str, output_dir: Path, base_filename: str) -> Optional[str]:
    """
    Downloads audio from a URL using yt-dlp.

    Args:
        url: The URL of the video/audio source.
        output_dir: The directory to save the audio file.
        base_filename: The base name for the output file (without extension).

    Returns:
        The full path to the downloaded audio file as a string, or None if download fails.
    """
    if not YT_DLP_PATH:
         logging.error("yt-dlp executable not found. Cannot download.")
         return None

    output_path_template = output_dir / f"{base_filename}.%(ext)s"
    final_audio_path = output_dir / f"{base_filename}.{Config.AUDIO_FORMAT}"

    # Ensure output directory exists
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.error(f"Failed to create output directory {output_dir}: {e}")
        return None

    cmd = [
        YT_DLP_PATH,
        url,
        "-x",  # Extract audio
        "--audio-format", Config.AUDIO_FORMAT,
        "--no-playlist",       # Avoid downloading entire playlists
        "--no-write-info-json", # Don't need metadata file
        "--progress",          # Show progress
        "--no-simulate",       # Ensure download actually happens
        "--no-abort-on-error", # Try to continue if parts fail
        "-o", str(output_path_template), # Output template
    ]

    logging.info(f"Attempting to download audio from: {url}")
    logging.info(f"yt-dlp command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,         # Raise error on non-zero exit code
            capture_output=True, # Capture stdout/stderr
            text=True,          # Decode output as text
            encoding='utf-8'    # Specify encoding
        )
        logging.info(f"yt-dlp stdout:\n{result.stdout}")
        if result.stderr:
            logging.warning(f"yt-dlp stderr:\n{result.stderr}")

        # Check if the expected final file exists
        if final_audio_path.exists():
            logging.info(f"Successfully downloaded audio to: {final_audio_path}")
            return str(final_audio_path)
        else:
            logging.error(f"yt-dlp completed but expected output file '{final_audio_path}' not found.")
            logging.error("Please check yt-dlp output above for clues.")
            # Attempt to find any audio file created
            audio_files = list(output_dir.glob(f"{base_filename}.*"))
            possible_audio = [f for f in audio_files if f.suffix.lower() in ['.mp3', '.m4a', '.wav', '.ogg', '.opus']]
            if possible_audio:
                 found_path = str(possible_audio[0])
                 logging.warning(f"Found an alternative audio file: {found_path}. Returning this path.")
                 return found_path
            return None

    except subprocess.CalledProcessError as e:
        logging.error(f"yt-dlp failed (Exit Code {e.returncode}). URL: {url}")
        logging.error(f"Command: {' '.join(e.cmd)}")
        logging.error(f"Stderr:\n{e.stderr}")
        return None
    except FileNotFoundError:
        logging.error(f"'{YT_DLP_PATH}' command not found. Is yt-dlp installed and in PATH?")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during download: {e}", exc_info=True)
        return None
