import json
from collections import defaultdict
from src.config import PROCESSED_MEMORY_DIR
def main():
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"
    with open(path) as f:
        packets = json.load(f)
    topics = defaultdict(list)
    for packet in packets:
        topics[packet["topic"]].append(packet["content"])
    print("\nFULL PROJECT CONTEXT\n")
    print("Project Knowledge Extracted From AI Conversations\n")
    for topic, items in topics.items():
        print(topic)
        for item in items:
            print(f"- {item}")

        print()


if __name__ == "__main__":
    main()