import argparse
import json
from pathlib import Path

import numpy as np

from app.embeddings.embedder import BgeM3Embedder
from app.ingestion.metadata import Chunk, DocumentMetadata
from app.retrieval.vector_store import FaissVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed processed chunks and build a FAISS index.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/vector_index"))
    parser.add_argument("--model", default="BAAI/bge-m3")
    parser.add_argument('--batch-size', type=int, default=1)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()

    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    chunks = [Chunk(record["chunk_id"], record["text"], DocumentMetadata(**record["metadata"])) for record in records]
    embedder = BgeM3Embedder(args.model, args.batch_size, args.device)
    vectors = embedder.embed_documents([chunk.text for chunk in chunks])
    store = FaissVectorStore(embedder.dimension)
    store.add_documents(chunks, vectors)
    store.save(args.output)
    print(f"chunks={len(chunks)} dimension={vectors.shape[1]} output={args.output}")


if __name__ == "__main__":
    main()
