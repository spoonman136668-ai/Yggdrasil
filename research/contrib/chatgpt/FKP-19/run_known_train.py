"""FKP-19 known-TRAIN-only real delayed-action diagnostic with strong controls.

No held DEV/TRANSFER. All seven policies independently experience the same
eight physically applied two-step interventions in each world before choosing
sixteen scored early actions. The reward at t+1 is revealed after the later
action is applied. Actual independent source returns, not model predictions,
determine the result. The conventional interaction logistic is fully fitted
from exactly the shared exploration data, not privileged world knowledge.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import time

import lag_credit as methods
import public_delayed_source as source

ARMS=("ELIGIBILITY_CONTRAST","EXACT_BAYES_CONTEXT",
      "FULLY_FITTED_INTERACTION_LOGISTIC","CURRENT_ACTION_ONLY",
      "CONTEXT_BLIND","EARLY_ACTION_SHUFFLED","NO_UPDATE")
INFORMED=("EXACT_BAYES_CONTEXT","FULLY_FITTED_INTERACTION_LOGISTIC")
SHAM=("CURRENT_ACTION_ONLY","CONTEXT_BLIND","EARLY_ACTION_SHUFFLED","NO_UPDATE")
EXPECTED_PREG_SHA="42642b3834a804a7a866a3de8b79790dc669ef20"


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _make_arm(name):
    if name=="EXACT_BAYES_CONTEXT":
        return methods.ExactBayesContext()
    if name=="FULLY_FITTED_INTERACTION_LOGISTIC":
        return methods.FullyFittedInteractionLogistic()
    return methods.SparseLagCredit(name)


def _public_episode(seed,ep,early,late):
    s=source.PublicDelayedSession(seed,ep)
    if s.public_state[0]!=source.context_at(seed,ep) or s.public_state[1]!=0:
        raise AssertionError("FKP19_PUBLIC_START_STATE_DRIFT")
    if type(early) is not int or early not in (0,1) or type(late) is not int or late not in (0,1):
        raise ValueError("FKP19_ACTION_INVALID")
    first=s.apply(early)  # action selected before result
    if first.reward!=0.0 or first.done or s.done:
        raise AssertionError("FKP19_EARLY_FEEDBACK_LEAK")
    second=s.apply(late)  # chosen distractor precedes delayed feedback
    if not second.done or not s.done or second.history[-1].action!=early:
        raise AssertionError("FKP19_MISSING_SELECTED_ACTION_HISTORY")
    return first,second


def _mean(values):
    if not values:
        raise ValueError("FKP19_NO_WORLDS")
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in values):
        raise ValueError("FKP19_NONFINITE_SOURCE_REWARD")
    return sum(values)/len(values)


def paired_known_train_bootstrap(rewards):
    if tuple(rewards)!=source.TRAIN or any(set(row)!=set(ARMS)
                 for row in rewards.values()):
        raise ValueError("FKP19_WORLD_OR_ARM_MISMATCH")
    rows=list(rewards.values())
    avg={a:_mean([row[a] for row in rows]) for a in ARMS}
    strongest=max(INFORMED,key=lambda a:avg[a])
    rng=random.Random(1919)
    differences=[]
    for _ in range(10000):
        sample=[rows[rng.randrange(len(rows))] for j in rows]
        c=_mean([r["ELIGIBILITY_CONTRAST"] for r in sample])
        b=max(_mean([r[a] for r in sample]) for a in INFORMED)
        differences.append(c-b)
    differences.sort()
    return {"means":avg,"strongest_informed":strongest,
            "candidate_minus_strongest":avg["ELIGIBILITY_CONTRAST"]-avg[strongest],
            "resampled_strongest_95_interval":[differences[249],differences[9749]],
            "bootstrap_seed":1919,"bootstrap_draws":10000,
            "known_family_only":True,"scientific_pass":False}


def run_public_train():
    pinned=os.getenv("FKP19_SOURCE_SHA","")
    if len(pinned)!=40 or any(ch not in "0123456789abcdef" for ch in pinned):
        raise ValueError("FKP19_UNPINNED_EXACT_SOURCE")
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    perworld=[]
    rewards={}
    cost={arm:{"fit_wall_seconds":0.0,"score_wall_seconds":0.0,
               "learned_logical_bytes_max":0,"train_actions":0,
               "scored_actions":0} for arm in ARMS}
    for seed in source.TRAIN:
        row={}
        recordings={}
        for name in ARMS:
            arm=_make_arm(name)
            t0=time.perf_counter()
            explored=[]
            for ep in range(source.TRAIN_EPISODES):
                early,late=source.exploratory_actions(seed,ep)
                observed=_public_episode(seed,ep,early,late)
                arm.observe_episode(observed,learn=True)
                ctx=source.context_at(seed,ep)
                explored.append([ctx,early,late,observed[0].reward,
                                 observed[1].reward])
            if isinstance(arm,methods.FullyFittedInteractionLogistic):
                arm.fit_after_exploration()
                if arm.training_bce>0.05 or arm.fit_epochs>1024:
                    raise AssertionError("FKP19_CONVENTIONAL_NOT_FULLY_FIT")
            if isinstance(arm,methods.SparseLagCredit):
                if arm.explored_episodes!=8:
                    raise AssertionError("FKP19_SPARSE_EVIDENCE_SHORT")
                if name=="ELIGIBILITY_CONTRAST" and (
                        arm.inferred_reward_cause_lag(0)!=1 or
                        arm.inferred_reward_cause_lag(1)!=1):
                    raise AssertionError("FKP19_CANDIDATE_DID_NOT_INFER_DELAYED_CAUSE")
                restored=methods.SparseLagCredit.restore(arm.checkpoint())
                if restored.state_receipt()!=arm.state_receipt():
                    raise AssertionError("FKP19_COLD_PUBLIC_LEARNER_MISMATCH")
            receipt=arm.state_receipt()
            learned=arm.learned_logical_bytes
            if learned>65536:
                raise AssertionError("FKP19_CAPACITY_EXCEEDED")
            cost[name]["fit_wall_seconds"]+=time.perf_counter()-t0
            cost[name]["learned_logical_bytes_max"]=max(cost[name]["learned_logical_bytes_max"],learned)
            cost[name]["train_actions"]+=2*source.TRAIN_EPISODES
            digest=sha256(_canonical(explored)).hexdigest()
            recordings[name]={"exploration_sha256":digest}
            t1=time.perf_counter()
            earned=0.0
            selected=[]
            for ep in range(source.TRAIN_EPISODES,source.TOTAL_EPISODES):
                ctx=source.context_at(seed,ep)
                selected_action=arm.choose_early(ctx)
                if type(selected_action) is not int or selected_action not in (0,1):
                    raise AssertionError("FKP19_INVALID_PREOUTCOME_CHOICE")
                distractor=source.scored_distractor(seed,ep)
                actual=_public_episode(seed,ep,selected_action,distractor)
                arm.observe_episode(actual,learn=False)
                earned+=actual[1].reward
                selected.append([ctx,selected_action,distractor,actual[1].reward])
            if arm.state_receipt()!=receipt:
                raise AssertionError("FKP19_SCORING_UPDATED_MODEL")
            cost[name]["score_wall_seconds"]+=time.perf_counter()-t1
            cost[name]["scored_actions"]+=2*source.SCORED_EPISODES
            row[name]=earned
            recordings[name]["selected_public_score_sha256"]=sha256(_canonical(selected)).hexdigest()
            recordings[name]["model_cold_state_sha256"]=receipt
            if isinstance(arm,methods.FullyFittedInteractionLogistic):
                recordings[name]["fully_fit_epochs"]=arm.fit_epochs
                recordings[name]["full_training_bce"]=arm.training_bce
        if len(set(recordings[a]["exploration_sha256"] for a in ARMS))!=1:
            raise AssertionError("FKP19_MISMATCHED_PUBLIC_ACTION_INFORMATION")
        rewards[seed]=row
        perworld.append({"seed":seed,"earned_public_reward":row,
                         "common_exploration_sha256":recordings[ARMS[0]]["exploration_sha256"],
                         "arms":recordings})
    score=paired_known_train_bootstrap(rewards)
    return {
        "schema":"fkp19.public-known-train-delayed-causal-credit.v1",
        "classification":"SOURCE_SAFE_KNOWN_TRAIN_DIAGNOSTIC_ONLY",
        "source_sha":pinned,"prereg_first_commit":EXPECTED_PREG_SHA,
        "world_count":len(source.TRAIN),"seed_min":min(source.TRAIN),
        "seed_max":max(source.TRAIN),"arms":list(ARMS),
        "exploration_episodes_per_arm_per_world":source.TRAIN_EPISODES,
        "scored_episodes_per_arm_per_world":source.SCORED_EPISODES,
        "source_physical_action_count":len(source.TRAIN)*len(ARMS)*2*source.TOTAL_EPISODES,
        "paired_bootstrap":score,"per_world":perworld,"cost_by_arm":cost,
        "total_wall_seconds":time.perf_counter()-start_wall,
        "total_cpu_seconds":time.process_time()-start_cpu,
        "fkp17_held_opened":False,"fkp19_dev_opened":False,
        "reserved_transfer_opened":False,"scientific_pass":False,
        "accepted_native_changed":False
    }


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-json",required=True)
    args=parser.parse_args()
    report=run_public_train()
    path=Path(args.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,allow_nan=False,indent=2)+"\n")
    print("FKP19_PUBLIC_KNOWN_TRAIN_DIAGNOSTIC="+json.dumps({
        "classification":report["classification"],
        "source_sha":report["source_sha"],
        "world_count":report["world_count"],
        "physical_actions":report["source_physical_action_count"],
        "paired_bootstrap":report["paired_bootstrap"],
        "total_wall_seconds":report["total_wall_seconds"],
        "total_cpu_seconds":report["total_cpu_seconds"],
        "fkp17_held_opened":False,"fkp19_dev_opened":False,
        "reserved_transfer_opened":False,"scientific_pass":False,
        "accepted_native_changed":False
    },sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
