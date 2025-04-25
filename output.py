import logging
from pathlib import Path

def save_text_file(content: str, filepath: Path) -> bool:
    """
    Saves text content to a specified file path.

    Args:
        content: The string content to save.
        filepath: The Path object representing the output file.

    Returns:
        True if saving was successful, False otherwise.
    """
    logging.info(f"Attempting to save text to: {filepath}")
    try:
        # Ensure the output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Successfully saved text file: {filepath}")
        return True
    except IOError as e:
        logging.error(f"Failed to write text file {filepath}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred saving text file {filepath}: {e}", exc_info=True)
        return False

# No need for separate functions for transcript/analysis if they just save text
# Alias for clarity if preferred:
save_transcript = save_text_file
save_analysis = save_text_file