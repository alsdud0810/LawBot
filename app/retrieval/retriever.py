from collections.abc import Sequence

from app.embeddings.embedder import Embedder
from app.retrieval.vector_store import FaissVectorStore, SearchResult


class Retriever:
    def __init__(self, store: FaissVectorStore, embedder: Embedder, top_k: int = 3, threshold: float = 0.35) -> None:
        self.store = store
        self.embedder = embedder
        self.top_k = top_k
        self.threshold = threshold

    def retrieve(self, question: str) -> list[SearchResult]:
        results = self.store.similarity_search(self.embedder.embed_query(question), self.top_k)
        return [result for result in results if result.score >= self.threshold]
