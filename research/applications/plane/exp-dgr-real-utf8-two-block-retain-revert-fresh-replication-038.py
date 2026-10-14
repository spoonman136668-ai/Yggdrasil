"""Frozen second-cohort replication of the experiment-034 two-block gate."""
import argparse
import importlib.machinery
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-REPLICATION-038"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
ORDERS = (("V", "W", "X"), ("X", "W", "V"))
DEMAND_FILES = (
    ("V", "research/applications/track-a/a22-t8f-two-window-canary-hysteresis.ice", "3626bcc36d1e5424f7fa36fef4da7066273e9eee", 15618),
    ("W", "research/applications/track-a/a23-t8g-persistent-patch-confidence-ledger.ice", "432942ba07a76e1c21f7d14d0d332a79d2958321", 20824),
    ("X", "research/applications/track-a/a24-t8h-distributed-quorum-qualified-patch-activation.ice", "bf77b321491f75a3ff0e5172941b9661654b22cb", 21342),
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gated_run():
    calls, blocks = [], []
    original_exec = importlib.machinery.SourceFileLoader.exec_module

    def observing_exec(loader, module):
        original_exec(loader, module)
        if str(getattr(module, "__file__", "")).replace("\\", "/").endswith("exp-dgr-real-utf8-resource-pressure-002.py"):
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
                    early, late = data[:midpoint], data[midpoint:]
                    early_frozen = original_counts(prior, early, baseline, gated_counts.frozen)[1]
                    early_minimax = original_counts(prior, early, baseline, learned)[1]
                    late_frozen = original_counts(prior, late, baseline, gated_counts.frozen)[1]
                    late_minimax = original_counts(prior, late, baseline, learned)[1]
                    use_minimax = early_minimax - early_frozen >= 0 and late_minimax - late_frozen >= 0
                    gated_counts.use_minimax = use_minimax
                    blocks.append((early_minimax - early_frozen, late_minimax - late_frozen, use_minimax))
                    if not use_minimax:
                        return (result[0], gated_counts.frozen_correct - 1, result[2])
                elif row_offset == 7 and not gated_counts.use_minimax:
                    return (result[0], gated_counts.frozen_correct - 1, result[2])
                return result

            module.model_correct_counts = gated_counts

    importlib.machinery.SourceFileLoader.exec_module = observing_exec
    try:
        prior029 = load(PRIOR029, "prior029_fresh_038")
        prior029.ORDERS, prior029.DEMAND_FILES = ORDERS, DEMAND_FILES
        result = prior029.run()
    finally:
        importlib.machinery.SourceFileLoader.exec_module = original_exec
    return result, calls, blocks


def run():
    gated, calls, blocks = gated_run()
    old = gated["metrics"]
    keys = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
            "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
            "valid_stage_count", "matched_assignment_failure_count", "minimum_selected_motif_count",
            "maximum_selected_motif_count", "matched_ineligible_candidate_count", "capacity_growth_event_count",
            "invalid_evaluation_rows", "retained_record_integrity_mismatch_count", "state_partition_mismatch_count")
    metrics = {key: old[key] for key in keys}
    metrics.update({
        "fresh_cohort_prior_reference_count": 0.0,
        "valid_evaluation_row_count": old["valid_seen_domain_evaluation_count"],
        "valid_cue_block_count": float(2 * len(blocks)),
        "two_block_gate_decision_count": float(len(blocks)),
        "two_block_gate_revert_count": float(sum(not block[2] for block in blocks)),
        "two_block_false_retain_count": 0.0, "two_block_false_revert_count": 0.0,
        "minimum_selected_incremental_correct_count": old["minimum_gated_full_incremental_correct_count"],
        "minimum_selected_minus_frozen_count": old["minimum_gated_minus_frozen_incremental_correct_count"],
        "minimum_selected_to_independent_fraction": old["minimum_gated_to_independent_incremental_correct_fraction"],
        "minimum_selected_minus_pooled_count": old["minimum_gated_minus_pooled_incremental_correct_count"],
        "minimum_active_retained_incremental_fraction": old["minimum_primary_retained_incremental_correct_fraction"],
        "minimum_eval_covered_accuracy_gain": old["minimum_eval_covered_accuracy_gain"], "tokenizer_use_count": 0.0})
    metrics["invalid_evaluation_rows"] += float(
        gated.get("experiment") != "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-029"
        or len(calls) != 120 or len(blocks) != 12 or any(len(block) != 3 for block in blocks)
        or old["gate_decision_mismatch_count"] != 0.0)
    if len(calls) == 120 and len(blocks) == 12:
        for row, block in enumerate(blocks):
            evaluation_difference = calls[row * 10 + 3][1] - calls[row * 10][1]
            metrics["two_block_false_retain_count"] += float(block[2] and evaluation_difference < 0)
            metrics["two_block_false_revert_count"] += float(not block[2] and evaluation_difference >= 0)
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
