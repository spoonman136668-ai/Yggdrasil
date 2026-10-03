"""Sealed source for EXP-DGR-EXTERNAL-FINAL-CUE-REACTIVATION-019."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-FINAL-CUE-REACTIVATION-019"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-raw-cumulative-consolidation-017.py")
ACTIVE_CEILING = 7
ORDERS = (("A", "B", "C"), ("C", "B", "A"))


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_external_017", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root):
    prior017 = load_prior_experiment()
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
        "valid_final_state_count": 0.0,
        "reactivation_evaluation_count": 0.0,
        "matched_assignment_failure_count": 0.0,
        "minimum_selected_motif_count": 16.0,
        "maximum_selected_motif_count": 0.0,
        "minimum_active_structure_count": 16.0,
        "maximum_active_structure_count": 0.0,
        "minimum_retained_structure_count": 16.0,
        "maximum_retained_structure_count": 0.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "active_reactivation_nonpositive_window_count": 0.0,
        "minimum_active_reactivation_incremental_correct_count": float("inf"),
        "minimum_domain_order_active_aggregate_incremental_correct_count": float("inf"),
        "independent_nonpositive_window_count": 0.0,
        "full_store_nonpositive_window_count": 0.0,
        "active_reactivation_rescue_window_count": 0.0,
        "minimum_active_to_independent_fraction_when_independent_positive": float("inf"),
        "independent_positive_window_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "external_model_call_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

    demands = prior017.load_external(root, metrics)
    base_train = []
    for path, expected in learner.TRAIN_FILES:
        data, ok = learner.load_checked(path, expected)
        metrics["base_training_identity_mismatch_count"] += float(not ok)
        base_train.append(data)
    baseline = learner.baseline_train(base_train)

    independent_full = {}
    independent_rows = {}
    for name in ("A", "B", "C"):
        stats, overflow, invalid = learner.candidate_stats(base_train + [demands[name][0]])
        metrics["invalid_evaluation_rows"] += float(overflow + invalid)
        cells, radius_violations = learner.develop(stats)
        metrics["invalid_evaluation_rows"] += float(radius_violations)
        full = learner.specialized_map(cells)
        rows = wake.known_rows(pressure, learner, cells, stats)
        if len(full) != 16 or len(rows) != 16:
            metrics["invalid_evaluation_rows"] += 1.0
        independent_full[name] = full
        independent_rows[name] = rows

    diagnostic_rows = []
    for order in ORDERS:
        seen = list(order)
        shared_stats, overflow, invalid = learner.candidate_stats(
            base_train + [demands[name][0] for name in seen]
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
            seen,
            demands,
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
        original_records = sorted(prior016.record(row) for row in full_rows)
        metrics["valid_final_state_count"] += 1.0

        for name in ("A", "B", "C"):
            cue, heldout = demands[name]
            split = len(heldout) // 2
            windows = (("H1", heldout[:split]), ("H2", heldout[split:]))
            if split <= 0 or split >= len(heldout):
                metrics["invalid_evaluation_rows"] += 1.0

            keys = {row["key"] for row in full_rows}
            cue_scores = error_guided.contributions(
                learner, cue, baseline, keys, full_map
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
            retained_rows = [row for row in full_rows if row["key"] not in active_keys]
            active_map = wake.active_map(active_rows)
            retained = wake.encode_retained(retained_rows)

            metrics["retained_record_integrity_mismatch_count"] += float(
                wake.verify_records(retained, retained_rows)
            )
            metrics["state_partition_mismatch_count"] += float(
                prior016.partition_mismatches(active_rows, retained_rows, original_records)
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

            aggregate_active_increment = 0
            for window_name, evaluation in windows:
                baseline_correct, _, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, {}
                )
                _, independent_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, independent_full[name]
                )
                _, full_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, full_map
                )
                _, active_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, active_map
                )
                independent_increment = independent_correct - baseline_correct
                full_increment = full_correct - baseline_correct
                active_increment = active_correct - baseline_correct
                aggregate_active_increment += active_increment

                if independent_increment <= 0:
                    metrics["independent_nonpositive_window_count"] += 1.0
                else:
                    metrics["independent_positive_window_count"] += 1.0
                    ratio = active_increment / independent_increment
                    metrics["minimum_active_to_independent_fraction_when_independent_positive"] = min(
                        metrics["minimum_active_to_independent_fraction_when_independent_positive"],
                        ratio,
                    )
                if full_increment <= 0:
                    metrics["full_store_nonpositive_window_count"] += 1.0
                if active_increment <= 0:
                    metrics["active_reactivation_nonpositive_window_count"] += 1.0
                if full_increment <= 0 and active_increment > 0:
                    metrics["active_reactivation_rescue_window_count"] += 1.0

                metrics["minimum_active_reactivation_incremental_correct_count"] = min(
                    metrics["minimum_active_reactivation_incremental_correct_count"],
                    float(active_increment),
                )
                metrics["reactivation_evaluation_count"] += 1.0

                diagnostic_rows.append({
                    "order": "-".join(order),
                    "domain": name,
                    "window": window_name,
                    "baseline_correct": baseline_correct,
                    "independent_correct": independent_correct,
                    "full_store_correct": full_correct,
                    "active_correct": active_correct,
                    "independent_incremental_correct": independent_increment,
                    "full_store_incremental_correct": full_increment,
                    "active_incremental_correct": active_increment,
                })

            metrics["minimum_domain_order_active_aggregate_incremental_correct_count"] = min(
                metrics["minimum_domain_order_active_aggregate_incremental_correct_count"],
                float(aggregate_active_increment),
            )

    if metrics["independent_positive_window_count"] == 0:
        metrics["invalid_evaluation_rows"] += 1.0
        metrics["minimum_active_to_independent_fraction_when_independent_positive"] = 0.0

    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "diagnostics": diagnostic_rows,
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
