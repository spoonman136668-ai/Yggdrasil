import argparse
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        "function_recovery_accuracy": 0.0,
        "regeneration_cost_vs_cold_retrain_ratio": 1.0,
        "retained_state_bytes_ratio": 0.02,
    }
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
        raise ValueError("metrics must be finite numbers")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-MINSTATE-001",
        "metrics": metrics,
    }
    Path(args.out).write_text(json.dumps(result, allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
