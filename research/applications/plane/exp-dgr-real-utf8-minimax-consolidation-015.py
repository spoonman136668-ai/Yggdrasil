"""Sealed source for EXP-DGR-REAL-UTF8-MINIMAX-CONSOLIDATION-015."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-MINIMAX-CONSOLIDATION-015"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-domain-balanced-consolidation-014.py")
ACTIVE_CEILING = 7
ORDERS = (("A", "B", "C"), ("C", "B", "A"))


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_balanced_014", PRIOR_PATH)
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


def pooled_successor_map(learner, shared_stats, keys):
    out = {}
    invalid = 0
    for key in keys:
        row = shared_stats.get(key)
        if row is None or row["total"] < learner.MIN_OCCURRENCE:
            invalid += 1
            continue
        best, best_count = learner.best_successor(row)
        consistency = best_count / row["total"] if row["total"] else 0.0
        if consistency < learner.MIN_CONSISTENCY:
            invalid += 1
            continue
        out[key] = best
    return out, invalid


def build_minimax_cells(learner, error_guided, baseline, shared_stats, pooled_cells, independent_rows, seen, demands):
    pooled_keys = {
        cell["key"]
        for cell in pooled_cells
        if cell["role"] == "specialized"
    }
    candidate_keys = set(pooled_keys)
    for name in seen:
        candidate_keys.update(row["key"] for row in independent_rows[name])

    candidate_full, invalid = pooled_successor_map(learner, shared_stats, candidate_keys)
    candidate_keys = set(candidate_full)
    domain_scores = {}
    for name in sorted(seen):
        cue = demands[name][0]
        domain_scores[name] = error_guided.contributions(
            learner, cue, baseline, candidate_keys, candidate_full
        )

    ranked = []
    for key in candidate_keys:
        values = [domain_scores[name][key] for name in sorted(seen)]
        ranked.append((key, min(values), sum(values)))
    ranked.sort(key=lambda item: (-item[1], -item[2], item[0]))

    cells = [
        {"index": i, "role": "generic", "key": None, "best": None, "home": None}
        for i in range(16)
    ]
    assigned = set()
    skipped_local = 0
    for key, _, _ in ranked:
        home = learner.home_cell(key)
        receiver = None
        for index in learner.local_cells(home):
            if cells[index]["role"] == "generic":
                receiver = index
                break
        if receiver is None:
            skipped_local += 1
            continue
        cells[receiver] = {
            "index": receiver,
            "role": "specialized",
            "key": key,
            "best": candidate_full[key],
            "home": home,
        }
        assigned.add(key)
        if len(assigned) == 16:
            break
    return cells, invalid, skipped_local


def run():
    prior014 = load_prior_experiment()
    prior013 = prior014.load_prior_experiment()
    adaptation = prior013.load_prior_experiment()
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
        "minimax_assignment_failure_count": 0.0,
        "minimax_ineligible_candidate_count": 0.0,
        "minimax_local_assignment_skip_count": 0.0,
        "minimum_minimax_full_incremental_correct_count": float("inf"),
        "minimum_minimax_minus_frozen_incremental_correct_count": float("inf"),
        "minimum_minimax_to_independent_incremental_correct_fraction": float("inf"),
        "minimum_prior_domain_minimax_incremental_correct_count": float("inf"),
        "minimum_prior_domain_minimax_to_at_first_encounter_fraction": float("inf"),
        "minimum_minimax_minus_pooled_incremental_correct_count": float("inf"),
        "rescued_nonpositive_pooled_evaluation_count": 0.0,
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
    for name, path, expected, expected_size in prior013.DEMAND_FILES:
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
    independent_rows = {}
    for name, _, _, _ in prior013.DEMAND_FILES:
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

    final_records = []
    for order in ORDERS:
        seen = []
        first_encounter_increment = {}
        for current_name in order:
            seen.append(current_name)
            shared_stats, overflow, invalid = learner.candidate_stats(
                base_train + [demands[name][0] for name in seen]
            )
            metrics["invalid_evaluation_rows"] += float(overflow + invalid)
            pooled_cells, radius_violations = learner.develop(shared_stats)
            metrics["invalid_evaluation_rows"] += float(radius_violations)
            pooled_full = learner.specialized_map(pooled_cells)
            if len(pooled_full) != 16:
                metrics["invalid_evaluation_rows"] += 1.0

            minimax_cells, ineligible, skipped_local = build_minimax_cells(
                learner,
                error_guided,
                baseline,
                shared_stats,
                pooled_cells,
                independent_rows,
                seen,
                demands,
            )
            metrics["minimax_ineligible_candidate_count"] += float(ineligible)
            metrics["minimax_local_assignment_skip_count"] += float(skipped_local)
            minimax_full = learner.specialized_map(minimax_cells)
            minimax_rows = wake.known_rows(pressure, learner, minimax_cells, shared_stats)
            if len(minimax_full) != 16 or len(minimax_rows) != 16:
                metrics["minimax_assignment_failure_count"] += 1.0
                metrics["invalid_evaluation_rows"] += 1.0
            original_records = sorted(record(row) for row in minimax_rows)
            metrics["valid_stage_count"] += 1.0

            for name in seen:
                cue, evaluation = demands[name]
                baseline_correct, frozen_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, frozen_full
                )
                _, independent_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, independent_full[name]
                )
                _, pooled_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, pooled_full
                )
                _, minimax_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, minimax_full
                )

                frozen_increment = frozen_correct - baseline_correct
                independent_increment = independent_correct - baseline_correct
                pooled_increment = pooled_correct - baseline_correct
                minimax_increment = minimax_correct - baseline_correct

                metrics["minimum_minimax_full_incremental_correct_count"] = min(
                    metrics["minimum_minimax_full_incremental_correct_count"],
                    float(minimax_increment),
                )
                metrics["minimum_minimax_minus_frozen_incremental_correct_count"] = min(
                    metrics["minimum_minimax_minus_frozen_incremental_correct_count"],
                    float(minimax_increment - frozen_increment),
                )
                independent_fraction = (
                    minimax_increment / independent_increment if independent_increment > 0 else 0.0
                )
                metrics["minimum_minimax_to_independent_incremental_correct_fraction"] = min(
                    metrics["minimum_minimax_to_independent_incremental_correct_fraction"],
                    independent_fraction,
                )
                metrics["minimum_minimax_minus_pooled_incremental_correct_count"] = min(
                    metrics["minimum_minimax_minus_pooled_incremental_correct_count"],
                    float(minimax_increment - pooled_increment),
                )
                if pooled_increment <= 0 and minimax_increment > 0:
                    metrics["rescued_nonpositive_pooled_evaluation_count"] += 1.0

                if name not in first_encounter_increment:
                    first_encounter_increment[name] = minimax_increment
                else:
                    first_increment = first_encounter_increment[name]
                    prior_fraction = minimax_increment / first_increment if first_increment > 0 else 0.0
                    metrics["minimum_prior_domain_minimax_incremental_correct_count"] = min(
                        metrics["minimum_prior_domain_minimax_incremental_correct_count"],
                        float(minimax_increment),
                    )
                    metrics["minimum_prior_domain_minimax_to_at_first_encounter_fraction"] = min(
                        metrics["minimum_prior_domain_minimax_to_at_first_encounter_fraction"],
                        prior_fraction,
                    )

                keys = {row["key"] for row in minimax_rows}
                cue_scores = error_guided.contributions(
                    learner, cue, baseline, keys, minimax_full
                )
                active_rows = sorted(
                    minimax_rows,
                    key=lambda row: (-cue_scores[row["key"]], -row["utility"], row["key"]),
                )[:ACTIVE_CEILING]
                active_keys = {row["key"] for row in active_rows}
                retained_rows = [row for row in minimax_rows if row["key"] not in active_keys]
                active = wake.active_map(active_rows)
                retained = wake.encode_retained(retained_rows)

                metrics["retained_record_integrity_mismatch_count"] += float(
                    wake.verify_records(retained, retained_rows)
                )
                metrics["state_partition_mismatch_count"] += float(
                    partition_mismatches(active_rows, retained_rows, original_records)
                )
                metrics["minimum_primary_active_structure_count"] = min(
                    metrics["minimum_primary_active_structure_count"], float(len(active_rows))
                )
                metrics["maximum_primary_active_structure_count"] = max(
                    metrics["maximum_primary_active_structure_count"], float(len(active_rows))
                )
                metrics["minimum_primary_retained_structure_count"] = min(
                    metrics["minimum_primary_retained_structure_count"], float(len(retained_rows))
                )
                metrics["maximum_primary_retained_structure_count"] = max(
                    metrics["maximum_primary_retained_structure_count"], float(len(retained_rows))
                )
                if minimax_increment > 0:
                    _, retained_fraction = error_guided.model_fraction(
                        pressure, learner, evaluation, baseline, minimax_full, active
                    )
                else:
                    retained_fraction = 0.0
                metrics["minimum_primary_retained_incremental_correct_fraction"] = min(
                    metrics["minimum_primary_retained_incremental_correct_fraction"],
                    retained_fraction,
                )
                _, _, gain, _ = pressure.pressured_eval(
                    learner, evaluation, baseline, active
                )
                metrics["minimum_eval_covered_accuracy_gain"] = min(
                    metrics["minimum_eval_covered_accuracy_gain"], gain
                )
                metrics["valid_seen_domain_evaluation_count"] += 1.0

        final_records.append(original_records)

    if final_records[0] != final_records[1]:
        mismatch = sum(a != b for a, b in zip(final_records[0], final_records[1]))
        mismatch += abs(len(final_records[0]) - len(final_records[1]))
        metrics["final_order_record_mismatch_count"] = float(mismatch)

    assert all(math.isfinite(value) for value in metrics.values())
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
