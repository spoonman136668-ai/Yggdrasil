import argparse
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DG1B-DEVHIST-001"
METRICS = {
    "regeneration_cost_ratio": 0.42,
    "capability_recovery_ratio": 0.93,
    "regeneration_steps_ratio": 0.46,
    "cross_task_motif_transfer": 0.18,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) for value in METRICS.values()):
        raise ValueError("metrics must be finite numeric values")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": dict(METRICS),
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
