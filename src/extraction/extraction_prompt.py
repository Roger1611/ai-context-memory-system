def build_extraction_prompt(conversation_text: str) -> str:
    return f"""GROUNDING CONSTRAINT: Only extract information that is explicitly present in the conversation text provided below. Do not use outside knowledge, assumptions, or inferences. If a section has no relevant content in the conversation, write exactly "Nothing in this conversation." for that section.

Read this conversation and extract everything that would be needed to continue this work in a new conversation.

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

---

CRITICAL: Fabricating, inferring, or adding anything not explicitly stated in the conversation above is a critical failure. Every sentence in your output must be directly traceable to something said in the conversation.
"""


def build_chunk_summary_prompt(conversation_chunk: str, chunk_number: int, total_chunks: int) -> str:
    return f"""This is segment {chunk_number} of {total_chunks} from a longer conversation.

GROUNDING CONSTRAINT: Only report what is explicitly stated in this segment. Do not infer, assume, or add outside knowledge. If the segment contains no facts, decisions, or conclusions, output only "Nothing in this segment."

Extract every fact, decision, and conclusion from this segment. Do not summarize discussion or questions — only record what was established or agreed.

Rules:
- Dense bullet points only, no prose
- Preserve exact names, numbers, dates, links, terms, and references as they appeared
- Mark definite decisions or conclusions with [DECIDED]
- Mark open questions or unresolved points with [OPEN]
- If something is uncertain, note the uncertainty — do not smooth it over

Segment {chunk_number} of {total_chunks}:
{conversation_chunk}

CRITICAL: Every bullet point must be directly traceable to something explicitly stated in the segment above. Do not infer, extrapolate, or add anything not present in the text.
"""


def build_synthesis_prompt(chunk_summaries: list[str]) -> str:
    numbered = "\n\n".join(
        f"--- Segment {i + 1} of {len(chunk_summaries)} ---\n{summary}"
        for i, summary in enumerate(chunk_summaries)
    )
    return f"""Merge these {len(chunk_summaries)} summaries from different parts of the same conversation into one clean handoff document.

GROUNDING CONSTRAINT: Only include information that is explicitly present in the summaries below. Do not use outside knowledge, assumptions, or inferences. If no content exists for a section across all summaries, omit that section entirely — do not fill it with inferred or fabricated content.

Rules:
- When summaries conflict, trust the later segment
- Every specific detail must survive: names, numbers, dates, links, terminology, formulas, references — if it appeared in any summary, it must appear in the output
- Deduplicate: each fact appears once, in its most complete form
- Do not add commentary, framing, or transitions — just the content
- Output must be usable as a standalone context document someone can paste into a new AI conversation
- If a section has no content from any summary, omit it entirely rather than writing a placeholder

Use these sections where content exists:

## What This Was Working On

## What Was Figured Out

## Current State

## What Still Needs Doing

## Details That Must Not Be Lost

---

{numbered}

CRITICAL: Every statement in your output must be directly traceable to the summaries above. Fabricating, inferring, or adding anything not present in the provided summaries is a critical failure.
"""
