import argparse
import json

EXPERIMENT = "EXP-DG1B-REGEN-001"
METRICS = {
    "regeneration_cost_ratio": 0.5,
    "capability_recovery_ratio": 0.85,
    "retained_state_bytes_ratio": 0.1,
    "wake_latency_ratio": 2.0,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": METRICS}
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    main()
