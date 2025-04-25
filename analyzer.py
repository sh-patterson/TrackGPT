import logging
import sys # Import sys
from typing import Optional
from config import Config
from prompts import format_analysis_prompt

# --- Dependency Checks ---
try:
    import openai
    from openai import OpenAI, APIError, AuthenticationError, RateLimitError
    from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
except ImportError:
    print(
        "ERROR: Required libraries ('openai', 'tenacity') not found. "
        "Install using: pip install openai tenacity",
        file=sys.stderr
    )
    sys.exit(1)

# --- Helper for Tenacity Retry Logging ---
def _log_retry_attempt(retry_state):
    """Logs details of a retry attempt for API calls."""
    exc = retry_state.outcome.exception()
    wait_time = getattr(retry_state.next_action, 'sleep', 0)
    logging.warning(
        f"API Error encountered: {exc}. Retrying attempt "
        f"{retry_state.attempt_number} after {wait_time:.2f} seconds..."
    )

# --- Core Function ---
@retry(
    wait=wait_random_exponential(min=3, max=30), # Wait 3-30 seconds between retries
    stop=stop_after_attempt(4), # Retry up to 3 times (4 attempts total)
    retry=retry_if_exception_type((APIError, RateLimitError)), # Retry on API errors & rate limits
    after=_log_retry_attempt, # Log on retries
    reraise=True # Re-raise the exception if all retries fail
)
def analyze_transcript(
    transcript_text: str,
    target_name: str,
) -> Optional[str]:
    """
    Analyzes the transcript using an LLM based on the defined prompt.

    Args:
        transcript_text: The full text of the transcript.
        target_name: The name of the person/entity to focus the analysis on.
    Returns:
        A plain text string containing the analysis results, or None if analysis fails.
    """
    logging.info(f"Starting analysis for target: {target_name} using model: {Config.ANALYSIS_MODEL}")

    if not transcript_text or not transcript_text.strip():
        logging.error("Cannot analyze an empty transcript.")
        return None
    if not target_name or not target_name.strip():
        logging.error("Target name cannot be empty for analysis.")
        return None

    try:
        # Ensure API key is loaded
        if not Config.OPENAI_API_KEY:
             raise AuthenticationError("OpenAI API key not configured.")

        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        prompt = format_analysis_prompt(transcript_text, target_name)

        logging.debug("Sending analysis prompt to LLM...")
        # Log the prompt being sent for debugging

        response = client.chat.completions.create(
            model=Config.ANALYSIS_MODEL,
            messages=[
                # Optional: Add a system message to further guide the AI's persona
                # {"role": "system", "content": "You are a helpful research assistant focused on accuracy and direct evidence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Lower temperature for more factual, less creative output
            # max_tokens=... # Consider setting max_tokens if outputs are too long or costly
        )

        analysis_content = response.choices[0].message.content
        logging.info("Analysis received from LLM.")
        # logging.debug(f"Raw LLM Analysis Output:\n{analysis_content}") # Uncomment for debugging

        if not analysis_content or not analysis_content.strip():
             logging.warning("LLM returned empty analysis content.")
             return None # Or return a default message like "Analysis returned no content."

        return analysis_content.strip()

    # Catch specific errors from the retry block if they persist
    except AuthenticationError:
        logging.error("OpenAI Authentication Failed during analysis. Check API key.")
        logging.debug("Re-raising AuthenticationError") # Added log
        # No need to return here, error will be raised by retry(reraise=True)
        raise # Re-raise to be caught by main
    except RateLimitError:
        logging.error("OpenAI Rate Limit Exceeded during analysis after retries.")
        logging.debug("Re-raising RateLimitError") # Added log
        raise # Re-raise
    except APIError as e:
        logging.error(f"OpenAI API error occurred during analysis after retries: {e}")
        logging.debug("Re-raising APIError") # Added log
        raise # Re-raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during analysis: {e}", exc_info=True)
        logging.debug("Re-raising unexpected exception") # Added log
        raise # Re-raise to be caught by main