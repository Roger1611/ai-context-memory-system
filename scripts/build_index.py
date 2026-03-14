#Build FAISS index from memory packets.
import json
from src.config import PROCESSED_MEMORY_DIR
from src.retrieval.embedding_model import EmbeddingModel
from src.retrieval.vector_index import VectorIndex

def main():
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"
    if not path.exists():
        print("[WARN] No memory packet file found. Skipping index build.")
        return

    with open(path) as f:
        packets = json.load(f)

    if not packets:
        print("[WARN] No packets available for indexing")
        return

    texts = [p["content"] for p in packets]
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.embed_text(texts)
    if len(embeddings) == 0:
        print("[WARN] No packets available for indexing")
        return
    dimension = len(embeddings[0])
    index = VectorIndex(dimension)
    index.add_vectors(embeddings)
    try:
        index.save(packets)
    except OSError as exc:
        print(f"[WARN] Unable to save vector index: {exc}")

if __name__ == "__main__":
    main()
