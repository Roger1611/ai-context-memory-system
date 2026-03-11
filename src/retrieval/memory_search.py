import json
from src.config import PROCESSED_MEMORY_DIR
from src.retrieval.embedding_model import EmbeddingModel
from src.retrieval.vector_index import VectorIndex
class MemorySearch:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.memory_packets = self.load_memory()
        texts = [packet["content"] for packet in self.memory_packets]
        embeddings = self.embedding_model.embed_text(texts)
        self.index = VectorIndex(len(embeddings[0]))
        self.index.add_vectors(embeddings)
    def load_memory(self):
        path = PROCESSED_MEMORY_DIR / "memory_packets.json"
        with open(path, "r") as f:
            return json.load(f)

    def search(self, query, top_k=3):

        query_embedding = self.embedding_model.embed_text([query])[0]

        indices = self.index.search(query_embedding, top_k)
        results = []
        for i in indices:
            if i < len(self.memory_packets):

                results.append(self.memory_packets[i])
        return results