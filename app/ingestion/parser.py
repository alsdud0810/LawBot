from pathlib import Path
import re
from typing import Any

from app.ingestion.metadata import DocumentMetadata


class PdfParser:
    def parse(self, path: Path, *, source_url: str | None = None, language: str = "ko") -> list[tuple[str, DocumentMetadata]]:
        import pymupdf

        document = pymupdf.open(path)
        pages: list[tuple[str, DocumentMetadata]] = []
        title = path.stem
        for page_number, page in enumerate(document, start=1):
            text = " ".join(page.get_text("text").split())
            if not text:
                continue
            metadata = DocumentMetadata(
                document_title=title,
                source_url=source_url,
                language=language,
                page=page_number,
            )
            pages.append((text, metadata))
        return pages


class OfficialHtmlParser:
    def parse(self, path: Path, *, source_url: str | None = None, language: str = "ko") -> list[tuple[str, DocumentMetadata]]:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        # Official DOM boundaries distinguish article headings from cross-references.
        effective = soup.select_one('input#efYd')
        date = effective.get('value', '') if effective else ''
        date = f'{date[:4]}-{date[4:6]}-{date[6:]}' if len(date) == 8 else None
        articles = []
        for node in soup.select('div.lawcon'):
            label = node.select_one('label')
            heading = label.get_text(' ', strip=True) if label else ''
            match = re.match(r'제\s*\d+조(?:의\s*\d+)?', heading)
            if not match:
                continue
            text = ' '.join(node.get_text(' ').split())
            articles.append((text, DocumentMetadata(
                document_title=path.stem.removesuffix('본문'),
                source_url=source_url or 'https://www.law.go.kr/법령/' + path.stem.removesuffix('본문'),
                language=language, effective_date=date,
                article=re.sub(r'\s+', '', match.group()),
            )))
        if articles:
            return articles
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = " ".join(soup.get_text(" ").split())
        if not text:
            return []
        metadata = DocumentMetadata(
            document_title=path.stem.removesuffix("본문"),
            source_url=source_url,
            language=language,
        )
        return [(text, metadata)]
