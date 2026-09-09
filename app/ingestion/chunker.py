import re
from collections.abc import Iterable

from app.ingestion.metadata import Chunk, DocumentMetadata


class FixedSizeChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be in [0, chunk_size)")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, pages: Iterable[tuple[str, DocumentMetadata]]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page_text, metadata in pages:
            start = 0
            while start < len(page_text):
                end = min(start + self.chunk_size, len(page_text))
                text = page_text[start:end].strip()
                if text:
                    chunks.append(Chunk(f"chunk-{len(chunks):06d}", text, metadata))
                if end == len(page_text):
                    break
                start = end - self.chunk_overlap
        return chunks


class LegalStructureChunker:
    ARTICLE_PATTERN = re.compile(r"(?=(?:^|\s)(제\s*\d+조(?:의\s*\d+)?))")
    PARAGRAPH_PATTERN = re.compile(r"(?=(?:^|\s)([①②③④⑤⑥⑦⑧⑨⑩]))")

    def chunk(self, pages: Iterable[tuple[str, DocumentMetadata]]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page_text, page_metadata in pages:
            article_parts = ([(page_text, page_metadata.article)] if page_metadata.article
                             else self._split(page_text, self.ARTICLE_PATTERN))
            for article_text, article in article_parts:
                paragraph_parts = self._split(article_text, self.PARAGRAPH_PATTERN)
                for paragraph_text, paragraph in paragraph_parts:
                    text = paragraph_text.strip()
                    if not text:
                        continue
                    metadata = DocumentMetadata(
                        document_title=page_metadata.document_title,
                        source_type=page_metadata.source_type,
                        source_url=page_metadata.source_url,
                        language=page_metadata.language,
                        effective_date=page_metadata.effective_date,
                        article=article or page_metadata.article,
                        paragraph=paragraph,
                        page=page_metadata.page,
                    )
                    chunks.append(Chunk(f"chunk-{len(chunks):06d}", text, metadata))
        return chunks

    @staticmethod
    def _split(text: str, pattern: re.Pattern[str]) -> list[tuple[str, str | None]]:
        matches = list(pattern.finditer(text))
        if not matches:
            return [(text, None)]
        parts: list[tuple[str, str | None]] = []
        if matches[0].start() > 0:
            parts.append((text[:matches[0].start()], None))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            parts.append((text[match.start():end], match.group(1)))
        return parts
