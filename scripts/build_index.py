#Build FAISS index from memory packets.
import json
from src.config import PROCESSED_MEMORY_DIR
from src.retrieval.embedding_model import EmbeddingModel
from src.retrieval.vector_index import VectorIndex

def main():
    path = PROCESSED_MEMORY_DIR / "memory_packets.json"
    with open(path) as f:
        packets = json.load(f)
    texts = [p["content"] for p in packets]
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.embed_text(texts)
    dimension = len(embeddings[0])
    index = VectorIndex(dimension)
    index.add_vectors(embeddings)
    index.save(packets)

if __name__ == "__main__":
    main()