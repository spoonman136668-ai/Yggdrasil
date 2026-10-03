"""Sealed source for EXP-DGR-EXTERNAL-RAW-CUMULATIVE-CONSOLIDATION-017."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-RAW-CUMULATIVE-CONSOLIDATION-017"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-real-utf8-minimax-matched-consolidation-016.py")
ACTIVE_CEILING = 7
ORDERS = (("A", "B", "C"), ("C", "B", "A"))
SOURCES = {
    "A": {
        "domain": "code",
        "file": "code.bin",
        "sha256": "7a95f1c506c9ac4b2277df5f2bdd9d61cc67b520c45021a5a961939770221ef6",
        "bytes": 41453,
    },
    "B": {
        "domain": "structured",
        "file": "structured.bin",
        "sha256": "4c5cbe6cbcd28af73761091367b20e07d0403847e236c06c31fc27061bd81192",
        "bytes": 14365,
    },
    "C": {
        "domain": "technical-prose",
        "file": "technical-prose.bin",
        "sha256": "8247b7c5de1e74854aac1a08aa5894444d1d33b4045c70d5cc3367ad0e25c3f3",
        "bytes": 1454,
    },
}


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_real_utf8_minimax_matched_016", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_external(root, metrics):
    demands = {}
    total = 0
    root = Path(root)
    for name in ("A", "B", "C"):
        spec = SOURCES[name]
        path = root / spec["file"]
        try:
            data = path.read_bytes()
        except OSError:
            metrics["source_identity_mismatch_count"] += 1.0
            data = b""
        actual = hashlib.sha256(data).hexdigest()
        if actual != spec["sha256"] or len(data) != spec["bytes"]:
            metrics["source_identity_mismatch_count"] += 1.0
        total += len(data)
        split = len(data) * 60 // 100
        if split <= 0 or split >= len(data):
            metrics["invalid_evaluation_rows"] += 1.0
            demands[name] = (b"", b"")
        else:
            demands[name] = (data[:split], data[split:])
    metrics["source_count"] = 3.0
    metrics["total_source_bytes"] = float(total)
    return demands


def record(prior016, row):
    return prior016.record(row)


def partition_mismatches(prior016, active_rows, retained_rows, original_records):
    return prior016.partition_mismatches(active_rows, retained_rows, original_records)


def run(root):
    prior016 = load_prior_experiment()
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
        "valid_stage_count": 0.0,
        "valid_seen_domain_evaluation_count": 0.0,
        "matched_assignment_failure_count": 0.0,
        "minimum_selected_motif_count": 16.0,
        "maximum_selected_motif_count": 0.0,
        "minimum_cumulative_incremental_correct_count": float("inf"),
        "minimum_cumulative_to_independent_incremental_correct_fraction": float("inf"),
        "minimum_prior_domain_incremental_correct_count": float("inf"),
        "minimum_prior_domain_to_first_encounter_fraction": float("inf"),
        "minimum_active_retained_incremental_correct_fraction": float("inf"),
        "minimum_primary_active_structure_count": 16.0,
        "maximum_primary_active_structure_count": 0.0,
        "minimum_primary_retained_structure_count": 16.0,
        "maximum_primary_retained_structure_count": 0.0,
        "retained_record_integrity_mismatch_count": 0.0,
        "state_partition_mismatch_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "external_model_call_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

    demands = load_external(root, metrics)

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

            minimax_full = learner.specialized_map(minimax_cells)
            minimax_rows = wake.known_rows(pressure, learner, minimax_cells, shared_stats)
            if len(minimax_full) != 16 or len(minimax_rows) != 16:
                metrics["matched_assignment_failure_count"] += 1.0
                metrics["invalid_evaluation_rows"] += 1.0

            original_records = sorted(record(prior016, row) for row in minimax_rows)
            metrics["valid_stage_count"] += 1.0

            for name in seen:
                cue, evaluation = demands[name]
                baseline_correct, _, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, {}
                )
                _, independent_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, independent_full[name]
                )
                _, minimax_correct, _ = pressure.model_correct_counts(
                    learner, evaluation, baseline, minimax_full
                )
                independent_increment = independent_correct - baseline_correct
                minimax_increment = minimax_correct - baseline_correct

                metrics["minimum_cumulative_incremental_correct_count"] = min(
                    metrics["minimum_cumulative_incremental_correct_count"],
                    float(minimax_increment),
                )
                fraction = (
                    minimax_increment / independent_increment
                    if independent_increment > 0
                    else 0.0
                )
                metrics["minimum_cumulative_to_independent_incremental_correct_fraction"] = min(
                    metrics["minimum_cumulative_to_independent_incremental_correct_fraction"],
                    fraction,
                )

                if name not in first_encounter_increment:
                    first_encounter_increment[name] = minimax_increment
                else:
                    first_increment = first_encounter_increment[name]
                    prior_fraction = (
                        minimax_increment / first_increment
                        if first_increment > 0
                        else 0.0
                    )
                    metrics["minimum_prior_domain_incremental_correct_count"] = min(
                        metrics["minimum_prior_domain_incremental_correct_count"],
                        float(minimax_increment),
                    )
                    metrics["minimum_prior_domain_to_first_encounter_fraction"] = min(
                        metrics["minimum_prior_domain_to_first_encounter_fraction"],
                        prior_fraction,
                    )

                keys = {row["key"] for row in minimax_rows}
                cue_scores = error_guided.contributions(
                    learner, cue, baseline, keys, minimax_full
                )
                active_rows = sorted(
                    minimax_rows,
                    key=lambda row: (
                        -cue_scores[row["key"]],
                        -row["utility"],
                        row["key"],
                    ),
                )[:ACTIVE_CEILING]
                active_keys = {row["key"] for row in active_rows}
                retained_rows = [
                    row for row in minimax_rows if row["key"] not in active_keys
                ]
                active = wake.active_map(active_rows)
                retained = wake.encode_retained(retained_rows)

                metrics["retained_record_integrity_mismatch_count"] += float(
                    wake.verify_records(retained, retained_rows)
                )
                metrics["state_partition_mismatch_count"] += float(
                    partition_mismatches(
                        prior016, active_rows, retained_rows, original_records
                    )
                )
                metrics["minimum_primary_active_structure_count"] = min(
                    metrics["minimum_primary_active_structure_count"],
                    float(len(active_rows)),
                )
                metrics["maximum_primary_active_structure_count"] = max(
                    metrics["maximum_primary_active_structure_count"],
                    float(len(active_rows)),
                )
                metrics["minimum_primary_retained_structure_count"] = min(
                    metrics["minimum_primary_retained_structure_count"],
                    float(len(retained_rows)),
                )
                metrics["maximum_primary_retained_structure_count"] = max(
                    metrics["maximum_primary_retained_structure_count"],
                    float(len(retained_rows)),
                )
                if minimax_increment > 0:
                    _, retained_fraction = error_guided.model_fraction(
                        pressure,
                        learner,
                        evaluation,
                        baseline,
                        minimax_full,
                        active,
                    )
                else:
                    retained_fraction = 0.0
                metrics["minimum_active_retained_incremental_correct_fraction"] = min(
                    metrics["minimum_active_retained_incremental_correct_fraction"],
                    retained_fraction,
                )
                metrics["valid_seen_domain_evaluation_count"] += 1.0

    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
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
