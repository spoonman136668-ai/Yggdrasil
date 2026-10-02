"""Sealed source for EXP-DGR-REAL-UTF8-CROSS-DOMAIN-FIRST-HALF-ADAPTATION-012."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-CROSS-DOMAIN-FIRST-HALF-ADAPTATION-012"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
DEMAND_FILES = (
    ("research/applications/track-a/a02-adaptive-transform-service-organism.ice", "2770482f2bd0fcffab8b00d206c54ae81f3ae7a1", 21855),
    ("research/applications/track-a/a03-fixa-dynamic-partition-remerge-alignment.ice", "ea322d9b33044d9c0442df460fc2b354b2d4830b", 11293),
    ("research/applications/track-a/a03-heldout-adaptive-generalization.ice", "fdb9b8c908ed45e075fdb39ac578c0e3c79edce5", 28605),
)
ACTIVE_CEILING = 7


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_error_guided", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(row):
    return bytes((row["cell_index"], *row["key"], row["best"]))


def partition_mismatches(active_rows, retained_rows, original_records):
    active_records = [record(row) for row in active_rows]
    retained_records = [record(row) for row in retained_rows]
    mismatch = 0
    if len(active_records) != ACTIVE_CEILING or len(retained_records) != 16 - ACTIVE_CEILING:
        mismatch += 1
    if set(active_records) & set(retained_records):
        mismatch += 1
    if sorted(active_records + retained_records) != original_records:
        mismatch += 1
    return mismatch


def run():
    prior_experiment = load_prior_experiment()
    wake = prior_experiment.load_wake()
    pressure = wake.load_pressure()
    prior = pressure.load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "cross_file_adaptation_access_count": 0.0,
        "valid_evaluation_file_count": 0.0,
        "minimum_adapted_full_incremental_correct_count": float("inf"),
        "minimum_adapted_minus_frozen_full_incremental_correct_count": float("inf"),
        "minimum_primary_active_structure_count": 16.0,
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": 16.0,
        "maximum_primary_retained_structure_count": 0.0,
        "minimum_primary_retained_incremental_correct_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "future_half_selection_access_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }
    base_train = []
    for path, expected in prior.TRAIN_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["training_file_identity_mismatch_count"] += float(not ok)
        base_train.append(data)
    demands = []
    for path, expected, expected_size in DEMAND_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["evaluation_file_identity_mismatch_count"] += float(not ok or len(data) != expected_size)
        demands.append(data)

    baseline = prior.baseline_train(base_train)
    frozen_stats, overflow, invalid = prior.candidate_stats(base_train)
    metrics["invalid_evaluation_rows"] += float(overflow + invalid)
    frozen_cells, radius_violations = prior.develop(frozen_stats)
    metrics["invalid_evaluation_rows"] += float(radius_violations)
    frozen_full = prior.specialized_map(frozen_cells)
    if len(frozen_full) != 16:
        metrics["invalid_evaluation_rows"] += 1.0

    for data in demands:
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]
        adapted_stats, overflow, invalid = prior.candidate_stats(base_train + [cue])
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        adapted_cells, radius_violations = prior.develop(adapted_stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)
        adapted_full = prior.specialized_map(adapted_cells)
        rows = wake.known_rows(pressure, prior, adapted_cells, adapted_stats)
        if len(adapted_full) != 16 or len(rows) != 16:
            metrics["invalid_evaluation_rows"] += 1.0
        keys = {row["key"] for row in rows}
        cue_scores = prior_experiment.contributions(prior, cue, baseline, keys, adapted_full)
        active_rows = sorted(rows, key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]))[:ACTIVE_CEILING]
        active_keys = {row["key"] for row in active_rows}
        retained_rows = [row for row in rows if row["key"] not in active_keys]
        active = wake.active_map(active_rows)
        retained = wake.encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(wake.verify_records(retained, retained_rows))
        original_records = sorted(record(row) for row in rows)
        metrics["state_partition_mismatch_count"] += float(partition_mismatches(active_rows, retained_rows, original_records))
        metrics["minimum_primary_active_structure_count"] = min(metrics["minimum_primary_active_structure_count"], float(len(active_rows)))
        metrics["maximum_primary_active_structure_count"] = max(metrics["maximum_primary_active_structure_count"], float(len(active_rows)))
        metrics["minimum_primary_retained_structure_count"] = min(metrics["minimum_primary_retained_structure_count"], float(len(retained_rows)))
        metrics["maximum_primary_retained_structure_count"] = max(metrics["maximum_primary_retained_structure_count"], float(len(retained_rows)))

        baseline_correct, frozen_correct, _ = pressure.model_correct_counts(prior, evaluation, baseline, frozen_full)
        _, adapted_correct, _ = pressure.model_correct_counts(prior, evaluation, baseline, adapted_full)
        adapted_increment = adapted_correct - baseline_correct
        frozen_increment = frozen_correct - baseline_correct
        metrics["minimum_adapted_full_incremental_correct_count"] = min(metrics["minimum_adapted_full_incremental_correct_count"], float(adapted_increment))
        metrics["minimum_adapted_minus_frozen_full_incremental_correct_count"] = min(metrics["minimum_adapted_minus_frozen_full_incremental_correct_count"], float(adapted_increment - frozen_increment))
        if adapted_increment > 0:
            _, primary_fraction = prior_experiment.model_fraction(pressure, prior, evaluation, baseline, adapted_full, active)
            metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], primary_fraction)
        else:
            metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], 0.0)
        _, _, gain, _ = pressure.pressured_eval(prior, evaluation, baseline, active)
        metrics["minimum_eval_covered_accuracy_gain"] = min(metrics["minimum_eval_covered_accuracy_gain"], gain)
        metrics["valid_evaluation_file_count"] += 1.0

    assert all(math.isfinite(value) for value in metrics.values())
    return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
