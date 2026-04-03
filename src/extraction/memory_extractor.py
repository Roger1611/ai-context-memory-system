import json
from pathlib import Path

from src.llm import generate_response
from src.extraction.extraction_prompt import (
    build_chunk_summary_prompt,
    build_extraction_prompt,
    build_synthesis_prompt,
)
from src.extraction.schema import create_memory_packet
from src.config import PROCESSED_MEMORY_DIR
from src.utils.conversation_chunker import chunk_text


def _synthesize(summaries: list[str], label: str) -> str:
    print(f"[INFO] Synthesizing {len(summaries)} {label}...")
    prompt = build_synthesis_prompt(summaries)
    try:
        result = generate_response(prompt).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to synthesize {label}: {e}") from e
    return result


def _build_context_source_text(text: str) -> str:
    chunks = chunk_text(text, max_chars=24000)
    if len(chunks) <= 1:
        return text

    total = len(chunks)
    print(f"[INFO] Conversation is large ({total} chunks). Summarizing each chunk first...")

    chunk_summaries = []
    for index, chunk in enumerate(chunks, start=1):
        print(f"[INFO] Processing chunk {index} of {total}...")
        prompt = build_chunk_summary_prompt(chunk, index, total)
        try:
            summary = generate_response(prompt).strip()
        except Exception as e:
            raise RuntimeError(f"Failed to summarize chunk {index}/{total}: {e}") from e
        chunk_summaries.append(summary)

    # For very large conversations (>6 chunks), do an intermediate pair-wise synthesis
    # before the final synthesis to keep each prompt manageable
    if len(chunk_summaries) > 6:
        print(f"[INFO] Large conversation detected ({len(chunk_summaries)} chunks). Running intermediate pair synthesis...")
        paired: list[str] = []
        for i in range(0, len(chunk_summaries), 2):
            pair = chunk_summaries[i:i + 2]
            if len(pair) == 1:
                paired.append(pair[0])
            else:
                paired.append(_synthesize(pair, f"chunks {i + 1}–{i + 2}"))
        chunk_summaries = paired

    return _synthesize(chunk_summaries, "chunk summaries")


def extract_memory_from_conversation(file_path: Path):
    print(f"\n[INFO] Extracting Context Summary from: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    convo_id = data.get("conversation_id", "unknown")
    text = "\n".join([m.get("content", "") for m in data.get("messages", [])])

    context_source_text = _build_context_source_text(text)
    prompt = build_extraction_prompt(context_source_text)

    print("[INFO] Generating fluid text summary with Context LLM...")
    try:
        response = generate_response(prompt).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to generate context summary: {e}") from e

    if len(response) < 100:
        raise RuntimeError(
            f"Model returned insufficient content ({len(response)} characters). "
            f"Response: {response!r}"
        )

    refusal_phrases = ("i cannot", "i'm unable", "i don't have enough")
    if any(phrase in response.lower() for phrase in refusal_phrases):
        raise RuntimeError(
            f"Model refused to extract content. Response: {response!r}"
        )

    word_count = len(response.split())
    print(f"[INFO] Extracted {len(response)} characters ({word_count} words) of context.")

    packet = create_memory_packet(
        "ai_context",
        "context_summary",
        "summary",
        response,
        convo_id,
        "context_extraction",
    )
    return [packet]


def save_memory_packets(packets):
    out = PROCESSED_MEMORY_DIR / "memory_packets.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(packets, f, indent=2)
