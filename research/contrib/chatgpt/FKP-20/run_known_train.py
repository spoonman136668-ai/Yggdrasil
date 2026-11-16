"""FKP-20 on-policy known-TRAIN-only multi-parent delayed-causality score.

Eight independent arms, identical 32 actually selected factorial exploration
episodes per public seed, then 16 separately selected real scored episodes.
Original held DEV/TRANSFER and all predecessor held seeds remain forbidden.
No source polarity/pair is passed to a model and no post-scoring retraining.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import time

import public_pair_source as source
import pair_credit as policies

ARMS=("SPARSE_CONTRADICTION_PAIRS","EXACT_VERSION_SPACE",
      "FULLY_FITTED_INTERACTION_LOGISTIC","UNARY_ONLY",
      "NO_CONTEXT","CURRENT_DISTRACTOR_ONLY",
      "TIME_PERMUTED_CREDIT","NO_UPDATE")
CONTROLS=("EXACT_VERSION_SPACE","FULLY_FITTED_INTERACTION_LOGISTIC")
PREREG_FIRST="70f636b34a9ca86b6371068e04c7b0c1368dd62b"


def _digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,allow_nan=False,
                            separators=(",",":")).encode("ascii")).hexdigest()


def _make(name):
    if name=="EXACT_VERSION_SPACE":
        return policies.ExactVersionSpace()
    if name=="FULLY_FITTED_INTERACTION_LOGISTIC":
        return policies.FullyFittedInteractionLogistic()
    return policies.SparsePairCredit(name)


def _real_actions(seed,episode,plan,distractor):
    if type(plan) not in (list,tuple) or len(plan)!=3 or any(
           type(x) is not int or x not in (0,1) for x in plan):
        raise ValueError("FKP20_INVALID_PRECOMMITTED_THREE_ACTION_PLAN")
    if type(distractor) is not int or distractor not in (0,1):
        raise ValueError("FKP20_INVALID_DISTRACTOR")
    s=source.SelectedPublicEpisode(seed,episode)
    ctx=source.context(seed,episode)
    if s.public_state[0]!=ctx or s.public_state[1]!=0:
        raise AssertionError("FKP20_PUBLIC_CONTEXT_DRIFT")
    actions=tuple(plan)+(distractor,)
    rows=[]
    for step,a in enumerate(actions):
        before=s.public_state
        row=s.apply(a) # physical action precedes feedback!
        if row.before!=before or row.action!=a:
            raise AssertionError("FKP20_OBSERVATION_NOT_SELECTED_ACTION")
        if step<3 and (row.reward!=0.0 or row.done):
            raise AssertionError("FKP20_PREMATURE_OUTCOME_LEAK")
        if step==3 and (not row.done or row.reward not in (-1.0,1.0)):
            raise AssertionError("FKP20_MISSING_TERMINAL_REWARD")
        rows.append(row)
    if not s.done:
        raise AssertionError("FKP20_INCOMPLETE_PHYSICAL_EPISODE")
    return tuple(rows)


def _mean(seq):
    if not seq or any(type(x) not in (int,float) or not math.isfinite(x) for x in seq):
        raise ValueError("FKP20_BAD_NUMERIC_RETURN")
    return sum(seq)/len(seq)


def matched_known_train_bootstrap(worlds):
    if tuple(worlds)!=source.TRAIN or any(set(d)!=set(ARMS) for d in worlds.values()):
        raise ValueError("FKP20_16_WORLD_ARM_LOCK")
    rows=list(worlds.values())
    means={name:_mean([r[name] for r in rows]) for name in ARMS}
    best=max(CONTROLS,key=lambda name:means[name])
    rng=random.Random(2020)
    diffs=[]
    for _ in range(10000):
        sample=[rows[rng.randrange(len(rows))] for __ in rows]
        lead=_mean([r["SPARSE_CONTRADICTION_PAIRS"] for r in sample])
        strong=max(_mean([r[name] for r in sample]) for name in CONTROLS)
        diffs.append(lead-strong)
    diffs.sort()
    return {
        "mean_actual_scored_reward_by_arm":means,
        "strongest_matched_conventional":best,
        "candidate_minus_strongest":means["SPARSE_CONTRADICTION_PAIRS"]-means[best],
        "paired_10000_world_resample_95_interval":[diffs[249],diffs[9749]],
        "bootstrap_seed":2020,
        "bootstrap_draws":10000,
        "known_source_family_only":True,
        "scientific_pass":False
    }


def run():
    original=os.environ.get("FKP20_SOURCE_SHA","")
    if len(original)!=40 or any(x not in "0123456789abcdef" for x in original):
        raise ValueError("FKP20_SOURCE_SHA_NOT_PINNED")
    start=time.perf_counter()
    start_cpu=time.process_time()
    cost={a:{"fit_wall_seconds":0.0,"score_wall_seconds":0.0,
             "max_logical_learned_bytes":0,"explore_public_actions":0,
             "score_public_actions":0} for a in ARMS}
    perworld=[]
    outcomes={}
    for seed in source.TRAIN:
        earned={}
        perarm={}
        for name in ARMS:
            learner=_make(name)
            t0=time.perf_counter()
            public_explore=[]
            for episode in range(source.EXPLORE):
                ctx,a0,a1,a2,d=source.exploration_tape(seed,episode)
                rows=_real_actions(seed,episode,(a0,a1,a2),d)
                if rows[0].before[0]!=ctx:
                    raise AssertionError("FKP20_EXPLORATION_CONTEXT_DRIFT")
                learner.observe_episode(rows,learn=True)
                public_explore.append((ctx,a0,a1,a2,d,rows[-1].reward))
            learner.freeze()
            if isinstance(learner,policies.SparsePairCredit):
                if learner.observed_episodes!=32:
                    raise AssertionError("FKP20_CANDIDATE_INCOMPLETE_EXPLORATION")
                before=learner.state_receipt()
                cold=policies.SparsePairCredit.restore(learner.checkpoint())
                if cold.state_receipt()!=before:
                    raise AssertionError("FKP20_COLD_CHECKPOINT_MISMATCH")
                learner=cold
            else:
                before=learner.state_receipt()
            info={
                "explore_public_sha256":_digest(public_explore),
                "frozen_learned_state_sha256":before,
                "logical_learned_bytes":learner.learned_logical_bytes,
            }
            if learner.learned_logical_bytes>65536:
                raise AssertionError("FKP20_MEMORY_BUDGET_EXCEEDED")
            if name=="SPARSE_CONTRADICTION_PAIRS":
                if learner.inferred_pair() is None or not learner._allocated_pairs():
                    raise AssertionError("FKP20_NO_CONTRADICTION_BASED_PAIR")
                info["inferred_temporal_parent_pair"]=list(learner.inferred_pair()[0])
                info["learned_interaction_slots"]=len(learner._allocated_pairs())
            if name=="EXACT_VERSION_SPACE":
                info["version_space_one_hypothesis"]=True
            if name=="FULLY_FITTED_INTERACTION_LOGISTIC":
                if learner.train_bce is None or learner.train_bce>0.05:
                    raise AssertionError("FKP20_CONVENTIONAL_INCOMPLETE_FIT")
                info["fully_fit_epochs"]=learner.fit_epochs
                info["fully_fit_bce"]=learner.train_bce
            cost[name]["fit_wall_seconds"]+=time.perf_counter()-t0
            cost[name]["max_logical_learned_bytes"]=max(
                cost[name]["max_logical_learned_bytes"],learner.learned_logical_bytes)
            cost[name]["explore_public_actions"]+=source.EXPLORE*4
            t1=time.perf_counter()
            total=0
            actual=[]
            for episode in range(source.EXPLORE,source.TOTAL):
                ctx=source.context(seed,episode)
                plan=learner.choose_plan(ctx)
                d=source.scored_distractor(seed,episode)
                rows=_real_actions(seed,episode,plan,d)
                learner.observe_episode(rows,learn=False)
                total+=rows[-1].reward
                actual.append((ctx,list(plan),d,rows[-1].reward))
            if learner.state_receipt()!=before:
                raise AssertionError("FKP20_SCORING_UPDATED_PARAMETERS")
            cost[name]["score_wall_seconds"]+=time.perf_counter()-t1
            cost[name]["score_public_actions"]+=source.SCORE*4
            earned[name]=total
            info["scored_real_actions_sha256"]=_digest(actual)
            perarm[name]=info
        if len({perarm[a]["explore_public_sha256"] for a in ARMS})!=1:
            raise AssertionError("FKP20_DIFFERENT_FACTS_OR_ACTIONS_BETWEEN_ARMS")
        outcomes[seed]=earned
        perworld.append({"seed":seed,"actual_public_reward":earned,
                         "exploration_tape_sha256":perarm[ARMS[0]]["explore_public_sha256"],
                         "arms":perarm})
    paired=matched_known_train_bootstrap(outcomes)
    return {
        "schema":"fkp20.public-multiparent-known-train.v1",
        "classification":"REAL_MULTI_PARENT_PUBLIC_TRAIN_ONLY",
        "source_sha":original,
        "prereg_first_commit":PREREG_FIRST,
        "world_count":len(source.TRAIN),
        "train_seed_min":source.TRAIN[0],
        "train_seed_max":source.TRAIN[-1],
        "full_factorial_explore_episodes_per_arm_world":32,
        "score_episodes_per_arm_world":16,
        "physical_public_actions":len(source.TRAIN)*len(ARMS)*source.TOTAL*4,
        "methods":list(ARMS),
        "paired_bootstrap":paired,
        "per_world":perworld,
        "per_arm_cost":cost,
        "total_wall_seconds":time.perf_counter()-start,
        "total_cpu_seconds":time.process_time()-start_cpu,
        "new_held_first_use":False,
        "original_fkp17_held_opened":False,
        "fkp19_held_opened":False,
        "native_accepted_changed":False,
        "scientific_pass":False
    }


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-json",required=True)
    args=parser.parse_args()
    result=run()
    output=Path(args.output_json)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    info={k:result[k] for k in (
        "classification","source_sha","world_count","physical_public_actions",
        "paired_bootstrap","total_wall_seconds","total_cpu_seconds",
        "new_held_first_use","original_fkp17_held_opened",
        "fkp19_held_opened","native_accepted_changed","scientific_pass")}
    print("FKP20_REAL_PUBLIC_TRAIN_MULTIPARENT="+json.dumps(
        info,sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
