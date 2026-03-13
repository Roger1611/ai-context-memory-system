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

        #CONTEXT KNOWLEDGE
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
        "limitations",

        # DEVELOPER KNOWLEDGE
        "folder_structure",
        "file_role",
        "dependency",
        "setup_step",
        "workflow",
        "entrypoint",
        "command"
    ]

    print("\nPROJECT CONTEXT SNAPSHOT\n")
    output_lines = []
    output_lines.append("PROJECT CONTEXT SNAPSHOT\n")
    for topic in ordered_topics:

        title = topic.replace("_", " ").title()
        print(title)
        output_lines.append(title)

        if topic in topics:

            for item in topics[topic]:

                print(f"- {item}")
                output_lines.append(f"- {item}")

        else:

            print("- information not available yet")
            output_lines.append("- information not available yet")
        print()
        output_lines.append("")

    snapshot_file = PROCESSED_MEMORY_DIR / "context_snapshot.txt"

    with open(snapshot_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"[SNAPSHOT SAVED] {snapshot_file}\n")


if __name__ == "__main__":
    main()