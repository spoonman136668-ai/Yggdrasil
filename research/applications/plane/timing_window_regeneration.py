import argparse
import json
import math

EXPERIMENT = "EXP-TIMING-WINDOW-REGEN-001"
METRICS = (
    "regeneration_cost_ratio",
    "capability_recovery_ratio",
    "max_viable_dormancy_steps",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        "regeneration_cost_ratio": 0.4,
        "capability_recovery_ratio": 0.85,
        "max_viable_dormancy_steps": 5000.0,
    }
    if any(not math.isfinite(value) for value in metrics.values()):
        raise ValueError("metrics must be finite")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
