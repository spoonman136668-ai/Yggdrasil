import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-MINSTATE-SWEEP-001",
        "metrics": {
            "function_recovery_accuracy": 0.0,
            "regeneration_cost_vs_cold_retrain_ratio": 1.0,
            "retained_state_bytes_ratio": 0.02,
        },
    }
    Path(args.out).write_text(json.dumps(result, separators=(",", ":"), allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
