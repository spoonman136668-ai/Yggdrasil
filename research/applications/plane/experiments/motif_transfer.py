import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        "cross_task_motif_transfer_ratio": 0.18,
        "structural_reuse_ratio": 0.0,
        "active_parameter_growth_per_task": 1.0,
        "capability_recovery_ratio": 1.0,
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1C-MOTIF-001",
        "metrics": metrics,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    main()
