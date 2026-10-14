import argparse
import importlib.machinery
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-RETAIN-REVERT-CUE-CONCORDANCE-030"
PRIOR = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")

def sign(value):
    return -1 if value < 0 else (1 if value > 0 else 0)

def run():
    calls = []
    original_exec = importlib.machinery.SourceFileLoader.exec_module
    def observing_exec(loader, module):
        original_exec(loader, module)
        if str(getattr(module, "__file__", "")).replace("\\", "/").endswith("exp-dgr-real-utf8-resource-pressure-002.py"):
            original_counts = module.model_correct_counts
            def observed_counts(prior, data, baseline, learned):
                result = original_counts(prior, data, baseline, learned)
                calls.append(result)
                return result
            module.model_correct_counts = observed_counts
    importlib.machinery.SourceFileLoader.exec_module = observing_exec
    try:
        spec = importlib.util.spec_from_file_location("prior029", PRIOR)
        if spec is None or spec.loader is None:
            raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
        prior = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prior)
        sealed = prior.run()
    finally:
        importlib.machinery.SourceFileLoader.exec_module = original_exec
    old = sealed["metrics"]
    metrics = {key: old[key] for key in (
        "training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
        "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
        "valid_stage_count", "matched_assignment_failure_count", "minimum_selected_motif_count",
        "maximum_selected_motif_count", "matched_ineligible_candidate_count", "capacity_growth_event_count",
        "invalid_evaluation_rows")}
    metrics.update({
        "valid_diagnostic_row_count": 0.0,
        "sealed_minimum_ungated_incremental_correct_count": old["minimum_ungated_minimax_full_incremental_correct_count"],
        "sealed_minimum_ungated_minus_frozen_count": old["minimum_ungated_minimax_minus_frozen_incremental_correct_count"],
        "sealed_gate_decision_count": old["gate_decision_count"],
        "sealed_gate_revert_count": old["gate_revert_count"],
        "cue_eval_sign_concordance_fraction": 0.0, "false_retain_count": 0.0,
        "false_revert_count": 0.0, "zero_cue_negative_eval_count": 0.0,
        "positive_cue_negative_eval_count": 0.0})
    expected = (sealed.get("experiment") == "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-029" and
                old["minimum_ungated_minimax_full_incremental_correct_count"] == 64.0 and
                old["minimum_ungated_minimax_minus_frozen_incremental_correct_count"] == -12.0 and
                old["gate_decision_count"] == 12.0 and old["gate_revert_count"] == 0.0)
    metrics["invalid_evaluation_rows"] += float(not expected or len(calls) != 120)
    if len(calls) == 120:
        concordant = 0
        for offset in range(0, 120, 10):
            evaluation = calls[offset + 3][1] - calls[offset][1]
            cue = calls[offset + 5][1] - calls[offset + 4][1]
            concordant += int(sign(cue) == sign(evaluation))
            metrics["false_retain_count"] += float(cue >= 0 and evaluation < 0)
            metrics["false_revert_count"] += float(cue < 0 and evaluation >= 0)
            metrics["zero_cue_negative_eval_count"] += float(cue == 0 and evaluation < 0)
            metrics["positive_cue_negative_eval_count"] += float(cue > 0 and evaluation < 0)
            metrics["valid_diagnostic_row_count"] += 1.0
        metrics["cue_eval_sign_concordance_fraction"] = concordant / 12.0
    assert all(math.isfinite(value) for value in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1", "experiment":EXPERIMENT, "metrics":metrics}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))

if __name__ == "__main__":
    main()
