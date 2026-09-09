import json
from pathlib import Path

import numpy as np

from app.ingestion.metadata import Chunk, DocumentMetadata
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore
from evaluation.retrieval_eval import evaluate_retrieval


class EvalEmbedder:
    dimension = 1

    def embed_query(self, text: str) -> np.ndarray:
        return np.array([1.0], dtype="float32")


def test_evaluation_metrics_are_reproducible(tmp_path: Path) -> None:
    embedder = EvalEmbedder()
    store = FaissVectorStore(1)
    metadata = DocumentMetadata("Labor Act", article="Article 36")
    store.add_documents([Chunk("1", "wage", metadata)], np.array([[1.0]], dtype="float32"))
    questions = tmp_path / "questions.json"
    questions.write_text(json.dumps([{"question_ko": "wage", "expected_document": "Labor Act", "expected_article": "Article 36"}]), encoding="utf-8")
    result = evaluate_retrieval(questions, Retriever(store, embedder))
    assert result["hit_at_1"] == 1.0
    assert result["mrr"] == 1.0


def test_fifth_rank_and_unanswerable_target(tmp_path: Path) -> None:
    from app.retrieval.vector_store import SearchResult

    class RankedRetriever:
        top_k = 5

        def retrieve(self, question):
            return [SearchResult('text', 1.0, {'document_title': 'Act', 'article': str(i)}, str(i))
                    for i in range(1, 6)]

    questions = tmp_path / 'questions.json'
    questions.write_text(json.dumps([
        {'question_ko': 'fifth', 'expected_document': 'Act', 'expected_article': '5'},
        {'question_ko': 'unavailable', 'expected_document': 'Act', 'expected_article': '1', 'answerable': False},
    ]), encoding='utf-8')
    result = evaluate_retrieval(questions, RankedRetriever())
    assert result['hit_at_1'] == 0
    assert result['hit_at_3'] == 0
    assert result['hit_at_5'] == 0.5
    assert result['mrr'] == 0.1
    assert [d['rank'] for d in result['details']] == [5, None]
