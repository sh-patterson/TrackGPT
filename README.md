# Video Research Transcriber and Analyzer

A Python tool designed to automate the process of researching video content. It downloads audio using `yt-dlp`, transcribes it via the OpenAI Whisper API, extracts structured factual statements about a specified target using the OpenAI GPT API, and generates a comprehensive HTML report.

## Overview

This script streamlines the analysis of video/audio sources by performing the following steps:

1.  **Download:** Fetches audio and associated metadata from a given URL (e.g., YouTube, Vimeo) using `yt-dlp`.
2.  **Transcribe:** Converts the downloaded audio into text using OpenAI's Whisper API.
3.  **Extract:** Analyzes the transcript using an OpenAI GPT model (e.g., GPT-4.1 Mini) with a carefully engineered prompt to identify and extract key factual statements, claims, or commitments related to a specific target person/entity. This step aims to capture structured data (headline, speaker, body quote/summary, source, date) via text delimiters parsed by the script.
4.  **Report:** Generates a self-contained HTML report containing the video metadata, formatted bullet points derived from the extracted data (including citations and links), and the full transcript.

## Key Features

*   **Automated Pipeline:** Full workflow from URL to HTML report.
*   **Metadata Extraction:** Captures video title, uploader, date, duration, etc., using `yt-dlp`.
*   **Accurate Transcription:** Leverages OpenAI's Whisper API for audio-to-text conversion.
*   **Structured Analysis:** Extracts key information about a target into structured bullet points (Headline, Speaker, Body, Source, Date) using an OpenAI GPT model and prompt engineering.
*   **Comprehensive Reporting:** Generates a clean, readable HTML report with a dynamic title, metadata, formatted/cited bullet points, and the full transcript.
*   **Robust Error Handling:** Includes retries for API calls (`tenacity`) and handles common errors gracefully.
*   **Flexible Usage:** Supports skipping specific steps (download, transcription, extraction) if intermediate files exist.
*   **Configurable:** Settings managed via a `.env` file (API keys, models, output).
*   **Command-Line Interface:** Easy to use via CLI arguments.

## Requirements

*   **Python:** Version 3.8 or higher.
*   **OpenAI API Key:** Required for transcription and analysis. Obtain from [OpenAI Platform](https://platform.openai.com/).
*   **External Tools:**
    *   `yt-dlp`: Command-line tool for downloading video/audio. ([Installation](https://github.com/yt-dlp/yt-dlp#installation))
    *   `ffmpeg`: Command-line tool for audio processing (required by `yt-dlp` for format conversion). ([Download](https://ffmpeg.org/download.html))
    *   Both `yt-dlp` and `ffmpeg` must be installed and accessible in your system's PATH.
*   **Python Packages:** Listed in `requirements.txt` (if you create one). Key dependencies include:
    *   `openai`: For interacting with OpenAI APIs.
    *   `python-dotenv`: For managing environment variables.
    *   `yt-dlp`: Python wrapper (used for metadata extraction).
    *   `tenacity`: For robust API call retries.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    *(Replace `<repository_url>` and `<repository_directory>`)*

2.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    # Make sure you have a requirements.txt file or install manually:
    pip install openai python-dotenv yt-dlp tenacity
    ```
    *(Create a `requirements.txt` file for easier setup: `pip freeze > requirements.txt`)*

4.  **Install `yt-dlp` and `ffmpeg`:**
    Follow the installation instructions linked in the [Requirements](#requirements) section to ensure these are installed and available in your system's PATH.

5.  **Configure OpenAI API Key (Required):**
    *   Create a file named `.env` in the project root directory.
    *   Add your OpenAI API key to the `.env` file:
        ```dotenv
        OPENAI_API_KEY=your-actual-api-key-here
        ```
    *   **Security:** Never commit your `.env` file to version control. Add `.env` to your `.gitignore` file.

6.  **Optional Configuration (in `.env`):**
    You can override default settings by adding these variables to your `.env` file:
    ```dotenv
    # Model for transcription (via OpenAI API)
    WHISPER_MODEL=whisper-1

    # Model for analysis/extraction (via OpenAI API)
    ANALYSIS_MODEL=gpt-4o-mini # Or your preferred model like gpt-4-turbo

    # Directory for output files
    DEFAULT_OUTPUT_DIR=output

    # Audio format for downloads (requires ffmpeg)
    AUDIO_FORMAT=mp3
    ```

## Usage

Run the script from your terminal using the following structure:

```bash
python main.py "<VIDEO_URL>" "<TARGET_NAME>" [OPTIONS]