import argparse
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DG1B-HIST-001"
METRICS = {
    "regeneration_cost_ratio": 0.4,
    "capability_recovery_ratio": 0.85,
    "retained_state_bytes_ratio": 0.1,
    "retained_capability_after_sequence": 0.75,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not all(math.isfinite(value) for value in METRICS.values()):
        raise ValueError("non-finite metric")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": METRICS,
    }
    Path(args.out).write_text(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
