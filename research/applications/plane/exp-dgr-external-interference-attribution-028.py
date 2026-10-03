"""Sealed source for EXP-DGR-EXTERNAL-INTERFERENCE-ATTRIBUTION-028."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-INTERFERENCE-ATTRIBUTION-028"
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
        "c_case_count": 0.0,
        "c_failure_reproduction_count": 0.0,
        "c_absent_critical_row_case_count": 0.0,
        "full_cue_positive_case_count": 0.0,
        "single_row_restore_case_count": 0.0,
        "single_row_restore_positive_case_count": 0.0,
        "minimum_single_row_restore_incremental_correct_count": float("inf"),
        "restored_state_structure_count_min": 16.0,
        "restored_state_structure_count_max": 0.0,
        "active_structure_count_min": 16.0,
        "active_structure_count_max": 0.0,
        "retained_structure_count_min": 16.0,
        "retained_structure_count_max": 0.0,
        "heldout_selection_use_count": 0.0,
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
    for name in ("A", "B", "C"):
        cue, _ = full_demands[name]
        found = None
        for packet_index in range(1, PACKET_COUNT + 1):
            partial = cue[:fine_prefix_length(len(cue), packet_index)]
            stats, overflow, invalid = learner.candidate_stats(base_train + [partial])
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            cells, radius_violations = learner.develop(stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            full = learner.specialized_map(cells)
            rows = wake.known_rows(pressure, learner, cells, stats)
            if len(full) != 16 or len(rows) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            keys = {row["key"] for row in rows}
            scores = error_guided.contributions(learner, partial, baseline, keys, full)
            if sum(1 for score in scores.values() if score > 0) >= 1:
                found = packet_index
                break
        if found is None:
            metrics["maturity_criterion_violation_count"] += 1.0
            found = PACKET_COUNT
        maturity_packet[name] = found

    def admission_order(schedule):
        admitted = []
        seen = set()
        for packet_index in range(1, PACKET_COUNT + 1):
            for name in schedule:
                if name not in seen and packet_index >= maturity_packet[name]:
                    seen.add(name)
                    admitted.append(name)
        return admitted

    def build_state(names):
        current_demands = {name: full_demands[name] for name in names}
        independent_rows = {}
        for name in names:
            cue, _ = current_demands[name]
            stats, overflow, invalid = learner.candidate_stats(base_train + [cue])
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            cells, radius_violations = learner.develop(stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            full = learner.specialized_map(cells)
            rows = wake.known_rows(pressure, learner, cells, stats)
            if len(full) != 16 or len(rows) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            independent_rows[name] = rows

        shared_stats, overflow, invalid = learner.candidate_stats(
            base_train + [current_demands[name][0] for name in names]
        )
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        pooled_cells, radius_violations = learner.develop(shared_stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)
        minimax_cells, selected_count, _, _ = prior016.build_matched_minimax_cells(
            learner, error_guided, baseline, shared_stats, pooled_cells,
            independent_rows, names, current_demands, prior015,
        )
        if selected_count != 16:
            metrics["matched_assignment_failure_count"] += 1.0
        full_map = learner.specialized_map(minimax_cells)
        full_rows = wake.known_rows(pressure, learner, minimax_cells, shared_stats)
        if len(full_map) != 16 or len(full_rows) != 16:
            metrics["matched_assignment_failure_count"] += 1.0
            metrics["invalid_evaluation_rows"] += 1.0
        return full_rows, full_map

    def select_active(full_rows, full_map, cue):
        original_records = sorted(prior016.record(row) for row in full_rows)
        keys = {row["key"] for row in full_rows}
        scores = error_guided.contributions(learner, cue, baseline, keys, full_map)
        active_rows = sorted(
            full_rows,
            key=lambda row: (-scores[row["key"]], -row["utility"], row["key"]),
        )[:ACTIVE_CEILING]
        active_keys = {row["key"] for row in active_rows}
        retained_rows = [row for row in full_rows if row["key"] not in active_keys]
        metrics["active_structure_count_min"] = min(metrics["active_structure_count_min"], float(len(active_rows)))
        metrics["active_structure_count_max"] = max(metrics["active_structure_count_max"], float(len(active_rows)))
        metrics["retained_structure_count_min"] = min(metrics["retained_structure_count_min"], float(len(retained_rows)))
        metrics["retained_structure_count_max"] = max(metrics["retained_structure_count_max"], float(len(retained_rows)))
        return active_rows, wake.active_map(active_rows), scores

    def score(evaluation, active_map):
        baseline_correct, _, _ = pressure.model_correct_counts(learner, evaluation, baseline, {})
        _, active_correct, _ = pressure.model_correct_counts(learner, evaluation, baseline, active_map)
        return active_correct - baseline_correct

    diagnostics = []
    c_full_cue, c_eval = full_demands["C"]
    c_maturity_cue = c_full_cue[:fine_prefix_length(len(c_full_cue), maturity_packet["C"])]

    for schedule_index, schedule in enumerate(SCHEDULES):
        all_names = admission_order(schedule)
        if len(all_names) != 3:
            metrics["maturity_criterion_violation_count"] += 1.0
            continue

        all_rows, all_map = build_state(all_names)
        non_targets = [name for name in schedule if name != "C"]
        interference_rows, interference_map = build_state(non_targets)
        metrics["c_case_count"] += 1.0

        base_active, base_active_map, _ = select_active(interference_rows, interference_map, c_maturity_cue)
        base_increment = score(c_eval, base_active_map)
        if base_increment <= 0:
            metrics["c_failure_reproduction_count"] += 1.0

        full_active, full_active_map, _ = select_active(interference_rows, interference_map, c_full_cue)
        full_increment = score(c_eval, full_active_map)
        if full_increment > 0:
            metrics["full_cue_positive_case_count"] += 1.0

        all_keys = {row["key"] for row in all_rows}
        interference_keys = {row["key"] for row in interference_rows}
        all_scores = error_guided.contributions(
            learner, c_maturity_cue, baseline, all_keys, all_map
        )
        critical_absent = [
            row for row in all_rows
            if all_scores[row["key"]] > 0 and row["key"] not in interference_keys
        ]
        critical_absent = sorted(
            critical_absent,
            key=lambda row: (-all_scores[row["key"]], -row["utility"], row["key"]),
        )
        restored_increment = 0
        critical_key = None
        replaced_key = None

        if critical_absent:
            metrics["c_absent_critical_row_case_count"] += 1.0
            critical = critical_absent[0]
            critical_key = critical["key"]
            interference_scores = error_guided.contributions(
                learner, c_maturity_cue, baseline, interference_keys, interference_map
            )
            replacement = sorted(
                interference_rows,
                key=lambda row: (
                    interference_scores[row["key"]],
                    row["utility"],
                    tuple(-value for value in row["key"]),
                ),
            )[0]
            replaced_key = replacement["key"]
            restored_rows = [row for row in interference_rows if row["key"] != replaced_key] + [critical]
            restored_map = dict(interference_map)
            restored_map.pop(replaced_key, None)
            restored_map[critical_key] = all_map[critical_key]
            metrics["single_row_restore_case_count"] += 1.0
            metrics["restored_state_structure_count_min"] = min(
                metrics["restored_state_structure_count_min"], float(len(restored_rows))
            )
            metrics["restored_state_structure_count_max"] = max(
                metrics["restored_state_structure_count_max"], float(len(restored_rows))
            )
            if len(restored_rows) != 16 or len({row["key"] for row in restored_rows}) != 16 or len(restored_map) != 16:
                metrics["invalid_evaluation_rows"] += 1.0
            _, restored_active_map, _ = select_active(restored_rows, restored_map, c_maturity_cue)
            restored_increment = score(c_eval, restored_active_map)
            if restored_increment > 0:
                metrics["single_row_restore_positive_case_count"] += 1.0
            metrics["minimum_single_row_restore_incremental_correct_count"] = min(
                metrics["minimum_single_row_restore_incremental_correct_count"],
                float(restored_increment),
            )

        diagnostics.append({
            "schedule": "-".join(schedule),
            "schedule_index": schedule_index,
            "maturity_packet_C": maturity_packet["C"],
            "base_maturity_cue_incremental_correct": base_increment,
            "full_cue_incremental_correct": full_increment,
            "absent_positive_critical_row_count": len(critical_absent),
            "restored_critical_key": list(critical_key) if critical_key is not None else None,
            "replaced_interference_key": list(replaced_key) if replaced_key is not None else None,
            "single_row_restore_incremental_correct": restored_increment,
            "base_active_keys": sorted(row["key"] for row in base_active),
            "full_cue_active_keys": sorted(row["key"] for row in full_active),
        })

    if metrics["minimum_single_row_restore_incremental_correct_count"] == float("inf"):
        metrics["minimum_single_row_restore_incremental_correct_count"] = 0.0
    if metrics["single_row_restore_case_count"] == 0:
        metrics["restored_state_structure_count_min"] = 0.0
    if metrics["c_case_count"] == 0:
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
