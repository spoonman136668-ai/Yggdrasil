"""Sealed source for EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-003."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-003"
PRESSURE_PATH = Path("research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py")
ACTIVE_CEILING = 8
RECORD_BYTES = 6


def load_pressure():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_pressure", PRESSURE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRESSURE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def known_rows(pressure, prior, cells, stats):
    rows = []
    for cell in cells:
        if cell["role"] != "specialized":
            continue
        row = pressure.row_for_key(prior, stats, cell["key"])
        row["cell_index"] = cell["index"]
        rows.append(row)
    return rows


def cue_counts(cue, keys):
    counts = {key: 0 for key in keys}
    if len(cue) < 4:
        return counts
    for start in range(0, len(cue) - 3):
        key = tuple(cue[start:start + 4])
        if key in counts:
            counts[key] += 1
    return counts


def encode_retained(rows):
    data = bytearray()
    for row in sorted(rows, key=lambda r: r["cell_index"]):
        data.extend(bytes((
            row["cell_index"],
            row["key"][0],
            row["key"][1],
            row["key"][2],
            row["key"][3],
            row["best"],
        )))
    return bytes(data)


def verify_records(retained, expected_rows):
    expected = {
        row["cell_index"]: (row["key"], row["best"])
        for row in expected_rows
    }
    mismatch = 0
    seen = set()
    if len(retained) != len(expected_rows) * RECORD_BYTES:
        mismatch += 1
    for offset in range(0, len(retained), RECORD_BYTES):
        record = retained[offset:offset + RECORD_BYTES]
        if len(record) != RECORD_BYTES:
            mismatch += 1
            continue
        cell_index = record[0]
        key = tuple(record[1:5])
        best = record[5]
        if cell_index in seen:
            mismatch += 1
        seen.add(cell_index)
        if cell_index not in expected:
            mismatch += 1
            continue
        want_key, want_best = expected[cell_index]
        if key != want_key or best != want_best:
            mismatch += 1
    if seen != set(expected):
        mismatch += len(set(expected) - seen)
    return mismatch


def active_map(rows):
    return {row["key"]: row["best"] for row in rows}


def run():
    pressure = load_pressure()
    prior = pressure.load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "train_eval_blob_overlap_count": 0.0,
        "valid_evaluation_file_count": 0.0,
        "minimum_woken_hibernated_motif_count_per_file": 8.0,
        "maximum_woken_hibernated_motif_count_per_file": 0.0,
        "minimum_post_wake_active_structure_count": 8.0,
        "maximum_post_wake_active_structure_count": 0.0,
        "minimum_post_wake_retained_structure_count": 8.0,
        "maximum_post_wake_retained_structure_count": 0.0,
        "minimum_retained_incremental_correct_fraction": 1.0,
        "minimum_improvement_over_static_fraction": 1.0,
        "minimum_eval_covered_position_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "minimum_effective_event_reduction_fraction": 1.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "cue_target_byte_access_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_wake_rows": 0.0,
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
        metrics["invalid_wake_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    if radius_violations:
        metrics["invalid_wake_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    static_active, static_hibernated_rows, static_retained = pressure.pressure(prior, cells, stats)
    if len(full) != 16 or len(static_active) != 8 or len(static_hibernated_rows) != 8:
        metrics["invalid_wake_rows"] += 1.0
    if pressure.verify_retained(static_retained, static_hibernated_rows) != 0:
        metrics["invalid_wake_rows"] += 1.0

    rows = known_rows(pressure, prior, cells, stats)
    row_by_key = {row["key"]: row for row in rows}
    static_active_keys = set(static_active)
    all_keys = set(row_by_key)

    for data in evals:
        midpoint = len(data) // 2
        cue = data[:midpoint]
        evaluation = data[midpoint:]
        counts = cue_counts(cue, all_keys)
        ranked = sorted(
            rows,
            key=lambda r: (
                -counts[r["key"]],
                -r["utility"],
                r["key"],
            ),
        )
        selected_rows = ranked[:ACTIVE_CEILING]
        selected_keys = {row["key"] for row in selected_rows}
        retained_rows = [row for row in rows if row["key"] not in selected_keys]
        adapted = active_map(selected_rows)
        retained = encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(
            verify_records(retained, retained_rows)
        )

        woken = len(selected_keys - static_active_keys)
        metrics["minimum_woken_hibernated_motif_count_per_file"] = min(
            metrics["minimum_woken_hibernated_motif_count_per_file"],
            float(woken),
        )
        metrics["maximum_woken_hibernated_motif_count_per_file"] = max(
            metrics["maximum_woken_hibernated_motif_count_per_file"],
            float(woken),
        )
        metrics["minimum_post_wake_active_structure_count"] = min(
            metrics["minimum_post_wake_active_structure_count"],
            float(len(adapted)),
        )
        metrics["maximum_post_wake_active_structure_count"] = max(
            metrics["maximum_post_wake_active_structure_count"],
            float(len(adapted)),
        )
        metrics["minimum_post_wake_retained_structure_count"] = min(
            metrics["minimum_post_wake_retained_structure_count"],
            float(len(retained_rows)),
        )
        metrics["maximum_post_wake_retained_structure_count"] = max(
            metrics["maximum_post_wake_retained_structure_count"],
            float(len(retained_rows)),
        )

        baseline_correct, full_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, full
        )
        _, static_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, static_active
        )
        _, adapted_correct, _ = pressure.model_correct_counts(
            prior, evaluation, baseline, adapted
        )
        full_increment = full_correct - baseline_correct
        if full_increment <= 0:
            metrics["invalid_wake_rows"] += 1.0
            adapted_fraction = 0.0
            static_fraction = 0.0
        else:
            adapted_fraction = (adapted_correct - baseline_correct) / full_increment
            static_fraction = (static_correct - baseline_correct) / full_increment
        metrics["minimum_retained_incremental_correct_fraction"] = min(
            metrics["minimum_retained_incremental_correct_fraction"],
            adapted_fraction,
        )
        metrics["minimum_improvement_over_static_fraction"] = min(
            metrics["minimum_improvement_over_static_fraction"],
            adapted_fraction - static_fraction,
        )

        _, coverage, gain, event_reduction = pressure.pressured_eval(
            prior, evaluation, baseline, adapted
        )
        metrics["minimum_eval_covered_position_fraction"] = min(
            metrics["minimum_eval_covered_position_fraction"],
            coverage,
        )
        metrics["minimum_eval_covered_accuracy_gain"] = min(
            metrics["minimum_eval_covered_accuracy_gain"],
            gain,
        )
        metrics["minimum_effective_event_reduction_fraction"] = min(
            metrics["minimum_effective_event_reduction_fraction"],
            event_reduction,
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
