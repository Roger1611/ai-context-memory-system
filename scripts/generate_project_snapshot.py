import json
import sys
from datetime import datetime, timezone

from src.config import PROCESSED_MEMORY_DIR


def _build_snapshot(packets: list[dict]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    source_id = packets[0].get("source_conversation", "unknown") if packets else "unknown"
    header = f"Project Context - generated {timestamp} - source conversation: {source_id}"

    sections = [
        packet.get("content", "").strip()
        for packet in packets
        if packet.get("content", "").strip()
    ]
    body = "\n\n".join(sections)

    return header + "\n\n" + body + "\n"


def _print_preview(snapshot: str) -> None:
    lines = snapshot.splitlines()
    preview_lines = lines[:60]
    output = "\n" + "\n".join(preview_lines)
    if len(lines) > 60:
        output += f"\n\n... ({len(lines) - 60} more lines - open the file to see the full snapshot)"
    sys.stdout.buffer.write(output.encode(sys.stdout.encoding or "utf-8", errors="replace") + b"\n")


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
