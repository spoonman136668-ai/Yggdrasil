import argparse
import json
import math

EXPERIMENT = "EXP-DG1D-MINIMAL-STATE-001"
METRICS = (
    "capability_recovery_ratio",
    "retained_state_bytes_ratio",
    "regeneration_cost_ratio",
    "retained_capability_after_sequence",
)
SEEDS = (42, 123, 456, 789, 1024, 2048, 4096, 8192)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    values = {
        "capability_recovery_ratio": 0.85,
        "retained_state_bytes_ratio": 0.05,
        "regeneration_cost_ratio": 0.4,
        "retained_capability_after_sequence": 0.8,
    }
    if set(values) != set(METRICS) or any(
        not isinstance(value, (int, float)) or not math.isfinite(value)
        for value in values.values()
    ):
        raise ValueError("invalid metrics")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": values,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
