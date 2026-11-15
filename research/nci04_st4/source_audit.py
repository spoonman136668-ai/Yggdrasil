"""Frozen ST4 source-only counterfactual identifiability screen.

Only in-house TRAIN law/seed pairs. Does NOT fit, import, score or run a
learner, nor access predeclared held DEV/negative law sources or protected
first-use. A pair is verified only after two REAL source arms execute.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

from research.nci04_st4.paired_world import (
    source_paired_trial,TRIALS,SOURCE_ACTIONS_PER_TRIAL
)

FREEZE_COMMIT="b03a33159905c1d0e8b2aa0965f418b9a35c455e"
FREEZE_BLOB="edaea790d3457bd91ea136a6b266c19e6dd61575"
FREEZE_PATH="research/nci04_st4/frozen_protocol.json"
TRAIN_LAWS=(3,5,7,11,13,17,19,23)
TRAIN_SEEDS=tuple(range(100,112))
HELD_DEV_LAWS=(29,31,37,41)
HELD_DEV_SEEDS=tuple(range(201,209))
SCHEMA="yggdrasil.nci04.st4.paired-source-stage0.v1"


def canonical(doc):
    return json.dumps(doc,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify_freeze():
    p=json.loads((Path(__file__).with_name("frozen_protocol.json"))
                 .read_text(encoding="utf-8"))
    expected={
        "schema":"yggdrasil.nci04.st4.balanced-intervention.dev.v1",
        "status":"PREREG_FROZEN_BEFORE_SOURCE_MODEL_OR_OUTCOMES",
        "source_parent_sha":"def4e3a9d803c80631c00b7e138a5c54cda349e9"
    }
    if any(p.get(k)!=v for k,v in expected.items()):
        raise ValueError("ST4_FROZEN_PROTOCOL_HEADER_CHANGED")
    s=p["source"]
    if (tuple(s["train_laws"])!=TRAIN_LAWS or
        tuple(s["train_seeds"])!=TRAIN_SEEDS or
        tuple(s["held_dev_laws"])!=HELD_DEV_LAWS or
        tuple(s["held_dev_seeds"])!=HELD_DEV_SEEDS or
        s["trial_count_per_law_seed"]!=TRIALS or
        s["arms_per_trial"]!=2 or s["steps_per_arm"]!=2 or
        s["frozen_training_action_steps"]!=6144 or
        s["frozen_held_dev_action_steps"]!=2048 or
        s["no_protected_first_use"] is not True or
        p["authority"]["protected_first_use"] is not False or
        p["authority"]["merge"] is not False or
        p["authority"]["new_schedule"] is not False or
        p["authority"]["paid_api"] is not False or
        ">=95%" not in p["stage0_source_only"]["before"]):
        raise ValueError("ST4_FROZEN_SOURCE_PROTOCOL_CHANGED")
    get=lambda *a:subprocess.check_output(["git",*a],text=True).strip()
    if get("rev-parse","HEAD:"+FREEZE_PATH)!=FREEZE_BLOB:
        raise ValueError("ST4_FROZEN_PREREG_BLOB_CHANGED")
    if subprocess.run(
        ["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],
        check=False
    ).returncode:
        raise ValueError("ST4_FROZEN_PREREG_NOT_ANCESTOR")
    return p


def evaluate_counts(total,law_trials,probe_counts,arm_orders):
    if (type(total) is not int or total<0 or
        type(law_trials) is not dict or
        set(law_trials)!=set(TRAIN_LAWS) or
        type(probe_counts) is not dict or
        set(probe_counts)!={0,1,3} or
        type(arm_orders) is not dict or
        set(arm_orders)!={"treatment","control"}):
        raise ValueError("ST4_STAGE0_INVALID_SOURCE_ACCOUNTING")
    for entries in (law_trials.values(),probe_counts.values(),
                    arm_orders.values()):
        if any(type(x) is not int or x<0 for x in entries):
            raise ValueError("ST4_STAGE0_BAD_COUNT")
    must={
        "at_least_1500_real_paired_source_interventions":total>=1500,
        "every_law_has_95pct_real_delayed_effect_pairs":
            all(correct/float(len(TRAIN_SEEDS)*TRIALS)>=.95
                for correct in law_trials.values()),
        "all_3_blind_probe_actions_represented_in_100_pairs":
            all(n>=100 for n in probe_counts.values()),
        "both_arm_orders_executed":min(arm_orders.values())>0,
    }
    return {
        "checks":must,
        "disposition":(
            "SOURCE_BALANCED_INTERVENTIONS_IDENTIFIABLE_DEV_ONLY"
            if all(must.values())
            else "SOURCE_COUNTERFACTUAL_IDENTIFIABILITY_NO_GO"
        ),
    }


def audit(output):
    begin=time.perf_counter_ns()
    verify_freeze()
    total_pairs=0
    total_actions=0
    law_contrast={law:0 for law in TRAIN_LAWS}
    probes=Counter({0:0,1:0,3:0})
    order=Counter({"treatment":0,"control":0})
    receipts=[]
    for law in TRAIN_LAWS:
        trace=sha256()
        for seed in TRAIN_SEEDS:
            for trial in range(TRIALS):
                r=source_paired_trial(law,seed,trial)
                if (r["learner_seen_private_law_or_paired_labels"] is not False
                    or not r["same_initial_public"]
                    or not r["same_pre_probe_public"]
                    or not r["same_current_probe_action"]
                    or r["treatment_first_action"]!=2
                    or r["control_first_action"]!=3
                    or r["original_action_steps"]!=SOURCE_ACTIONS_PER_TRIAL
                    or not r["cold_source_restore_exact"]):
                    raise ValueError("ST4_ORIGINAL_CAUSAL_PAIR_DRIFT")
                total_pairs+=1
                total_actions+=r["original_action_steps"]
                probes[r["actor_probe_action"]]+=1
                order[r["actor_arm_order"][0]]+=1
                law_contrast[law]+=int(r["different_real_probe_outcomes"])
                trace.update(bytes.fromhex(
                    r["paired_original_action_consequence_sha256"]
                ))
        receipts.append({
            "law_evaluator_only":law,
            "trials":len(TRAIN_SEEDS)*TRIALS,
            "contrasting_original_public_probe_pairs":law_contrast[law],
            "original_source_pair_action_history_sha256":trace.hexdigest(),
        })
    if total_actions!=6144 or total_pairs!=1536:
        raise ValueError("ST4_SOURCE_ACTION_BUDGET_DRIFT")
    result=evaluate_counts(total_pairs,law_contrast,
                           dict(probes),dict(order))
    doc={
        "schema":SCHEMA,
        "frozen_protocol_git_blob":FREEZE_BLOB,
        "preregistration_commit":FREEZE_COMMIT,
        "source_laws_used":list(TRAIN_LAWS),
        "source_seeds_used":list(TRAIN_SEEDS),
        "held_development_source_unopened":True,
        "source_only":True,
        "trained_candidate_or_conventional":False,
        "protected_scientific_first_use":False,
        "original_public_real_paired_trials":total_pairs,
        "original_public_real_source_actions":total_actions,
        "probe_action_pair_counts":dict(probes),
        "first_arm_counts":dict(order),
        "source_law_receipts":receipts,
        "result":result,
        "whole_source_audit_wall_ns":time.perf_counter_ns()-begin,
        "scientific_qualification":"NOT_EVALUATED",
    }
    output.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST4_SOURCE_PAIRED_TRIALS="+str(total_pairs))
    print("ST4_SOURCE_REAL_ACTIONS="+str(total_actions))
    print("ST4_SOURCE_LAW_CONTRASTS="+canonical(law_contrast))
    print("ST4_SOURCE_PROBE_COUNTS="+canonical(dict(probes)))
    print("ST4_SOURCE_ARM_ORDER_COUNTS="+canonical(dict(order)))
    print("ST4_SOURCE_DISPOSITION="+result["disposition"])
    print("ST4_SOURCE_NO_PROTECTED_FIRST_USE=PASS")
    return doc


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    audit(args.output)
