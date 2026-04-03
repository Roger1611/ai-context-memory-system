import re

# Blank line(s) between turns — a reliable turn boundary signal
_TURN_BOUNDARY = re.compile(r'\n{2,}')

OVERLAP_CHARS = 500


def chunk_text(text: str, max_chars: int = 24000) -> list[str]:
    """
    Split text into chunks of at most max_chars characters.

    Strategy:
    1. Split the text into turn-level blocks (separated by blank lines).
    2. Pack turns into chunks greedily without exceeding max_chars.
    3. If a single turn exceeds max_chars, split it by lines as a last resort.
    4. Prepend the last OVERLAP_CHARS characters of the previous chunk to each
       subsequent chunk to prevent context loss at boundaries.
    """
    turns = [t.strip() for t in _TURN_BOUNDARY.split(text) if t.strip()]

    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    def flush():
        if current_parts:
            chunks.append("\n\n".join(current_parts))

    for turn in turns:
        if len(turn) > max_chars:
            # Oversized single turn — flush current chunk, then split turn by lines
            flush()
            current_parts = []
            current_len = 0

            lines = turn.split("\n")
            sub_parts: list[str] = []
            sub_len = 0
            for line in lines:
                if sub_len + len(line) + 1 > max_chars and sub_parts:
                    chunks.append("\n".join(sub_parts))
                    sub_parts = [line]
                    sub_len = len(line)
                else:
                    sub_parts.append(line)
                    sub_len += len(line) + 1
            if sub_parts:
                chunks.append("\n".join(sub_parts))
            continue

        # Normal turn: fits within max_chars
        if current_len + len(turn) + 2 > max_chars and current_parts:
            flush()
            current_parts = [turn]
            current_len = len(turn)
        else:
            current_parts.append(turn)
            current_len += len(turn) + 2  # +2 for "\n\n" separator

    flush()

    if len(chunks) <= 1:
        return chunks

    # Add overlap: prepend tail of previous chunk to each subsequent chunk
    overlapped: list[str] = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-OVERLAP_CHARS:]
        overlapped.append(f"[...continued]\n{tail}\n\n{chunks[i]}")

    return overlapped
