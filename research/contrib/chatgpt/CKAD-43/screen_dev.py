"""CKAD43 frozen, one-shot two-seed development-only causal-recovery screen.

Reserved pilot/primary cohorts never have a runnable mode here.
"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad43_source_screen",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def main():
    cases=[D.score_seed(seed) for seed in D.DEV]  # each new DEV seed once
    decision=D.classify(cases)
    if decision=="SOURCE_INTEGRITY_FAILURE":
        raise AssertionError("CKAD43_COLD_OR_CUSTODY_INVALID")
    report={
      "schema":"yggdrasil.ckad43.dev-screen.v1",
      "preregistration_commit":D.PREREG,
      "parent_sha":"d477f4f2c4eec401c66cb6b66fffc6d78edd8a39",
      "decision":decision,"scientific_pass":False,
      "pilot_scored":False,"primary_scored":False,
      "dev_seeds_consumed":list(D.DEV),
      "pilots_reserved_untouched":list(D.PILOT),
      "primary_reserved_untouched":list(D.PRIMARY),
      "frozen_thresholds":{
        "max_pooled_late_brier_each_seed":.15,
        "min_pooled_gain_vs_all_trained_controls":.01,
        "min_late_return_A_gain_vs_original_native":.02,
        "max_early_return_A_worsening_vs_native":.005,
        "max_late_B_worsening_vs_native":.005,
        "require_two_persistent_source_trained_experts":True,
        "alarm_mean_brier_over_previous_12":.21,
        "new_B_initial_samples_to_compare":16,
        "min_witnessed_loss_margin_to_switch":.035,
        "min_dwell":8
      },
      "cases":cases,
      "limit":"Only reused-family stochastic synthetic source-trained DEV. Even DEV_FEASIBLE is not scientific qualification, new unknown-family transfer, first-use, accepted model or deployment."
    }
    print("CKAD43_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    main()
