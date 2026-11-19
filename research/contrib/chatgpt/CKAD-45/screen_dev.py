"""One original frozen two-seed closed-loop intervention DEV qualification.

No original pilot or primary first-use path exists. No held outcomes enter
policy. Independent common-probe examiner outputs are never training records.
"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad45_frozen_source",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def screen():
    cases=[D.score_seed(s) for s in D.DEV]
    decision=D.classify(cases)
    if decision=="SOURCE_INTEGRITY_FAILURE":
        raise AssertionError("CKAD45_SOURCE_OR_COLD_INVALID")
    return {
     "schema":"yggdrasil.ckad45.closed-loop-dev-screen.v1",
     "prereg_commit":D.PREREG,
     "parent_source_sha":"c61e5d28a6e87542ed4018cd3da07216dadc669b",
     "decision":decision,"scientific_pass":False,"first_use":False,
     "dev_seeds_consumed":list(D.DEV),
     "pilot_untouched":list(D.PILOT),"primary_untouched":list(D.PRIMARY),
     "world_variants":2,
     "frozen_settings":{"episodes_per_world_policy":D.N,
        "first_shift":D.FIRST_CHANGE,"return":D.RETURN,
        "evaluation_probe_stride":D.PROBE_STEP,
        "warm_events_before_native_stream":D.WARM,
        "recent_prequential_alarm_window":D.RECENT,
        "prequential_Brier_alarm_threshold":D.ALARM,
        "full_short_causal_disagreement_multiplier":D.DISAGREE,
        "require_same_context_exogenous_noise_for_all_policies":True,
        "require_exact_retrieval_and_no_counterfactual_learning":True,
        "max_pooled_candidate_expected_brier":.145,
        "min_pooled_gain_vs_best_active_control":.010,
        "max_pooled_native_worsening_vs_best_native":.005,
        "max_early_return_worsening_vs_best_active_control":.010,
        "min_late_return_gain_vs_exact_info_gain":.010,
        "min_candidate_action_change_fraction_vs_exact_info_gain":.10},
     "cases":cases,
     "limits":"Two development seeds, two novel hand-specified binary causal-family pairs. All policies have matched interventions/observed outcomes per episode and common exogenous noise; decisions choose distinct actions so samples are not identical action IDs. Evaluation is same exhaustive counterfactual EXPECTED-Brier grid, not a hidden reward or any training event. Extra policy and examiner compute is NOT matched. No real-world general intelligence, unfamiliar action semantics, owner held first-use, native runtime merge, full regression or deployment."
    }


if __name__=="__main__":
    print("CKAD45_DEV_REPORT="+json.dumps(screen(),sort_keys=True,separators=(",",":")))
