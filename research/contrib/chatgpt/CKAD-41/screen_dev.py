"""CKAD41 single frozen DEV cohort screen. No pilot or primary first-use."""
import importlib.util
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad41_screen_campaign",HERE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def screen():
    cases=[C.run(seed) for seed in C.DEV]
    decision=C.classify(cases)
    if decision=="INVALID_SOURCE":
        raise AssertionError("CKAD41_SOURCE_INTEGRITY_INVALID")
    report={
      "schema":"yggdrasil.ckad41.dev-screen.v1",
      "prereg_commit":C.PREREG,
      "parent_source_sha":"d95674f3edae01268353f47c2d8dddd85ab8f21b",
      "decision":decision,"engineering_integrity":True,
      "science_pass":False,"pilot_scored":False,"primary_scored":False,
      "dev_seeds":list(C.DEV),"reserved_unconsumed":list(C.RESERVED),
      "cases":cases,
      "fixed_thresholds":{
          "max_native_micro16_pooled_brier":0.145,
          "min_pooled_gain_vs_all_native_and_conventional_controls":0.015,
          "max_early_phase_worsening_vs_original_native":0.005,
          "cap_retained_source_episodes_per_archive":128,
          "evidence_window_episodes":16
      },
      "limits":"DEV cohort from previously used binary synthetic families; trained anchor replicas increase model update cost. No owner first-use, transfer, engineering full final regression, scientific pass, accepted ref or deployment."
    }
    print("CKAD41_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    screen()
