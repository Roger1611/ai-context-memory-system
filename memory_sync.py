import uuid
import json
from datetime import datetime
from pathlib import Path
from src.ingestion.fetch_share_link import fetch_share_page
from src.ingestion.conversation_parser import parse_conversation
from src.extraction.memory_extractor import extract_memory_from_conversation, save_memory_packets
from src.extraction.dev_memory_extractor import extract_dev_knowledge
from src.utils.conversation_chunker import chunk_text
from src.utils.packet_deduplicator import remove_duplicate_packets
from src.config import RAW_CONVO_DIR

SESSION_DIR = RAW_CONVO_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

def ingest_link(link, source, session_id):

    html = fetch_share_page(link)
    messages = parse_conversation(html)
    conversation_id = str(uuid.uuid4())[:8]

    convo = {
        "conversation_id": conversation_id,
        "session_id": session_id,
        "source": source,
        "share_link": link,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages
    }

    session_path = SESSION_DIR / session_id
    session_path.mkdir(exist_ok=True)
    file_path = session_path / f"{conversation_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(convo, f, indent=2)

    return file_path

def main():

    print("\nMemory Sync\n")
    session_id = "session_" + str(uuid.uuid4())[:6]
    print(f"Session created: {session_id}\n")
    print("Paste chat links. Press ENTER when finished.\n")
    links = []
    while True:

        link = input("Chat link: ").strip()
        if link == "":
            break
        links.append(link)

    source = input("\nSource platform (chatgpt / claude / gemini): ")
    files = []
    for link in links:

        file_path = ingest_link(link, source, session_id)
        files.append(file_path)
        print(f"[INGESTED] {file_path.name}")

    print("\nRunning memory extraction...\n")
    from src.config import PROCESSED_MEMORY_DIR

    packet_file = PROCESSED_MEMORY_DIR / "memory_packets.json"

    if packet_file.exists():
        packet_file.unlink()
        print("[INFO] Cleared previous memory packets")
    packets = []

    for file in files:

        context_packets = extract_memory_from_conversation(file)
        with open(file, "r", encoding="utf-8") as f:
            convo_data = json.load(f)
        conversation_text = "\n".join(
            [m["content"] for m in convo_data["messages"] if "content" in m]
        )

        chunks = chunk_text(conversation_text)
        dev_packets = []

        for chunk in chunks:
            extracted = extract_dev_knowledge(chunk)

            if extracted:
                dev_packets.extend(extracted)

        for p in context_packets:
            p["source"] = "context_extraction"

        for p in dev_packets:
            p["source"] = "dev_extraction"
        packets.extend(context_packets)
        packets.extend(dev_packets)

    packets = remove_duplicate_packets(packets)
    save_memory_packets(packets)
    print("\nUpdating vector index...\n")
    from scripts.build_index import main as build_index
    build_index()
    print("\nGenerating project snapshot...\n")

    from scripts.generate_project_snapshot import main as snapshot

    snapshot()
    print("\nGenerating developer snapshot...\n")

    from scripts.generate_dev_snapshot import main as dev_snapshot

    dev_snapshot()
    print("\nMemory sync complete.\n")

if __name__ == "__main__":
    main()