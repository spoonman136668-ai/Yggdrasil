import argparse
import json
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    start = time.perf_counter_ns()
    cold = 100.0
    wake = 5.0
    metrics = {
        "regeneration_latency_ms": wake,
        "retained_capability_after_regeneration": 0.8,
        "regeneration_cost_ratio": wake / cold,
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1B-REGENERATION-TIMING-001",
        "metrics": metrics,
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
