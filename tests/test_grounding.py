import numpy as np

from app.ingestion.metadata import Chunk, DocumentMetadata
from app.models.response import ChatResponse
from app.rag.generator import DeterministicGenerator
from app.rag.grounding import refusal_message
from app.rag.pipeline import RagPipeline
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore


class FakeEmbedder:
    dimension = 2

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return np.asarray([[1.0, 0.0] for _ in texts], dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        return np.asarray([1.0, 0.0], dtype="float32")


def test_pipeline_refuses_without_evidence() -> None:
    response = RagPipeline(None, DeterministicGenerator()).answer("unindexed question", "en")
    assert response.answer == refusal_message("en")
    assert response.sources == []


def test_pipeline_generates_with_sources() -> None:
    embedder = FakeEmbedder()
    store = FaissVectorStore(2)
    metadata = DocumentMetadata("Labor Act", article="Article 36", source_url="https://example.gov")
    store.add_documents([Chunk("1", "Wages must be paid.", metadata)], embedder.embed_documents(["Wages must be paid."]))
    pipeline = RagPipeline(Retriever(store, embedder, threshold=0.5), DeterministicGenerator())
    response = pipeline.answer("wages", "en")
    assert isinstance(response, ChatResponse)
    assert response.sources[0].document == "Labor Act"
    assert response.sources[0].article == "Article 36"
    assert "Wages must be paid." in response.answer
