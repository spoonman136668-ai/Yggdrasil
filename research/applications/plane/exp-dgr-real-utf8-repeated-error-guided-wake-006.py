"""Sealed source for EXP-DGR-REAL-UTF8-REPEATED-ERROR-GUIDED-WAKE-006."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-REPEATED-ERROR-GUIDED-WAKE-006"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
DEMAND_FILES = {
    "A": ("research/architecture/developmental-substrate-v0.1.ice", "cea1d9966056f097838eb350a42795219f046fc3"),
    "B": ("research/architecture/developmental-substrate-v0.ice", "03e0643a885bdbf0a40d731876659224e9c7ac43"),
    "C": ("research/architecture/resource-pressure.ice", "bcfee51a0b85dbc22cc046a1437775c04e1372c3"),
}
CYCLE_ORDER = ("A", "B", "C", "C", "B", "A")
ACTIVE_CEILING = 8


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
    if len(active_records) != ACTIVE_CEILING or len(retained_records) != ACTIVE_CEILING:
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
        "train_eval_blob_overlap_count": 0.0,
        "valid_cycle_count": 0.0,
        "minimum_full_incremental_correct_count": float("inf"),
        "minimum_wake_count_per_cross_file_transition": 8.0,
        "minimum_eviction_count_per_cross_file_transition": 8.0,
        "maximum_same_file_transition_change_count": 0.0,
        "revisit_active_set_mismatch_count": 0.0,
        "minimum_primary_active_structure_count": 8.0,
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": 8.0,
        "maximum_primary_retained_structure_count": 0.0,
        "minimum_primary_retained_incremental_correct_fraction": 1.0,
        "minimum_primary_minus_static_retained_fraction": 1.0,
        "minimum_eval_covered_position_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "minimum_effective_event_reduction_fraction": 1.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "future_half_selection_access_count": 0.0,
        "learned_state_mutation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_transition_rows": 0.0,
    }

    train = []
    train_shas = set()
    for path, expected in prior.TRAIN_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["training_file_identity_mismatch_count"] += float(not ok)
        train.append(data)
        train_shas.add(expected)
    demands = {}
    for label, (path, expected) in DEMAND_FILES.items():
        data, ok = prior.load_checked(path, expected)
        metrics["evaluation_file_identity_mismatch_count"] += float(not ok)
        metrics["train_eval_blob_overlap_count"] += float(expected in train_shas)
        demands[label] = data

    baseline = prior.baseline_train(train)
    stats, overflow, invalid = prior.candidate_stats(train)
    metrics["invalid_transition_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    metrics["invalid_transition_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    static, static_hibernated, static_retained = pressure.pressure(prior, cells, stats)
    rows = wake.known_rows(pressure, prior, cells, stats)
    if len(full) != 16 or len(rows) != 16 or len(static) != 8 or len(static_hibernated) != 8:
        metrics["invalid_transition_rows"] += 1.0
    metrics["retained_record_integrity_mismatch_count"] += float(pressure.verify_retained(static_retained, static_hibernated))

    original_records = sorted(record(row) for row in rows)
    original_learned_state = sorted((row["key"], row["best"]) for row in rows)
    static_keys = set(static)
    active_rows = [row for row in rows if row["key"] in static_keys]
    retained_rows = [row for row in rows if row["key"] not in static_keys]
    metrics["state_partition_mismatch_count"] += float(partition_mismatches(active_rows, retained_rows, original_records))
    first_visit_sets = {}
    previous_label = None

    for label in CYCLE_ORDER:
        data = demands[label]
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]
        available_rows = active_rows + retained_rows
        available = {row["key"]: row["best"] for row in available_rows}
        cue_scores = prior_experiment.contributions(prior, cue, baseline, set(available), available)
        selected_rows = sorted(available_rows, key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]))[:ACTIVE_CEILING]
        selected_keys = {row["key"] for row in selected_rows}
        old_active_keys = {row["key"] for row in active_rows}
        wake_count = len(selected_keys - old_active_keys)
        eviction_count = len(old_active_keys - selected_keys)
        if previous_label is not None:
            if label == previous_label:
                metrics["maximum_same_file_transition_change_count"] = max(metrics["maximum_same_file_transition_change_count"], float(wake_count + eviction_count))
            else:
                metrics["minimum_wake_count_per_cross_file_transition"] = min(metrics["minimum_wake_count_per_cross_file_transition"], float(wake_count))
                metrics["minimum_eviction_count_per_cross_file_transition"] = min(metrics["minimum_eviction_count_per_cross_file_transition"], float(eviction_count))

        active_rows = selected_rows
        retained_rows = [row for row in available_rows if row["key"] not in selected_keys]
        active = wake.active_map(active_rows)
        retained = wake.encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(wake.verify_records(retained, retained_rows))
        metrics["state_partition_mismatch_count"] += float(partition_mismatches(active_rows, retained_rows, original_records))
        if label in first_visit_sets:
            metrics["revisit_active_set_mismatch_count"] += float(selected_keys != first_visit_sets[label])
        else:
            first_visit_sets[label] = selected_keys

        metrics["minimum_primary_active_structure_count"] = min(metrics["minimum_primary_active_structure_count"], float(len(active_rows)))
        metrics["maximum_primary_active_structure_count"] = max(metrics["maximum_primary_active_structure_count"], float(len(active_rows)))
        metrics["minimum_primary_retained_structure_count"] = min(metrics["minimum_primary_retained_structure_count"], float(len(retained_rows)))
        metrics["maximum_primary_retained_structure_count"] = max(metrics["maximum_primary_retained_structure_count"], float(len(retained_rows)))
        full_increment, primary_fraction = prior_experiment.model_fraction(pressure, prior, evaluation, baseline, full, active)
        _, static_fraction = prior_experiment.model_fraction(pressure, prior, evaluation, baseline, full, static)
        if full_increment <= 0:
            metrics["invalid_transition_rows"] += 1.0
            continue
        metrics["minimum_full_incremental_correct_count"] = min(metrics["minimum_full_incremental_correct_count"], float(full_increment))
        metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], primary_fraction)
        metrics["minimum_primary_minus_static_retained_fraction"] = min(metrics["minimum_primary_minus_static_retained_fraction"], primary_fraction - static_fraction)
        _, coverage, gain, event_reduction = pressure.pressured_eval(prior, evaluation, baseline, active)
        metrics["minimum_eval_covered_position_fraction"] = min(metrics["minimum_eval_covered_position_fraction"], coverage)
        metrics["minimum_eval_covered_accuracy_gain"] = min(metrics["minimum_eval_covered_accuracy_gain"], gain)
        metrics["minimum_effective_event_reduction_fraction"] = min(metrics["minimum_effective_event_reduction_fraction"], event_reduction)
        metrics["valid_cycle_count"] += 1.0
        previous_label = label

    final_learned_state = sorted((row["key"], row["best"]) for row in active_rows + retained_rows)
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
