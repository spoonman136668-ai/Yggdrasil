import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-REGEN-COMPRESSION-001"
METRICS = {
    "regeneration_cost_ratio": 0.4,
    "retained_capability_ratio": 0.9,
    "genome_size_bytes_per_capability": 4096.0,
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
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in METRICS.values()):
        raise ValueError("metrics must be finite numeric values")
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
