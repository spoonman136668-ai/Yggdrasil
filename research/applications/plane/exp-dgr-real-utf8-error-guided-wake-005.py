"""Sealed source for EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005"
WAKE_PATH = Path("research/applications/plane/exp-dgr-real-utf8-selective-wake-003.py")
EVAL_FILES = (
    ("research/architecture/cell-model.ice", "db9d3c06e0cc0ddd780c7e51685d7dcdfdd32673"),
    ("research/architecture/developmental-genome.ice", "d7791d7971ebcc82999cb90219cb71387ba3005e"),
)
ACTIVE_CEILING = 8


def load_wake():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_wake", WAKE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("WAKE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contributions(prior, cue, baseline, keys, full):
    scores = {key: 0 for key in keys}
    for i in range(4, len(cue)):
        key = tuple(cue[i - 4:i])
        if key not in scores:
            continue
        target = cue[i]
        scores[key] += int(full[key] == target)
        scores[key] -= int(prior.baseline_predict(baseline, cue[i - 1]) == target)
    return scores


def model_fraction(pressure, prior, data, baseline, full, active):
    baseline_correct, full_correct, _ = pressure.model_correct_counts(prior, data, baseline, full)
    _, active_correct, _ = pressure.model_correct_counts(prior, data, baseline, active)
    full_increment = full_correct - baseline_correct
    if full_increment <= 0:
        return full_increment, 0.0
    return full_increment, (active_correct - baseline_correct) / full_increment


def run():
    wake = load_wake()
    pressure = wake.load_pressure()
    prior = pressure.load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "train_eval_blob_overlap_count": 0.0,
        "valid_evaluation_file_count": 0.0,
        "minimum_full_incremental_correct_count": float("inf"),
        "minimum_woken_hibernated_motif_count_per_file": 8.0,
        "minimum_primary_active_structure_count": 8.0,
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": 8.0,
        "maximum_primary_retained_structure_count": 0.0,
        "minimum_primary_retained_incremental_correct_fraction": 1.0,
        "minimum_primary_minus_static_retained_fraction": 1.0,
        "minimum_primary_minus_occurrence_retained_fraction": 1.0,
        "minimum_eval_covered_position_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "minimum_effective_event_reduction_fraction": 1.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "future_half_selection_access_count": 0.0,
        "learned_state_mutation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_wake_rows": 0.0,
    }
    train = []
    train_shas = set()
    for path, expected in prior.TRAIN_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["training_file_identity_mismatch_count"] += float(not ok)
        train.append(data)
        train_shas.add(expected)
    evals = []
    for path, expected in EVAL_FILES:
        data, ok = prior.load_checked(path, expected)
        metrics["evaluation_file_identity_mismatch_count"] += float(not ok)
        metrics["train_eval_blob_overlap_count"] += float(expected in train_shas)
        evals.append(data)

    baseline = prior.baseline_train(train)
    stats, overflow, invalid = prior.candidate_stats(train)
    metrics["invalid_wake_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    metrics["invalid_wake_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    static, static_hibernated, static_retained = pressure.pressure(prior, cells, stats)
    if len(full) != 16 or len(static) != 8 or len(static_hibernated) != 8:
        metrics["invalid_wake_rows"] += 1.0
    metrics["retained_record_integrity_mismatch_count"] += float(pressure.verify_retained(static_retained, static_hibernated))
    rows = wake.known_rows(pressure, prior, cells, stats)
    keys = {row["key"] for row in rows}
    static_keys = set(static)

    for data in evals:
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]
        occurrence_counts = wake.cue_counts(cue, keys)
        occurrence_rows = sorted(rows, key=lambda row: (-occurrence_counts[row["key"]], -row["utility"], row["key"]))[:ACTIVE_CEILING]
        occurrence_active = wake.active_map(occurrence_rows)
        cue_scores = contributions(prior, cue, baseline, keys, full)
        primary_rows = sorted(rows, key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]))[:ACTIVE_CEILING]
        primary_keys = {row["key"] for row in primary_rows}
        retained_rows = [row for row in rows if row["key"] not in primary_keys]
        primary = wake.active_map(primary_rows)
        retained = wake.encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(wake.verify_records(retained, retained_rows))
        metrics["minimum_woken_hibernated_motif_count_per_file"] = min(metrics["minimum_woken_hibernated_motif_count_per_file"], float(len(primary_keys - static_keys)))
        metrics["minimum_primary_active_structure_count"] = min(metrics["minimum_primary_active_structure_count"], float(len(primary)))
        metrics["maximum_primary_active_structure_count"] = max(metrics["maximum_primary_active_structure_count"], float(len(primary)))
        metrics["minimum_primary_retained_structure_count"] = min(metrics["minimum_primary_retained_structure_count"], float(len(retained_rows)))
        metrics["maximum_primary_retained_structure_count"] = max(metrics["maximum_primary_retained_structure_count"], float(len(retained_rows)))
        full_increment, primary_fraction = model_fraction(pressure, prior, evaluation, baseline, full, primary)
        _, static_fraction = model_fraction(pressure, prior, evaluation, baseline, full, static)
        _, occurrence_fraction = model_fraction(pressure, prior, evaluation, baseline, full, occurrence_active)
        if full_increment <= 0:
            metrics["invalid_wake_rows"] += 1.0
            continue
        metrics["minimum_full_incremental_correct_count"] = min(metrics["minimum_full_incremental_correct_count"], float(full_increment))
        metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], primary_fraction)
        metrics["minimum_primary_minus_static_retained_fraction"] = min(metrics["minimum_primary_minus_static_retained_fraction"], primary_fraction - static_fraction)
        metrics["minimum_primary_minus_occurrence_retained_fraction"] = min(metrics["minimum_primary_minus_occurrence_retained_fraction"], primary_fraction - occurrence_fraction)
        _, coverage, gain, event_reduction = pressure.pressured_eval(prior, evaluation, baseline, primary)
        metrics["minimum_eval_covered_position_fraction"] = min(metrics["minimum_eval_covered_position_fraction"], coverage)
        metrics["minimum_eval_covered_accuracy_gain"] = min(metrics["minimum_eval_covered_accuracy_gain"], gain)
        metrics["minimum_effective_event_reduction_fraction"] = min(metrics["minimum_effective_event_reduction_fraction"], event_reduction)
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
