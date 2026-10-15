"""Frozen fresh-cohort replication of the qualified experiment-043 gate."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-GIT-REPLICATION-044"
PRIOR043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
CURRENT_PREREG = "exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.ice"
ORDERS = (("Y", "Z", "AA"), ("AA", "Z", "Y"))
DEMAND_FILES = (
    ("Y", "research/applications/track-a/a25-t8i-temporal-low-pass-persistence-calibration.ice", "af5a14691830a487f81a202c9880bc03c5591283", 20253),
    ("Z", "research/applications/track-a/a26-t8j-threshold-ultrasensitivity-calibration.ice", "18cec23aa4d8b6a62020904f19066c9f9ea957d2", 18258),
    ("AA", "research/applications/track-a/a27-t8k-negative-feedback-homeostatic-authority-correction.ice", "4451649de0edf3fe16de362b5b266ed9437db01b", 22531),
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prior_reference_count():
    names = tuple(Path(row[1]).name for row in DEMAND_FILES)
    count = 0
    for path in Path("research/experiments").glob("*.ice"):
        if path.name == CURRENT_PREREG:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        count += sum(text.count(name) for name in names)
    return count


def run():
    freshness = prior_reference_count()
    if freshness != 0:
        raise RuntimeError("FRESH_DEMAND_PREREGISTRATION_REFERENCE_MISMATCH")
    prior043 = load(PRIOR043, "prior043_fresh_git_044")
    prior043.ORDERS, prior043.DEMAND_FILES = ORDERS, DEMAND_FILES
    gated, calls, blocks = prior043.gated_run()
    old = gated["metrics"]
    keys = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
            "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
            "valid_stage_count", "matched_assignment_failure_count", "minimum_selected_motif_count",
            "maximum_selected_motif_count", "matched_ineligible_candidate_count", "capacity_growth_event_count",
            "invalid_evaluation_rows", "retained_record_integrity_mismatch_count", "state_partition_mismatch_count")
    metrics = {key: old[key] for key in keys}
    metrics.update({
        "fresh_demand_preregistration_reference_count": float(freshness),
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
