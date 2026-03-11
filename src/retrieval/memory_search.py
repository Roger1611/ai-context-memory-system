#Loads the persistent FAISS index and performs semantic search over stored memory packets.
from src.retrieval.embedding_model import EmbeddingModel
from src.retrieval.vector_index import VectorIndex
class MemorySearch:
    def __init__(self):

       
        self.embedding_model = EmbeddingModel()
        self.index = VectorIndex(384)
        self.memory_packets = self.index.load()
        if self.memory_packets is None:
            raise RuntimeError(
                "FAISS index not found. Run `python -m scripts.build_index` first."
            )
    def search(self, query, top_k=3):

        query_embedding = self.embedding_model.embed_text([query])[0]
        indices = self.index.search(query_embedding, top_k)
        results = []
        for i in indices:
            if i < len(self.memory_packets):
                results.append(self.memory_packets[i])
        return results