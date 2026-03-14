import json
import uuid
from datetime import datetime

from scripts.build_index import main as build_index_main
from scripts.generate_dev_snapshot import main as generate_dev_snapshot_main
from scripts.generate_project_snapshot import main as generate_project_snapshot_main
from src.config import PROCESSED_MEMORY_DIR, RAW_CONVO_DIR
from src.extraction.artifact_extractor import (
    describe_file_role,
    extract_code_blocks,
    extract_commands,
    extract_entrypoints,
    extract_file_paths,
    extract_folder_trees,
    extract_module_imports,
)
from src.extraction.memory_extractor import (
    extract_memory_from_conversation,
    save_memory_packets,
)
from src.extraction.schema import create_memory_packet
from src.ingestion.conversation_parser import parse_conversation
from src.ingestion.fetch_share_link import fetch_share_page
from src.utils.packet_deduplicator import remove_duplicate_packets


SESSION_DIR = RAW_CONVO_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def ingest_link(link, source, session_id):
    html = fetch_share_page(link)
    messages = parse_conversation(html)
    convo_id = str(uuid.uuid4())[:8]

    convo = {
        "conversation_id": convo_id,
        "session_id": session_id,
        "source": source,
        "share_link": link,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages,
    }

    session_path = SESSION_DIR / session_id
    session_path.mkdir(exist_ok=True)

    file_path = session_path / f"{convo_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(convo, f, indent=2)

    return file_path


def build_dev_packets(conversation_text, conversation_id):
    packets = []

    folder_trees = extract_folder_trees(conversation_text)
    file_paths = extract_file_paths(conversation_text)
    module_imports = extract_module_imports(conversation_text)
    commands = extract_commands(conversation_text)
    code_blocks = extract_code_blocks(conversation_text)
    entrypoints = extract_entrypoints(
        conversation_text,
        file_paths=file_paths,
        commands=commands,
    )

    print(
        "[DEBUG] Parser Found: "
        f"{len(folder_trees)} Trees, "
        f"{len(file_paths)} Python Files, "
        f"{len(module_imports)} Modules, "
        f"{len(code_blocks)} Code Blocks, "
        f"{len(commands)} Commands, "
        f"{len(entrypoints)} Entry Points."
    )

    for tree in folder_trees:
        packets.append(
            create_memory_packet(
                "ai_context",
                "folder_structure",
                "folder_structure",
                tree,
                conversation_id,
                "dev_extraction",
            )
        )

    for file_path in file_paths:
        packets.append(
            create_memory_packet(
                "ai_context",
                file_path,
                "file_role",
                describe_file_role(file_path),
                conversation_id,
                "dev_extraction",
            )
        )

    for module_name in module_imports:
        packets.append(
            create_memory_packet(
                "ai_context",
                module_name,
                "module_import",
                module_name,
                conversation_id,
                "dev_extraction",
            )
        )

    for command in commands:
        packets.append(
            create_memory_packet(
                "ai_context",
                "command",
                "command",
                command,
                conversation_id,
                "dev_extraction",
            )
        )

    for entrypoint in entrypoints:
        packets.append(
            create_memory_packet(
                "ai_context",
                entrypoint,
                "entrypoint",
                entrypoint,
                conversation_id,
                "dev_extraction",
            )
        )

    for code_block in code_blocks:
        packets.append(
            create_memory_packet(
                "ai_context",
                code_block["filename"],
                "code_block",
                (
                    f"**File:** `{code_block['filename']}`\n\n"
                    f"```{code_block['language']}\n{code_block['code']}\n```"
                ),
                conversation_id,
                "dev_extraction",
            )
        )

    return packets


def main():
    print("\nMemory Sync\n")
    session_id = "session_" + str(uuid.uuid4())[:6]
    links = []

    while True:
        link = input("Chat link: ").strip()
        if link == "":
            break
        links.append(link)

    if not links:
        return

    source = input("\nSource platform (chatgpt / claude / gemini): ")
    files = []

    for link in links:
        file = ingest_link(link, source, session_id)
        files.append(file)
        print(f"[INGESTED] {file.name}")

    print("\nRunning extraction pipeline...\n")

    packet_file = PROCESSED_MEMORY_DIR / "memory_packets.json"
    if packet_file.exists():
        packet_file.unlink()
        print("[INFO] Cleared previous memory packets")

    all_packets = []

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            convo_data = json.load(f)

        convo_id = convo_data["conversation_id"]
        text = "\n".join(
            [message.get("content", "") for message in convo_data.get("messages", [])]
        )

        dev_packets = build_dev_packets(text, convo_id)
        context_packets = extract_memory_from_conversation(file)

        all_packets.extend(dev_packets)
        all_packets.extend(context_packets)

    all_packets = remove_duplicate_packets(all_packets)
    save_memory_packets(all_packets)

    print("[INFO] Building vector index...")
    build_index_main()

    print("[INFO] Generating context snapshot...")
    generate_project_snapshot_main()

    print("[INFO] Generating developer snapshot...")
    generate_dev_snapshot_main()

    print(f"\nSaved {len(all_packets)} memory packets.\n")


if __name__ == "__main__":
    main()
