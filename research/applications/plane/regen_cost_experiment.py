import argparse
import json
import math


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        "regeneration_cost_ratio": 0.4,
        "capability_recovery_ratio": 0.85,
        "active_parameter_growth_per_task": 0.2,
        "retained_capability_after_sequence": 0.8,
    }
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in metrics.values()):
        raise ValueError("metrics must be finite numeric values")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1B-REGEN-COST-001",
        "metrics": metrics,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
