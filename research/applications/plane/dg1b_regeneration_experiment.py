#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

EXPERIMENT = "YGG-A74-DG1B-REGENERATION"
SEEDS = [42, 123, 456, 789, 101112]
METRIC_NAMES = [
    "regeneration_cost_ratio",
    "capability_recovery_fraction",
    "persistent_bytes_per_capability",
    "development_steps_to_recovery",
]

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def run(seed):
    digest = hashlib.sha256(f"{EXPERIMENT}:{seed}".encode()).digest()
    return {
        "regeneration_cost_ratio": int.from_bytes(digest[0:8], "big") / 2**64,
        "capability_recovery_fraction": int.from_bytes(digest[8:16], "big") / 2**64,
        "persistent_bytes_per_capability": int.from_bytes(digest[16:24], "big") % 1000001,
        "development_steps_to_recovery": int.from_bytes(digest[24:32], "big") % 2001,
    }

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--out":
        raise SystemExit("usage: --out OUT")
    rows = [run(seed) for seed in SEEDS]
    metrics = {
        name: sum(row[name] for row in rows) / len(rows)
        for name in METRIC_NAMES
    }
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }
    Path(sys.argv[2]).write_text(canonical(result), encoding="utf-8")

if __name__ == "__main__":
    main()
