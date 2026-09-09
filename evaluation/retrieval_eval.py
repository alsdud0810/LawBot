import json
import time
from pathlib import Path
from typing import Any

from app.retrieval.retriever import Retriever


def evaluate_retrieval(questions_path: Path, retriever: Retriever, language: str = "ko") -> dict[str, Any]:
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    ranks: list[int | None] = []
    latencies: list[float] = []
    details = []
    for item in questions:
        question = item[f"question_{language}"]
        started = time.perf_counter()
        results = retriever.retrieve(question)
        latencies.append((time.perf_counter() - started) * 1000)
        rank = next(
            (
                index
                for index, result in enumerate(results, start=1)
                if item.get('answerable', True)
                and result.metadata.get("document_title") == item["expected_document"]
                and result.metadata.get("article") == item["expected_article"]
            ),
            None,
        )
        ranks.append(rank)
        details.append({'id': item.get('id'), 'question': question, 'rank': rank,
                        'latency_ms': latencies[-1], 'results': [r.to_dict() for r in results]})

    count = len(ranks)
    return {
        "count": count,
        "language": language,
        "mrr_cutoff": retriever.top_k,
        "details": details,
        "hit_at_1": sum(rank is not None and rank <= 1 for rank in ranks) / count if count else 0.0,
        "hit_at_3": sum(rank is not None and rank <= 3 for rank in ranks) / count if count else 0.0,
        "hit_at_5": sum(rank is not None and rank <= 5 for rank in ranks) / count if count else 0.0,
        "mrr": sum(1 / rank for rank in ranks if rank is not None) / count if count else 0.0,
        "average_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
    }
