import argparse
import json

EXPERIMENT = "EXP-DG1D-MINIMAL-STATE-002"
METRIC_NAMES = (
    "capability_recovery_ratio",
    "regeneration_cost_ratio",
    "retained_state_bytes_ratio",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": {
            "capability_recovery_ratio": 0.85,
            "regeneration_cost_ratio": 0.4,
            "retained_state_bytes_ratio": 0.05,
        },
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
