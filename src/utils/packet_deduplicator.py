def remove_duplicate_packets(packets):

    seen = set()
    unique_packets = []
    for packet in packets:
        key = (
            packet.get("topic", "").strip(),
            packet.get("type", "").strip(),
            packet.get("content", "").strip()
        )
        if key not in seen:
            seen.add(key)
            unique_packets.append(packet)
    return unique_packets