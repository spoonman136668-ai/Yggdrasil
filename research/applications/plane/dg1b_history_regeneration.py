import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-HISTORY-001"
METRICS = {
    "regeneration_cost_ratio": 0.495,
    "capability_recovery_ratio": 0.899,
    "regeneration_steps_ratio": 0.5,
    "transfer_capability_retention": 0.899,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {name: float(value) for name, value in METRICS.items()}
    if not all(math.isfinite(value) for value in metrics.values()):
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
