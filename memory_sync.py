import json
import sys
import uuid
from datetime import datetime

from scripts.build_index import main as build_index_main
from scripts.generate_project_snapshot import main as generate_project_snapshot_main
from src.config import PROCESSED_MEMORY_DIR, RAW_CONVO_DIR
from src.extraction.memory_extractor import (
    extract_memory_from_conversation,
    save_memory_packets,
)
from src.ingestion.conversation_parser import parse_conversation
from src.ingestion.fetch_share_link import fetch_share_page
from src.utils.packet_deduplicator import remove_duplicate_packets


SESSION_DIR = RAW_CONVO_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def ingest_link(link, source, session_id):
    html = fetch_share_page(link)
    messages = parse_conversation(html, source=source)
    convo_id = str(uuid.uuid4())[:8]

    convo = {
        "conversation_id": convo_id,
        "session_id": session_id,
        "source": source,
        "share_link": link,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages,
    }

    session_path = SESSION_DIR / session_id
    session_path.mkdir(exist_ok=True)

    file_path = session_path / f"{convo_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(convo, f, indent=2)

    return file_path


def main():
    print("\nMemory Sync\n")
    session_id = "session_" + str(uuid.uuid4())[:6]
    links = []

    while True:
        link = input("Chat link: ").strip()
        if link == "":
            break
        links.append(link)

    if not links:
        return

    source = input("\nSource platform (chatgpt / claude / gemini): ").strip()
    files = []

    for link in links:
        try:
            file = ingest_link(link, source, session_id)
            files.append(file)
            print(f"[INGESTED] {file.name}")
        except Exception as e:
            print(f"[WARN] Failed to ingest {link}: {e}")
            continue

    if not files:
        print("[ERROR] No conversations successfully ingested. Aborting.")
        return

    print("\nRunning extraction pipeline...\n")

    all_packets = []

    for file in files:
        try:
            context_packets = extract_memory_from_conversation(file)
            all_packets.extend(context_packets)
        except Exception as e:
            print(f"[ERROR] Extraction failed for {file.name}: {e}")
            continue

    if not all_packets:
        print("[ERROR] No memory packets extracted. Aborting — existing data preserved.")
        return

    all_packets = remove_duplicate_packets(all_packets)
    save_memory_packets(all_packets)

    print("[INFO] Building vector index...")
    build_index_main()

    print("[INFO] Generating context snapshot...")
    generate_project_snapshot_main()

    print(f"\nSaved {len(all_packets)} memory packets.\n")


def preview():
    """Print the last generated snapshot without running the pipeline."""
    out_path = PROCESSED_MEMORY_DIR / "context_snapshot.txt"
    if not out_path.exists():
        print("[WARN] No snapshot found. Run the pipeline first: python memory_sync.py")
        return
    print(out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview()
    else:
        main()
