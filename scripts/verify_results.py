"""Check saved measurements without rerunning or changing retrieval."""
import csv
import hashlib
import json
from pathlib import Path


def main():
    results = json.loads(Path('evaluation/chunking_results.json').read_text())
    with Path('evaluation/chunking_results.csv').open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    digest = hashlib.sha256(Path('evaluation/questions.json').read_bytes()).hexdigest()
    for strategy, values in results.items():
        assert values['manifest']['questions_sha256'] == digest
        for language in ('ko', 'en'):
            result = values[language]
            ranks = [detail['rank'] for detail in result['details']]
            assert len(ranks) == 25
            for k in (1, 3, 5):
                assert sum(rank is not None and rank <= k for rank in ranks) / 25 == result[f'hit_at_{k}']
            assert abs(sum(1/rank for rank in ranks if rank) / 25 - result['mrr']) < 1e-12
            row = next(row for row in rows if row['strategy'] == strategy and row['language'] == language)
            for key in ('hit_at_1', 'hit_at_3', 'hit_at_5', 'mrr', 'average_latency_ms'):
                assert float(row[key]) == result[key]
    print('Saved ranks, metrics, CSV and frozen question hash verified')


if __name__ == '__main__':
    main()
