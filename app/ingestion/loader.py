from pathlib import Path


def iter_pdf_files(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("*.pdf"))


def iter_html_files(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("*본문.html"))
