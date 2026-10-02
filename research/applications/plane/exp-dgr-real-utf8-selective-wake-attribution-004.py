"""Sealed source for EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-ATTRIBUTION-004."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-ATTRIBUTION-004"
WAKE_PATH = Path("research/applications/plane/exp-dgr-real-utf8-selective-wake-003.py")


def load_wake():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_wake", WAKE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("WAKE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def motif_contributions(prior, data, baseline, full):
    contributions = {key: 0 for key in full}
    for i in range(4, len(data)):
        key = tuple(data[i - 4:i])
        if key not in full:
            continue
        target = data[i]
        motif_hit = int(full[key] == target)
        baseline_hit = int(prior.baseline_predict(baseline, data[i - 1]) == target)
        contributions[key] += motif_hit - baseline_hit
    return contributions


def jaccard(a, b):
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def minv(a, b):
    return b if b < a else a


def maxv(a, b):
    return b if b > a else a


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
        "minimum_optimal_active_structure_count": 8.0,
        "maximum_optimal_active_structure_count": 0.0,
        "minimum_optimal_retained_incremental_correct_fraction": 1.0,
        "minimum_optimal_minus_cue_retained_fraction": 1.0,
        "minimum_optimal_minus_static_retained_fraction": 1.0,
        "maximum_cue_optimal_jaccard": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_attribution_rows": 0.0,
    }

    train = []
    evals = []
    train_shas = set()
    for path, expected in prior.TRAIN_FILES:
        data, ok = prior.load_checked(path, expected)
        if not ok:
            metrics["training_file_identity_mismatch_count"] += 1.0
        train.append(data)
        train_shas.add(expected)
    for path, expected in prior.EVAL_FILES:
        data, ok = prior.load_checked(path, expected)
        if not ok:
            metrics["evaluation_file_identity_mismatch_count"] += 1.0
        if expected in train_shas:
            metrics["train_eval_blob_overlap_count"] += 1.0
        evals.append(data)

    baseline = prior.baseline_train(train)
    stats, overflow, invalid = prior.candidate_stats(train)
    if overflow or invalid:
        metrics["invalid_attribution_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    if radius_violations:
        metrics["invalid_attribution_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    static_active, static_hibernated, static_retained = pressure.pressure(prior, cells, stats)
    if len(full) != 16 or len(static_active) != 8 or len(static_hibernated) != 8:
        metrics["invalid_attribution_rows"] += 1.0
    if pressure.verify_retained(static_retained, static_hibernated) != 0:
        metrics["invalid_attribution_rows"] += 1.0

    rows = wake.known_rows(pressure, prior, cells, stats)
    row_by_key = {row["key"]: row for row in rows}
    all_keys = set(row_by_key)
    static_keys = set(static_active)

    for data in evals:
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]

        counts = wake.cue_counts(cue, all_keys)
        cue_rows = sorted(
            rows,
            key=lambda r: (-counts[r["key"]], -r["utility"], r["key"]),
        )[:8]
        cue_keys = {row["key"] for row in cue_rows}
        cue_map = wake.active_map(cue_rows)

        contributions = motif_contributions(prior, evaluation, baseline, full)
        optimal_rows = sorted(
            rows,
            key=lambda r: (
                -contributions[r["key"]],
                -r["utility"],
                r["key"],
            ),
        )[:8]
        optimal_keys = {row["key"] for row in optimal_rows}
        optimal_map = wake.active_map(optimal_rows)

        baseline_correct, full_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, full
        )
        _, static_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, static_active
        )
        _, cue_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, cue_map
        )
        _, optimal_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, optimal_map
        )

        full_increment = full_correct - baseline_correct
        if full_increment <= 0:
            metrics["invalid_attribution_rows"] += 1.0
            continue
        static_fraction = (static_correct - baseline_correct) / full_increment
        cue_fraction = (cue_correct - baseline_correct) / full_increment
        optimal_fraction = (optimal_correct - baseline_correct) / full_increment

        metrics["minimum_full_incremental_correct_count"] = minv(
            metrics["minimum_full_incremental_correct_count"],
            float(full_increment),
        )
        metrics["minimum_optimal_active_structure_count"] = minv(
            metrics["minimum_optimal_active_structure_count"],
            float(len(optimal_map)),
        )
        metrics["maximum_optimal_active_structure_count"] = maxv(
            metrics["maximum_optimal_active_structure_count"],
            float(len(optimal_map)),
        )
        metrics["minimum_optimal_retained_incremental_correct_fraction"] = minv(
            metrics["minimum_optimal_retained_incremental_correct_fraction"],
            optimal_fraction,
        )
        metrics["minimum_optimal_minus_cue_retained_fraction"] = minv(
            metrics["minimum_optimal_minus_cue_retained_fraction"],
            optimal_fraction - cue_fraction,
        )
        metrics["minimum_optimal_minus_static_retained_fraction"] = minv(
            metrics["minimum_optimal_minus_static_retained_fraction"],
            optimal_fraction - static_fraction,
        )
        metrics["maximum_cue_optimal_jaccard"] = maxv(
            metrics["maximum_cue_optimal_jaccard"],
            jaccard(cue_keys, optimal_keys),
        )
        metrics["valid_evaluation_file_count"] += 1.0

    assert all(math.isfinite(v) for v in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
