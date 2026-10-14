"""Frozen two-block retain/revert gate for experiment 034."""
import argparse
import importlib.machinery
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-GATE-034"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRIOR030 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-cue-concordance-030.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gated_run():
    calls = []
    blocks = []
    original_exec = importlib.machinery.SourceFileLoader.exec_module

    def observing_exec(loader, module):
        original_exec(loader, module)
        if str(getattr(module, "__file__", "")).replace("\\", "/").endswith(
            "exp-dgr-real-utf8-resource-pressure-002.py"
        ):
            original_counts = module.model_correct_counts

            def gated_counts(prior, data, baseline, learned):
                row_offset = len(calls) % 10
                result = original_counts(prior, data, baseline, learned)
                calls.append(result)
                if row_offset == 4:
                    gated_counts.frozen = learned
                    gated_counts.frozen_correct = result[1]
                elif row_offset == 5:
                    midpoint = len(data) // 2
                    early = data[:midpoint]
                    late = data[midpoint:]
                    early_frozen = original_counts(
                        prior, early, baseline, gated_counts.frozen
                    )[1]
                    early_minimax = original_counts(prior, early, baseline, learned)[1]
                    late_frozen = original_counts(
                        prior, late, baseline, gated_counts.frozen
                    )[1]
                    late_minimax = original_counts(prior, late, baseline, learned)[1]
                    use_minimax = (
                        early_minimax - early_frozen >= 0
                        and late_minimax - late_frozen >= 0
                    )
                    gated_counts.use_minimax = use_minimax
                    blocks.append(
                        (
                            early_minimax - early_frozen,
                            late_minimax - late_frozen,
                            use_minimax,
                        )
                    )
                    if not use_minimax:
                        return (result[0], gated_counts.frozen_correct - 1, result[2])
                elif row_offset == 7 and not gated_counts.use_minimax:
                    return (result[0], gated_counts.frozen_correct - 1, result[2])
                return result

            module.model_correct_counts = gated_counts

    importlib.machinery.SourceFileLoader.exec_module = observing_exec
    try:
        result = load(PRIOR029, "prior029_gated").run()
    finally:
        importlib.machinery.SourceFileLoader.exec_module = original_exec
    return result, calls, blocks


def run():
    sealed = load(PRIOR030, "prior030_sealed").run()
    gated, calls, blocks = gated_run()
    old = gated["metrics"]
    sealed_metrics = sealed["metrics"]
    metrics = {
        key: old[key]
        for key in (
            "training_file_identity_mismatch_count",
            "evaluation_file_identity_mismatch_count",
            "future_stage_adaptation_access_count",
            "second_half_adaptation_access_count",
            "valid_stage_count",
            "matched_assignment_failure_count",
            "minimum_selected_motif_count",
            "maximum_selected_motif_count",
            "matched_ineligible_candidate_count",
            "capacity_growth_event_count",
            "invalid_evaluation_rows",
            "retained_record_integrity_mismatch_count",
            "state_partition_mismatch_count",
        )
    }
    metrics.update(
        {
            "valid_evaluation_row_count": old[
                "valid_seen_domain_evaluation_count"
            ],
            "valid_cue_block_count": float(2 * len(blocks)),
            "sealed_minimum_ungated_incremental_correct_count": sealed_metrics[
                "sealed_minimum_ungated_incremental_correct_count"
            ],
            "sealed_minimum_ungated_minus_frozen_count": sealed_metrics[
                "sealed_minimum_ungated_minus_frozen_count"
            ],
            "sealed_single_cue_concordance_fraction": sealed_metrics[
                "cue_eval_sign_concordance_fraction"
            ],
            "sealed_single_cue_false_retain_count": sealed_metrics[
                "false_retain_count"
            ],
            "two_block_gate_decision_count": float(len(blocks)),
            "two_block_gate_revert_count": float(
                sum(not block[2] for block in blocks)
            ),
            "two_block_false_retain_count": 0.0,
            "two_block_false_revert_count": 0.0,
            "minimum_selected_incremental_correct_count": old[
                "minimum_gated_full_incremental_correct_count"
            ],
            "minimum_selected_minus_frozen_count": old[
                "minimum_gated_minus_frozen_incremental_correct_count"
            ],
            "minimum_selected_to_independent_fraction": old[
                "minimum_gated_to_independent_incremental_correct_fraction"
            ],
            "minimum_selected_minus_pooled_count": old[
                "minimum_gated_minus_pooled_incremental_correct_count"
            ],
            "minimum_active_retained_incremental_fraction": old[
                "minimum_primary_retained_incremental_correct_fraction"
            ],
            "minimum_eval_covered_accuracy_gain": old[
                "minimum_eval_covered_accuracy_gain"
            ],
        }
    )
    metrics["invalid_evaluation_rows"] += float(
        sealed.get("experiment")
        != "EXP-DGR-REAL-UTF8-RETAIN-REVERT-CUE-CONCORDANCE-030"
        or gated.get("experiment")
        != "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-029"
        or len(calls) != 120
        or len(blocks) != 12
        or any(len(block) != 3 for block in blocks)
        or old["gate_decision_mismatch_count"] != 0.0
    )
    if len(calls) == 120 and len(blocks) == 12:
        for row, block in enumerate(blocks):
            evaluation_difference = calls[row * 10 + 3][1] - calls[row * 10][1]
            use_minimax = block[2]
            metrics["two_block_false_retain_count"] += float(
                use_minimax and evaluation_difference < 0
            )
            metrics["two_block_false_revert_count"] += float(
                not use_minimax and evaluation_difference >= 0
            )
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
