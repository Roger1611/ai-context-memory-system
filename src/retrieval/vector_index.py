#Manages persistent FAISS vector index.
import json
import faiss
import numpy as np
from src.config import VECTOR_INDEX_DIR
class VectorIndex:

    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.index_path = VECTOR_INDEX_DIR / "faiss_index.bin"
        self.meta_path = VECTOR_INDEX_DIR / "metadata.json"

    def add_vectors(self, vectors):
        vectors = np.array(vectors).astype("float32")
        self.index.add(vectors)
    def save(self, metadata):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print("[INFO] FAISS index saved")

    def load(self):
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.meta_path) as f:
                metadata = json.load(f)

            print("[INFO] FAISS index loaded")
            return metadata
        return None
    def search(self, query_vector, top_k=5):
        query_vector = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        return indices[0]