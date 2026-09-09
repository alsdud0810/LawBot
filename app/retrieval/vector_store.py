import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.ingestion.metadata import Chunk


class SearchResult:
    def __init__(self, text: str, score: float, metadata: dict[str, Any], chunk_id: str) -> None:
        self.text = text
        self.score = score
        self.metadata = metadata
        self.chunk_id = chunk_id

    def to_dict(self) -> dict[str, Any]:
        return {"chunk_id": self.chunk_id, "text": self.text, "score": self.score, "metadata": self.metadata}


class FaissVectorStore:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.records: list[dict[str, Any]] = []

    def add_documents(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        vectors = np.asarray(vectors, dtype="float32")
        if vectors.ndim != 2 or vectors.shape != (len(chunks), self.dimension):
            raise ValueError("vectors must have shape (number of chunks, dimension)")
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.records.extend(chunk.to_dict() for chunk in chunks)

    def similarity_search(self, query_vector: np.ndarray, top_k: int = 3) -> list[SearchResult]:
        if not self.records:
            return []
        vector = np.asarray(query_vector, dtype="float32").reshape(1, -1)
        if vector.shape[1] != self.dimension:
            raise ValueError("query vector dimension does not match the index")
        faiss.normalize_L2(vector)
        scores, indices = self.index.search(vector, min(top_k, len(self.records)))
        return [
            SearchResult(
                text=self.records[index]["text"],
                score=float(score),
                metadata=self.records[index]["metadata"],
                chunk_id=self.records[index]["chunk_id"],
            )
            for score, index in zip(scores[0], indices[0], strict=True)
            if index >= 0
        ]

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(directory / "index.faiss"))
        (directory / "metadata.json").write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, directory: Path) -> "FaissVectorStore":
        index = faiss.read_index(str(directory / "index.faiss"))
        store = cls(index.d)
        store.index = index
        store.records = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        return store
