"""FKP-21 first source-safe known-TRAIN physical rule/feedback comparison.

The protocol, NOT the learner, chooses a frozen 12+4 sequence of actions;
each model predicts the outcome of a previously unseen source input BEFORE
any phase of that probe is physically applied. It then receives ONLY the
actually earned final reward. Exact cold recall of directly experienced data
is kept distinct from inference about still-unobserved combinations.

No original protected cohort, arbitrary primitive-invention claim, or native
integration. A first-preregistered GF2 control may tie the candidate.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import random
import time

import public_rule_source as source
import rule_learning as learner

ARMS=learner.MODES
PREREG_FIRST="ef9ee3fa690a77250829424070ec4a8fc87b2197"


def _encode(x):
    return json.dumps(x,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _digest(x):
    return sha256(_encode(x)).hexdigest()


def _do_world(seed,mode):
    arm=learner.PublicRuleArm(mode)
    start=time.perf_counter()
    observations=[]
    for i,x in enumerate(source.TRAIN_PATTERNS):
        # Each of four source-public action phases occurs before its actual
        # feedback. No private law or counterfactual is passed to the arm.
        steps=source.physical_probe(seed,x)
        actual=1 if steps[-1].reward==1.0 else 0
        arm.observe_train(steps,event_id=i)
        observations.append((x,actual))
    if arm.observations!=12:
        raise AssertionError("FKP21_NOT_ALL_12_PHYSICAL_OUTCOMES")
    arm.freeze()
    trained=arm.state_receipt()
    fit_wall=time.perf_counter()-start
    earned=[]
    unknown_predictions=[]
    first_hit=0
    abstained=0
    start=time.perf_counter()
    for i,x in enumerate(source.FIRST_PROBES):
        p=arm.predict_first(x)
        if p not in (0,1,None):
            raise AssertionError("FKP21_INVALID_PREOUTCOME_PREDICTION")
        # No source action for x has occurred before this prediction.
        physical=source.physical_probe(seed,x)
        actual=1 if physical[-1].reward==1.0 else 0
        unknown_predictions.append((x,p,actual))
        if p is None:
            abstained+=1
        else:
            first_hit+=int(p==actual)
        feedback_digest=arm.record_actual_feedback(physical,index=i)
        earned.append((x,actual,feedback_digest))
    score_wall=time.perf_counter()-start
    if arm.observations!=16:
        raise AssertionError("FKP21_NOT_ALL_REAL_FEEDBACK_OBSERVED")
    cold=learner.PublicRuleArm.restore(arm.checkpoint())
    if cold.state_receipt()!=arm.state_receipt() or cold.checkpoint()!=arm.checkpoint():
        raise AssertionError("FKP21_COLD_RESTORE_NOT_BITWISE")
    recalled=sum(int(cold.recall(x)==actual) for x,actual,_ in earned)
    return {
        "observed_train_sha256":_digest(observations),
        "trained_model_receipt":trained,
        "first_held_predictions":unknown_predictions,
        "first_held_correct":first_hit,
        "first_held_abstain":abstained,
        "actual_held_outcomes":earned,
        "first_feedback_sha256":_digest(earned),
        "cold_direct_recall_correct":recalled,
        "checkpoint_sha256":sha256(arm.checkpoint()).hexdigest(),
        "learned_logical_bytes":cold.logical_learned_bytes,
        "fit_wall_seconds":fit_wall,
        "first_score_wall_seconds":score_wall
    }


def _paired_bootstrap(byseed):
    if tuple(byseed)!=source.TRAIN:
        raise ValueError("FKP21_SEED_SCHEDULE_DRIFT")
    pairs=[(byseed[source.TRAIN[i]],byseed[source.TRAIN[i+8]]) for i in range(8)]
    rng=random.Random(2121)
    candidate="INNOVATION_GF2"
    informed="INDEPENDENT_GF2_ELIMINATION"
    differences=[]
    for _ in range(10000):
        chosen=[pairs[rng.randrange(8)] for _ in range(8)]
        flat=[w for pair in chosen for w in pair]
        candidate_sum=sum(w["arms"][candidate]["first_held_correct"] for w in flat)
        control_sum=sum(w["arms"][informed]["first_held_correct"] for w in flat)
        differences.append(candidate_sum-control_sum)
    differences.sort()
    return {
        "worlds":16,"paired_world_groups":8,
        "candidate_total_first_held_correct":sum(w["arms"][candidate]["first_held_correct"]
                                                 for w in byseed.values()),
        "independent_gf2_total_first_held_correct":sum(w["arms"][informed]["first_held_correct"]
                                                     for w in byseed.values()),
        "candidate_minus_strongest_matched_control":sum(
            w["arms"][candidate]["first_held_correct"]-
            w["arms"][informed]["first_held_correct"] for w in byseed.values()),
        "paired_resampled_95_interval":[differences[249],differences[9749]],
        "draws":10000,"seed":2121,
        "scientific_pass":False
    }


def run():
    source_sha=os.environ.get("FKP21_SOURCE_SHA","")
    if len(source_sha)!=40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("FKP21_UNPINNED_SOURCE_SHA")
    start=time.perf_counter()
    byseed={}
    for seed in source.TRAIN:
        perarm={name:_do_world(seed,name) for name in ARMS}
        if len({item["observed_train_sha256"] for item in perarm.values()})!=1:
            raise AssertionError("FKP21_ARMS_DID_NOT_SEE_SAME_PHYSICAL_DATA")
        byseed[seed]={
            "seed":seed,
            "class":"LOW_COMPLEXITY" if seed-source.TRAIN[0]<8 else "ADVERSARIAL_EXTENSION",
            "arms":perarm
        }
    candidate=ARMS[0]
    informed="INDEPENDENT_GF2_ELIMINATION"
    pairs=[]
    for i in range(8):
        low=byseed[source.TRAIN[i]]
        high=byseed[source.TRAIN[i+8]]
        if low["arms"][candidate]["observed_train_sha256"]!=(
                high["arms"][candidate]["observed_train_sha256"]):
            raise AssertionError("FKP21_PAIRED_WORLD_TRAIN_TRANSCRIPTS_NOT_IDENTICAL")
        for name in ARMS:
            if low["arms"][name]["trained_model_receipt"]!=high["arms"][name]["trained_model_receipt"]:
                raise AssertionError("FKP21_SAME_DATA_DIFFERENT_TRAINED_POLICY")
        outcomes_low=[v[2] for v in low["arms"][candidate]["first_held_predictions"]]
        outcomes_high=[v[2] for v in high["arms"][candidate]["first_held_predictions"]]
        if sum(a!=b for a,b in zip(outcomes_low,outcomes_high))!=1:
            raise AssertionError("FKP21_SOURCE_FROZEN_ONE_HIDDEN_CONTRADICTION_DRIFT")
        if [v[1] for v in low["arms"][candidate]["first_held_predictions"]] != (
                [v[1] for v in high["arms"][candidate]["first_held_predictions"]]):
            raise AssertionError("FKP21_UNEARNED_HIDDEN_LAW_SIDE_CHANNEL")
        pairs.append({"pair_id":i,"low_seed":low["seed"],"high_seed":high["seed"],
                      "identical_training_sha256":low["arms"][candidate]["observed_train_sha256"],
                      "distinct_first_held_labels":1,
                      "identical_first_held_predictions":True})
    summary={}
    for name in ARMS:
        data=[w["arms"][name] for w in byseed.values()]
        summary[name]={
            "low_family_first_held_correct":sum(x["first_held_correct"] for x in data[:8]),
            "adversarial_first_held_correct":sum(x["first_held_correct"] for x in data[8:]),
            "total_first_held_correct":sum(x["first_held_correct"] for x in data),
            "total_unseen_abstained":sum(x["first_held_abstain"] for x in data),
            "cold_direct_feedback_recall_correct":sum(x["cold_direct_recall_correct"] for x in data),
            "max_model_logical_bytes":max(x["learned_logical_bytes"] for x in data),
            "total_fit_wall_seconds":sum(x["fit_wall_seconds"] for x in data),
            "total_first_probe_wall_seconds":sum(x["first_score_wall_seconds"] for x in data)
        }
    if summary[candidate]["low_family_first_held_correct"]!=32 or (
        summary[candidate]["adversarial_first_held_correct"]!=24):
        raise AssertionError("FKP21_FIRST_OBSERVATION_MATH_RESULT_DRIFT")
    if summary[informed]["total_first_held_correct"]!=summary[candidate]["total_first_held_correct"]:
        raise AssertionError("FKP21_INDEPENDENT_EXACT_SOLVER_NOT_MATCHED")
    if summary[candidate]["cold_direct_feedback_recall_correct"]!=64:
        raise AssertionError("FKP21_REPAIR_NOT_PERSISTENT_AFTER_COLD")
    if any(rec["max_model_logical_bytes"]>65536 for rec in summary.values()):
        raise AssertionError("FKP21_CAPACITY_LIMIT")
    paired=_paired_bootstrap(byseed)
    return {
        "schema":"fkp21.public-rule-first-probe-cold-feedback.v1",
        "classification":"CONSTRUCTIVE_KNOWN_TRAIN_IDENTIFIABILITY_AND_FEEDBACK_ONLY",
        "source_sha":source_sha,"prereg_first":PREREG_FIRST,
        "worlds":16,"paired_world_groups":8,
        "train_patterns":list(source.TRAIN_PATTERNS),
        "first_unseen_patterns":list(source.FIRST_PROBES),
        "source_physically_selected_actions":16*len(ARMS)*(12+4)*4,
        "first_probe_actual_public_returns_only":True,
        "source_not_independent_hidden_evaluator":True,
        "by_world":list(byseed.values()),
        "paired_identifiability":pairs,
        "per_arm":summary,
        "paired_bootstrap":paired,
        "process_wall_seconds":time.perf_counter()-start,
        "protected_source_first_use":False,
        "fkp20_protected_opened":False,
        "science_unfamiliar_transfer_run":False,
        "scientific_pass":False,
        "native_accepted_changed":False
    }


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-json",required=True)
    args=ap.parse_args()
    r=run()
    target=Path(args.output_json)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    summary={k:r[k] for k in (
        "schema","classification","source_sha","worlds","paired_world_groups",
        "source_physically_selected_actions","per_arm","paired_bootstrap",
        "process_wall_seconds","protected_source_first_use",
        "science_unfamiliar_transfer_run","scientific_pass","native_accepted_changed")}
    print("FKP21_CONSTRUCTIVE_REAL_FEEDBACK="+json.dumps(summary,
          sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
