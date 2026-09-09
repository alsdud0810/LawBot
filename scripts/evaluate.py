import argparse
import json
from pathlib import Path

from app.embeddings.embedder import BgeM3Embedder
from app.ingestion.metadata import Chunk, DocumentMetadata
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore
from evaluation.retrieval_eval import evaluate_retrieval


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval against an annotated question set.")
    parser.add_argument("--questions", type=Path, default=Path("evaluation/questions.json"))
    parser.add_argument("--index", type=Path, default=Path("data/vector_index"))
    parser.add_argument("--output", type=Path, default=Path("evaluation/results.json"))
    parser.add_argument("--model", default="BAAI/bge-m3")
    parser.add_argument("--language", choices=['ko', 'en'], default='ko')
    args = parser.parse_args()

    embedder = BgeM3Embedder(args.model)
    retriever = Retriever(FaissVectorStore.load(args.index), embedder, top_k=5, threshold=-1.0)
    result = evaluate_retrieval(args.questions, retriever, args.language)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
