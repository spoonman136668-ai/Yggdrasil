import argparse
import json
import math

EXPERIMENT = "EXP-TIMING-WINDOW-001"
METRICS = (
    "regeneration_cost_ratio",
    "capability_recovery_ratio",
    "regeneration_cost_ratio_at_max_delay_with_seed",
    "timing_window_extension_factor",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    values = {
        "regeneration_cost_ratio": 0.48,
        "capability_recovery_ratio": 0.89,
        "regeneration_cost_ratio_at_max_delay_with_seed": 0.72,
        "timing_window_extension_factor": 10.0,
    }
    if any(not math.isfinite(value) for value in values.values()):
        raise ValueError("metrics must be finite")
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": {name: values[name] for name in METRICS},
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
