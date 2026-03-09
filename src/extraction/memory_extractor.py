
import json
from pathlib import Path
from src.llm import generate_response
from src.extraction.extraction_prompt import build_extraction_prompt
from src.extraction.schema import create_memory_packet
from src.config import RAW_CONVO_DIR, PROCESSED_MEMORY_DIR

def extract_memory_from_conversation(file_path: Path):

    print(f"\n[INFO] Processing conversation: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        conversation_data = json.load(f)
    conversation_id = conversation_data["conversation_id"]
    messages = conversation_data["messages"]
    conversation_text = "\n".join(
        m["content"] for m in messages
    )

    prompt = build_extraction_prompt(conversation_text)
    print("[INFO] Sending conversation to LLM...")
    response = generate_response(prompt)

    import re

    try:
        json_match = re.search(r"\[.*\]", response, re.DOTALL)

        if not json_match:
            raise ValueError("No JSON array found in response")

        json_text = json_match.group(0)

        extracted_items = json.loads(json_text)

    except Exception:

        print("[WARNING] Model returned unparsable output")
        print(response)
        return []

    packets = []

    for item in extracted_items:

        packet = create_memory_packet(
            project="default_project",
            topic=item["topic"],
            packet_type=item["type"],
            content=item["content"],
            source_conversation=conversation_id
        )

        packets.append(packet)
    return packets


def save_memory_packets(packets):

    output_file = PROCESSED_MEMORY_DIR / "memory_packets.json"

    if output_file.exists():

        with open(output_file, "r") as f:
            existing = json.load(f)

    else:
        existing = []

    existing.extend(packets)

    with open(output_file, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"[SUCCESS] Stored {len(packets)} memory packets")