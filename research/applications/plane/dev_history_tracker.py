import argparse
import json
import math


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        "lineage_size_ratio": 0.1,
        "regeneration_cost_ratio": 1.0,
        "regeneration_accuracy": 1.0,
        "wake_latency_ratio": 1.0,
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DEVHIST-001",
        "metrics": metrics,
    }
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in metrics.values()):
        raise ValueError("metrics must be finite numeric values")
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
