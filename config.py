import os
from dotenv import load_dotenv
import sys # Import sys for sys.stderr and sys.exit

load_dotenv()

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class Config:
    """Simplified configuration settings"""

    # --- Essential ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # --- Models ---
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "whisper-1")
    ANALYSIS_MODEL: str = os.getenv("ANALYSIS_MODEL", "gpt-4o-mini") # Model for analysis

    # --- Processing ---
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "mp3")

    # --- Output ---
    DEFAULT_OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ConfigError(
                "ERROR: OPENAI_API_KEY is not set. "
                "Please create a .env file and add your OpenAI API key."
            )
        print("Configuration validated.") # Add confirmation

# Validate configuration immediately upon import
try:
    Config.validate()
except ConfigError as e:
    print(str(e), file=sys.stderr)
    sys.exit(1) # Exit if config is invalid