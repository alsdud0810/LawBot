# Repository inspection — 2026-09-09

The initial inspection preceded all source edits. The existing app, ingestion, embedding protocol, FAISS store, grounded pipeline, adapters and tests were retained.

The previous ten-test report matches the ten tests under `tests/`. Running both `tests` and `evaluation` produced **11 passed**, with two dependency deprecation warnings. The first sandboxed attempt had temporary-directory permission errors; rerunning in the user context passed. `pyproject.toml` initially excluded the evaluation test from default collection.

Confirmed implementations: FastAPI health/chat, Pydantic validation, PDF text extraction, metadata dataclasses, fixed and legal chunkers, BGE-M3 adapter, FAISS save/load/search, top-k/threshold, no-evidence refusal, OpenAI-compatible adapter, deterministic generator, source attribution and metric calculations. These unit tests use fake embeddings and do not demonstrate real-model retrieval or paid LLM quality.

Differences from a complete implementation:

- No generated index existed initially. Five official HTML snapshots and processed legal chunks were present.
- README contradicted itself about having one schema example versus 25 questions.
- The HTML parser flattened controls, body and supplementary amendments together and did not preserve effective dates. Regex article splitting mistook inline references for headings.
- Fixed windows had no article labels, making document/article comparison systematically unfair.
- The standalone evaluator used default top-3 and threshold 0.35 while reporting Hit@5. The comparison script ran only Korean and did not persist indexes or CSV.
- The deterministic generator is an excerpt fixture, not multilingual LLM answer generation. Source responses expose document/article/URL; only the maximum retrieval score is exposed, not a per-source score.
- Git 2.55.0.windows.3 and gh 2.100.0 are installed, but the initial folder had no `.git`, no remote, and gh was not authenticated. No organization repositories were queried.

The resulting work keeps the architecture, diagnoses BGE-M3 from small inputs, corrects corpus boundaries/metadata and evaluation mechanics, and runs actual retrieval. Historical implementation is imported as a present-day snapshot; no historical commit dates or invented milestones are created.
