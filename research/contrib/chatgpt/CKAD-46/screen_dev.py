"""CKAD46 exactly-two-seed DEV-only source training and frozen stop."""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad46_frozen_dev_module",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def screen():
    cases=[D.run(s) for s in D.DEV]
    decision=D.classify(cases)
    if decision=="SOURCE_INVALID":
        raise AssertionError("CKAD46_NATIVE_SOURCE_CUSTODY_FAILED")
    return {
      "schema":"yggdrasil.ckad46.unseen-actions-dev-screen.v1",
      "preregistration_sha":D.PREREG,
      "research_parent":"b9cdc894a7e499f8ba74fcbac64fbb824259daa7",
      "decision":decision,"scientific_pass":False,
      "dev_first_uses_scored":list(D.DEV),
      "pilot_reserved_unconsumed":list(D.PILOT),
      "primary_reserved_unconsumed":list(D.PRIMARY),
      "source_structure":{"canonical_action_ids":[0,1],
           "new_unseen_identity_ids":list(D.TOKENS),
           "unknown_class_hidden":True,
           "balanced_map_hypotheses":36,
           "old_training_episodes_per_world":D.SOURCE,
           "unseen_transfer_end":D.TRANSFER_END,
           "source_episodes_per_world":D.TOTAL,
           "conditional_episode_noise_observed_only":True},
      "fixed_screen":{"pooled_late_transfer_cold_brier_max":.150,
          "absolute_gain_vs_strongest_control_min":.015,
          "max_early_transfer_worsening_vs_best_control":.015,
          "max_old_action_return_worsening_vs_native_hash":.005,
          "need_new_4_action_symbol_coverage_per_stage":True,
          "exact_original_native_and_learned_causal_cold":True},
      "cases":cases,
      "limitations":"Latent binary actuator mapping assumption is explicitly part of task; genuinely unseen symbols but not novel underlying primitive semantics. This DEV screen does not prove general language grounding, unrestricted causal discovery, or scientific acceptance. Original Yggdrasil binary native API remains untouched. No original source seed replay or held first-use."
    }


if __name__=="__main__":
    print("CKAD46_DEV_REPORT="+json.dumps(screen(),sort_keys=True,separators=(",",":")))
