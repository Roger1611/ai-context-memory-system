def build_extraction_prompt(conversation_text: str) -> str:
    return f"""Read this conversation and extract everything that would be needed to continue this work in a new conversation.

Do not classify or label the domain. Do not add commentary. Do not restate questions that were asked but not answered.
Write only what is true and concrete at the end of this conversation.
Be specific — exact names, numbers, dates, terms, and references must be preserved. Vague statements are useless.

Use these sections exactly:

## What This Was Working On
The core question, problem, or goal. One short paragraph.

## What Was Figured Out
Everything that was decided, concluded, or confirmed. Be specific — include exact details, numbers, names, terms, and reasoning if given. This is the most important section.

## Current State
What exists or has been produced right now. What is working, agreed on, or in place.

## What Still Needs Doing
Specific remaining tasks, unanswered questions, or unresolved decisions. If nothing is unresolved, say so.

## Details That Must Not Be Lost
Names, numbers, dates, links, formulas, frameworks, tools, specific terminology, or references that appeared in the conversation. Copy them exactly. If none, omit this section.

---

Conversation:
{conversation_text}
"""


def build_chunk_summary_prompt(conversation_chunk: str, chunk_number: int, total_chunks: int) -> str:
    return f"""This is segment {chunk_number} of {total_chunks} from a longer conversation.

Extract every fact, decision, and conclusion from this segment. Do not summarize discussion or questions — only record what was established or agreed.

Rules:
- Dense bullet points only, no prose
- Preserve exact names, numbers, dates, links, terms, and references as they appeared
- Mark definite decisions or conclusions with [DECIDED]
- Mark open questions or unresolved points with [OPEN]
- If something is uncertain, note the uncertainty — do not smooth it over

Segment {chunk_number} of {total_chunks}:
{conversation_chunk}
"""


def build_synthesis_prompt(chunk_summaries: list[str]) -> str:
    numbered = "\n\n".join(
        f"--- Segment {i + 1} of {len(chunk_summaries)} ---\n{summary}"
        for i, summary in enumerate(chunk_summaries)
    )
    return f"""Merge these {len(chunk_summaries)} summaries from different parts of the same conversation into one clean handoff document.

Rules:
- When summaries conflict, trust the later segment
- Every specific detail must survive: names, numbers, dates, links, terminology, formulas, references — if it appeared in any summary, it must appear in the output
- Deduplicate: each fact appears once, in its most complete form
- Do not add commentary, framing, or transitions — just the content
- Output must be usable as a standalone context document someone can paste into a new AI conversation

Use these sections exactly:

## What This Was Working On

## What Was Figured Out

## Current State

## What Still Needs Doing

## Details That Must Not Be Lost

---

{numbered}
"""
