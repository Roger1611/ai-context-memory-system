def build_extraction_prompt(conversation_text: str):
    return f"""TASK: Write a concise technical project summary.
DO NOT OUTPUT JSON.
Write plain readable Markdown.
Keep the response focused and compact.

Include these exact sections:
### Project Goal & Problem Statement
### Architecture & Important Technical Decisions
### Current Progress (Exactly where we left off)
### Next Steps

Conversation:
{conversation_text}
"""


def build_chunk_summary_prompt(conversation_chunk: str, chunk_number: int, total_chunks: int):
    return f"""TASK: Summarize this chunk of a developer conversation.
This is chunk {chunk_number} of {total_chunks}.
Extract only durable project context and the latest progress described in this chunk.
Do not output JSON.
Write plain readable Markdown with short bullet points.

Include these exact sections:
### Project Goal & Problem Statement
### Architecture & Important Technical Decisions
### Current Progress (Exactly where we left off)
### Next Steps

Conversation Chunk:
{conversation_chunk}
"""
