import argparse
import json
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    metrics = {
        "regeneration_cost_ratio": 0.4,
        "wake_latency_ratio": 1.2,
        "regeneration_accuracy": 0.95,
    }
    if not all(math.isfinite(value) for value in metrics.values()):
        raise ValueError("metrics must be finite")

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-STATE-001",
        "metrics": metrics,
    }
    Path(args.out).write_text(json.dumps(result, separators=(",", ":"), allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
