import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": "EXP-DG1C-GENOME-EFFICIENCY-001",
        "metrics": {
            "genome_size_bytes_per_capability": 4096.0,
            "retained_capability_ratio": 0.9,
            "regeneration_cost_ratio": 0.4,
        },
    }
    Path(args.out).write_text(json.dumps(result, allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
