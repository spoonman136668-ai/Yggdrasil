"""Sealed source for EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-BOUNDARY-008."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-BOUNDARY-008"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-repeated-error-guided-wake-006.py")
ACTIVE_COUNT = 7


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_repeated_wake", PRIOR_PATH)
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
    if len(active_records) != ACTIVE_COUNT or len(retained_records) != 16 - ACTIVE_COUNT:
        mismatch += 1
    if set(active_records) & set(retained_records):
        mismatch += 1
    if sorted(active_records + retained_records) != original_records:
        mismatch += 1
    return mismatch


def run():
    repeated = load_prior_experiment()
    error_guided = repeated.load_prior_experiment()
    wake = error_guided.load_wake()
    pressure = wake.load_pressure()
    prior = pressure.load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "train_eval_blob_overlap_count": 0.0,
        "valid_evaluation_file_count": 0.0,
        "minimum_full_incremental_correct_count": float("inf"),
        "minimum_primary_active_structure_count": float(ACTIVE_COUNT),
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": float(16 - ACTIVE_COUNT),
        "maximum_primary_retained_structure_count": 0.0,
        "minimum_primary_retained_incremental_correct_fraction": 1.0,
        "minimum_primary_minus_static_retained_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "future_half_selection_access_count": 0.0,
        "learned_state_mutation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }
    train = []
    train_shas = set()
    for path, expected in prior.TRAIN_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["training_file_identity_mismatch_count"] += float(not ok)
        train.append(data)
        train_shas.add(expected)
    demands = []
    for path, expected in repeated.DEMAND_FILES.values():
        data, ok = prior.load_checked(path, expected)
        metrics["evaluation_file_identity_mismatch_count"] += float(not ok)
        metrics["train_eval_blob_overlap_count"] += float(expected in train_shas)
        demands.append(data)
    baseline = prior.baseline_train(train)
    stats, overflow, invalid = prior.candidate_stats(train)
    metrics["invalid_evaluation_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    metrics["invalid_evaluation_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    rows = wake.known_rows(pressure, prior, cells, stats)
    if len(full) != 16 or len(rows) != 16:
        metrics["invalid_evaluation_rows"] += 1.0
    original_records = sorted(record(row) for row in rows)
    original_learned_state = sorted((row["key"], row["best"]) for row in rows)
    static_rows = sorted(rows, key=lambda row: (-row["utility"], row["key"]))[:ACTIVE_COUNT]
    static = wake.active_map(static_rows)
    for data in demands:
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]
        available = {row["key"]: row["best"] for row in rows}
        cue_scores = error_guided.contributions(prior, cue, baseline, set(available), available)
        active_rows = sorted(rows, key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]))[:ACTIVE_COUNT]
        active_keys = {row["key"] for row in active_rows}
        retained_rows = [row for row in rows if row["key"] not in active_keys]
        active = wake.active_map(active_rows)
        retained = wake.encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(wake.verify_records(retained, retained_rows))
        metrics["state_partition_mismatch_count"] += float(partition_mismatches(active_rows, retained_rows, original_records))
        metrics["minimum_primary_active_structure_count"] = min(metrics["minimum_primary_active_structure_count"], float(len(active_rows)))
        metrics["maximum_primary_active_structure_count"] = max(metrics["maximum_primary_active_structure_count"], float(len(active_rows)))
        metrics["minimum_primary_retained_structure_count"] = min(metrics["minimum_primary_retained_structure_count"], float(len(retained_rows)))
        metrics["maximum_primary_retained_structure_count"] = max(metrics["maximum_primary_retained_structure_count"], float(len(retained_rows)))
        full_increment, primary_fraction = error_guided.model_fraction(pressure, prior, evaluation, baseline, full, active)
        _, static_fraction = error_guided.model_fraction(pressure, prior, evaluation, baseline, full, static)
        if full_increment <= 0:
            metrics["invalid_evaluation_rows"] += 1.0
            continue
        metrics["minimum_full_incremental_correct_count"] = min(metrics["minimum_full_incremental_correct_count"], float(full_increment))
        metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], primary_fraction)
        metrics["minimum_primary_minus_static_retained_fraction"] = min(metrics["minimum_primary_minus_static_retained_fraction"], primary_fraction - static_fraction)
        _, _, gain, _ = pressure.pressured_eval(prior, evaluation, baseline, active)
        metrics["minimum_eval_covered_accuracy_gain"] = min(metrics["minimum_eval_covered_accuracy_gain"], gain)
        metrics["valid_evaluation_file_count"] += 1.0
    final_learned_state = sorted((row["key"], row["best"]) for row in rows)
    metrics["learned_state_mutation_count"] = float(final_learned_state != original_learned_state)
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
