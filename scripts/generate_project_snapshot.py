import json
import sys
from src.config import PROCESSED_MEMORY_DIR


def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(encoding)
        print(safe_text)

def main():
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"
    if not path.exists(): return
    with open(path) as f: packets = json.load(f)

    ctx_packets = [p for p in packets if p.get("source") == "context_extraction"]
    
    out = ["PROJECT CONTEXT SNAPSHOT\n=========================\n"]
    for p in ctx_packets: out.append(p.get("content", "") + "\n")
    
    text = "\n".join(out)
    _safe_print(text)
    
    with open(PROCESSED_MEMORY_DIR / "context_snapshot.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    main()
