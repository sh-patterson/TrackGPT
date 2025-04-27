# prompts.py
from typing import Dict, Any

TEXT_BULLET_PROMPT_TEMPLATE = """# ROLE: Meticulous Communications Analyst & Information Extractor

# GOAL: Extract key factual statements, claims, commitments, or potentially sensitive remarks made by or directly concerning **{target_name}** from the transcript. Output the raw components for each extracted point using specific text delimiters, suitable for identifying key messages and potential public relations risks.

# --- CONTEXTUAL METADATA (Use for source/date identification) ---
# Source Title: {video_title}
# Source Provider: {video_platform} # Default source provider
# Provider Channel/Uploader: {video_uploader} # Use as potential source if needed
# Upload Date (YYYYMMDD): {video_upload_date} # Default date
# Source URL: {video_url} # Default URL
# --- END METADATA ---

# --- TRANSCRIPT TEXT ---
{transcript_text}
# --- END TRANSCRIPT ---

# ================== INSTRUCTIONS ==================

# 1.  **Focus:** Identify significant factual claims, commitments, announced plans, specific actions, noteworthy opinions, or direct quotes attributed to **{target_name}**, or facts *about* {target_name}'s verifiable actions mentioned in the transcript. Focus on statements with potential public impact or that reveal key information about the target's views or activities. Ignore interviewer questions or general commentary unless explicitly confirmed/adopted by {target_name}.
# 2.  **Speaker Identification (Per Bullet):** Identify the person speaking the quote for the `Body:` section. Use their name (e.g., "KANYE WEST") or role (e.g., "INTERVIEWER", "CEO") in ALL CAPS. If the speaker is the video's main subject ({target_name}), use their name (ALL CAPS). If unknown, use "UNKNOWN SPEAKER".
# 3.  **Source/Date Identification (Per Bullet):**
 *   **Default:** Assume the source is `{video_platform}` and the date is `{video_upload_date}`.
 *   **Override:** If the text context *explicitly* names a different primary source (e.g., "Variety reported...", "According to the filing...") or a specific event date (e.g., "On March 15th, he said...") for *that specific fact*, use THAT source name or date string.
 *   **Fallback:** Use "Unknown Source" or "Date Unknown" if neither context nor metadata provides them.
# 4.  **Body Quote Selection (STRICT):**
#     *   Select **ONLY verbatim quote(s) DIRECTLY SPOKEN BY THE IDENTIFIED SPEAKER (`Speaker:`)**.
#     *   The quote MUST be text immediately following an explicit speaker identifier for the target (e.g., text after "West said:", "{target_name}:") or text clearly enclosed in quotation marks attributed to the target in the transcript.
#     *   **CRITICAL: DO NOT include reporter summaries, paraphrases, or narrative descriptions** of what the speaker said (e.g., DO NOT include sentences starting like "He explained that...", "West wants...", "The candidate stated his support for..."). Only extract the actual words spoken.
#     *   Aim for 2-4 full sentences of the *direct quote* for context.
#     *   Use ` [...] ` for minor omissions *within* the direct quote if absolutely necessary for brevity, preserving the original meaning.
#     *   If no suitable *direct quote* supporting the headline fact can be found according to these strict rules, output an empty string for the `Body:` field.
# 5.  **Headline Content (`headline_raw`):** Generate the raw text for the `Headline:` field following these sub-rules precisely:
 *   **Summarize Core Fact (PAST TENSE):** Concisely summarize the absolute core finding, action, or statement (1-2 sentences maximum). Use **simple PAST TENSE** verbs (e.g., Said, Stated, Announced, Claimed, Revealed, Launched, Criticized, Denied, Confirmed, Met).
 *   **Natural Actor Inclusion (STRONGLY PREFERRED):** The summary itself should clearly state *who* performed the action or made the statement whenever possible, typically starting with the actor's name. Examples: `Kanye West Announced Surprise Album Drop.`, `Acme CEO Claimed Record Profits For Q3.`, `Interviewer Asked About Recent Controversy.` This style is preferred over passive phrasing like `Surprise Album Drop Was Announced.`
 *   **Be Descriptive & Significant:** Make the summary informative. Capture the *essence* of the point. GOOD: `Kanye West Stated His New Shoe Line Would Use Sustainable Materials.` BAD: `Kanye West Discussed Shoe Line.`
 *   **Optional Short Quote Snippet:** You MAY include a *very short* (under 10 words), impactful, verbatim quote snippet in double quotes within the summary *if* it *is* the core point (e.g., `Kanye West Described New Project As "Revolutionary".`). Use sparingly.
 *   **Final Format:** Ensure the entire headline ends with a single period. Output as plain text. **DO NOT apply special capitalization (like Title Case) here.**
# 6.  **Limit:** Extract up to **{max_bullets}** distinct factual points. Prioritize statements with potential PR implications or significant informational value.
# 7.  **Empty Result:** If no relevant points are found, output only the text "@@NO BULLETS FOUND@@".

# ================== OUTPUT FORMAT (PLAIN TEXT ONLY) ==================

# For EACH bullet point extracted, output EXACTLY the following block structure, using "@@DELIM@@" as the separator:

*** BULLET START ***
**Headline:** [Concise PAST TENSE Summary (preferably starting with Actor) + Period. Raw text.]
@@DELIM@@
**Speaker:** [Identified Speaker (ALL CAPS)]
@@DELIM@@
**Body:** [Verbatim quote(s) here. DO NOT add surrounding quotes or 'According to...']
@@DELIM@@
**Source:** [Identified source name here]
@@DELIM@@
**Date:** [Identified date string here, e.g., YYYYMMDD or M/D/YY or Month Day, Year or Date Unknown]
*** BULLET END ***

# Repeat the entire "*** BULLET START ***" to "*** BULLET END ***" block for each bullet.
# Put a single blank line between each "*** BULLET END ***" and the next "*** BULLET START ***".

# == CRITICAL: DO NOT ==
#   *   DO NOT output JSON.
#   *   DO NOT add any text before the first "*** BULLET START ***" (unless it's "@@NO BULLETS FOUND@@").
#   *   DO NOT add any text after the final "*** BULLET END ***".
#   *   DO NOT use markdown formatting (like **). Use the exact delimiters shown.
#   *   DO NOT apply Title Case formatting to the **Headline:** output. Python code will handle capitalization later.

# Begin Extraction:
"""

def format_text_bullet_prompt(
    transcript_text: str,
    target_name: str,
    metadata: Dict[str, Any],
    max_bullets: int = 15
) -> str:
    """Formats the Text Bullet Extraction prompt."""
    import logging # Ensure logging is imported

    if not transcript_text or not transcript_text.strip():
        logging.warning("Formatting Text Bullet prompt with empty transcript text.")

    if not metadata:
         logging.warning("Formatting Text Bullet prompt with missing metadata. Using defaults.")
         metadata = {}

    title = metadata.get('title', 'Unknown Title')
    uploader = metadata.get('uploader', 'Unknown Uploader')
    upload_date = metadata.get('upload_date') or "Date Unknown"
    platform = metadata.get('extractor', 'Unknown Platform')
    url = metadata.get('webpage_url', '#')
    platform_display = "YouTube" if str(platform).lower() == "youtube" else str(platform)

    logging.debug(f"Formatting Text Bullet prompt: Title='{title}', Uploader='{uploader}', Date='{upload_date}', Platform='{platform_display}', URL='{url}'")

    try:
        return TEXT_BULLET_PROMPT_TEMPLATE.format(
            target_name=target_name,
            transcript_text=transcript_text,
            video_title=title,
            video_uploader=uploader,
            video_upload_date=upload_date,
            video_platform=platform_display,
            video_url=url,
            max_bullets=max_bullets
        )
    except KeyError as e:
        logging.error(f"Missing key in Text Bullet prompt formatting: {e}")
        raise ValueError(f"Failed to format Text Bullet prompt due to missing key: {e}")