from pathlib import Path

import numpy as np

from app.embeddings.embedder import Embedder
from app.ingestion.metadata import Chunk, DocumentMetadata
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore


class FakeEmbedder:
    dimension = 2

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return np.asarray([[1.0, 0.0] if "wage" in text else [0.0, 1.0] for text in texts], dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        return np.asarray([1.0, 0.0] if "wage" in text else [0.0, 1.0], dtype="float32")


def make_chunks() -> list[Chunk]:
    metadata = DocumentMetadata("Labor Act", article="Article 36", source_url="https://example.gov")
    return [Chunk("wage", "wage payment", metadata), Chunk("safety", "workplace safety", metadata)]


def test_faiss_save_load_and_retrieve(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = FaissVectorStore(embedder.dimension)
    chunks = make_chunks()
    store.add_documents(chunks, embedder.embed_documents([chunk.text for chunk in chunks]))
    store.save(tmp_path)

    loaded = FaissVectorStore.load(tmp_path)
    results = Retriever(loaded, embedder, top_k=1, threshold=0.9).retrieve("wage question")
    assert len(results) == 1
    assert results[0].chunk_id == "wage"
    assert results[0].metadata["article"] == "Article 36"


def test_retriever_applies_evidence_threshold() -> None:
    embedder = FakeEmbedder()
    store = FaissVectorStore(embedder.dimension)
    chunks = make_chunks()
    store.add_documents(chunks, embedder.embed_documents([chunk.text for chunk in chunks]))
    assert Retriever(store, embedder, threshold=1.01).retrieve("wage question") == []
