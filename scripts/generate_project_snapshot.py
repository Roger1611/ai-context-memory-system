import json
from datetime import datetime, timezone

from src.config import OPENROUTER_MODEL, PROCESSED_MEMORY_DIR

SEPARATOR = "=" * 60


def _build_snapshot(packets: list[dict]) -> str:
    source_convos = list(dict.fromkeys(
        p.get("source_conversation", "unknown") for p in packets
    ))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    convo_count = len(source_convos)

    intro = (
        "This file contains context extracted from "
        + ("one previous AI conversation" if convo_count == 1 else f"{convo_count} previous AI conversations")
        + ". It captures the key decisions, current state, open questions, and next actions discussed. "
        "To continue your work in a new AI session, copy everything below the dashed line and paste it "
        "at the start of your next conversation."
    )

    meta = "\n".join([
        f"Generated:            {timestamp}",
        f"Source conversations: {convo_count}",
        f"Model:                {OPENROUTER_MODEL}",
    ])

    sections = []
    for i, packet in enumerate(packets, start=1):
        content = packet.get("content", "").strip()
        if not content:
            continue
        if len(packets) > 1:
            convo_id = packet.get("source_conversation", "unknown")
            label = f"{'─' * 40}\nSession {i} (id: {convo_id})\n{'─' * 40}"
            sections.append(f"{label}\n\n{content}")
        else:
            sections.append(content)

    body = "\n\n".join(sections)

    ready_prompt = (
        "─" * 40 + "\n"
        "READY-TO-USE PROMPT\n"
        "─" * 40 + "\n"
        "Copy and paste the following at the start of your next AI conversation:\n\n"
        "Here is context from a previous conversation. Please read it carefully before we continue:\n\n"
        + body
    )

    return "\n\n".join([
        intro,
        SEPARATOR,
        meta,
        SEPARATOR,
        body,
        SEPARATOR,
        ready_prompt,
    ]) + "\n"


def _print_preview(snapshot: str) -> None:
    lines = snapshot.splitlines()
    preview_lines = lines[:60]
    print("\n" + "\n".join(preview_lines))
    if len(lines) > 60:
        print(f"\n... ({len(lines) - 60} more lines — open the file to see the full snapshot)")


def main(print_preview: bool = True) -> None:
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"
    if not path.exists():
        print("[WARN] No memory_packets.json found. Run the pipeline first.")
        return

    with open(path, encoding="utf-8") as f:
        packets = json.load(f)

    ctx_packets = [p for p in packets if p.get("source") == "context_extraction"]

    if not ctx_packets:
        print("[WARN] No context_extraction packets found in memory_packets.json.")
        return

    snapshot = _build_snapshot(ctx_packets)

    out_path = PROCESSED_MEMORY_DIR / "context_snapshot.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(snapshot)

    print(f"[INFO] Context snapshot saved to {out_path.resolve()}")

    if print_preview:
        _print_preview(snapshot)


if __name__ == "__main__":
    main()
