"""AAI-08B: preregistered sparse A-return vs B-stays paired counterfactual.

DO NOT RUN SCIENTIFIC FIRST USE without separate owner authorization.
No native Yggdrasil integration; independent official NS-Gym Bridge only.
Registered protocol SHA: da868ed0438a2407a6523f5a8ac3040df892a350.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time

import gymnasium as gym
import ns_gym
import numpy as np
from ns_gym.schedulers import DiscreteScheduler
from ns_gym.update_functions import DistributionStepWiseUpdate
from ns_gym.wrappers import NSBridgeWrapper

from models import (NAMES,MATCHED,RegimeCache,create,cloned,shared_update,
                    snapshot,a_origin_marker)

PREREG="da868ed0438a2407a6523f5a8ac3040df892a350"
UPSTREAM="127df4b714fe4fcf680721d8e9278a96090acd7e"
DEV=range(894000,894016)
TRANSFER=range(895000,895064)
NEGATIVE=range(896000,896032)
MECHANICAL=range(899000,899004)
BUDGETS=(0,1,2,4,8)
TRAIN_EPISODES=24
BOOTSTRAP=1024
BOOTSTRAP_SEED=28081
ACTIONS=(2,0,2)
INITIAL=[1.,0.,0.]
LAWS={
    "dev":{"A":[.72,.18,.10],"B":[.18,.72,.10]},
    "transfer":{"A":[.63,.23,.14],"B":[.23,.63,.14]},
}
SCENARIOS=("return_A","hold_B")


def stable_seed(*parts):
    value=hashlib.sha256(":".join(str(x) for x in parts).encode()).digest()
    return int.from_bytes(value[:8],"big")%(2**32)


def equal_rng(a,b):
    return a[0]==b[0] and np.array_equal(a[1],b[1]) and a[2:]==b[2:]


def official_episode(law, seed, decision):
    """Single unmodified official upstream NS-Gym action-consequence episode."""
    saved=np.random.get_state()
    env=None
    started=time.perf_counter()
    try:
        np.random.seed(seed)
        env=NSBridgeWrapper(
            gym.make("ns_gym/Bridge-v0"),
            tunable_params={"P":DistributionStepWiseUpdate(
                DiscreteScheduler({3}),[list(law)])},
            initial_prob_dist=list(INITIAL),
            change_notification=False,
            delta_change_notification=False,
            scalar_reward=True,
            persistent_params=False,
        )
        obs,_discard_info=env.reset(seed=seed)
        assert int(obs["state"])>=0
        for i,action in enumerate(ACTIONS):
            obs,reward,ended,truncated,_discard_info=env.step(action)
            assert not (ended or truncated),(seed,i)
            assert float(reward)==0
            assert obs["env_change"]["P"]==0
            assert obs["delta_change"]["P"]==0
        prior=int(obs["state"])
        assert decision in (2,3) and env.action_space.contains(decision)
        obs,reward,ended,truncated,_discard_info=env.step(decision)
        assert obs["env_change"]["P"]==0
        assert obs["delta_change"]["P"]==0
        assert int(obs["relative_time"])==4
        assert float(reward) in (-1.,0.,1.)
        return {
            "action":int(decision),
            "previous_state":prior,
            "next_state":int(obs["state"]),
            "forward":bool(decision==2 and int(obs["state"])==prior+1),
            "reward":float(reward),
            "terminal":bool(ended or truncated),
            "safe":bool(float(reward)>=0),
            "episode_seconds":time.perf_counter()-started,
        }
    finally:
        if env is not None:
            env.close()
        np.random.set_state(saved)
        assert equal_rng(saved,np.random.get_state())


def update(models, observed_forward, costs):
    for name,model in models.items():
        t=time.perf_counter()
        model.learn(observed_forward)
        costs[name]+=time.perf_counter()-t


def prehistory(world,laws):
    models={name:create(name,laws["A"][0],laws["B"][0]) for name in NAMES}
    costs={name:0.0 for name in NAMES}
    data=[]
    after_a=None
    marker=None
    for phase,law_name in enumerate(("A","B")):
        for i in range(TRAIN_EPISODES):
            sample=official_episode(laws[law_name],stable_seed(world,"prehistory",phase,i),2)
            update(models,sample["forward"],costs)
            data.append({"action":sample["action"],
                         "forward":sample["forward"],
                         "previous_state":sample["previous_state"],
                         "next_state":sample["next_state"],
                         "reward":sample["reward"]})
        if phase==0:
            after_a=snapshot(models)
            marker=a_origin_marker(models["candidate"])
    after_b=snapshot(models)
    assert len(data)==48
    for name in NAMES:
        original=after_b[name]
        assert snapshot({name:cloned({name:original})[name]})[name]==original
    return after_a,after_b,marker,data,costs


def compare_models(models, law, world, budget):
    """Final official reward, paired RNG seed; no model updates on heldout outcome."""
    decisions={}
    rewards={}
    safe={}
    actions={}
    costs={}
    for name,model in models.items():
        t=time.perf_counter()
        decision=model.choose()
        costs[name]=time.perf_counter()-t
        assert decision in (2,3)
        decisions[name]=decision
        sample=official_episode(law,stable_seed(world,"heldout",budget),decision)
        rewards[name]=sample["reward"]
        safe[name]=sample["safe"]
        actions[name]=sample["action"]
    return decisions,rewards,safe,costs


def run_fork(world,laws,after_b,a_marker,condition,budget):
    assert condition in SCENARIOS and budget in BUDGETS
    law=laws["A"] if condition=="return_A" else laws["B"]
    models=cloned(after_b)
    costs={name:0.0 for name in NAMES}
    challenge_data=[]
    for i in range(budget):
        sample=official_episode(law,stable_seed(world,"challenge",condition,i),2)
        update(models,sample["forward"],costs)
        challenge_data.append({"action":2,
                               "forward":sample["forward"],
                               "reward":sample["reward"],
                               "previous_state":sample["previous_state"],
                               "next_state":sample["next_state"]})
    candidate=models["candidate"]
    # Origin marker is a frozen view of the A-learned hypothesis at end-A.
    checkpoint=cloned(after_b)["candidate"]
    preserved_after_b=(
        len(checkpoint.slots)>=2 and
        a_marker["index"]<len(checkpoint.slots) and
        list(checkpoint.slots[a_marker["index"]].state())==a_marker["counts"]
    )
    old_a_retrieved=preserved_after_b and candidate.active==a_marker["index"]
    decisions,rewards,safe,decision_times=compare_models(models,law,world,budget)
    for name in NAMES:
        costs[name]+=decision_times[name]
    records={
        "condition":condition,
        "budget":budget,
        "observed":challenge_data,
        "decisions":decisions,
        "rewards":rewards,
        "safe":safe,
        "correct_decision":2 if condition=="return_A" else 3,
        "candidate_slots":[s.state() for s in candidate.slots],
        "candidate_active":candidate.active,
        "candidate_pending":list(candidate.pending),
        "old_A_preserved_after_B":bool(preserved_after_b),
        "old_A_origin_retrieved":bool(old_a_retrieved),
        "serialized_bytes":{name:len(json.dumps(model.state(),sort_keys=True,
                                separators=(",",":")).encode()) for name,model in models.items()},
        "learner_seconds":costs,
    }
    return records


def one_world(world,laws):
    started=time.perf_counter()
    after_a,after_b,marker,history,pre_costs=prehistory(world,laws)
    forks={}
    for budget in BUDGETS:
        for condition in SCENARIOS:
            k=condition+":"+str(budget)
            forks[k]=run_fork(world,laws,after_b,marker,condition,budget)
        if budget==0:
            assert forks["return_A:0"]["decisions"]==forks["hold_B:0"]["decisions"],(
                "No-probe counterfactual must have indistinguishable learner data"
            )
    return {
        "world":world,
        "prehistory":history,
        "after_A_candidate":json.loads(after_a["candidate"]),
        "after_B_candidate":json.loads(after_b["candidate"]),
        "A_origin_marker":marker,
        "prehistory_learner_seconds":pre_costs,
        "forks":forks,
        "whole_process_seconds":time.perf_counter()-started,
    }


def per_world_reward(worlds,name,condition,budgets):
    return [
        sum(world["forks"][condition+":"+str(b)]["rewards"][name] for b in budgets)/len(budgets)
        for world in worlds
    ]


def paired_ci(xs,ys,seed=BOOTSTRAP_SEED):
    assert len(xs)==len(ys)>0
    diffs=[a-b for a,b in zip(xs,ys)]
    randomizer=random.Random(seed)
    n=len(diffs)
    samples=sorted(
        sum(diffs[randomizer.randrange(n)] for _ in range(n))/n
        for _ in range(BOOTSTRAP)
    )
    return [round(samples[25],8),round(samples[998],8)]


def record_metrics(worlds):
    output={}
    for condition in SCENARIOS:
        output[condition]={}
        for budget in BUDGETS:
            cases=[w["forks"][condition+":"+str(budget)] for w in worlds]
            output[condition][str(budget)]={
                name:{
                    "mean_reward":round(sum(c["rewards"][name] for c in cases)/len(cases),8),
                    "decision_accuracy":round(sum(c["decisions"][name]==c["correct_decision"]
                                                    for c in cases)/len(cases),8),
                    "safe_fraction":round(sum(c["safe"][name] for c in cases)/len(cases),8),
                    "learner_seconds_per_world":round(
                        sum(c["learner_seconds"][name] for c in cases)/len(cases),8),
                    "mean_serialized_bytes":round(
                        sum(c["serialized_bytes"][name] for c in cases)/len(cases),2),
                } for name in NAMES
            }
            output[condition][str(budget)]["candidate_slot_diagnostic"]={
                "two_slots":sum(len(c["candidate_slots"])==2 for c in cases),
                "old_A_preserved_after_B":sum(c["old_A_preserved_after_B"] for c in cases),
                "old_A_origin_retrieved":sum(c["old_A_origin_retrieved"] for c in cases),
            }
    return output


def negative_control(laws):
    results=[]
    for world in NEGATIVE:
        after_a,after_b,_marker,history,_costs=prehistory(world,laws)
        law=laws["A"]
        challenge=[]
        for i in range(4):
            challenge.append(official_episode(law,stable_seed(world,"negative_challenge",i),2)["forward"])
        proper=cloned(after_b)["candidate"]
        for event in challenge:
            proper.learn(event)
        labels=[h["forward"] for h in history]+challenge
        random.Random(stable_seed(world,"label_shuffle",28081)).shuffle(labels)
        shuffled=RegimeCache(2)
        for event in labels:
            shuffled.learn(event)
        result={}
        for name,model in (("proper",proper),("shuffled",shuffled)):
            action=model.choose()
            sample=official_episode(law,stable_seed(world,"negative_heldout"),action)
            result[name]={"reward":sample["reward"],"action":action}
        results.append({"world":world,"paired":result})
    proper=[x["paired"]["proper"]["reward"] for x in results]
    scrambled=[x["paired"]["shuffled"]["reward"] for x in results]
    return results,{
        "n":len(results),
        "proper_minus_shuffled":round(sum(a-b for a,b in zip(proper,scrambled))/len(results),8),
        "paired_ci_95":paired_ci(proper,scrambled),
    }


def only_mechanical():
    """Reserved seeds ONLY, with real official transition effects; no science data."""
    tests=[]
    law=LAWS["dev"]
    for seed in MECHANICAL:
        a=official_episode(law["A"],stable_seed(seed,"mechanical"),2)
        b=official_episode(law["B"],stable_seed(seed,"mechanical"),2)
        a2=official_episode(law["A"],stable_seed(seed,"mechanical"),2)
        assert a["forward"]==a2["forward"] and a["reward"]==a2["reward"]
        tests.append({"seed":seed,"A_forward":a["forward"],"B_forward":b["forward"],
                      "A_reward":a["reward"],"B_reward":b["reward"]})
    source=json.dumps(tests,sort_keys=True,separators=(",",":")).encode()
    return {
        "phase":"MECHANICAL_ONLY",
        "scientific_first_use":False,
        "upstream_sha":UPSTREAM,
        "reserved_samples":len(tests),
        "source_trace_sha256":hashlib.sha256(source).hexdigest(),
        "events":tests,
    }


def primary():
    start=time.perf_counter()
    assert len(DEV)==16 and len(TRANSFER)==64 and len(NEGATIVE)==32
    assert len(MECHANICAL)==4 and BUDGETS==(0,1,2,4,8)
    assert set(DEV).isdisjoint(TRANSFER)
    assert set(TRANSFER).isdisjoint(NEGATIVE)
    dev=[one_world(w,LAWS["dev"]) for w in DEV]
    transfer=[one_world(w,LAWS["transfer"]) for w in TRANSFER]
    neg,negative=negative_control(LAWS["transfer"])
    dmetrics=record_metrics(dev)
    tmetrics=record_metrics(transfer)
    key_budgets=(2,4)
    return_scores={name:per_world_reward(transfer,name,"return_A",key_budgets)
                   for name in NAMES}
    hold_scores={name:per_world_reward(transfer,name,"hold_B",key_budgets)
                 for name in NAMES}
    strongest=max(MATCHED,key=lambda name:sum(return_scores[name])/len(return_scores[name]))
    def avg(xs):
        return sum(xs)/len(xs)
    reward_delta=avg(return_scores["candidate"])-avg(return_scores[strongest])
    hold_delta=avg(hold_scores["candidate"])-avg(hold_scores[strongest])
    ablated_delta=avg(return_scores["candidate"])-avg(return_scores["one_slot"])
    return_cases=[w["forks"]["return_A:"+str(b)] for w in transfer for b in key_budgets]
    return_accuracy=sum(x["decisions"]["candidate"]==2 for x in return_cases)/len(return_cases)
    retrieved=sum(x["old_A_origin_retrieved"] for x in return_cases)/len(return_cases)
    score_ci=paired_ci(return_scores["candidate"],return_scores[strongest])
    ablation_ci=paired_ci(return_scores["candidate"],return_scores["one_slot"])
    candidate_update=sum(c["learner_seconds"]["candidate"] for c in return_cases)/len(return_cases)
    fast_cost=min(sum(c["learner_seconds"][k] for c in return_cases)/len(return_cases) for k in MATCHED)
    cost_ratio=candidate_update/max(1e-10,fast_cost)
    zero_data=all(w["forks"]["return_A:0"]["decisions"]==
                  w["forks"]["hold_B:0"]["decisions"] for w in transfer)
    # The oracle may have information about the A/B distribution absent to
    # matched controls; it is only a benchmark-headroom control.
    oracle_return_improvement=max(
        tmetrics["return_A"][str(b)]["oracle"]["mean_reward"]-
        tmetrics["return_A"]["0"]["oracle"]["mean_reward"]
        for b in (2,4)
    )
    oracle_hold_loss=max(
        tmetrics["hold_B"]["0"]["oracle"]["mean_reward"]-
        tmetrics["hold_B"][str(b)]["oracle"]["mean_reward"]
        for b in (2,4)
    )
    admission=oracle_return_improvement>=.08 and oracle_hold_loss<=.03
    tests={
        "benchmark_headroom":admission,
        "candidate_over_strongest":reward_delta>=.04 and score_ci[0]>0,
        "hold_B_non_degradation":hold_delta>=-.02,
        "return_A_action_accuracy":return_accuracy>=.80,
        "intact_historical_A_retrieved":retrieved>=.60,
        "candidate_over_one_slot":ablated_delta>=.04 and ablation_ci[0]>0,
        "shuffled_negative":negative["proper_minus_shuffled"]>=.10,
        "zero_probe_no_information":zero_data,
        "learner_compute":cost_ratio<=2.,
        "cold_forks_exact":True,
    }
    if not admission:
        classification="HEADROOM_INADEQUATE_NO_PROMOTION"
    elif all(tests.values()):
        classification="SCIENTIFIC_CANDIDATE_UNQUALIFIED"
    else:
        classification="VALID_NEGATIVE_NO_INTEGRATION"
    records={"dev":dev,"transfer":transfer,"negative":neg}
    # Exclude microsecond timings from deterministic scientific receipt.
    def clean_timings(obj):
        if isinstance(obj,dict):
            return {k:clean_timings(v) for k,v in obj.items()
                    if k not in ("whole_process_seconds","prehistory_learner_seconds",
                                 "episode_seconds","learner_seconds")}
        if isinstance(obj,list):
            return [clean_timings(v) for v in obj]
        return obj
    worlds_sha=hashlib.sha256(json.dumps(clean_timings(records),sort_keys=True,
                                      separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"yggdrasil.contrib.aai08b.sparse-recurrence.v1",
        "prereg_commit":PREREG,
        "upstream_source_commit":UPSTREAM,
        "classification":classification,
        "strongest_matched_control":strongest,
        "dev":dmetrics,
        "transfer":tmetrics,
        "negative_control":negative,
        "primary_return_A_budget":[2,4],
        "primary_gains":{
            "candidate_minus_strongest":round(reward_delta,8),
            "candidate_minus_strongest_ci95":score_ci,
            "candidate_minus_one_slot":round(ablated_delta,8),
            "candidate_minus_one_slot_ci95":ablation_ci,
            "candidate_minus_strongest_hold_B":round(hold_delta,8),
            "return_A_candidate_accuracy":round(return_accuracy,8),
            "candidate_intact_A_retrieval_rate":round(retrieved,8),
            "candidate_to_fastest_model_time_ratio":round(cost_ratio,6),
            "oracle_return_improvement":round(oracle_return_improvement,8),
            "oracle_hold_loss":round(oracle_hold_loss,8),
        },
        "checks":tests,
        "raw_worlds_sha256":worlds_sha,
        "world_records":records,
        "whole_process_seconds":round(time.perf_counter()-start,6),
        "science_limits":"Official NS-Gym external laws with public map and scripted probe action. RegimeCache is original conventional Beta model. Oracle sees extra likelihood priors. No native Yggdrasil weight/architecture science, no general intelligence evidence.",
        "integration":"NONE",
    }


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--mechanical",action="store_true")
    parser.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if args.mechanical==args.primary:
        parser.error("Choose exactly one --mechanical or --primary")
    if args.primary:
        parser.error("Scientific first-use disabled in this preparatory branch. Requires separate approved one-shot workflow.")
    print(json.dumps(only_mechanical(),sort_keys=True,indent=2))
