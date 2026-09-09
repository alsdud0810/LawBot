from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentMetadata:
    document_title: str
    source_type: str = "official"
    source_url: str | None = None
    language: str = "ko"
    effective_date: str | None = None
    article: str | None = None
    paragraph: str | None = None
    page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: DocumentMetadata

    def to_dict(self) -> dict[str, Any]:
        return {"chunk_id": self.chunk_id, "text": self.text, "metadata": self.metadata.to_dict()}
