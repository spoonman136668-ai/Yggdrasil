#!/usr/bin/env python3
"""EXP-DG1B-WINDOW-CAUSALITY-005 sealed isolated-run result contract."""

import argparse
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DG1B-WINDOW-CAUSALITY-005"
METRIC_NAMES = (
    "full_order_advantage",
    "distributed_order_synergy",
    "leave_one_sensitive_window_count",
    "full_ordered_functional_recovery_ratio",
    "regeneration_cost_ratio",
    "condition_resident_byte_spread",
    "global_signal_fraction",
)


def finite_metrics(values):
    """Return only the preregistered finite numeric metric mapping."""
    metrics = {}
    for name in METRIC_NAMES:
        value = float(values[name])
        if not math.isfinite(value):
            raise ValueError("nonfinite preregistered metric: " + name)
        metrics[name] = value
    if set(metrics) != set(METRIC_NAMES):
        raise ValueError("metric contract mismatch")
    return metrics


def sealed_invalid_result(reason):
    """Preserve a fail-closed outcome without inventing fixture measurements."""
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "status": "invalid",
        "reason": reason,
        "metrics": finite_metrics({name: 0.0 for name in METRIC_NAMES}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    # This source is intentionally fail-closed until the isolated harness supplies
    # the sealed, evidence-associated DG-1B fixture and frozen scorer.  It never
    # substitutes a scorer, target, lineage, seed, or scientific measurement.
    result = sealed_invalid_result(
        "sealed DG-1B fixture and frozen scorer must be resolved by the isolated harness"
    )

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()
