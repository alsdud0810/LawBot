from collections.abc import Sequence
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    dimension: int

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray: ...

    def embed_query(self, text: str) -> np.ndarray: ...


class BgeM3Embedder:
    def __init__(self, model_name: str = "BAAI/bge-m3", batch_size: int = 1, device: str = "cpu") -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return np.asarray(
            self.model.encode(list(texts), batch_size=self.batch_size, normalize_embeddings=True, show_progress_bar=True),
            dtype="float32",
        )

    def embed_query(self, text: str) -> np.ndarray:
        return np.asarray(self.model.encode([text], normalize_embeddings=True)[0], dtype="float32")
