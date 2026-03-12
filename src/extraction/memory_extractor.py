"""
memory_extractor.py

Converts raw conversations into structured memory packets.
Handles imperfect LLM output safely.
"""

import json
import ast
from pathlib import Path

from src.llm import generate_response
from src.extraction.extraction_prompt import build_extraction_prompt
from src.extraction.schema import create_memory_packet
from src.config import PROCESSED_MEMORY_DIR


def extract_memory_from_conversation(file_path: Path):

    print(f"\n[INFO] Processing conversation: {file_path.name}")

    with open(file_path, "r", encoding="utf-8") as f:
        conversation_data = json.load(f)

    conversation_id = conversation_data["conversation_id"]
    messages = conversation_data["messages"]

    # Combine conversation text
    conversation_text = "\n".join(m["content"] for m in messages)

    prompt = build_extraction_prompt(conversation_text)

    print("[INFO] Sending conversation to LLM...")

    response = generate_response(prompt)

    print("\n[DEBUG] MODEL RESPONSE:\n")
    print(response)

    # -------------------------------
    # Robust parsing of model output
    # -------------------------------
    try:

        # Case 1: Already a Python object (if generate_response parsed JSON)
        if isinstance(response, list):
            extracted_items = response

        # Case 2: Try standard JSON
        else:
            try:
                extracted_items = json.loads(response)
            except Exception:
                # Case 3: Python literal (single quotes)
                extracted_items = ast.literal_eval(response)

        if not isinstance(extracted_items, list):
            raise ValueError("Model output is not a list")

    except Exception as e:

        print("[WARNING] Failed to parse model output")
        print(e)
        return []

    packets = []

    for item in extracted_items:

        # Defensive parsing
        topic = item.get("topic", "general")
        packet_type = item.get("type", "knowledge")
        content = str(item.get("content", "")).strip()

        if not content:
            continue

        packet = create_memory_packet(
            project="ai_context_memory_system",
            topic=topic,
            packet_type=packet_type,
            content=content,
            source_conversation=conversation_id
        )

        packets.append(packet)

    print(f"[INFO] Extracted {len(packets)} memory packets")

    return packets


def save_memory_packets(packets):

    output_file = PROCESSED_MEMORY_DIR / "memory_packets.json"

    if output_file.exists():

        with open(output_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

    else:
        existing = []

    existing.extend(packets)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    print(f"[SUCCESS] Stored {len(packets)} memory packets")