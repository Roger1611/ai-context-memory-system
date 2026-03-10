#Handles text embedding generation.
from sentence_transformers import SentenceTransformer
class EmbeddingModel:
    def __init__(self):
        # Small fast embedding model
        self.model = SentenceTransformer(
        )
    def embed_text(self, texts):

        return self.model.encode(texts)