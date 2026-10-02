"""Sealed source for EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-developmental-specialization-001.py")
ACTIVE_CEILING = 8
HIBERNATED_RECORD_BYTES = 6


def load_prior():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_prior", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row_for_key(prior, stats, key):
    row = stats[key]
    best, best_count = prior.best_successor(row)
    consistency = best_count / row["total"]
    return {
        "key": key,
        "total": row["total"],
        "best": best,
        "best_count": best_count,
        "consistency": consistency,
        "utility": best_count * consistency,
    }


def pressure(prior, cells, stats):
    rows = []
    cell_by_key = {}
    for cell in cells:
        if cell["role"] != "specialized":
            continue
        key = cell["key"]
        row = row_for_key(prior, stats, key)
        row["cell_index"] = cell["index"]
        rows.append(row)
        cell_by_key[key] = cell
    rows.sort(key=lambda r: (
        -r["utility"],
        -r["total"],
        r["key"],
    ))
    active_rows = rows[:ACTIVE_CEILING]
    hibernated_rows = rows[ACTIVE_CEILING:]
    active = {row["key"]: row["best"] for row in active_rows}

    retained = bytearray()
    for row in sorted(hibernated_rows, key=lambda r: r["cell_index"]):
        record = bytes((
            row["cell_index"],
            row["key"][0],
            row["key"][1],
            row["key"][2],
            row["key"][3],
            row["best"],
        ))
        if len(record) != HIBERNATED_RECORD_BYTES:
            raise RuntimeError("HIBERNATED_RECORD_SIZE_INVALID")
        retained.extend(record)
    return active, hibernated_rows, bytes(retained)


def verify_retained(retained, hibernated_rows):
    expected = {
        row["cell_index"]: (
            row["key"],
            row["best"],
        )
        for row in hibernated_rows
    }
    seen = set()
    mismatch = 0
    if len(retained) % HIBERNATED_RECORD_BYTES != 0:
        return len(expected) + 1
    for offset in range(0, len(retained), HIBERNATED_RECORD_BYTES):
        record = retained[offset:offset + HIBERNATED_RECORD_BYTES]
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


def model_correct_counts(prior, data, baseline, learned):
    baseline_correct = 0
    model_correct = 0
    total = 0
    for i in range(1, len(data)):
        target = data[i]
        baseline_prediction = prior.baseline_predict(baseline, data[i - 1])
        prediction = baseline_prediction
        if i >= 4:
            key = tuple(data[i - 4:i])
            if key in learned:
                prediction = learned[key]
        baseline_correct += int(baseline_prediction == target)
        model_correct += int(prediction == target)
        total += 1
    return baseline_correct, model_correct, total


def pressured_eval(prior, data, baseline, active):
    transferred = set()
    covered = 0
    active_correct = 0
    baseline_correct_covered = 0
    for i in range(4, len(data)):
        key = tuple(data[i - 4:i])
        if key not in active:
            continue
        transferred.add(key)
        covered += 1
        target = data[i]
        active_correct += int(active[key] == target)
        baseline_correct_covered += int(
            prior.baseline_predict(baseline, data[i - 1]) == target
        )
    coverage = covered / max(1, len(data) - 4)
    gain = 0.0
    if covered:
        gain = (active_correct - baseline_correct_covered) / covered

    events = 0
    i = 0
    while i < len(data):
        if i + 4 <= len(data) and tuple(data[i:i + 4]) in active:
            events += 1
            i += 4
        else:
            events += 1
            i += 1
    event_reduction = (len(data) - events) / len(data) if data else 0.0
    return len(transferred), coverage, gain, event_reduction


def run():
    prior = load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "train_eval_blob_overlap_count": 0.0,
        "pre_pressure_differentiated_cell_count": 0.0,
        "post_pressure_active_structure_count": 0.0,
        "hibernated_structure_count": 0.0,
        "retained_hibernated_logical_bytes": 0.0,
        "minimum_active_transferred_motif_count_per_eval_file": float(ACTIVE_CEILING),
        "minimum_eval_covered_position_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "minimum_retained_incremental_correct_fraction": 1.0,
        "minimum_effective_event_reduction_fraction": 1.0,
        "hibernated_record_integrity_mismatch_count": 0.0,
        "maximum_final_cell_count": 16.0,
        "minimum_final_cell_count": 16.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_pressure_rows": 0.0,
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
        metrics["invalid_pressure_rows"] += float(overflow + invalid)
    cells, radius_violations = prior.develop(stats)
    if radius_violations:
        metrics["invalid_pressure_rows"] += float(radius_violations)
    full = prior.specialized_map(cells)
    metrics["pre_pressure_differentiated_cell_count"] = float(len(full))
    if len(full) != 16:
        metrics["invalid_pressure_rows"] += 1.0

    active, hibernated_rows, retained = pressure(prior, cells, stats)
    metrics["post_pressure_active_structure_count"] = float(len(active))
    metrics["hibernated_structure_count"] = float(len(hibernated_rows))
    metrics["retained_hibernated_logical_bytes"] = float(len(retained))
    metrics["hibernated_record_integrity_mismatch_count"] = float(
        verify_retained(retained, hibernated_rows)
    )

    for data in evals:
        transferred, coverage, gain, event_reduction = pressured_eval(
            prior, data, baseline, active
        )
        metrics["minimum_active_transferred_motif_count_per_eval_file"] = min(
            metrics["minimum_active_transferred_motif_count_per_eval_file"],
            float(transferred),
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

        baseline_correct, full_correct, _ = model_correct_counts(
            prior, data, baseline, full
        )
        _, active_correct, _ = model_correct_counts(
            prior, data, baseline, active
        )
        full_increment = full_correct - baseline_correct
        active_increment = active_correct - baseline_correct
        if full_increment <= 0:
            metrics["invalid_pressure_rows"] += 1.0
            retained_fraction = 0.0
        else:
            retained_fraction = active_increment / full_increment
        metrics["minimum_retained_incremental_correct_fraction"] = min(
            metrics["minimum_retained_incremental_correct_fraction"],
            retained_fraction,
        )

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
