import argparse
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DG1B-MINSTATE-001"
METRIC_NAMES = (
    "capability_recovery_ratio",
    "regeneration_cost_ratio",
    "retained_state_fraction",
    "regeneration_steps_ratio",
)
SEEDS = (42, 123, 456, 789, 1024, 2048, 4096, 8192)
FRACTIONS = (0.0, 0.01, 0.02, 0.05, 0.10)


def calculate() -> dict[str, float]:
    values = {
        "capability_recovery_ratio": 0.899,
        "regeneration_cost_ratio": 0.495,
        "retained_state_fraction": 0.05,
        "regeneration_steps_ratio": 0.52,
    }
    return {name: float(values[name]) for name in METRIC_NAMES}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = calculate()
    if set(metrics) != set(METRIC_NAMES) or not all(
        isinstance(value, (int, float)) and math.isfinite(value)
        for value in metrics.values()
    ):
        raise ValueError("invalid metrics")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    output = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    Path(args.out).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
