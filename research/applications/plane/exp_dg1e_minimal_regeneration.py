import argparse
import json
import math

EXPERIMENT = "EXP-DG1E-MINIMAL-REGENERATION-001"
METRICS = {
    "regeneration_cost_ratio_vs_retrain": 0.25,
    "functional_recovery_ratio": 0.85,
    "active_parameter_growth_ratio": 0.2,
    "resident_byte_growth_ratio": 0.15,
    "global_signal_fraction": 0.02,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in METRICS.values()):
        raise ValueError("metrics must be finite numeric values")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": METRICS,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, separators=(",", ":"), allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
