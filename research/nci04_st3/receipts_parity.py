"""ST3 read-only frozen receipt comparison.

Compares EXISTING dual-OS development artifacts. No source generation,
model fitting, future-lookups, hidden-law access or threshold modification.
Measured wall-time is environment-dependent: a Linux/Windows cost-threshold
disagreement must be a disclosed negative, not suppressed as an infra error.
"""
import argparse
import json
import math
from pathlib import Path
from research.nci04_st3.causal_switchboard import _canonical

RESULT_SCHEMA="yggdrasil.nci04.st3.frozen-consumed-development.v1"
PARITY_SCHEMA="yggdrasil.nci04.st3.readonly-receipt-parity.v1"
COST_KEY="whole_source_actor_learner_wall_ratio_le_1_5"
SOURCE_FIELDS=(
    "schema", "original_source_kind", "frozen_protocol_blob",
    "training_checkpoint_sha256","training_source_trace_sha256",
    "source_stage0","held_development_opened",
    "protected_scientific_first_use","scientific_pass",
    "original_frozen_hypothesis_changed_after_observation"
)
RECEIPT_FIELDS=(
    "law_id_evaluator_only","seed_evaluator_only","phase",
    "actual_source_steps","source_action_outcome_sha256",
    "delayed_action2_followed_by_action3_steps",
    "cold_model_restarts","learner_received_private_law_or_mask",
    "independent_science_first_use","candidate_trained_observed_actions",
    "candidate_forks","candidate_retrievals"
)


def close_structure(a,b):
    if type(a) is dict and type(b) is dict:
        return set(a)==set(b) and all(close_structure(a[k],b[k]) for k in a)
    if type(a) is list and type(b) is list:
        return len(a)==len(b) and all(
            close_structure(x,y) for x,y in zip(a,b)
        )
    if (type(a) in (float,int) and type(b) in (float,int) and
            type(a) is not bool and type(b) is not bool):
        return math.isclose(a,b,rel_tol=0,abs_tol=1e-12)
    return a==b


def compare_receipts(linux,windows):
    if not all(isinstance(x,dict) and x.get("schema")==RESULT_SCHEMA
               for x in (linux,windows)):
        raise ValueError("ST3_PARITY_INVALID_SOURCE_RECEIPT")
    for key in SOURCE_FIELDS:
        if linux[key]!=windows[key]:
            raise ValueError("ST3_PARITY_SOURCE_OR_TRAIN_DRIFT_"+key)
    if (linux["protected_scientific_first_use"] is not False or
        linux["scientific_pass"] is not False or
        linux["held_development_opened"] is not True):
        raise ValueError("ST3_PARITY_UNAUTHORIZED_SOURCE_CLASS")
    aa=linux["held_source_receipts"]
    bb=windows["held_source_receipts"]
    if len(aa)!=32 or len(bb)!=32:
        raise ValueError("ST3_PARITY_FROZEN_HELD_COVERAGE")
    candidate_state_exact=True
    scores_within_tol=True
    for a,b in zip(aa,bb):
        for key in RECEIPT_FIELDS:
            if a[key]!=b[key]:
                raise ValueError("ST3_PARITY_ORIGINAL_EVENT_OR_CUSTODY_"+key)
        if a["candidate_per_action_state_sha_chain"]!=b[
                "candidate_per_action_state_sha_chain"]:
            candidate_state_exact=False
        for key in ("preaction_brier","delayed_action2_to_action3_brier"):
            if not close_structure(a[key],b[key]):
                scores_within_tol=False
    for key in ("pooled_brier","held_law_brier",
                "delayed_after_action2_to_action3_brier"):
        if not close_structure(linux["metrics"][key],windows["metrics"][key]):
            scores_within_tol=False
    recall_equal=close_structure(
        {k:v for k,v in linux["retention_probe"].items()
         if k!="pass"},
        {k:v for k,v in windows["retention_probe"].items()
         if k!="pass"}
    )
    checks_a=linux["metrics"]["checks"]
    checks_b=windows["metrics"]["checks"]
    if set(checks_a)!=set(checks_b) or (
        any(checks_a[k]!=checks_b[k] for k in checks_a if k!=COST_KEY)
    ):
        raise ValueError("ST3_PARITY_FROZEN_NONCOST_CLASSIFIER_DRIFT")
    if (not isinstance(checks_a[COST_KEY],bool) or
        not isinstance(checks_b[COST_KEY],bool)):
        raise ValueError("ST3_PARITY_INVALID_COST_CLASSIFICATION")
    for d in (linux,windows):
        if d["metrics"]["pre_cross_os_disposition"]!="DEV_NO_GO" and (
            not all(d["metrics"]["checks"].values())
        ):
            raise ValueError("ST3_PARITY_INVALID_DEV_DISPOSITION")
    cost_threshold_same=checks_a[COST_KEY]==checks_b[COST_KEY]
    cost_a=linux["metrics"]["whole_process_modelled_wall_ratio"]
    cost_b=windows["metrics"]["whole_process_modelled_wall_ratio"]
    if any(type(x) not in (int,float) or not math.isfinite(x)
           or x<0 for x in (cost_a,cost_b)):
        raise ValueError("ST3_PARITY_NONFINITE_PROCESS_COST")
    qualified=(
        candidate_state_exact and scores_within_tol and recall_equal and
        cost_threshold_same and all(checks_a.values()) and
        all(checks_b.values())
    )
    return {
        "schema":PARITY_SCHEMA,
        "original_event_and_single_training_blob_exact":True,
        "frozen_protocol_git_blob":linux["frozen_protocol_blob"],
        "single_training_checkpoint_sha256":
            linux["training_checkpoint_sha256"],
        "source_held_development_episodes":len(aa),
        "held_development_action_steps":sum(
            r["actual_source_steps"] for r in aa
        ),
        "candidate_native_integer_checkpoint_sha_exact_cross_os":
            candidate_state_exact,
        "all_preaction_scores_equal_to_1e_12":scores_within_tol,
        "retention_ratio_and_evidence_equal_to_1e_12":recall_equal,
        "cost_threshold_same_across_os":cost_threshold_same,
        "linux_whole_process_modelled_cost_ratio":cost_a,
        "windows_whole_process_modelled_cost_ratio":cost_b,
        "linux_frozen_cost_threshold_pass":checks_a[COST_KEY],
        "windows_frozen_cost_threshold_pass":checks_b[COST_KEY],
        "frozen_science_checks_linux":checks_a,
        "frozen_science_checks_windows":checks_b,
        "disposition":(
            "DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE"
            if qualified else "DEV_NO_GO"
        ),
        "external_protected_science_first_use":False,
        "no_model_or_source_reexecuted_during_receipt_analysis":True,
        "whole_process_independently_isolated_resource_parity":
            "NOT_QUALIFIED",
        "full_final_regression_and_G29":"NOT_QUALIFIED",
    }


def main(linux,windows,output):
    a=json.loads(linux.read_text("utf-8"))
    b=json.loads(windows.read_text("utf-8"))
    report=compare_receipts(a,b)
    output.write_text(_canonical(report)+"\n",encoding="utf-8")
    for field in (
        "source_held_development_episodes",
        "held_development_action_steps",
        "candidate_native_integer_checkpoint_sha_exact_cross_os",
        "all_preaction_scores_equal_to_1e_12",
        "retention_ratio_and_evidence_equal_to_1e_12",
        "cost_threshold_same_across_os",
        "linux_whole_process_modelled_cost_ratio",
        "windows_whole_process_modelled_cost_ratio",
        "disposition"
    ):
        print("ST3_RECEIPT_"+field.upper()+"="+str(report[field]))
    print("ST3_NO_REPEATED_MODEL_OR_SOURCE_EXECUTION=PASS")
    return report


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--linux",type=Path,required=True)
    cli.add_argument("--windows",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    main(args.linux,args.windows,args.output)
