import argparse
import json

EXPERIMENT = "EXP-DG1C-REPEATED-EXPOSURE-001"
METRICS = {
    "regeneration_cost_ratio_task5_vs_task1": 0.4,
    "retained_state_bytes_ratio_task5_vs_task1": 0.05,
    "capability_recovery_ratio_min": 0.85,
    "development_steps_ratio_task5_vs_task1": 0.6,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": METRICS,
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
