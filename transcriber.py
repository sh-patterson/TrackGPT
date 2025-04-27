"""
Module for transcribing audio files using OpenAI's Whisper API.

Handles:
- Audio file validation and size checks
- API authentication and configuration
- Error handling and rate limiting
- Conversion of audio to text transcripts

Requirements:
- OpenAI API key (via Config.OPENAI_API_KEY)
- Audio files under 25MB (Whisper API limit)
"""
import logging
import sys
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
    Transcribes an audio file using OpenAI's Whisper API.

    This function takes the path to an audio file, validates its existence and
    size against the Whisper API's limits, and sends it to the API for
    transcription. It handles API authentication, rate limiting, and other
    potential API errors.

    Args:
        audio_filepath: The path to the audio file that needs to be transcribed.
                        Supported formats typically include mp3, wav, m4a, etc.,
                        depending on the Whisper API's capabilities.

    Returns:
        A string containing the transcribed text if the transcription is
        successful. Returns None if the file is not found, exceeds the size
        limit (with a warning), or if any API or unexpected errors occur.
    """
    audio_path = Path(audio_filepath)
    logging.info(f"Attempting transcription for: {audio_path}")

    # Validate that the provided path points to an existing file
    if not audio_path.is_file():
        logging.error(f"Audio file not found or is not a file: {audio_path}")
        return None

    # --- File Validation ---
    # Check the file size against the Whisper API's 25MB limit.
    # The API might reject files larger than this or produce suboptimal results.
    try:
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            # Log a warning if the file size exceeds the recommended limit
            logging.warning(
                f"Audio file size ({file_size_mb:.2f} MB) exceeds 25MB limit for Whisper API. "
                "Transcription may fail or be incomplete. "
                "For large files, consider pre-processing (e.g., splitting) or using a library that handles chunking."
            )
            # We proceed despite the warning, as the API might still process it,
            # albeit potentially with reduced quality or errors.
    except OSError as e:
        # Log a warning if unable to determine the file size
        logging.warning(f"Could not determine file size for {audio_path}: {e}")

    try:
        # Validate that the OpenAI API key is configured
        if not Config.OPENAI_API_KEY:
            # This should ideally be caught during configuration validation,
            # but included here as a safeguard.
            raise AuthenticationError("OpenAI API key not configured.")

        # --- API Client Setup ---
        # Initialize the OpenAI client with the API key.
        # The client library is designed to handle standard API practices
        # like rate limiting and retries automatically for transient issues.
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # Open the audio file in binary read mode
        with open(audio_path, "rb") as audio_file:
            logging.info(f"Sending {audio_path.name} to Whisper API (model: {Config.WHISPER_MODEL})...")
            # Call the transcription creation endpoint
            transcript_response = client.audio.transcriptions.create(
                model=Config.WHISPER_MODEL,  # Specify the Whisper model to use (e.g., "whisper-1")
                file=audio_file,             # Pass the audio file object
                response_format="text"       # Request the response as plain text
            )
            # Other supported formats include: json, srt, verbose_json, vtt

        logging.info("Transcription successful.")
        # For the "text" response format, the result is a simple string
        return str(transcript_response)

    # --- Error Handling Strategy ---
    # Handle specific exceptions raised by the OpenAI client library:
    # 1. AuthenticationError: Occurs if the API key is invalid or missing.
    # 2. RateLimitError: Occurs if the API usage exceeds the allowed rate limits.
    # 3. APIError: Catches other general API-related errors (e.g., invalid parameters, server errors).
    # 4. FileNotFoundError: Catches errors related to opening or reading the audio file.
    # 5. Generic Exception: A catch-all for any other unexpected errors during the process.
    except AuthenticationError:
        logging.error("OpenAI Authentication Failed. Check your API key in config.py.")
        return None
    except RateLimitError:
        logging.error("OpenAI Rate Limit Exceeded. Please wait and try again, or check your usage limits.")
        return None
    except APIError as e:
        logging.error(f"OpenAI API error occurred during transcription: {e}")
        # Log additional details from the API error for debugging
        logging.debug(f"API Error Details - Status: {e.status_code}, Body: {e.body}")
        return None
    except FileNotFoundError:
        logging.error(f"Audio file could not be opened at {audio_path}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during transcription: {e}", exc_info=True)
        return None