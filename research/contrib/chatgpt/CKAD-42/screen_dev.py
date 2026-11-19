"""CKAD42 frozen two-seed DEV-only scientific falsification.

There is no pilot or reserved primary execution mode in this contribution.
"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad42_dev_screen",HERE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def main():
    cases=[C.run(seed) for seed in C.DEV]
    decision=C.classify(cases)
    if decision=="INVALID_SOURCE":
        raise AssertionError("CKAD42_SOURCE_INVALID")
    report={
        "schema":"yggdrasil.ckad42.dev-screen.v1",
        "prereg_commit":C.PREREG,
        "source_parent":"c4aca6373211487f8cbe07ef0f64f88b937bd0f2",
        "decision":decision,
        "engineering_integrity":True,
        "scientific_pass":False,
        "pilot_scored":False,"primary_scored":False,
        "dev_seeds_consumed":list(C.DEV),
        "original_pilots_reserved":list(C.PILOT),
        "primary_reserved":list(C.PRIMARY),
        "basis_hypothesis_count":[len(C.TRANSITION),len(C.TERMINAL)],
        "cases":cases,
        "fixed_thresholds":{
            "pooled_candidate_brier_at_most":.15,
            "pooled_gain_over_all_full_fit_controls_at_least":.01,
            "pooled_gain_over_action_ablation_at_least":.01,
            "max_early_phase_worsening_against_native":.01},
        "limits":"Only frozen two-seed DEV synthetic observed-action training; the grammar is a declared prior. This is not an unfamiliar-world or native scientific qualification, accepted research state, autonomous loop execution, or deployment."
    }
    print("CKAD42_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    main()
