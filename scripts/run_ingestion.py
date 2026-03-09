"""
runs the conversation ingestion pipeline.

Steps:
Share Link
-Headless Browser
-Conversation Extraction
-Stre in JSON format
"""

import json
from datetime import datetime, timezone

from src.ingestion.fetch_share_link import fetch_share_page
from src.ingestion.conversation_parser import parse_conversation
from src.utils.id_generator import generate_conversation_id
from src.config import RAW_CONVO_DIR


def ingest_conversation(share_link: str, source: str):


    print("\n[STEP 1] Fetching conversation page...")

    html = fetch_share_page(share_link)

    print("[STEP 2] Parsing conversation...")

    messages = parse_conversation(html)

    print(f"[INFO] Extracted {len(messages)} message blocks")

    conversation_id = generate_conversation_id()

    conversation_data = {
        "conversation_id": conversation_id,
        "source": source,
        "share_link": share_link,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "messages": messages
    }

    output_file = RAW_CONVO_DIR / f"{conversation_id}.json"

    print("[STEP 3] Saving conversation...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=2)

    print(f"[SUCCESS] Conversation saved → {output_file}")



if __name__ == "__main__":

    share_link = input("Paste AI share link: ")
    source = input("Source platform (chatgpt / claude / gemini): ")

    ingest_conversation(share_link, source)