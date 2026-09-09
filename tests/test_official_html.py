from app.ingestion.parser import OfficialHtmlParser
from app.ingestion.chunker import FixedSizeChunker, LegalStructureChunker


def test_dom_article_boundary_ignores_inline_references(tmp_path):
    path = tmp_path / 'fixture본문.html'
    path.write_text('''<input id="efYd" value="20260801">
    <div class="lawcon"><label>제52조(작업중지)</label>① 제38조에 따른 조치 ② 보고</div>
    <div>부칙 제1조 시행일</div>''', encoding='utf-8')
    pages = OfficialHtmlParser().parse(path)
    assert len(pages) == 1
    assert pages[0][1].effective_date == '2026-08-01'
    for chunker in (FixedSizeChunker(20, 3), LegalStructureChunker()):
        chunks = chunker.chunk(pages)
        assert all(c.metadata.article == '제52조' for c in chunks)
        assert all(c.metadata.source_url for c in chunks)
