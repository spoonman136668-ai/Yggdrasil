"""Frozen one-shot CKAD44 development-only classification.

The original pilot and primary cohorts have no executable scoring mode.
"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad44_source_scored",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def screen():
    cases=[D.run(seed) for seed in D.DEV]
    decision=D.classify(cases)
    if decision=="SOURCE_INTEGRITY_FAILURE":
        raise AssertionError("CKAD44_SOURCE_INVALID")
    report={
      "schema":"yggdrasil.ckad44.dev-screen.v1",
      "prereg_commit":D.PREREG,
      "parent_source":"d11cb31d7fad45d917068703982c9ab4df85e2bc",
      "decision":decision,"scientific_pass":False,
      "registered_dev_consumed":list(D.DEV),
      "registered_pilot_reserved_untouched":list(D.PILOT),
      "registered_primary_reserved_untouched":list(D.PRIMARY),
      "scored_pilot":False,"scored_primary":False,
      "frozen_config":{
        "reference_initial_public_source_events":D.REFERENCE_EVENTS,
        "rolling_witness_log_evidence_events":D.EVIDENCE_WINDOW,
        "log_bayes_factor_clip":D.CLIP,
        "bocpd_hazard":D.HAZARD,
        "bocpd_run_length_cap":D.RUN_CAP,
        "required_distinct_first_and_second_interventions":2,
        "pooled_candidate_brier_max":.145,
        "pooled_gain_over_strongest_fully_trained_control_min":.01,
        "late_return_A_gain_vs_original_native_min":.02,
        "early_return_A_max_worsening_vs_original_native":.005,
        "late_B_max_worsening_vs_original_native":.005,
        "gain_vs_action_masked_ablation_min":.015
      },
      "cases":cases,
      "limits":"Two previously reused binary stochastic generator families only. 64-event stable reference is a task-defined structural advantage, NOT unknown-world zero-shot transfer. Additional frozen memory and online changepoint states add compute. Scientific primary/first-use, real-world grounding, native architecture adoption, deployment, full regression and autonomous training are not justified by a DEV result."
    }
    print("CKAD44_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    screen()
