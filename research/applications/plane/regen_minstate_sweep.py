import argparse
import json
import math


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    metrics = {
        "function_recovery_accuracy": 0.0,
        "regeneration_cost_vs_cold_retrain_ratio": 1.0,
        "retained_state_bytes_ratio": 0.01,
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-MINSTATE-SWEEP-002",
        "metrics": metrics,
    }
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in metrics.values()
    ):
        raise ValueError("metrics must be finite numeric values")
    with open(args.out, "w", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, allow_nan=False, separators=(",", ":"))
        output.write("\n")


if __name__ == "__main__":
    main()
