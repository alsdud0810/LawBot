import argparse
import json
import platform
import sys
import traceback
from pathlib import Path


MODEL = "BAAI/bge-m3"


def environment_report() -> dict[str, object]:
    import numpy
    import sentence_transformers
    import torch
    import transformers

    return {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "sentence_transformers": sentence_transformers.__version__,
        "transformers": transformers.__version__,
        "numpy": numpy.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "cuda_memory": [
            {
                "device": index,
                "total_bytes": torch.cuda.get_device_properties(index).total_memory,
                "allocated_bytes": torch.cuda.memory_allocated(index),
                "reserved_bytes": torch.cuda.memory_reserved(index),
            }
            for index in range(torch.cuda.device_count())
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["environment", "load", "one", "ten", "hundred"])
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("data/embedding_diagnostics/result.json"))
    args = parser.parse_args()

    result: dict[str, object] = {"stage": args.stage, "model": args.model, "batch_size": args.batch_size}
    result['exit_code'] = 0
    try:
        result["environment"] = environment_report()
        if args.stage == "environment":
            print(json.dumps(result, indent=2))
            return 0

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(args.model, device=result["environment"]["device"])
        result["dimension"] = model.get_sentence_embedding_dimension()
        if args.stage == "load":
            print(json.dumps(result, indent=2))
            return 0

        count = {"one": 1, "ten": 10, "hundred": 100}[args.stage]
        texts = [f"한국 노동법 공식 문서 테스트 문장 {index}" for index in range(count)]
        embeddings = model.encode(
            texts,
            batch_size=args.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        result["count"] = count
        result["shape"] = list(embeddings.shape)
        result["norm_first"] = float((embeddings[0] ** 2).sum() ** 0.5)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as error:
        result['exit_code'] = 1
        result["error_type"] = type(error).__name__
        result["error"] = str(error)
        result["traceback"] = traceback.format_exc()
        print(json.dumps(result, indent=2))
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
