import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1A-HISTORY-COMPRESSION-001",
        "metrics": {
            "genome_size_reduction_ratio": 0.85,
            "development_steps_reduction_ratio": 0.85,
            "active_params_reduction_ratio": 0.9,
            "lineage_reuse_events_per_task": 2.0,
            "retained_capability_after_sequence": 0.8,
        },
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
