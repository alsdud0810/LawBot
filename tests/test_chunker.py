from pathlib import Path

import pymupdf

from app.ingestion.chunker import FixedSizeChunker, LegalStructureChunker
from app.ingestion.parser import PdfParser


def test_fixed_size_chunker_preserves_metadata() -> None:
    pages = [("a" * 10, __import__("app.ingestion.metadata", fromlist=["DocumentMetadata"]).DocumentMetadata("Labor Act", page=2))]
    chunks = FixedSizeChunker(chunk_size=4, chunk_overlap=1).chunk(pages)
    assert [chunk.text for chunk in chunks] == ["aaaa", "aaaa", "aaaa"]
    assert all(chunk.metadata.document_title == "Labor Act" for chunk in chunks)
    assert all(chunk.metadata.page == 2 for chunk in chunks)


def test_legal_chunker_preserves_articles_and_paragraphs() -> None:
    pages = [("제1조 목적 ① 첫째 내용 ② 둘째 내용 제2조 적용범위 ① 적용 내용", __import__("app.ingestion.metadata", fromlist=["DocumentMetadata"]).DocumentMetadata("근로기준법"))]
    chunks = LegalStructureChunker().chunk(pages)
    assert len(chunks) == 5
    assert chunks[1].metadata.article == "제1조"
    assert chunks[1].metadata.paragraph == "①"
    assert chunks[-1].metadata.article == "제2조"


def test_pdf_parser_reads_text_and_page_metadata(tmp_path: Path) -> None:
    path = tmp_path / "fixture.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Article 1 official document test")
    document.save(path)
    document.close()

    pages = PdfParser().parse(path, source_url="https://example.gov", language="ko")
    assert len(pages) == 1
    text, metadata = pages[0]
    assert "Article 1" in text
    assert metadata.document_title == "fixture"
    assert metadata.source_url == "https://example.gov"
    assert metadata.page == 1
