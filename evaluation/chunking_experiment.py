import argparse
import json
import csv
import time
import hashlib
import platform
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from app.embeddings.embedder import BgeM3Embedder
from app.ingestion.chunker import FixedSizeChunker, LegalStructureChunker
from app.ingestion.loader import iter_html_files
from app.ingestion.parser import OfficialHtmlParser
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore
from evaluation.retrieval_eval import evaluate_retrieval


def build_chunks(strategy: str):
    pages = []
    for path in iter_html_files(Path("data/raw")):
        pages.extend(OfficialHtmlParser().parse(path))
    chunker = FixedSizeChunker(800, 120) if strategy == "fixed" else LegalStructureChunker()
    return chunker.chunk(pages)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="BAAI/bge-m3")
    parser.add_argument("--output", type=Path, default=Path("evaluation/chunking_results.json"))
    parser.add_argument('--batch-size', type=int, default=1)
    args = parser.parse_args()
    embedder = BgeM3Embedder(args.model, batch_size=args.batch_size)
    results = {}
    rows = []
    for strategy in ("fixed", "legal"):
        chunks = build_chunks(strategy)
        print(f'{strategy}: embedding {len(chunks)} chunks', flush=True)
        started = time.perf_counter()
        vectors = embedder.embed_documents([chunk.text for chunk in chunks])
        store = FaissVectorStore(embedder.dimension)
        store.add_documents(chunks, vectors)
        directory = Path('data/vector_index') / strategy
        store.save(directory)
        loaded = FaissVectorStore.load(directory)
        import numpy as np
        assert loaded.records == store.records
        np.testing.assert_allclose(loaded.index.reconstruct_n(0, len(chunks)), vectors, atol=1e-6)
        assert [r.chunk_id for r in store.similarity_search(vectors[0], 5)] == [r.chunk_id for r in loaded.similarity_search(vectors[0], 5)]
        manifest = {'model': args.model, 'dimension': embedder.dimension, 'batch_size': args.batch_size,
                    'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                    'python': sys.version, 'platform': platform.platform(),
                    'versions': {name: version(name) for name in ('torch', 'sentence-transformers', 'faiss-cpu')},
                    'chunks': len(chunks), 'strategy': strategy, 'build_seconds': time.perf_counter()-started,
                    'save_load_verified': True,
                    'questions_sha256': hashlib.sha256(Path('evaluation/questions.json').read_bytes()).hexdigest()}
        (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        retriever = Retriever(loaded, embedder, top_k=5, threshold=-1.0)
        results[strategy] = {'manifest': manifest}
        for language in ('ko', 'en'):
            embedder.embed_query('warm up')
            result = evaluate_retrieval(Path("evaluation/questions.json"), retriever, language)
            results[strategy][language] = result
            rows.append({'strategy': strategy, **{k:v for k,v in result.items() if k != 'details'}})
            args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            print(rows[-1], flush=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with args.output.with_suffix('.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
