def create_memory_packet(
    project,
    topic,
    packet_type,
    content,
    source_conversation,
    source,
):
    return {
        "project": project,
        "topic": topic,
        "type": packet_type,
        "content": content,
        "source_conversation": source_conversation,
        "source": source,
    }
