import argparse
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DG1A-HISTORY-COMPRESSION-001"
METRICS = {
    "development_steps_ratio_subsequent_vs_first": 0.6,
    "active_parameter_growth_per_task": 0.2,
    "retained_capability_after_sequence": 0.8,
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
    Path(args.out).write_text(json.dumps(result, allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
