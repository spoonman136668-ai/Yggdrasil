"""Sealed source for EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-REACTIVATION-026."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-REACTIVATION-026"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
PACKET_COUNT = 12
SCHEDULES = (
    ("A", "B", "C"),
    ("A", "C", "B"),
    ("B", "A", "C"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("C", "B", "A"),
)


def fine_prefix_length(length, packet_index):
    if packet_index >= PACKET_COUNT:
        return length
    candidate = max(1, (length * packet_index) // PACKET_COUNT)
    return min(candidate, length - 1)


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_external_020", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root):
    prior020 = load_prior_experiment()
    prior017 = prior020.load_prior_experiment()
    prior016 = prior017.load_prior_experiment()
    prior015 = prior016.load_prior_experiment()
    prior014 = prior015.load_prior_experiment()
    prior013 = prior014.load_prior_experiment()
    adaptation = prior013.load_prior_experiment()
    error_guided = adaptation.load_prior_experiment()
    wake = error_guided.load_wake()
    pressure = wake.load_pressure()
    learner = pressure.load_prior()

    metrics = {
        "source_identity_mismatch_count": 0.0,
        "source_count": 0.0,
        "total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "schedule_count": float(len(SCHEDULES)),
        "reactivation_case_count": 0.0,
        "positive_reactivation_case_count": 0.0,
        "minimum_reactivation_to_final_active_fraction": float("inf"),
        "minimum_reactivation_incremental_correct_count": float("inf"),
        "reactivation_active_structure_count_min": 16.0,
        "reactivation_active_structure_count_max": 0.0,
        "reactivation_retained_structure_count_min": 16.0,
        "reactivation_retained_structure_count_max": 0.0,
        "reactivation_state_mutation_count": 0.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "matched_assignment_failure_count": 0.0,
        "maturity_criterion_violation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "external_model_call_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

    full_demands = prior017.load_external(root, metrics)

    base_train = []
    for path, expected in learner.TRAIN_FILES:
        data, ok = learner.load_checked(path, expected)
        metrics["base_training_identity_mismatch_count"] += float(not ok)
        base_train.append(data)
    baseline = learner.baseline_train(base_train)

    maturity_packet = {}
    maturity_positive_rows = {}
    for name in ("A", "B", "C"):
        full_cue, _ = full_demands[name]
        found = None
        found_rows = None
        for packet_index in range(1, PACKET_COUNT + 1):
            cue = full_cue[:fine_prefix_length(len(full_cue), packet_index)]
            stats, overflow, invalid = learner.candidate_stats(base_train + [cue])
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            cells, radius_violations = learner.develop(stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            full = learner.specialized_map(cells)
            rows = wake.known_rows(pressure, learner, cells, stats)
            if len(full) != 16 or len(rows) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            keys = {row["key"] for row in rows}
            scores = error_guided.contributions(learner, cue, baseline, keys, full)
            positives = sum(1 for score in scores.values() if score > 0)
            if positives >= 1:
                found = packet_index
                found_rows = positives
                break
        if found is None:
            metrics["maturity_criterion_violation_count"] += 1.0
            maturity_packet[name] = PACKET_COUNT
            maturity_positive_rows[name] = 0
        else:
            maturity_packet[name] = found
            maturity_positive_rows[name] = found_rows

    diagnostics = []

    def select_active(full_rows, full_map, cue, original_records):
        keys = {row["key"] for row in full_rows}
        cue_scores = error_guided.contributions(learner, cue, baseline, keys, full_map)
        active_rows = sorted(
            full_rows,
            key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]),
        )[:ACTIVE_CEILING]
        active_keys = {row["key"] for row in active_rows}
        retained_rows = [row for row in full_rows if row["key"] not in active_keys]
        retained = wake.encode_retained(retained_rows)
        metrics["retained_record_integrity_mismatch_count"] += float(
            wake.verify_records(retained, retained_rows)
        )
        metrics["state_partition_mismatch_count"] += float(
            prior016.partition_mismatches(active_rows, retained_rows, original_records)
        )
        metrics["reactivation_active_structure_count_min"] = min(
            metrics["reactivation_active_structure_count_min"], float(len(active_rows))
        )
        metrics["reactivation_active_structure_count_max"] = max(
            metrics["reactivation_active_structure_count_max"], float(len(active_rows))
        )
        metrics["reactivation_retained_structure_count_min"] = min(
            metrics["reactivation_retained_structure_count_min"], float(len(retained_rows))
        )
        metrics["reactivation_retained_structure_count_max"] = max(
            metrics["reactivation_retained_structure_count_max"], float(len(retained_rows))
        )
        return active_rows, retained_rows, wake.active_map(active_rows)

    for schedule_index, schedule in enumerate(SCHEDULES):
        admitted = []
        admitted_set = set()
        for packet_index in range(1, PACKET_COUNT + 1):
            for name in schedule:
                if name not in admitted_set and packet_index >= maturity_packet[name]:
                    admitted_set.add(name)
                    admitted.append(name)

        if len(admitted) != 3:
            metrics["maturity_criterion_violation_count"] += 1.0
            continue

        current_demands = {name: full_demands[name] for name in admitted}
        independent_full = {}
        independent_rows = {}
        for name in admitted:
            cue, _ = current_demands[name]
            stats, overflow, invalid = learner.candidate_stats(base_train + [cue])
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            cells, radius_violations = learner.develop(stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            full = learner.specialized_map(cells)
            rows = wake.known_rows(pressure, learner, cells, stats)
            if len(full) != 16 or len(rows) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            independent_full[name] = full
            independent_rows[name] = rows

        shared_stats, overflow, invalid = learner.candidate_stats(
            base_train + [current_demands[name][0] for name in admitted]
        )
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        pooled_cells, radius_violations = learner.develop(shared_stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)

        minimax_cells, selected_count, _, _ = prior016.build_matched_minimax_cells(
            learner,
            error_guided,
            baseline,
            shared_stats,
            pooled_cells,
            independent_rows,
            admitted,
            current_demands,
            prior015,
        )
        if selected_count != 16:
            metrics["matched_assignment_failure_count"] += 1.0

        full_map = learner.specialized_map(minimax_cells)
        full_rows = wake.known_rows(pressure, learner, minimax_cells, shared_stats)
        if len(full_map) != 16 or len(full_rows) != 16:
            metrics["matched_assignment_failure_count"] += 1.0
            metrics["invalid_evaluation_rows"] += 1.0
            continue
        original_records = sorted(prior016.record(row) for row in full_rows)

        final_increment = {}
        final_active_keys = {}
        for name in admitted:
            cue, evaluation = current_demands[name]
            active_rows, _, active_map = select_active(full_rows, full_map, cue, original_records)
            final_active_keys[name] = tuple(sorted(row["key"] for row in active_rows))
            baseline_correct, _, _ = pressure.model_correct_counts(
                learner, evaluation, baseline, {}
            )
            _, active_correct, _ = pressure.model_correct_counts(
                learner, evaluation, baseline, active_map
            )
            final_increment[name] = active_correct - baseline_correct
            if final_increment[name] <= 0:
                metrics["invalid_evaluation_rows"] += 1.0

        frozen_records = tuple(original_records)
        for target in ("A", "B", "C"):
            displacement = []
            for other in schedule:
                if other == target:
                    continue
                cue, _ = full_demands[other]
                maturity_cue = cue[:fine_prefix_length(len(cue), maturity_packet[other])]
                active_rows, _, _ = select_active(
                    full_rows, full_map, maturity_cue, original_records
                )
                displacement.append(tuple(sorted(row["key"] for row in active_rows)))

            target_cue, target_eval = full_demands[target]
            reactivation_cue = target_cue[
                :fine_prefix_length(len(target_cue), maturity_packet[target])
            ]
            active_rows, _, active_map = select_active(
                full_rows, full_map, reactivation_cue, original_records
            )
            if tuple(original_records) != frozen_records:
                metrics["reactivation_state_mutation_count"] += 1.0

            baseline_correct, _, _ = pressure.model_correct_counts(
                learner, target_eval, baseline, {}
            )
            _, reactivated_correct, _ = pressure.model_correct_counts(
                learner, target_eval, baseline, active_map
            )
            increment = reactivated_correct - baseline_correct
            reference = final_increment[target]
            metrics["reactivation_case_count"] += 1.0
            if increment > 0:
                metrics["positive_reactivation_case_count"] += 1.0
            metrics["minimum_reactivation_incremental_correct_count"] = min(
                metrics["minimum_reactivation_incremental_correct_count"],
                float(increment),
            )
            if reference > 0:
                ratio = increment / reference
                metrics["minimum_reactivation_to_final_active_fraction"] = min(
                    metrics["minimum_reactivation_to_final_active_fraction"],
                    ratio,
                )
            else:
                metrics["invalid_evaluation_rows"] += 1.0
                ratio = 0.0

            diagnostics.append({
                "schedule": "-".join(schedule),
                "schedule_index": schedule_index,
                "target": target,
                "maturity_packet": maturity_packet[target],
                "maturity_positive_rows": maturity_positive_rows[target],
                "final_active_incremental_correct": reference,
                "reactivated_incremental_correct": increment,
                "reactivation_to_final_active_fraction": ratio,
                "final_active_keys": list(final_active_keys[target]),
                "displacement_active_keys": [list(x) for x in displacement],
                "reactivated_active_keys": sorted(row["key"] for row in active_rows),
            })

    if metrics["reactivation_case_count"] == 0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["minimum_reactivation_to_final_active_fraction"] == float("inf"):
        metrics["minimum_reactivation_to_final_active_fraction"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["minimum_reactivation_incremental_correct_count"] == float("inf"):
        metrics["minimum_reactivation_incremental_correct_count"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0

    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "maturity_packet": maturity_packet,
        "diagnostics": diagnostics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(args.root), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
