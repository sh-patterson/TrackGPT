# prompts.py

# New prompt designed for extracting facts and hot-button issues as plain text.
ANALYSIS_PROMPT_TEMPLATE = """
You are a meticulous research assistant analyzing a transcript of an interview or speech.
Your target is: **{target_name}**

Your task is to extract specific information about **{target_name}**'s statements from the provided transcript text and format it clearly for a text file report.

**Transcript Text:**
--- START TRANSCRIPT ---
{transcript_text}
--- END TRANSCRIPT ---

**Instructions:**

1.  **Factual Statements by {target_name}:**
    *   Identify key factual claims, policy positions, commitments, or statements of intent made *directly by {target_name}* in the transcript.
    *   Focus ONLY on what **{target_name}** said. Do not include statements *about* them made by others unless {target_name} explicitly agrees or confirms.
    *   Present these as a simple bulleted list (using '-' or '*').
    *   Each bullet point should be concise and based *verbatim* or paraphrased *very closely* on the transcript.
    *   Use past tense (e.g., "{target_name} stated...", "{target_name} claimed...").
    *   If no relevant factual statements by {target_name} are found, state "No specific factual statements by {target_name} were identified in this transcript."

2.  **Hot-Button Political Issues Assessment:**
    *   Review the statements made by **{target_name}**.
    *   Determine if **{target_name}** discussed any common political "hot-button" issues. Examples include (but are not limited to): abortion, gun control, immigration, climate change, specific economic policies (taxes, spending), healthcare reform, LGBTQ+ rights, election integrity, foreign policy conflicts.
    *   If hot-button issues were discussed by **{target_name}**:
        *   Briefly state which issues were touched upon.
        *   Provide **direct quotes** from **{target_name}** from the transcript as evidence for each issue mentioned. Ensure the quotes clearly show discussion of the hot-button topic. Format quotes clearly (e.g., using indentation or quotation marks).
    *   If no hot-button issues were discussed by **{target_name}**, state "No specific hot-button political issues were discussed by {target_name} in this transcript."

**Output Format:**

Provide the output as plain text, structured exactly like this:

```text
## Factual Statements by {target_name}

- [Statement 1 based on transcript]
- [Statement 2 based on transcript]
- ...

## Hot-Button Political Issues Assessment

[State which issues were discussed, e.g., "Immigration and Healthcare Reform were discussed."]

**Supporting Quotes:**

*   **[Issue 1, e.g., Immigration]:**
    > "[Direct quote from {target_name} about Issue 1]"
*   **[Issue 2, e.g., Healthcare]:**
    > "[Direct quote from {target_name} about Issue 2]"
    > "[Another relevant quote from {target_name} about Issue 2, if applicable]"

(Or, if none found: "No specific hot-button political issues were discussed by {target_name} in this transcript.")
```

**Begin Analysis:**
"""

def format_analysis_prompt(transcript_text: str, target_name: str) -> str:
    """Formats the analysis prompt with the transcript and target name."""
    if not transcript_text or not transcript_text.strip():
        raise ValueError("Transcript text cannot be empty for analysis.")
    if not target_name or not target_name.strip():
        raise ValueError("Target name cannot be empty for analysis.")

    return ANALYSIS_PROMPT_TEMPLATE.format(
        transcript_text=transcript_text,
        target_name=target_name
    )