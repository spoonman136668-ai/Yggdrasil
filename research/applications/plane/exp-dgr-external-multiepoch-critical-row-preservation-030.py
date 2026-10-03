"""Sealed source for EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
PACKET_COUNT = 12
EPOCH_PACKETS = (3, 6, 9, 12)
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
        "epoch_count": float(len(EPOCH_PACKETS)),
        "multiepoch_case_count": 0.0,
        "c_positive_reactivation_case_count": 0.0,
        "minimum_c_preserved_incremental_correct_count": float("inf"),
        "minimum_non_target_preserved_to_unprotected_fraction": float("inf"),
        "protected_row_missing_after_preservation_count": 0.0,
        "preservation_insert_count": 0.0,
        "preserved_state_structure_count_min": 16.0,
        "preserved_state_structure_count_max": 0.0,
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

    def build_state(names, cues):
        current_demands = {
            name: (cues[name], full_demands[name][1]) for name in names
        }
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

    def select_active(rows, full_map, cue):
        keys = {row["key"] for row in rows}
        scores = error_guided.contributions(learner, cue, baseline, keys, full_map)
        active = sorted(
            rows,
            key=lambda row: (-scores[row["key"]], -row["utility"], row["key"]),
        )[:ACTIVE_CEILING]
        active_keys = {row["key"] for row in active}
        retained = [row for row in rows if row["key"] not in active_keys]
        metrics["active_structure_count_min"] = min(
            metrics["active_structure_count_min"], float(len(active))
        )
        metrics["active_structure_count_max"] = max(
            metrics["active_structure_count_max"], float(len(active))
        )
        metrics["retained_structure_count_min"] = min(
            metrics["retained_structure_count_min"], float(len(retained))
        )
        metrics["retained_structure_count_max"] = max(
            metrics["retained_structure_count_max"], float(len(retained))
        )
        return active, wake.active_map(active)

    def incremental_correct(evaluation, active_map):
        baseline_correct, _, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, {}
        )
        _, active_correct, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, active_map
        )
        return active_correct - baseline_correct

    c_full, c_eval = full_demands["C"]
    c_maturity = c_full[:fine_prefix_length(len(c_full), maturity_packet["C"])]
    diagnostics = []

    for schedule_index, schedule in enumerate(SCHEDULES):
        all_names = admission_order(schedule)
        if len(all_names) != 3:
            metrics["maturity_criterion_violation_count"] += 1.0
            continue

        full_cues = {name: full_demands[name][0] for name in all_names}
        all_rows, all_map = build_state(all_names, full_cues)
        if len(all_rows) != 16 or len(all_map) != 16:
            continue

        all_keys = {row["key"] for row in all_rows}
        c_scores = error_guided.contributions(
            learner, c_maturity, baseline, all_keys, all_map
        )
        candidates = sorted(
            [row for row in all_rows if c_scores[row["key"]] > 0],
            key=lambda row: (-c_scores[row["key"]], -row["utility"], row["key"]),
        )
        if not candidates:
            metrics["invalid_evaluation_rows"] += 1.0
            continue
        protected = candidates[0]
        protected_key = protected["key"]

        non_targets = [name for name in schedule if name != "C"]
        if len(non_targets) != 2:
            metrics["invalid_evaluation_rows"] += 1.0
            continue

        for epoch_packet in EPOCH_PACKETS:
            epoch_cues = {
                name: full_demands[name][0][
                    :fine_prefix_length(len(full_demands[name][0]), epoch_packet)
                ]
                for name in non_targets
            }
            ordinary_rows, ordinary_map = build_state(non_targets, epoch_cues)
            if len(ordinary_rows) != 16 or len(ordinary_map) != 16:
                continue
            metrics["multiepoch_case_count"] += 1.0

            ordinary_keys = {row["key"] for row in ordinary_rows}
            preserved_rows = list(ordinary_rows)
            preserved_map = dict(ordinary_map)
            evicted_key = None

            if protected_key not in ordinary_keys:
                a_scores = error_guided.contributions(
                    learner, epoch_cues["A"], baseline, ordinary_keys, ordinary_map
                )
                b_scores = error_guided.contributions(
                    learner, epoch_cues["B"], baseline, ordinary_keys, ordinary_map
                )
                summed = {
                    row["key"]: a_scores[row["key"]] + b_scores[row["key"]]
                    for row in ordinary_rows
                }
                min_sum = min(summed.values())
                evict_candidates = [
                    row for row in ordinary_rows if summed[row["key"]] == min_sum
                ]
                min_utility = min(row["utility"] for row in evict_candidates)
                evict_candidates = [
                    row for row in evict_candidates if row["utility"] == min_utility
                ]
                evicted = max(evict_candidates, key=lambda row: row["key"])
                evicted_key = evicted["key"]
                preserved_rows = [
                    row for row in ordinary_rows if row["key"] != evicted_key
                ] + [protected]
                preserved_map.pop(evicted_key, None)
                preserved_map[protected_key] = all_map[protected_key]
                metrics["preservation_insert_count"] += 1.0

            preserved_keys = {row["key"] for row in preserved_rows}
            if protected_key not in preserved_keys:
                metrics["protected_row_missing_after_preservation_count"] += 1.0
            metrics["preserved_state_structure_count_min"] = min(
                metrics["preserved_state_structure_count_min"], float(len(preserved_rows))
            )
            metrics["preserved_state_structure_count_max"] = max(
                metrics["preserved_state_structure_count_max"], float(len(preserved_rows))
            )
            if len(preserved_rows) != 16 or len(preserved_keys) != 16 or len(preserved_map) != 16:
                metrics["invalid_evaluation_rows"] += 1.0

            _, c_active_map = select_active(preserved_rows, preserved_map, c_maturity)
            c_increment = incremental_correct(c_eval, c_active_map)
            if c_increment > 0:
                metrics["c_positive_reactivation_case_count"] += 1.0
            metrics["minimum_c_preserved_incremental_correct_count"] = min(
                metrics["minimum_c_preserved_incremental_correct_count"],
                float(c_increment),
            )

            non_target_rows = []
            for name in ("A", "B"):
                cue = epoch_cues[name]
                evaluation = full_demands[name][1]
                _, ordinary_active_map = select_active(
                    ordinary_rows, ordinary_map, cue
                )
                _, preserved_active_map = select_active(
                    preserved_rows, preserved_map, cue
                )
                ordinary_increment = incremental_correct(
                    evaluation, ordinary_active_map
                )
                preserved_increment = incremental_correct(
                    evaluation, preserved_active_map
                )
                if ordinary_increment > 0:
                    ratio = preserved_increment / ordinary_increment
                    metrics["minimum_non_target_preserved_to_unprotected_fraction"] = min(
                        metrics["minimum_non_target_preserved_to_unprotected_fraction"],
                        ratio,
                    )
                else:
                    ratio = 0.0
                    metrics["invalid_evaluation_rows"] += 1.0
                non_target_rows.append({
                    "domain": name,
                    "ordinary_incremental_correct": ordinary_increment,
                    "preserved_incremental_correct": preserved_increment,
                    "preserved_to_unprotected_fraction": ratio,
                })

            diagnostics.append({
                "schedule": "-".join(schedule),
                "schedule_index": schedule_index,
                "epoch_packet": epoch_packet,
                "protected_key": list(protected_key),
                "evicted_key": list(evicted_key) if evicted_key is not None else None,
                "c_preserved_incremental_correct": c_increment,
                "non_target": non_target_rows,
            })

    if metrics["minimum_c_preserved_incremental_correct_count"] == float("inf"):
        metrics["minimum_c_preserved_incremental_correct_count"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["minimum_non_target_preserved_to_unprotected_fraction"] == float("inf"):
        metrics["minimum_non_target_preserved_to_unprotected_fraction"] = 0.0
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
