import json
from collections import defaultdict
from src.config import PROCESSED_MEMORY_DIR


def main():

    path = PROCESSED_MEMORY_DIR / "memory_packets.json"

    with open(path) as f:
        packets = json.load(f)

    dev_packets = [p for p in packets if p.get("source") == "dev_extraction"]

    grouped = defaultdict(list)

    for packet in dev_packets:
        grouped[packet["type"]].append(packet["content"])

    ordered_sections = [
        "folder_structure",
        "file_role",
        "dependency",
        "setup_step",
        "workflow",
        "entrypoint",
        "command"
    ]

    print("\nDEVELOPER KNOWLEDGE SNAPSHOT\n")

    output = []
    output.append("DEVELOPER KNOWLEDGE SNAPSHOT\n")

    for section in ordered_sections:

        title = section.replace("_", " ").title()
        print(title)
        output.append(title)

        if section in grouped:
            for item in grouped[section]:
                print(f"- {item}")
                output.append(f"- {item}")
        else:
            print("- information not available yet")
            output.append("- information not available yet")

        print()
        output.append("")

    snapshot_file = PROCESSED_MEMORY_DIR / "developer_snapshot.txt"

    with open(snapshot_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"[DEV SNAPSHOT SAVED] {snapshot_file}\n")


if __name__ == "__main__":
    main()