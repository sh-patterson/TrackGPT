# TrackGPT

**Automated video & audio analysis, transcription, and targeted statement extraction with HTML reporting**

---

## Overview

TrackGPT is a command-line tool that automates the process of researching video and audio content. It downloads the source, transcribes the audio using OpenAI's Whisper API, and utilizes an LLM (like GPT-4.1 Mini) with a specialized prompt to extract key statements, claims, commitments, or potentially sensitive remarks made by or directly concerning a specified target individual or entity. The results, including video metadata and the full transcript, are compiled into a user-friendly HTML report.

Ideal for communications professionals, researchers, journalists, and compliance monitoring, TrackGPT helps you:

- Quickly identify key messages and talking points.
- Extract relevant statements from long recordings efficiently.
- Monitor public statements for PR risks or opportunities.
- Verify claims against the original transcript context.

---

## Features

- **Content Download & Metadata Extraction:**
  Uses `yt-dlp` to fetch audio directly from URLs (e.g., YouTube, Vimeo) and extracts relevant metadata (title, uploader, date, etc.). Requires `ffmpeg` for audio format conversion.

- **High-Quality Transcription:**
  Leverages OpenAI’s Whisper API for accurate audio-to-text conversion.

- **Structured Statement Extraction (PR Focus):**
  Analyzes the transcript using an LLM (e.g., GPT-4.1 Mini) guided by a detailed prompt (`prompts.py`) focused on identifying statements relevant to communications analysis (factual claims, commitments, noteworthy opinions, sensitive remarks). Extracts findings into structured components (Headline, Speaker, Body, Source, Date) via text delimiters.

- **Comprehensive HTML Reporting:**
  Generates a self-contained HTML report (`_report.html`) that includes:
    - A dynamically generated report title (Target, Source, Date).
    - A detailed metadata section.
    - Formatted bullet points summarizing key extracted statements, with citations and links back to the source URL.
    - The full, searchable transcript for verification.

- **Robust Error Handling:**
  Includes API retry logic (`tenacity`) for transient network/API issues.

- **Flexible Workflow:**
  Allows skipping download, transcription, or extraction steps if intermediate files exist.

- **Configurable:**
  Uses a `.env` file for API keys and model selection.

---

## Prerequisites

1.  **Python 3.8+**
    Install from [python.org](https://www.python.org/).

2.  **yt-dlp & ffmpeg**
    These external command-line tools are required.
    -   `yt-dlp`: [Installation Guide](https://github.com/yt-dlp/yt-dlp#installation)
    -   `ffmpeg`: [Download & Setup](https://ffmpeg.org/download.html)
    *Ensure both are installed and accessible in your system's PATH.*

3.  **OpenAI API Key**
    -   Required for transcription (Whisper) and analysis (GPT model).
    -   Obtain from [OpenAI Platform](https://platform.openai.com/).
    -   *Note: Using the OpenAI API incurs costs based on usage.*
    -   Create a file named `.env` in the project root directory:
        ```dotenv
        OPENAI_API_KEY=your_openai_api_key_here

        # Optional: Override default models (examples)
        # WHISPER_MODEL=whisper-1
        # ANALYSIS_MODEL=gpt-4.1-mini
        # AUDIO_FORMAT=mp3
        # DEFAULT_OUTPUT_DIR=output
        ```

---

## Installation

```bash
# 1. Clone the repository (replace with the actual URL)
# git clone https://github.com/sh-patterson/TrackGPT-Audio
# cd TrackGPT-Audio

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate  | macOS/Linux: source .venv/bin/activate

# 3. Install Python dependencies from requirements.txt
pip install -r requirements.txt
```

*(Ensure `requirements.txt` exists and is up-to-date: `pip freeze > requirements.txt`)*

---

## Usage

```bash
python main.py <URL> "<Target Name>" [options]
```

-   `<URL>`: Link to the video or audio source. **Enclose in quotes** if it contains special characters.
-   `<Target Name>`: The exact name of the person/entity to analyze. **Enclose in quotes** if it contains spaces.

**Common Options**

| Flag                    | Description                                            | Default Value         |
| :---------------------- | :----------------------------------------------------- | :-------------------- |
| `-o`, `--output_dir <dir>` | Specify directory for output files                     | `output/`             |
| `--skip_download`       | Skip download (requires existing audio file)           | `False`               |
| `--skip_transcription`  | Skip transcription (requires existing transcript file) | `False`               |
| `--skip_extraction`     | Skip analysis/extraction step                          | `False`               |
| `-v`, `--verbose`       | Enable detailed debug logging                          | `False`               |
| `-h`, `--help`          | Show help message and exit                             |                       |

**Example**

```bash
# Using an example target
python main.py \
  "https://www.youtube.com/watch?v=abcdef12345" \
  "Kanye West" \
  -o results/kanye_analysis -v
```

This command:
1.  Downloads audio from the YouTube video.
2.  Transcribes the audio using Whisper API.
3.  Analyzes the transcript focusing on statements related to "Kanye West".
4.  Saves the output files (`Kanye_West_..._transcript.txt` and `Kanye_West_..._report.html`) into the `results/kanye_analysis` directory.
5.  Prints verbose logs during execution.

---

## Output Files

Located in the specified output directory (`output/` by default), named using the target and timestamp:

1.  **`<safe_target_name>_<timestamp>_transcript.txt`**
    -   Contains the full, plain text transcription generated by the Whisper API. Useful for searching and verification.

2.  **`<safe_target_name>_<timestamp>_report.html`**
    -   A self-contained HTML file presenting the research findings.
    -   **Contents:**
        -   **Dynamic Title:** Based on target, source, and date.
        -   **Metadata Section:** Key details about the source video/audio.
        -   **Extracted Bullet Points Section:** Lists key points identified by the LLM analysis. Each bullet is formatted as:
            `<b>Formatted Headline.</b> "Extracted Text Block" [Source, Formatted Date with Link]`
            *(See Limitations section below regarding the "Extracted Text Block")*
        -   **Full Transcript Section:** The complete transcript text within a scrollable `<pre>` block for reference.

---

## Limitations and Disclaimer

*   **Quote Accuracy:** The "Extracted Bullet Points" section relies on an LLM interpreting the transcript based on the prompt in `prompts.py`. While the prompt includes **strict instructions** aiming for direct quotes, LLMs can still make errors. Accuracy depends heavily on transcript clarity and LLM interpretation.
*   **Verification Required:** Users should **always verify the content of the extracted text blocks within the bullet points against the "Full Transcript" section** provided in the HTML report to ensure accuracy and context.
*   **API Costs:** This tool uses paid OpenAI APIs. Monitor your usage.
*   **Dependencies:** Requires `yt-dlp` and `ffmpeg` to be correctly installed and accessible in the system PATH.

---

## Troubleshooting

-   **“`yt-dlp` not found” / “`ffmpeg` not found”**
    -   Ensure installation and verify system PATH includes their locations. Restart terminal after PATH changes.
-   **API Key / OpenAI Errors**
    -   Double-check `.env` file for correct `OPENAI_API_KEY`.
    -   Check OpenAI account status (active, funds/credits, usage limits).
    -   Check network connection / firewalls.
-   **Permission Errors**
    -   Ensure write permissions for the output directory.
-   **File Not Found (Skip Options)**
    -   Verify the expected audio/transcript file exists in the output directory with the correct naming convention if using skip flags.

---

## Contributing

Contributions welcome! Please fork, create a feature branch, commit changes, push, and open a Pull Request. Adhere to existing code style.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
```
