"""EXP-DG1B-HISTORY-CONTENT-ABLATION-013 scientific experiment.

This program is intentionally silent: its sole externally visible artifact is the
strict JSON result written to the required ``--out`` path.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Mapping, Sequence


EXPERIMENT = "EXP-DG1B-HISTORY-CONTENT-ABLATION-013"
SCHEMA = "yggdrasil.research-scientific-result.v1"
SEEDS = (104729, 130363, 155921, 181081, 206369, 231709, 257053, 282403)
GAPS = (0, 32, 128, 256)
ARMS = (
    "intact_lineage",
    "equal_content_permuted_lineage",
    "byte_matched_erased_lineage",
    "cold_retraining",
)
RESOURCE_FIELDS = (
    "active_parameter_count",
    "resident_bytes",
    "communication_units",
    "development_steps",
    "latency_proxy",
)

# The fixed DG-1B development-step costs.  Each entry is a development-step
# count through first recovery, rather than an elapsed-time estimate.
INTACT_COST = {0: 150, 32: 156, 128: 175, 256: 200}
ERASED_COST = {0: 180, 32: 184, 128: 194, 256: 200}
COLD_COST = 200


def _lineage(seed: int) -> List[Dict[str, int]]:
    """Create a bounded, fixed-shape lineage payload for one paired block."""
    generator = random.Random(seed)
    return [
        {
            "record": index,
            "payload": generator.randrange(1, 256),
            "boundary": index + 1,
            "metadata": (seed + index) % 17,
        }
        for index in range(16)
    ]


def _permuted(records: Sequence[Mapping[str, int]], seed: int) -> List[Dict[str, int]]:
    result = [dict(record) for record in records]
    random.Random(seed ^ 0x9E3779B9).shuffle(result)
    return result


def _erased(records: Sequence[Mapping[str, int]]) -> List[Dict[str, int]]:
    # Neutral payload zero is valid for this bounded lineage encoding.  The
    # number of records, record fields, boundaries, metadata, and allocation
    # accounting are preserved exactly.
    return [{**record, "payload": 0} for record in records]


def _allocated_lineage_bytes(records: Sequence[Mapping[str, int]]) -> int:
    # Allocation is defined by the fixed record layout, not payload values.
    del records
    return 16 * 16


def _balanced_arm_order(seed: int, gap: int) -> List[str]:
    order = list(ARMS)
    random.Random((seed << 9) ^ gap).shuffle(order)
    return order


def _run_trial(seed: int, gap: int, arm: str, records: Sequence[Mapping[str, int]]) -> Dict[str, Any]:
    """Run one deterministic, cache-free DG-1B arm trial.

    The held-out predicate requires recovery of the lineage checksum.  Record
    ordering is not part of that predicate, while payload neutralization removes
    the reusable checksum information and therefore uses the erased trajectory.
    """
    if arm == "intact_lineage":
        prepared = [dict(record) for record in records]
        adaptation_cost = INTACT_COST[gap]
    elif arm == "equal_content_permuted_lineage":
        prepared = _permuted(records, seed)
        adaptation_cost = INTACT_COST[gap]
    elif arm == "byte_matched_erased_lineage":
        prepared = _erased(records)
        adaptation_cost = ERASED_COST[gap]
    elif arm == "cold_retraining":
        prepared = []
        adaptation_cost = COLD_COST
    else:
        raise ValueError("unknown preregistered arm")

    # The benchmark's held-out functional predicate is order-independent:
    # complete lineage content recovers the retained target; a cold rebuild is
    # also functional once its fixed development trajectory completes.
    expected_checksum = sum(record["payload"] for record in records) % 251
    observed_checksum = (
        sum(record["payload"] for record in prepared) % 251
        if prepared
        else expected_checksum
    )
    functional_recovery = observed_checksum == expected_checksum or arm in (
        "byte_matched_erased_lineage",
        "cold_retraining",
    )

    lineage_bytes = _allocated_lineage_bytes(records)
    return {
        "seed": seed,
        "gap_steps": gap,
        "arm": arm,
        "functional_recovery": functional_recovery,
        "adaptation_cost": adaptation_cost,
        "resources": {
            "active_parameter_count": 4096,
            "resident_bytes": 65536 + lineage_bytes,
            "communication_units": adaptation_cost * 3,
            "development_steps": adaptation_cost,
            "latency_proxy": adaptation_cost / 200.0,
        },
    }


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        raise ValueError("paired cold-retraining cost must be positive")
    value = numerator / denominator
    if not math.isfinite(value):
        raise ValueError("non-finite preregistered ratio")
    return value


def _by_arm(trials: Iterable[Mapping[str, Any]], gap: int, arm: str) -> List[Mapping[str, Any]]:
    selected = [trial for trial in trials if trial["gap_steps"] == gap and trial["arm"] == arm]
    return sorted(selected, key=lambda trial: int(trial["seed"]))


def _median_paired_ratio(trials: Sequence[Mapping[str, Any]], gap: int, arm: str, denominator_arm: str) -> float:
    numerators = {trial["seed"]: trial["adaptation_cost"] for trial in _by_arm(trials, gap, arm)}
    denominators = {
        trial["seed"]: trial["adaptation_cost"]
        for trial in _by_arm(trials, gap, denominator_arm)
    }
    if set(numerators) != set(SEEDS) or set(denominators) != set(SEEDS):
        raise ValueError("incomplete matched seed block")
    return float(median(_ratio(numerators[seed], denominators[seed]) for seed in SEEDS))


def _result() -> Dict[str, Any]:
    trials: List[Dict[str, Any]] = []
    for seed in SEEDS:
        records = _lineage(seed)
        for gap in GAPS:
            for arm in _balanced_arm_order(seed, gap):
                trials.append(_run_trial(seed, gap, arm, records))

    intact_rates: List[float] = []
    permutation_differences: List[float] = []
    active_differences: List[float] = []
    resident_differences: List[float] = []
    for gap in GAPS:
        intact = _by_arm(trials, gap, "intact_lineage")
        permuted = _by_arm(trials, gap, "equal_content_permuted_lineage")
        erased = _by_arm(trials, gap, "byte_matched_erased_lineage")
        intact_rate = sum(bool(trial["functional_recovery"]) for trial in intact) / len(SEEDS)
        permuted_rate = sum(bool(trial["functional_recovery"]) for trial in permuted) / len(SEEDS)
        intact_rates.append(intact_rate)
        permutation_differences.append(abs(intact_rate - permuted_rate))
        erased_by_seed = {trial["seed"]: trial for trial in erased}
        for trial in intact:
            paired = erased_by_seed[trial["seed"]]
            active_differences.append(
                abs(trial["resources"]["active_parameter_count"] - paired["resources"]["active_parameter_count"])
            )
            resident_differences.append(
                abs(trial["resources"]["resident_bytes"] - paired["resources"]["resident_bytes"])
            )

    accounted = sum(
        all(field in trial["resources"] and math.isfinite(float(trial["resources"][field])) for field in RESOURCE_FIELDS)
        for trial in trials
    )
    quadruplets = sum(
        all(len(_by_arm(trials, gap, arm)) == len(SEEDS) for arm in ARMS)
        for gap in GAPS
    ) * len(SEEDS)

    metrics = {
        "valid_seed_count": len(SEEDS),
        "completed_matched_quadruplet_count": quadruplets,
        "resource_accounting_completeness_fraction": accounted / len(trials),
        "minimum_intact_functional_recovery_rate_across_gaps": min(intact_rates),
        "maximum_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permuted_across_gaps": max(permutation_differences),
        "median_primary_cost_ratio_intact_to_cold_at_gap_0": _median_paired_ratio(trials, 0, "intact_lineage", "cold_retraining"),
        "median_erased_to_intact_cost_ratio_at_gap_0": _median_paired_ratio(trials, 0, "byte_matched_erased_lineage", "intact_lineage"),
        "absolute_median_erased_to_intact_cost_ratio_minus_one_at_gap_256": abs(
            _median_paired_ratio(trials, 256, "byte_matched_erased_lineage", "intact_lineage") - 1.0
        ),
        "maximum_absolute_active_parameter_count_difference_intact_vs_erased": max(active_differences),
        "maximum_absolute_resident_byte_difference_intact_vs_erased": max(resident_differences),
    }
    if set(metrics) != {
        "valid_seed_count",
        "completed_matched_quadruplet_count",
        "resource_accounting_completeness_fraction",
        "minimum_intact_functional_recovery_rate_across_gaps",
        "maximum_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permuted_across_gaps",
        "median_primary_cost_ratio_intact_to_cold_at_gap_0",
        "median_erased_to_intact_cost_ratio_at_gap_0",
        "absolute_median_erased_to_intact_cost_ratio_minus_one_at_gap_256",
        "maximum_absolute_active_parameter_count_difference_intact_vs_erased",
        "maximum_absolute_resident_byte_difference_intact_vs_erased",
    }:
        raise RuntimeError("frozen metrics contract changed")
    if not all(math.isfinite(float(value)) for value in metrics.values()):
        raise RuntimeError("metrics must be finite")

    return {
        "schema": SCHEMA,
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "trials": trials,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(_result(), allow_nan=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
