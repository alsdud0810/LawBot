import argparse
import json
from pathlib import Path

from app.ingestion.chunker import FixedSizeChunker, LegalStructureChunker
from app.ingestion.loader import iter_html_files, iter_pdf_files
from app.ingestion.parser import OfficialHtmlParser, PdfParser


OFFICIAL_URLS = {
    "근로기준법": "https://www.law.go.kr/법령/근로기준법",
    "근로기준법시행령": "https://www.law.go.kr/법령/근로기준법시행령",
    "산업안전보건법": "https://www.law.go.kr/법령/산업안전보건법",
    "근로자퇴직급여보장법": "https://www.law.go.kr/법령/근로자퇴직급여보장법",
    "외국인근로자의고용등에관한법률": "https://www.law.go.kr/법령/외국인근로자의고용등에관한법률",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse and chunk official PDF documents.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--strategy", choices=["fixed", "legal"], default="legal")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    args = parser.parse_args()

    parsed_pages = []
    for pdf_path in iter_pdf_files(args.raw_dir):
        parsed_pages.extend(PdfParser().parse(pdf_path))
    for html_path in iter_html_files(args.raw_dir):
        parsed_pages.extend(OfficialHtmlParser().parse(html_path, source_url=OFFICIAL_URLS.get(html_path.stem.removesuffix("본문"))))
    chunker = FixedSizeChunker(args.chunk_size, args.chunk_overlap) if args.strategy == "fixed" else LegalStructureChunker()
    chunks = chunker.chunk(parsed_pages)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
    print(f"documents={len(iter_pdf_files(args.raw_dir)) + len(iter_html_files(args.raw_dir))} pages={len(parsed_pages)} chunks={len(chunks)} strategy={args.strategy}")


if __name__ == "__main__":
    main()
