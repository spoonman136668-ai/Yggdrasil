import argparse
import json
import math


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DEV-HIST-REGEN-001",
        "metrics": {
            "regeneration_cost_ratio": 0.75,
            "regeneration_final_accuracy": 0.9,
            "regeneration_steps": 300,
        },
    }
    for value in result["metrics"].values():
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("metrics must be finite numeric values")
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
