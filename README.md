# LawBot 2026

Multilingual RAG-based Korean labor-law information assistant for migrant workers.

## Project overview

LawBot helps migrant workers find understandable, source-traceable information about Korean labor issues. It is an informational system, not a lawyer and not a substitute for professional legal advice.

In 2023, LawBot was primarily a university service-planning and architecture-design project. The presentation described target users, scenarios, screens, data ideas, and a proposed AWS architecture. It does not establish that the proposed RAG, FAISS, SageMaker, ECS, or other infrastructure was implemented.

In 2026, the project is being revisited as a small, testable implementation of the core AI system: official documents are parsed, chunked, embedded, searched, and passed to a grounded answer generator with citations.

## Architecture

```text
official PDFs -> PyMuPDF parser -> metadata-aware chunking
    -> BGE-M3 embeddings -> FAISS + metadata persistence
    -> top-k retriever -> evidence threshold -> prompt
    -> OpenAI-compatible LLM -> answer + sources
```

The 2026 MVP intentionally does not reproduce the 2023 proposal's ECS, RDS, DynamoDB, Redis, SageMaker, mobile app, payment, or CI/CD architecture.

## Technical highlights

- Fixed-size and Korean legal-structure-aware chunking.
- `BAAI/bge-m3` adapter for multilingual retrieval.
- FAISS inner-product search with persisted metadata.
- Configurable `TOP_K` and evidence threshold.
- Refusal before generation when evidence is insufficient.
- Source document, article, URL, and retrieval score exposure.
- Retrieval evaluation: Hit@1, Hit@3, Hit@5, MRR, and average latency.
- Tests use fake embeddings and a deterministic generator; paid LLM access is not required for pytest.

## Quick start

Python 3.12+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
pytest
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. OpenAPI is available at `/docs`.

## Official documents

Place real, public-sector source PDFs under `data/raw/`. The ingestion path also accepts official `*본문.html` body responses from the Korean National Law Information Center. The current corpus plan and source URLs are recorded in `docs/corpus.md`. Preserve the source URL, title, language, and effective date. Do not place the supplied 2023 presentation in the legal corpus: it is a planning presentation, not an official legal source.

The local corpus contains five official statute body snapshots (508 operative articles). Raw snapshots are ignored by Git. `evaluation/questions.json` contains 25 bilingual questions; 24 targets have operative article support, and one is explicitly marked unavailable in the snapshot. See `docs/ground_truth_changes.md` and the source hashes in `evaluation/ground_truth_audit.json`.

```powershell
python scripts/ingest.py --strategy legal
python scripts/build_index.py
```

The first BGE-M3 run downloads model weights and needs network access, disk, and memory. Generated chunks, indexes, and downloaded model artifacts are ignored by Git.

## API

`GET /health`

```json
{"status":"ok"}
```

`POST /api/v1/chat`

```json
{"question":"퇴사 후 회사가 임금을 언제까지 지급해야 하나요?","language":"ko"}
```

When no index or sufficient evidence is available, the service refuses to answer. With an index and configured LLM credentials, the response includes `answer`, `language`, `sources`, and retrieval diagnostics.

## Evaluation

The BGE-M3 model passed load-only, one-sentence and ten-sentence CPU diagnostics (batch sizes 1 and 2). See `docs/embedding_decision.md`. Retrieval results are generated from the frozen local corpus, not assumed from unit tests.

Run the paired experiment (CPU indexing can take substantial time):

```powershell
python -m evaluation.chunking_experiment --output evaluation/chunking_results.json
python scripts/evaluate.py --index data/vector_index/fixed --language en --output evaluation/results.json
```

The experiment saves separate `data/vector_index/fixed` and `data/vector_index/legal` indexes, verifies save/load, and writes per-query JSON plus summary CSV. Both strategies operate within the same official article boundaries. Hit@1/3/5 and MRR@5 use document/article matching over five retrieved chunks, without threshold filtering. Latency includes warm query embedding and search. The one unavailable target stays a miss in the 25-question denominator. These are retrieval metrics, not answer correctness or refusal quality.

To serve a comparison index, set `VECTOR_INDEX_DIR=data/vector_index/fixed` (or `data/vector_index/legal`) in `.env`. Keep `EMBEDDING_MODEL` consistent with the index manifest. With no LLM credentials, the current deterministic generator returns retrieved excerpts; it does not translate or synthesize an English answer.

Measured on 2026-09-09, BGE-M3 on CPU, batch 1, 25 questions per language:

| Strategy | Query language | Chunks | Hit@1 | Hit@3 | Hit@5 | MRR@5 | Mean latency (ms) |
|---|---|---:|---:|---:|---:|---:|---:|
| Fixed (article-bounded) | Korean | 574 | 0.92 | 0.96 | 0.96 | 0.9400 | 224.92 |
| Fixed (article-bounded) | English → Korean | 574 | 0.72 | 0.92 | 0.96 | 0.8080 | 197.41 |
| Legal-aware | Korean | 1,588 | 0.88 | 0.96 | 0.96 | 0.9133 | 175.38 |
| Legal-aware | English → Korean | 1,588 | 0.80 | 0.96 | 0.96 | 0.8733 | 174.60 |

Source artifacts: [JSON](evaluation/chunking_results.json), [CSV](evaluation/chunking_results.csv), [annotation audit](docs/ground_truth_changes.md). Both indexes passed persistence checks. Fixed indexing took 679.19 seconds; legal-aware indexing took 801.91 seconds. This small dataset favors fixed at Korean rank 1 and legal-aware at English rank 1, with equal Hit@5. Latencies are single sequential-run observations, not controlled evidence that either chunker is faster. The unavailable question caps these 25-question hit rates at 0.96.

## Testing

```powershell
pytest
```

The tests cover API validation, PDF parsing, metadata preservation, both chunkers, FAISS persistence, threshold filtering, refusal, and source citation.

Verified on 2026-09-09: **13 passed** (two upstream deprecation warnings). Real Uvicorn HTTP checks also passed for health and Korean/English chat, both without an index and with the measured fixed-size index. `evaluation/api_smoke_*.json` records the responses. Paid LLM generation was not tested.

## Configuration and credentials

Copy `.env.example` to `.env`. `LLM_API_KEY` and `LLM_MODEL` are required only for remote OpenAI-compatible generation. Never commit `.env` or credentials. Ingestion, FAISS, and tests do not require an API key.

## Limitations and future work

- The initial MVP does not perform OCR for scanned legal PDFs.
- Translate-first retrieval has not been measured; the experiment uses direct English-to-Korean retrieval.
- Similarity is an evidence signal, not a legal conclusion; thresholds need calibration.
- Document versioning, reranking, hybrid search, official crawling, observability, and production deployment remain future work.
- Legal information changes; users should verify current official guidance and seek qualified help for case-specific matters.

## Legal disclaimer

LawBot provides general legal information based on indexed sources. It is not a law firm, does not provide legal representation, and must not be treated as definitive case-specific legal advice.
