from sentence_transformers import SentenceTransformer
import torch

class EmbeddingModel:

    def __init__(self):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"[INFO] Loading embedding model on {device}")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device=device
        )

    def embed_text(self, texts):

        if isinstance(texts, str):
            texts = [texts]

        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )