# Embedding decision — 2026-09-09

Retain `BAAI/bge-m3`. No fallback was selected: the original model passed the actual minimal reproductions on this computer. The existing Embedder protocol and model-name configuration remain intact. CPU and batch size are now configurable; batch 1 is the conservative default.

## Observed environment

- Python 3.14.6, PyTorch 2.14.0+cpu, sentence-transformers 5.7.0, transformers 5.16.1, NumPy 2.5.3, FAISS CPU 1.15.0.
- Windows 11; CUDA unavailable (0 devices). Approximately 31.69 GiB physical RAM, 15.99 GiB available at the inspection instant.
- Historical `data/build_index.log` contains a SciPy `_stats` DLL application-control rejection. This did not recur in current imports. It is not evidence of BGE-M3 running out of memory.
- Sandboxed Hugging Face HEAD requests encountered WinError 10013. Cached weights eventually loaded with exit 0; the network-enabled rerun also loaded successfully. Network permissions and model computation are separate findings.

## Actual minimal reproduction results

| Stage | Batch | Result | Process exit |
|---|---:|---|---:|
| Environment imports | — | Success, CPU | 0 |
| Model load only | 1 | 1,024 dimensions | 0 |
| One sentence | 1 | shape (1, 1024), first norm 1.0 | 0 |
| Ten sentences | 1 | shape (10, 1024), first norm 1.0 | 0 |
| Ten sentences | 2 | shape (10, 1024), first norm 1.0 | 0 |

The first-stage inputs were synthetic Korean diagnostic sentences, not the full corpus. Raw local diagnostics are in `data/embedding_diagnostics/current_*.json`. Process exits above were captured by the invoking PowerShell process. The diagnostic script now includes its own handled exit code in future JSON runs; a native crash still requires observing the parent process exit.

## Trade-offs

BGE-M3 preserves the intended multilingual retrieval model but CPU indexing is slow and its weights consume substantial memory. Batch 1 limits padding and peak batch memory. No smaller model's quality or speed was measured, so no comparative claims are made. A successful short-input diagnosis does not establish production reliability or legal answer quality; the full-corpus experiment is recorded separately.

No paid LLM or remote answer-generation evaluation is included.
