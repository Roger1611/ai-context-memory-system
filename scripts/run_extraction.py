
from pathlib import Path
from src.config import RAW_CONVO_DIR
from src.extraction.memory_extractor import (
    extract_memory_from_conversation,
    save_memory_packets
)

def main():
    print("\nScanning conversations...\n")
    files = list(Path(RAW_CONVO_DIR).rglob("*.json"))
    if not files:
        print("No conversations found.")
        return

    all_packets = []

    for file in files:
        packets = extract_memory_from_conversation(file)
        all_packets.extend(packets)
    save_memory_packets(all_packets)

if __name__ == "__main__":
    main()