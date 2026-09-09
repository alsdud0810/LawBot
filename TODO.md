# LawBot 2026 TODO

## Phase 0
- [x] Read `prompt_1.txt`.
- [x] Inspect `이주노동자.pdf` and distinguish 2023 planning from implementation evidence.
- [x] Record scope and risks in `docs/phase0.md`.

## Phase 1: application foundation
- [x] Add settings and logging.
- [x] Add FastAPI application and health endpoint.
- [x] Add request/response schemas.
- [x] Add API tests.

## Phase 2: ingestion
- [x] Add PDF loader/parser.
- [x] Add metadata model.
- [x] Add fixed-size chunker.
- [x] Add Korean legal-structure-aware chunker.
- [x] Add chunking tests.

## Phase 3: retrieval
- [x] Add embedding interface and BGE-M3 adapter.
- [x] Add FAISS vector store persistence.
- [x] Add top-k retrieval and threshold.
- [x] Add retrieval tests.

## Phase 4: grounded RAG
- [x] Add evidence gate and refusal.
- [x] Add prompt builder.
- [x] Add OpenAI-compatible generator.
- [x] Add deterministic test generator.
- [x] Add citations and chat endpoint.

## Phase 5: evaluation and delivery
- [x] Add reproducible Hit@1/3/5, MRR, and latency evaluation.
- [x] Add 25-question official-corpus evaluation schema.
- [x] Add fixed-size vs legal-aware comparison script.
- [x] Add Dockerfile and README.
- [x] Run full pytest and startup checks.
- [ ] Verify Git/GitHub tools and create milestones when available.

## Data requirements
- [x] Download official Korean legal body responses under `data/raw/`.
- [x] Preserve source URL, title, language, and article metadata where available.
- [x] Run BGE-M3 batch embedding successfully (one/ten sentences; batch 1 and 2).
- [x] Create persisted official-corpus FAISS indexes (fixed and legal).
- [x] Measure chunking metrics and save JSON/CSV results.
- [x] Review staged files to exclude secrets, model caches, raw private data and generated indexes.

## Repository continuation (2026-09-09)
- [x] Verify prior implementation against actual source and tests (11 baseline tests).
- [x] Include evaluation tests in default pytest discovery.
- [x] Preserve operative article boundaries, effective dates and official URLs from HTML.
- [x] Audit all 25 targets before retrieval; flag kb_018 as unavailable in the snapshot.
- [x] Diagnose model load and small embeddings without replacing BGE-M3.
- [x] Fix standalone top-5 evaluation and add English queries, per-query JSON and summary CSV.
- [x] Verify actual HTTP health/chat without an index.
- [x] Complete both full-corpus indexes and record measured comparison.
- [x] Verify actual HTTP chat with an index and rerun all tests (13 passed).
- [ ] Authenticate gh and confirm only alsdud0810/lawbot-2026; do not create a remote repository.
- [x] Review staged files for the honest present-day implementation/evaluation snapshot.
- [ ] Push the local snapshot to the confirmed personal remote after gh authentication.
