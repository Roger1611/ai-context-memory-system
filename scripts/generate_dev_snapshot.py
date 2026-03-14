import json
import sys

from src.config import PROCESSED_MEMORY_DIR


def _collect(dev_packets, packet_type):
    return [packet for packet in dev_packets if packet.get("type") == packet_type]


def _path_from_file_role(content):
    path, _, _ = content.partition(" - ")
    return path.strip()


def _dedupe_file_roles(file_roles):
    preferred = {}
    order = []

    for packet in file_roles:
        path = _path_from_file_role(packet.get("content", ""))
        if not path:
            continue

        key = path.split("/")[-1]
        current = preferred.get(key)
        if current is None:
            preferred[key] = packet
            order.append(key)
            continue

        current_path = _path_from_file_role(current.get("content", ""))
        if "/" in path and "/" not in current_path:
            preferred[key] = packet

    return [preferred[key] for key in order]


def _dedupe_entrypoints(entrypoints):
    preferred = {}
    order = []

    for packet in entrypoints:
        path = packet.get("content", "").strip()
        if not path:
            continue

        key = path.split("/")[-1]
        current = preferred.get(key)
        if current is None:
            preferred[key] = packet
            order.append(key)
            continue

        current_path = current.get("content", "").strip()
        if "/" in path and "/" not in current_path:
            preferred[key] = packet

    return [preferred[key] for key in order]


def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(encoding)
        print(safe_text)


def main():
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"

    if not path.exists():
        print("No memory packets found.")
        return

    with open(path, encoding="utf-8") as f:
        packets = json.load(f)

    dev_packets = [p for p in packets if p.get("source") == "dev_extraction"]
    trees = _collect(dev_packets, "folder_structure")
    file_roles = _dedupe_file_roles(_collect(dev_packets, "file_role"))
    commands = _collect(dev_packets, "command")
    entrypoints = _dedupe_entrypoints(_collect(dev_packets, "entrypoint"))
    code_blocks = _collect(dev_packets, "code_block")

    out = [
        "DEVELOPER KNOWLEDGE & LATEST REPO INFO\n"
        "========================================\n"
    ]

    out.append("### FOLDER STRUCTURE\n")
    if trees:
        for tree in trees:
            out.append(tree.get("content", "") + "\n")
    else:
        out.append("No folder structure detected.\n")

    out.append("\n### FILE ROLES\n")
    if file_roles:
        for file_role in file_roles:
            out.append(f"- {file_role.get('content', '')}\n")
    else:
        out.append("No python file roles detected.\n")

    out.append("\n### COMMANDS\n")
    if commands:
        for command in commands:
            out.append(f"`{command.get('content', '')}`\n")
    else:
        out.append("No commands detected.\n")

    out.append("\n### ENTRY POINTS\n")
    if entrypoints:
        for entrypoint in entrypoints:
            out.append(f"- {entrypoint.get('content', '')}\n")
    else:
        out.append("No entry points detected.\n")

    out.append("\n### CODE BLOCKS\n")
    if code_blocks:
        for code_block in code_blocks:
            out.append(code_block.get("content", "") + "\n\n")
    else:
        out.append("No code blocks detected.\n")

    text = "\n".join(out)

    _safe_print(text)

    with open(
        PROCESSED_MEMORY_DIR / "developer_snapshot.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)


if __name__ == "__main__":
    main()
