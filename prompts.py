# --- START OF FILE prompts.py ---

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

# 1.  **Focus:** Identify significant factual claims, commitments, announced plans, specific actions, noteworthy opinions, or direct quotes attributed to **{target_name}**, **OR significant factual assertions/claims made *by others* (e.g., interviewer, narrator) *about* {target_name}** or {target_name}'s record/actions mentioned in the transcript. Focus on statements with potential public impact or that reveal key information about the target's views or activities. **Ignore simple interviewer questions or off-topic commentary, but DO capture factual statements or claims made by the interviewer/narrator *about* {target_name}, even if not explicitly confirmed by {target_name} during the exchange.**
# 2.  **Speaker Identification (Per Bullet):** Identify the primary person speaking the text selected for the `Body:` section below. Use their name (e.g., "KANYE WEST") or role (e.g., "INTERVIEWER", "NARRATOR", "CEO") in ALL CAPS. If the speaker is the video's main subject ({target_name}), use their name (ALL CAPS). If unknown, use "UNKNOWN SPEAKER". **Crucially, this speaker should match the actor identified in the Headline if the Headline attributes the statement directly.**
# 3.  **Source/Date Identification (Per Bullet):**
#     *   **Default:** Assume the source is `{video_platform}` and the date is `{video_upload_date}`.
#     *   **Override:** If the text context *explicitly* names a different primary source (e.g., "Variety reported...", "According to the filing...") or a specific event date (e.g., "On March 15th, he said...") for *that specific fact*, use THAT source name or date string.
#     *   **Fallback:** Use "Unknown Source" or "Date Unknown" if neither context nor metadata provides them.

# 4.  **Body Text Selection (Contextual):**
#     *   Select the most relevant **continuous passage** (ideally 2-4 sentences) from the transcript that directly supports or contains the core fact/statement summarized in the `Headline:`.
#     *   This passage **should primarily feature words spoken by the identified `Speaker:`** but **MAY include necessary surrounding context**, such as brief introductory phrases from a reporter or interviewer (e.g., "When asked about X, {target_name} stated:", or "Margaret Hoover noted that {target_name}...") if it directly precedes the key statement and aids understanding.
#     *   The goal is to provide **contextual evidence** for the headline, not necessarily *only* a pure verbatim quote. Ensure the selected text clearly relates to the headline's core assertion.
#     *   Prioritize clarity and relevance to the headline over strict verbatim-only extraction if needed.
#     *   Extract the text block exactly as found in the transcript. Do not add surrounding quotation marks or prefixes like "According to..." yourself.
#     *   Use ` [...] ` for minor omissions *within* the selected passage if helpful for clarity or brevity while preserving meaning.
#     *   If no relevant passage supporting the headline can be found, output an empty string for the `Body:` field.

# 5.  **Headline Content (`headline_raw`):** Generate the raw text for the `Headline:` field following these sub-rules precisely:
#     *   **Summarize Core Fact (PAST TENSE):** Concisely summarize the absolute core finding, action, or statement (1-2 sentences maximum), **CRITICALLY, accurately attributing it to the correct actor** (e.g., {target_name}, Interviewer, Narrator, Cited Source) based on who made the statement or claim *in the provided transcript context*. Use **simple PAST TENSE** verbs (e.g., Said, Stated, Announced, Claimed, Revealed, Launched, Criticized, Denied, Confirmed, Met, Asked, Noted, Reported).
#     *   **Natural Actor Inclusion (STRONGLY PREFERRED):** The summary itself should clearly state *who* performed the action or made the statement whenever possible, typically starting with the actor's name. Examples: `{target_name} Announced...`, `CEO Claimed...`, **`Interviewer Stated That {target_name} Sponsored The Bill.`**, **`Narrator Reported {target_name} Was The First Female Combat Vet Elected To Senate From Iowa.`**, **`Margaret Hoover Asserted That {target_name} Warned The Secretary Of Education About Campus Antisemitism.`** This style is strongly preferred over passive phrasing like `Sponsorship Of The Bill Was Mentioned.` or phrasing that incorrectly implies {target_name} said it (e.g., `{target_name} Sponsored The Bill...` when the interviewer was the one stating it).
#     *   **Be Descriptive & Significant:** Make the summary informative. Capture the *essence* of the point. GOOD: `Interviewer Claimed {target_name}'s New Policy Would Impact Farmers.` BAD: `Interviewer Talked About Policy.`
#     *   **Optional Short Quote Snippet:** You MAY include a *very short* (under 10 words), impactful, verbatim quote snippet in double quotes within the summary *if* it *is* the core point AND is directly spoken by the actor named in the headline (e.g., `{target_name} Described New Project As "Revolutionary".`). Use sparingly, especially for third-party claims.
#     *   **Final Format:** Ensure the entire headline ends with a single period. Output as plain text. **DO NOT apply special capitalization (like Title Case) here.**
# 6.  **Limit:** Extract up to **{max_bullets}** distinct factual points. Prioritize statements with potential PR implications or significant informational value, including both self-stated points and claims made *about* the target.
# 7.  **Empty Result:** If no relevant points are found, output only the text "@@NO BULLETS FOUND@@".

# ================== OUTPUT FORMAT (PLAIN TEXT ONLY) ==================

# For EACH bullet point extracted, output EXACTLY the following block structure, using "@@DELIM@@" as the separator:

*** BULLET START ***
**Headline:** [Concise PAST TENSE Summary (Accurately Attributed Actor) + Period. Raw text.]
@@DELIM@@
**Speaker:** [Primary Speaker of Body Text (ALL CAPS) - Should align with Headline actor if directly quoted]
@@DELIM@@
**Body:** [Relevant contextual passage from transcript. No added quotes/prefixes.]
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
#   *   DO NOT add surrounding double quotes or prefixes like "According to..." to the **Body:** output field.

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
# --- END OF FILE prompts.py ---