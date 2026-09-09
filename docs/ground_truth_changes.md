# Corpus-grounded annotation audit

The audit was performed before retrieval scores were available. `evaluation/ground_truth_audit.json` records all 25 original targets, supporting article texts and source file SHA-256 hashes. Five local official HTML body snapshots contain 508 operative articles. Dates come from their `efYd` fields, not from assumptions about today's law.

24 targets exist and their text supports the topic of the question; their expected document and article are unchanged.

`kb_018`: 산업안전보건법 제31조의2 does not occur as an operative article in the snapshot effective 2026-08-01. It is mentioned in a supplementary provision for a later amendment (law 21853, 2026-07-07; six-month commencement). An inline mention is not the article's body. Article 31 concerns construction day workers and cannot replace a question about foreign workers generally. The original target and question are retained for audit, with `answerable: false` and an explanation. It remains a miss in the 25-question metrics; no score-driven relabeling or silent denominator reduction occurs. An answerable-only supplementary view may be computed from the same ranks, but is not the headline benchmark.

`kb_016` Korean wording describes an accident occurring, while English and the target refer to imminent danger. Both questions are retained; this wording mismatch is a dataset limitation.

## Parser and comparison corrections

Official HTML `div.lawcon` and its heading label identify operative articles. Page controls and historical supplementary amendments are excluded from the retrieval corpus: those amendments must not masquerade as current article bodies. All five documents and all 508 operative articles are included, with effective dates and official URLs preserved.

Previously, whole-page regex splitting mislabeled inline article references and supplementary article numbers. Parsing now supplies an authoritative article boundary and legal chunking keeps that label. Fixed-size chunking uses 800 characters / 120 overlap **within each parsed article**. Legal-aware chunking uses paragraphs within the same articles. This is an article-bounded fixed-size baseline, not an unrestricted whole-document fixed-window experiment.

Metrics match document + article, not paragraph-level answer sufficiency. Top 5 chunks are searched with no evidence threshold; MRR is therefore MRR@5. Duplicate article chunks may occupy multiple ranks. Latency is warm query embedding + FAISS lookup, excluding model loading and corpus indexing. No translation is used for English queries.
