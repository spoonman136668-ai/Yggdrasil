import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1A-HISTORY-001",
        "metrics": {
            "development_steps_ratio_taskN_task1": 0.8,
            "trajectory_compression_ratio": 1.25,
            "active_parameter_growth_per_task": 0.9,
        },
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
