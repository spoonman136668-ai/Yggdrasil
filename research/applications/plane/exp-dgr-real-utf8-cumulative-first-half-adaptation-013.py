"""Sealed source for EXP-DGR-REAL-UTF8-CUMULATIVE-FIRST-HALF-ADAPTATION-013."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-CUMULATIVE-FIRST-HALF-ADAPTATION-013"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-cross-domain-first-half-adaptation-012.py")
DEMAND_FILES = (
    ("A", "research/applications/track-a/a02-adaptive-transform-service-organism.ice", "2770482f2bd0fcffab8b00d206c54ae81f3ae7a1", 21855),
    ("B", "research/applications/track-a/a03-fixa-dynamic-partition-remerge-alignment.ice", "ea322d9b33044d9c0442df460fc2b354b2d4830b", 11293),
    ("C", "research/applications/track-a/a03-heldout-adaptive-generalization.ice", "fdb9b8c908ed45e075fdb39ac578c0e3c79edce5", 28605),
)
ORDERS = (("A", "B", "C"), ("C", "B", "A"))
ACTIVE_CEILING = 7


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_adaptation_012", PRIOR_PATH)
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
    adaptation = load_prior_experiment()
    error_guided = adaptation.load_prior_experiment()
    wake = error_guided.load_wake()
    pressure = wake.load_pressure()
    learner = pressure.load_prior()
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "future_stage_adaptation_access_count": 0.0,
        "second_half_adaptation_access_count": 0.0,
        "valid_stage_count": 0.0,
        "valid_seen_domain_evaluation_count": 0.0,
        "minimum_shared_full_incremental_correct_count": float("inf"),
        "minimum_shared_minus_frozen_incremental_correct_count": float("inf"),
        "minimum_shared_to_independent_incremental_correct_fraction": float("inf"),
        "minimum_prior_domain_shared_incremental_correct_count": float("inf"),
        "minimum_prior_domain_shared_to_at_first_encounter_fraction": float("inf"),
        "final_order_record_mismatch_count": 0.0,
        "minimum_primary_active_structure_count": 16.0,
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": 16.0,
        "maximum_primary_retained_structure_count": 0.0,
        "minimum_primary_retained_incremental_correct_fraction": float("inf"),
        "minimum_eval_covered_accuracy_gain": float("inf"),
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }
    base_train = []
    for path, expected in learner.TRAIN_FILES:
        data, ok = learner.load_checked(path, expected)
        metrics["training_file_identity_mismatch_count"] += float(not ok)
        base_train.append(data)
    demands = {}
    for name, path, expected, expected_size in DEMAND_FILES:
        data, ok = learner.load_checked(path, expected)
        metrics["evaluation_file_identity_mismatch_count"] += float(not ok or len(data) != expected_size)
        midpoint = len(data) // 2
        demands[name] = (data[:midpoint], data[midpoint:])

    baseline = learner.baseline_train(base_train)
    frozen_stats, overflow, invalid = learner.candidate_stats(base_train)
    metrics["invalid_evaluation_rows"] += float(overflow + invalid)
    frozen_cells, radius_violations = learner.develop(frozen_stats)
    metrics["invalid_evaluation_rows"] += float(radius_violations)
    frozen_full = learner.specialized_map(frozen_cells)
    if len(frozen_full) != 16:
        metrics["invalid_evaluation_rows"] += 1.0

    independent_full = {}
    for name, _, _, _ in DEMAND_FILES:
        independent_stats, overflow, invalid = learner.candidate_stats(base_train + [demands[name][0]])
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        independent_cells, radius_violations = learner.develop(independent_stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)
        independent_full[name] = learner.specialized_map(independent_cells)
        if len(independent_full[name]) != 16:
            metrics["invalid_evaluation_rows"] += 1.0

    final_records = []
    for order in ORDERS:
        seen = []
        first_encounter_increment = {}
        for current_name in order:
            seen.append(current_name)
            shared_stats, overflow, invalid = learner.candidate_stats(base_train + [demands[name][0] for name in seen])
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            shared_cells, radius_violations = learner.develop(shared_stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            shared_full = learner.specialized_map(shared_cells)
            rows = wake.known_rows(pressure, learner, shared_cells, shared_stats)
            if len(shared_full) != 16 or len(rows) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            original_records = sorted(record(row) for row in rows)
            metrics["valid_stage_count"] += 1.0

            for name in seen:
                cue, evaluation = demands[name]
                baseline_correct, frozen_correct, _ = pressure.model_correct_counts(learner, evaluation, baseline, frozen_full)
                _, independent_correct, _ = pressure.model_correct_counts(learner, evaluation, baseline, independent_full[name])
                _, shared_correct, _ = pressure.model_correct_counts(learner, evaluation, baseline, shared_full)
                frozen_increment = frozen_correct - baseline_correct
                independent_increment = independent_correct - baseline_correct
                shared_increment = shared_correct - baseline_correct
                metrics["minimum_shared_full_incremental_correct_count"] = min(metrics["minimum_shared_full_incremental_correct_count"], float(shared_increment))
                metrics["minimum_shared_minus_frozen_incremental_correct_count"] = min(metrics["minimum_shared_minus_frozen_incremental_correct_count"], float(shared_increment - frozen_increment))
                independent_fraction = shared_increment / independent_increment if independent_increment > 0 else 0.0
                metrics["minimum_shared_to_independent_incremental_correct_fraction"] = min(metrics["minimum_shared_to_independent_incremental_correct_fraction"], independent_fraction)
                if name not in first_encounter_increment:
                    first_encounter_increment[name] = shared_increment
                else:
                    first_increment = first_encounter_increment[name]
                    prior_fraction = shared_increment / first_increment if first_increment > 0 else 0.0
                    metrics["minimum_prior_domain_shared_incremental_correct_count"] = min(metrics["minimum_prior_domain_shared_incremental_correct_count"], float(shared_increment))
                    metrics["minimum_prior_domain_shared_to_at_first_encounter_fraction"] = min(metrics["minimum_prior_domain_shared_to_at_first_encounter_fraction"], prior_fraction)

                keys = {row["key"] for row in rows}
                cue_scores = error_guided.contributions(learner, cue, baseline, keys, shared_full)
                active_rows = sorted(rows, key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]))[:ACTIVE_CEILING]
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
                if shared_increment > 0:
                    _, retained_fraction = error_guided.model_fraction(pressure, learner, evaluation, baseline, shared_full, active)
                else:
                    retained_fraction = 0.0
                metrics["minimum_primary_retained_incremental_correct_fraction"] = min(metrics["minimum_primary_retained_incremental_correct_fraction"], retained_fraction)
                _, _, gain, _ = pressure.pressured_eval(learner, evaluation, baseline, active)
                metrics["minimum_eval_covered_accuracy_gain"] = min(metrics["minimum_eval_covered_accuracy_gain"], gain)
                metrics["valid_seen_domain_evaluation_count"] += 1.0
        final_records.append(original_records)

    if final_records[0] != final_records[1]:
        metrics["final_order_record_mismatch_count"] = float(sum(a != b for a, b in zip(final_records[0], final_records[1])) + abs(len(final_records[0]) - len(final_records[1])))
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
