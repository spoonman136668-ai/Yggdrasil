"""Sealed source for EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-ORDER-STRESS-024."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-ORDER-STRESS-024"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
SCHEDULES = (("A", "C", "B"), ("B", "A", "C"), ("B", "C", "A"), ("C", "A", "B"))
PACKET_COUNT = 6


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
        "packet_event_count": 0.0,
        "admitted_domain_count": 0.0,
        "preadmission_evaluation_count": 0.0,
        "maturity_criterion_violation_count": 0.0,
        "minimum_positive_contribution_rows_at_admission": float("inf"),
        "buffered_packet_event_count": 0.0,
        "valid_pipeline_state_count": 0.0,
        "postadmission_evaluation_count": 0.0,
        "matched_assignment_failure_count": 0.0,
        "minimum_selected_motif_count": 16.0,
        "maximum_selected_motif_count": 0.0,
        "minimum_active_structure_count": 16.0,
        "maximum_active_structure_count": 0.0,
        "minimum_retained_structure_count": 16.0,
        "maximum_retained_structure_count": 0.0,
        "positive_then_nonpositive_transition_count": 0.0,
        "final_nonpositive_domain_count": 0.0,
        "minimum_active_to_independent_fraction_when_independent_positive": float("inf"),
        "minimum_active_incremental_correct_count_after_admission": float("inf"),
        "independent_positive_evaluation_count": 0.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
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

    diagnostics = []
    maturity_stage = {}

    for schedule_index, schedule in enumerate(SCHEDULES):
        delivered = {name: 0 for name in ("A", "B", "C")}
        admitted = []
        admitted_set = set()
        ever_positive = {name: False for name in ("A", "B", "C")}
        stage_index = 0

        for packet_index in range(1, PACKET_COUNT + 1):
            for admitted_name in schedule:
                stage_index += 1
                metrics["packet_event_count"] += 1.0
                delivered[admitted_name] = packet_index

                full_cue, _ = full_demands[admitted_name]
                plen = fine_prefix_length(len(full_cue), packet_index)
                cue = full_cue[:plen]

                independent_stats, overflow, invalid = learner.candidate_stats(base_train + [cue])
                metrics["invalid_evaluation_rows"] += float(overflow + invalid)
                independent_cells, radius_violations = learner.develop(independent_stats)
                metrics["invalid_evaluation_rows"] += float(radius_violations)
                independent_full_updated = learner.specialized_map(independent_cells)
                independent_rows_updated = wake.known_rows(
                    pressure, learner, independent_cells, independent_stats
                )
                if len(independent_full_updated) != 16 or len(independent_rows_updated) != 16:
                    metrics["invalid_evaluation_rows"] += 1.0
                independent_keys = {row["key"] for row in independent_rows_updated}
                contribution_scores = error_guided.contributions(
                    learner, cue, baseline, independent_keys, independent_full_updated
                )
                positive_rows = sum(1 for score in contribution_scores.values() if score > 0)

                newly_admitted = False
                if admitted_name not in admitted_set:
                    if positive_rows >= 1:
                        admitted_set.add(admitted_name)
                        admitted.append(admitted_name)
                        newly_admitted = True
                        metrics["admitted_domain_count"] += 1.0
                        metrics["minimum_positive_contribution_rows_at_admission"] = min(
                            metrics["minimum_positive_contribution_rows_at_admission"],
                            float(positive_rows),
                        )
                        if positive_rows < 1:
                            metrics["maturity_criterion_violation_count"] += 1.0
                        maturity_stage[f"{schedule_index}:{admitted_name}"] = stage_index
                    else:
                        metrics["buffered_packet_event_count"] += 1.0

                diagnostics.append({
                    "kind": "maturity",
                    "schedule": "-".join(schedule),
                    "stage": stage_index,
                    "delivered_packet": f"{admitted_name}{packet_index}",
                    "domain": admitted_name,
                    "available_cue_bytes": len(cue),
                    "positive_contribution_row_count": positive_rows,
                    "admitted_after_event": admitted_name in admitted_set,
                    "newly_admitted": newly_admitted,
                })

                if admitted_name not in admitted_set:
                    continue

                current_demands = {}
                independent_full = {}
                independent_rows = {}
                for name in admitted:
                    source_cue, heldout = full_demands[name]
                    current_len = fine_prefix_length(len(source_cue), delivered[name])
                    current_cue = source_cue[:current_len]
                    current_demands[name] = (current_cue, heldout)

                    stats, overflow, invalid = learner.candidate_stats(base_train + [current_cue])
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
                metrics["minimum_selected_motif_count"] = min(
                    metrics["minimum_selected_motif_count"], float(selected_count)
                )
                metrics["maximum_selected_motif_count"] = max(
                    metrics["maximum_selected_motif_count"], float(selected_count)
                )

                full_map = learner.specialized_map(minimax_cells)
                full_rows = wake.known_rows(pressure, learner, minimax_cells, shared_stats)
                if len(full_map) != 16 or len(full_rows) != 16:
                    metrics["matched_assignment_failure_count"] += 1.0
                    metrics["invalid_evaluation_rows"] += 1.0
                else:
                    metrics["valid_pipeline_state_count"] += 1.0
                original_records = sorted(prior016.record(row) for row in full_rows)

                is_final_event = all(value == PACKET_COUNT for value in delivered.values())
                for name in admitted:
                    current_cue, evaluation = current_demands[name]
                    keys = {row["key"] for row in full_rows}
                    cue_scores = error_guided.contributions(
                        learner, current_cue, baseline, keys, full_map
                    )
                    active_rows = sorted(
                        full_rows,
                        key=lambda row: (
                            -cue_scores[row["key"]],
                            -row["utility"],
                            row["key"],
                        ),
                    )[:ACTIVE_CEILING]
                    active_keys = {row["key"] for row in active_rows}
                    retained_rows = [
                        row for row in full_rows if row["key"] not in active_keys
                    ]
                    active_map = wake.active_map(active_rows)
                    retained = wake.encode_retained(retained_rows)

                    metrics["retained_record_integrity_mismatch_count"] += float(
                        wake.verify_records(retained, retained_rows)
                    )
                    metrics["state_partition_mismatch_count"] += float(
                        prior016.partition_mismatches(
                            active_rows, retained_rows, original_records
                        )
                    )
                    metrics["minimum_active_structure_count"] = min(
                        metrics["minimum_active_structure_count"], float(len(active_rows))
                    )
                    metrics["maximum_active_structure_count"] = max(
                        metrics["maximum_active_structure_count"], float(len(active_rows))
                    )
                    metrics["minimum_retained_structure_count"] = min(
                        metrics["minimum_retained_structure_count"], float(len(retained_rows))
                    )
                    metrics["maximum_retained_structure_count"] = max(
                        metrics["maximum_retained_structure_count"], float(len(retained_rows))
                    )

                    baseline_correct, _, _ = pressure.model_correct_counts(
                        learner, evaluation, baseline, {}
                    )
                    _, independent_correct, _ = pressure.model_correct_counts(
                        learner, evaluation, baseline, independent_full[name]
                    )
                    _, active_correct, _ = pressure.model_correct_counts(
                        learner, evaluation, baseline, active_map
                    )
                    independent_increment = independent_correct - baseline_correct
                    active_increment = active_correct - baseline_correct
                    metrics["minimum_active_incremental_correct_count_after_admission"] = min(
                        metrics["minimum_active_incremental_correct_count_after_admission"],
                        float(active_increment),
                    )
                    if independent_increment > 0:
                        metrics["independent_positive_evaluation_count"] += 1.0
                        ratio = active_increment / independent_increment
                        metrics["minimum_active_to_independent_fraction_when_independent_positive"] = min(
                            metrics["minimum_active_to_independent_fraction_when_independent_positive"],
                            ratio,
                        )

                    if active_increment > 0:
                        ever_positive[name] = True
                    elif ever_positive[name]:
                        metrics["positive_then_nonpositive_transition_count"] += 1.0

                    if is_final_event and active_increment <= 0:
                        metrics["final_nonpositive_domain_count"] += 1.0

                    diagnostics.append({
                        "kind": "evaluation",
                        "schedule": "-".join(schedule),
                        "stage": stage_index,
                        "trigger_packet": f"{admitted_name}{packet_index}",
                        "evaluated_domain": name,
                        "available_cue_bytes": len(current_cue),
                        "baseline_correct": baseline_correct,
                        "independent_correct": independent_correct,
                        "active_correct": active_correct,
                        "independent_incremental_correct": independent_increment,
                        "active_incremental_correct": active_increment,
                    })
                    metrics["postadmission_evaluation_count"] += 1.0

    if metrics["admitted_domain_count"] == 0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["independent_positive_evaluation_count"] == 0:
        metrics["invalid_evaluation_rows"] += 1.0
        metrics["minimum_active_to_independent_fraction_when_independent_positive"] = 0.0
    if metrics["minimum_positive_contribution_rows_at_admission"] == float("inf"):
        metrics["minimum_positive_contribution_rows_at_admission"] = 0.0
    if metrics["minimum_active_incremental_correct_count_after_admission"] == float("inf"):
        metrics["minimum_active_incremental_correct_count_after_admission"] = 0.0

    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "maturity_stage": maturity_stage,
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
