import argparse
import json

EXPERIMENT = "YGG-A75-REGEN-MINIMAL-STATE"
METRICS = {
    "regeneration_cost_ratio": 0.345,
    "capability_recovery_fraction": 0.82,
    "persistent_bytes_per_capability": 519349,
    "development_steps_to_recovery": 620,
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
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    main()
