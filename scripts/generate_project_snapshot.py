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
    ordered_topics = [
        "project_goal",
        "problem_statement",
        "architecture",
        "repository_structure",
        "completed_components",
        "current_progress",
        "important_decisions",
        "experimental_results",
        "datasets",
        "algorithms",
        "open_questions",
        "next_steps",
        "limitations"
    ]
    print("\nPROJECT CONTEXT SNAPSHOT\n")
    for topic in ordered_topics:
        if topic in topics:
            title = topic.replace("_", " ").title()
            print(title)
            for item in topics[topic]:
                print(f"- {item}")
            print()
        else:
            print(f"{topic.replace('_',' ').title()}")
            print("- information not available yet\n")

if __name__ == "__main__":
    main()