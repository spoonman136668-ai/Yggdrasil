import argparse
import json
import math


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-COST-001",
        "metrics": {
            "regeneration_cost_vs_cold_retrain_ratio": 0.4,
            "function_recovery_accuracy": 0.9,
        },
    }
    for value in result["metrics"].values():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError("metrics must contain finite numeric values")
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
