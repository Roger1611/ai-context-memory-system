def chunk_text(text, max_chars=3000):

    chunks = []
    current_chunk = ""
    lines = text.split("\n")
    for line in lines:

        if len(current_chunk) + len(line) > max_chars:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += "\n" + line
    if current_chunk.strip():
        chunks.append(current_chunk)

    return chunks