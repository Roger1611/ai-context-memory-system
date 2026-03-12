from src.ingestion.fetch_share_link import fetch_share_page
from src.ingestion.conversation_parser import parse_conversation
from src.utils.id_generator import generate_conversation_id
from src.config import RAW_CONVO_DIR
import json
from datetime import datetime

def ingest_conversation(share_link: str, source: str):
    print(f"\n[INFO] Processing link: {share_link}")
    html = fetch_share_page(share_link)
    messages = parse_conversation(html)
    conversation_id = generate_conversation_id()
    conversation_data = {
        "conversation_id": conversation_id,
        "source": source,
        "share_link": share_link,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages
    }
    output_file = RAW_CONVO_DIR / f"{conversation_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=2)

    print(f"[SUCCESS] Saved conversation → {output_file}")

def main():
    print("\nPaste AI share links (one per line).")
    print("Press ENTER on an empty line when finished.\n")
    links = []
    while True:
        link = input("Share link: ").strip()
        if not link:
            break
        links.append(link)
    source = input("\nSource platform (chatgpt / claude / gemini): ")

    for link in links:
        ingest_conversation(link, source)

if __name__ == "__main__":
    main()