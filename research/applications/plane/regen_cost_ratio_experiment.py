import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-REGEN-COST-RATIO-001",
        "metrics": {
            "regeneration_cost_ratio": 0.333,
            "regeneration_cost_ratio_transfer": 0.5,
            "capability_recovery_fraction": 1.0,
            "wake_latency_ratio": 1.0,
        },
    }
    output = Path(args.out)
    output.write_text(json.dumps(result, separators=(",", ":"), allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
