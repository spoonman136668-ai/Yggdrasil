"""Frozen source for EXP-DGR-EXTERNAL-MULTIROW-LOW-SIGNAL-COMPETITION-032."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-MULTIROW-LOW-SIGNAL-COMPETITION-032"
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
TARGET_PAIRS = (("A", "B"), ("A", "C"), ("B", "C"))


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
        "target_pair_count": float(len(TARGET_PAIRS)),
        "competition_case_count": 0.0,
        "target_reactivation_evaluation_count": 0.0,
        "positive_target_reactivation_evaluation_count": 0.0,
        "minimum_target_preserved_incremental_correct_count": float("inf"),
        "minimum_non_target_preserved_to_unprotected_fraction": float("inf"),
        "minimum_unique_requested_protected_row_count": float("inf"),
        "maximum_unique_requested_protected_row_count": 0.0,
        "preserved_state_structure_count_min": 16.0,
        "preserved_state_structure_count_max": 0.0,
        "active_structure_count_min": 16.0,
        "active_structure_count_max": 0.0,
        "retained_structure_count_min": 16.0,
        "retained_structure_count_max": 0.0,
        "target_interference_leakage_count": 0.0,
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
    maturity_cue = {}
    for name in ("A", "B", "C"):
        cue, _ = full_demands[name]
        found = None
        found_cue = None
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
                found_cue = partial
                break
        if found is None:
            metrics["maturity_criterion_violation_count"] += 1.0
            found = PACKET_COUNT
            found_cue = cue
        maturity_packet[name] = found
        maturity_cue[name] = found_cue

    def admission_order(schedule):
        admitted = []
        seen = set()
        for packet_index in range(1, PACKET_COUNT + 1):
            for name in schedule:
                if name not in seen and packet_index >= maturity_packet[name]:
                    seen.add(name)
                    admitted.append(name)
        return admitted

    def build_state(current_demands, ordered_names):
        independent_rows = {}
        for name in ordered_names:
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
            base_train + [current_demands[name][0] for name in ordered_names]
        )
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        pooled_cells, radius_violations = learner.develop(shared_stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)
        minimax_cells, selected_count, _, _ = prior016.build_matched_minimax_cells(
            learner, error_guided, baseline, shared_stats, pooled_cells,
            independent_rows, ordered_names, current_demands, prior015,
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
        return active, wake.active_map(active), scores

    def score(evaluation, active_map):
        baseline_correct, _, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, {}
        )
        _, active_correct, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, active_map
        )
        return active_correct - baseline_correct

    diagnostics = []

    for schedule_index, schedule in enumerate(SCHEDULES):
        all_names = admission_order(schedule)
        if len(all_names) != 3:
            metrics["maturity_criterion_violation_count"] += 1.0
            continue
        all_rows, all_map = build_state(full_demands, all_names)
        all_keys = {row["key"] for row in all_rows}

        for target_pair in TARGET_PAIRS:
            metrics["competition_case_count"] += 1.0
            protected_by_key = {}
            protected_for_target = {}

            for target in target_pair:
                cue = maturity_cue[target]
                scores = error_guided.contributions(
                    learner, cue, baseline, all_keys, all_map
                )
                candidates = sorted(
                    [row for row in all_rows if scores[row["key"]] > 0],
                    key=lambda row: (
                        -scores[row["key"]],
                        -row["utility"],
                        row["key"],
                    ),
                )
                if not candidates:
                    metrics["invalid_evaluation_rows"] += 1.0
                    continue
                protected = candidates[0]
                protected_for_target[target] = protected
                protected_by_key[protected["key"]] = protected

            if len(protected_for_target) != 2:
                metrics["invalid_evaluation_rows"] += 1.0
                continue

            unique_count = len(protected_by_key)
            metrics["minimum_unique_requested_protected_row_count"] = min(
                metrics["minimum_unique_requested_protected_row_count"],
                float(unique_count),
            )
            metrics["maximum_unique_requested_protected_row_count"] = max(
                metrics["maximum_unique_requested_protected_row_count"],
                float(unique_count),
            )

            non_targets = [name for name in ("A", "B", "C") if name not in target_pair]
            if len(non_targets) != 1 or non_targets[0] in target_pair:
                metrics["target_interference_leakage_count"] += 1.0
                metrics["invalid_evaluation_rows"] += 1.0
                continue
            non_target = non_targets[0]
            interference_demands = {non_target: full_demands[non_target]}
            interference_rows, interference_map = build_state(
                interference_demands, [non_target]
            )
            interference_keys = {row["key"] for row in interference_rows}
            requested_keys = set(protected_by_key)
            absent = [
                (key, protected_by_key[key])
                for key in sorted(requested_keys)
                if key not in interference_keys
            ]

            non_target_cue, non_target_eval = full_demands[non_target]
            non_target_scores = error_guided.contributions(
                learner,
                non_target_cue,
                baseline,
                interference_keys,
                interference_map,
            )
            eviction_candidates = sorted(
                [
                    row
                    for row in interference_rows
                    if row["key"] not in requested_keys
                ],
                key=lambda row: (
                    non_target_scores[row["key"]],
                    row["utility"],
                    tuple(-value for value in row["key"]),
                ),
            )
            if len(eviction_candidates) < len(absent):
                metrics["invalid_evaluation_rows"] += 1.0
                continue

            evictions = eviction_candidates[: len(absent)]
            evicted_keys = {row["key"] for row in evictions}
            preserved_rows = [
                row for row in interference_rows if row["key"] not in evicted_keys
            ] + [row for _, row in absent]
            preserved_map = dict(interference_map)
            for key in evicted_keys:
                preserved_map.pop(key, None)
            for key, row in absent:
                preserved_map[key] = all_map[key]

            metrics["preserved_state_structure_count_min"] = min(
                metrics["preserved_state_structure_count_min"],
                float(len(preserved_rows)),
            )
            metrics["preserved_state_structure_count_max"] = max(
                metrics["preserved_state_structure_count_max"],
                float(len(preserved_rows)),
            )
            if (
                len(preserved_rows) != 16
                or len({row["key"] for row in preserved_rows}) != 16
                or len(preserved_map) != 16
            ):
                metrics["invalid_evaluation_rows"] += 1.0

            target_results = {}
            for target in target_pair:
                metrics["target_reactivation_evaluation_count"] += 1.0
                cue = maturity_cue[target]
                _, evaluation = full_demands[target]
                _, target_active_map, _ = select_active(
                    preserved_rows, preserved_map, cue
                )
                increment = score(evaluation, target_active_map)
                if increment > 0:
                    metrics["positive_target_reactivation_evaluation_count"] += 1.0
                metrics["minimum_target_preserved_incremental_correct_count"] = min(
                    metrics["minimum_target_preserved_incremental_correct_count"],
                    float(increment),
                )
                target_results[target] = {
                    "protected_key": list(protected_for_target[target]["key"]),
                    "preserved_incremental_correct": increment,
                }

            _, unprotected_active_map, _ = select_active(
                interference_rows, interference_map, non_target_cue
            )
            _, preserved_active_map, _ = select_active(
                preserved_rows, preserved_map, non_target_cue
            )
            unprotected_increment = score(non_target_eval, unprotected_active_map)
            preserved_increment = score(non_target_eval, preserved_active_map)
            if unprotected_increment > 0:
                ratio = preserved_increment / unprotected_increment
                metrics["minimum_non_target_preserved_to_unprotected_fraction"] = min(
                    metrics["minimum_non_target_preserved_to_unprotected_fraction"],
                    ratio,
                )
            else:
                ratio = 0.0
                metrics["invalid_evaluation_rows"] += 1.0

            diagnostics.append({
                "schedule": "-".join(schedule),
                "schedule_index": schedule_index,
                "target_pair": list(target_pair),
                "non_target": non_target,
                "unique_requested_protected_row_count": unique_count,
                "evicted_keys": [list(row["key"]) for row in evictions],
                "target_results": target_results,
                "non_target_unprotected_incremental_correct": unprotected_increment,
                "non_target_preserved_incremental_correct": preserved_increment,
                "non_target_preserved_to_unprotected_fraction": ratio,
            })

    if metrics["minimum_target_preserved_incremental_correct_count"] == float("inf"):
        metrics["minimum_target_preserved_incremental_correct_count"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["minimum_non_target_preserved_to_unprotected_fraction"] == float("inf"):
        metrics["minimum_non_target_preserved_to_unprotected_fraction"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["minimum_unique_requested_protected_row_count"] == float("inf"):
        metrics["minimum_unique_requested_protected_row_count"] = 0.0
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["competition_case_count"] == 0:
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
