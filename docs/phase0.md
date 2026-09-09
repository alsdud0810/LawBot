# Phase 0 Analysis

## Source material

- `prompt_1.txt`: 2026 implementation requirements.
- `이주노동자.pdf`: 38-page scanned presentation for the 2023 LawBot planning project.

The presentation is treated as a source for the 2023 problem, users, service concept, scenarios, and proposed architecture. It is not treated as proof that the proposed cloud or AI components were implemented.

## 1. Ideas to preserve from 2023

- Focus on migrant workers in South Korea.
- Reduce language and legal-information barriers.
- Cover labor topics such as unpaid wages, workplace conditions, dismissal, and industrial accidents.
- Provide multilingual, easy-to-understand legal information.
- Make official sources visible and traceable.
- Keep escalation to qualified legal professionals as a future safety path.
- Design for a realistic migrant-worker scenario rather than a generic chatbot.

## 2. Architecture intentionally excluded from the 2026 MVP

The 2023 presentation proposes API Gateway, load balancing, ECS, S3, RDS, DynamoDB, Redis, SageMaker, CI/CD services, mobile delivery, and a full business model. These are not reproduced in the MVP. The MVP uses a single FastAPI service, local document files, a persisted FAISS index, and replaceable LLM/embedding adapters.

The 2023 presentation also does not establish that RAG, FAISS, BGE-M3, SageMaker, or ECS were actually implemented. The 2026 README will preserve this distinction.

## 3. MVP scope for today

- PDF ingestion with PyMuPDF.
- Document and article metadata preservation.
- Configurable fixed-size chunking.
- Korean legal-structure-aware chunking.
- Multilingual embedding interface with BAAI/bge-m3.
- FAISS vector search with persisted metadata.
- Configurable top-k and evidence threshold.
- Grounded generation through an OpenAI-compatible adapter, plus a deterministic local fallback for tests.
- Korean and English request paths.
- Source citations and refusal when evidence is insufficient.
- FastAPI `/health` and `/api/v1/chat` endpoints.
- Reproducible retrieval evaluation metrics.
- pytest, Docker, and documentation.

## 4. Final architecture

```text
official documents -> loader/parser -> metadata-aware chunker
    -> embedding adapter -> FAISS index + metadata
    -> retriever -> evidence gate -> prompt -> LLM adapter
    -> answer, language, sources, retrieval diagnostics
```

The embedding and LLM implementations are interfaces so direct multilingual retrieval can later be compared with translate-first retrieval.

## 5. Required official data

The first real corpus must be obtained from authoritative Korean sources, for example:

- 국가법령정보센터 statutes and enforcement ordinances.
- 고용노동부 official labor guidance.
- 근로복지공단 or other official industrial-accident guidance.
- Official multilingual guidance where available.

The repository must not invent legal text. Documents belong under `data/raw/` and should retain title, URL, language, effective date, and article information.

## 6. Credentials

- No credential is required for ingestion, chunking, FAISS, or tests.
- `OPENAI_API_KEY` is required only when using the remote OpenAI-compatible generator.
- `OPENAI_BASE_URL` and `LLM_MODEL` are configurable; secrets are never committed.
- BGE-M3 downloads model weights on first use and may require network access, disk, and memory. A test fake embedder avoids that dependency in pytest.

## 7. Technical risks

- The supplied presentation PDF is image-based; it cannot be used as a legal corpus without OCR and is not itself an official legal source.
- Korean article boundaries and PDF layouts vary by source.
- BGE-M3 and FAISS add large native/model dependencies.
- Similarity scores are not legal truth and require threshold calibration.
- A retrieved passage can still be insufficient or misleading; refusal and citations are mandatory.
- Cross-lingual retrieval quality must be measured rather than assumed.
- Legal documents change over time, so effective dates and source URLs must remain traceable.
- External LLM availability, cost, and prompt adherence are not guaranteed.

## 8. Implementation order

1. FastAPI configuration, models, health endpoint, and tests.
2. PDF loading, parsing, metadata, and both chunking strategies.
3. Embedding interface, FAISS persistence, and retrieval tests.
4. Evidence gate, prompt construction, generator adapter, citations, and chat API.
5. Retrieval evaluation and example schema without fabricated scores.
6. Docker and README, then full validation.
7. Git milestones where Git tooling is available; GitHub creation only after authentication is verified.
