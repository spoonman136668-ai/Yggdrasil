"""CKAD48: one original frozen two-seed development screen.

Only registered DEV cohort is executable. Held pilot and primary action
sequences have not been generated or tested.
"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad48_dev_source",HERE/"campaign.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def main():
    cases=[M.score_seed(seed) for seed in M.DEV]
    result=M.classify(cases)
    if result=="SOURCE_INVALID":
        raise AssertionError("CKAD48_SOURCE_INTEGRITY_FAILURE")
    report={
        "schema":"yggdrasil.ckad48.original-dev-report.v1",
        "prereg_sha":"dba16e4e3a1c7f51ea18b45b15da84761de9e5ba",
        "parent_source_sha":"a29b6e668fe1435bd9345664d5b9d2db87b46b7a",
        "dev_decision":result,
        "scientific_pass":False,
        "dev_seeds_consumed":list(M.DEV),
        "pilots_reserved_untouched":list(M.PILOT),
        "primaries_reserved_untouched":list(M.PRIMARY),
        "hypothesis":"Native source-trained contextual state-partition selection with genuine four-action and two-intervention consequence learning.",
        "frozen_gates":{
            "max_pooled_expected_Brier":.19,
            "min_gain_over_tabular":.010,
            "min_gain_over_false_XOR_invariance":.025,
            "max_gap_vs_exact_source_trained_BMA":.004,
            "max_early_unseen_gap_vs_exact_BMA":.015,
            "max_return_gap_vs_exact_BMA":.008,
            "four_action_identity_coverage_and_native_cold":True,
            "cross_platform_original_source_hash_and_metrics":True},
        "cases":cases,
        "limits":"Source-trained research-only four-state/four-action model. Two hand-specified synthetic state-dependent physical worlds; all candidates share a predeclared set of state partitions, exact Bayes is a stronger fully source-trained class control, no unknown arbitrary mechanics. No accepted Yggdrasil native binary source change, no autonomous owner use, no matched compute, no held pilot/primary first use or full final regression. Even DEV_FEASIBLE is NOT a scientific pass."
    }
    print("CKAD48_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    main()
