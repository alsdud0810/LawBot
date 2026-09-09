"""Freeze source-derived annotations before running retrieval experiments."""
import hashlib
import json
from pathlib import Path
from app.ingestion.loader import iter_html_files
from app.ingestion.parser import OfficialHtmlParser


def main():
    sources, articles = [], {}
    for path in iter_html_files(Path('data/raw')):
        pages = OfficialHtmlParser().parse(path)
        sources.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'articles': len(pages), 'effective_date': pages[0][1].effective_date})
        for text, meta in pages:
            assert (meta.document_title, meta.article) not in articles, 'Duplicate operative article'
            articles[(meta.document_title, meta.article)] = text
    questions = json.loads(Path('evaluation/questions.json').read_text(encoding='utf-8'))
    audit = []
    for q in questions:
        text = articles.get((q['expected_document'], q['expected_article']))
        audit.append({**q, 'exists': text is not None, 'official_text': text})
    output = {'sources': sources, 'questions': audit}
    Path('evaluation/ground_truth_audit.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
