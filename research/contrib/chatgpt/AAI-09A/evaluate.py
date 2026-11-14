"""AAI-09A frozen external NS-Gym causal-recurrence evaluator.

NO SCIENTIFIC FIRST USE FROM CLI. Reserved mechanical samples can be run
by pinned source workflow only; any future science first use requires distinct
explicit owner permission and an exact-blob-locked one-shot workflow.

Preregistered before source: d9e9f3f11d04cdcf99c5e5b1e0c7a5008e0c2026.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import (NAMES,MATCHED,KnownLawOracle,ProtectedBank,
                    create,checkpoint,cold_restore,origin_marker,
                    preserved_original,recalled_original,canonical)

PREREG="d9e9f3f11d04cdcf99c5e5b1e0c7a5008e0c2026"
UPSTREAM="127df4b714fe4fcf680721d8e9278a96090acd7e"
DEV=range(887000,887016)
TRANSFER=range(888000,888064)
NEGATIVE=range(889000,889032)
MECHANICAL=range(887950,887954)
BUDGETS=(0,1,2,4)
PRIMARY_BUDGETS=(2,4)
TRAIN_PER_REGIME=32
BOOTSTRAP_DRAWS=2048
BOOTSTRAP_SEED=39091
LAWS={
  "dev":{"A":(.94,.035,.025),"B":(.03,.49,.48)},
  "transfer":{"A":(.90,.06,.04),"B":(.05,.47,.48)},
}
CONDITIONS=("A_returns","B_continues")
ACTIONS={"RIGHT":2,"UP":3}
ONEHOT=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
MAP=("HHHHHHHH","FFFFFHHH","GFHFSFFG","FFFFFHHH","HHHHHHHH")

def seed_of(*parts):
    data=":".join(str(x) for x in parts).encode("utf8")
    return int.from_bytes(hashlib.sha256(data).digest()[:8],"big")%(2**32)

def official_episode(law,seed,action):
    """Real unmodified official NS-Gym action consequences; serial scoped RNG.

    Info including 'Ground Truth Env Change' is discarded without inspection.
    No planning_env/unwrapped/hidden law access by a model.
    """
    import gymnasium as gym
    import ns_gym
    import numpy as np
    from ns_gym.schedulers import DiscreteScheduler
    from ns_gym.update_functions import DistributionStepWiseUpdate
    from ns_gym.wrappers import NSBridgeWrapper
    saved=np.random.get_state()
    env=None
    started=time.perf_counter()
    try:
        np.random.seed(seed)
        env=NSBridgeWrapper(
            gym.make("ns_gym/Bridge-v0"),
            tunable_params={"P":DistributionStepWiseUpdate(
                DiscreteScheduler({3}),[list(law)])},
            initial_prob_dist=[1.,0.,0.],
            change_notification=False,
            delta_change_notification=False,
            scalar_reward=True,
            persistent_params=False)
        obs,_discarded_info=env.reset(seed=seed)
        assert int(obs["state"])==20
        for action_prefix,expected_state in ((2,21),(0,20),(2,21)):
            obs,reward,ended,truncated,_discarded_info=env.step(action_prefix)
            assert int(obs["state"])==expected_state
            assert float(reward)==0 and not ended and not truncated
            assert obs["env_change"]["P"]==0
            assert obs["delta_change"]["P"]==0
        assert action in (2,3)
        state_before=int(obs["state"])
        obs,reward,ended,truncated,_discarded_info=env.step(action)
        assert obs["env_change"]["P"]==0
        assert obs["delta_change"]["P"]==0
        assert int(obs["relative_time"])==4
        assert float(reward) in (-1.,0.,1.)
        state_after=int(obs["state"])
        return {
            "action":int(action),
            "before":state_before,"after":state_after,
            "forward":int(action)==2 and state_after==state_before+1,
            "reward":float(reward),
            "terminated":bool(ended or truncated),
            "elapsed_seconds":time.perf_counter()-started,
        }
    finally:
        if env is not None: env.close()
        np.random.set_state(saved)
        restored=np.random.get_state()
        assert saved[0]==restored[0] and np.array_equal(saved[1],restored[1]) and saved[2:]==restored[2:]

def public_evidence(observation):
    return {"before":observation["before"],"after":observation["after"],
            "action":observation["action"],"reward":observation["reward"],
            "forward":observation["forward"]}

def official_mechanical():
    """Only four preregistered reserved seeds, NEVER science splits."""
    rows=[]
    geometry={
        2:{"state":(22,13,29),"reward":(0.,-1.,-1.)},
        3:{"state":(13,20,22),"reward":(-1.,0.,0.)},
    }
    for seed in MECHANICAL:
        for action in ACTIONS.values():
            for idx,law in enumerate(ONEHOT):
                first=official_episode(law,seed,action)
                second=official_episode(law,seed,action)
                assert first["after"]==second["after"]
                assert first["reward"]==second["reward"]
                assert first["before"]==21
                assert first["after"]==geometry[action]["state"][idx],(seed,action,idx,first)
                assert first["reward"]==geometry[action]["reward"][idx],(seed,action,idx,first)
                assert first["terminated"]==(first["reward"]!=0.)
                rows.append({"seed":seed,"action":action,"slip_index":idx,
                             "state":first["after"],"reward":first["reward"],
                             "terminated":first["terminated"]})
    receipt=hashlib.sha256((canonical(rows)+"\n").encode()).hexdigest()
    return {"phase":"MECHANICAL_ONLY","worlds":len(MECHANICAL),"actual_cases":len(rows),
            "source_sha":UPSTREAM,"first_use":False,
            "public_official_trace_sha256":receipt,"records":rows}

def update_all(models,observation,costs):
    for name,m in models.items():
        before=time.perf_counter()
        m.learn(observation)
        costs[name]+=time.perf_counter()-before

def prehistory(world,laws):
    models={name:create(name) for name in NAMES}
    costs={name:0. for name in NAMES}
    record=[]
    after_A=None
    A_marker=None
    for phase in ("A","B"):
        for i in range(TRAIN_PER_REGIME):
            obs=official_episode(laws[phase],seed_of(world,"train",phase,i),2)
            update_all(models,obs["forward"],costs)
            record.append({"phase_for_evaluator_only":phase,
                           "record":public_evidence(obs)})
        if phase=="A":
            after_A=checkpoint(models)
            A_marker=origin_marker(models["candidate"])
    after_B=checkpoint(models)
    assert len(record)==64 and len(after_B)==len(NAMES)
    for name,snapshot in after_B.items():
        assert checkpoint({name:cold_restore({name:snapshot})[name]})[name]==snapshot
    # The phase string in the returned record is evaluator metadata only.
    # Models received identical boolean action consequences, never the phase.
    return after_A,after_B,A_marker,record,costs

def one_branch(world,laws,after_B,marker,condition,budget):
    assert condition in CONDITIONS and budget in BUDGETS
    law=laws["A"] if condition=="A_returns" else laws["B"]
    models=cold_restore(after_B)
    initial_candidate=models["candidate"]
    intact_at_B=preserved_original(initial_candidate,marker)
    costs={name:0. for name in NAMES}
    challenge=[]
    oracle=KnownLawOracle(laws["A"][0],laws["B"][0],prior=.2)
    for i in range(budget):
        obs=official_episode(law,seed_of(world,"challenge",condition,i),2)
        update_all(models,obs["forward"],costs)
        oracle.learn(obs["forward"])
        challenge.append(public_evidence(obs))
    actions={}
    rewards={}
    predicted={}
    safe={}
    model_bytes={}
    for name,model in models.items():
        tick=time.perf_counter()
        action=model.choose()
        costs[name]+=time.perf_counter()-tick
        sample=official_episode(law,seed_of(world,"eval",condition,budget),action)
        actions[name]=action
        rewards[name]=sample["reward"]
        safe[name]=sample["reward"]>=0
        predicted[name]=model.prediction()
        model_bytes[name]=len(canonical(model.state()).encode())
    oracle_tick=time.perf_counter()
    oracle_action=oracle.choose()
    oracle_elapsed=time.perf_counter()-oracle_tick
    oracle_result=official_episode(law,seed_of(world,"eval",condition,budget),oracle_action)
    candidate=models["candidate"]
    return {
        "condition":condition,"budget":budget,
        "challenge":challenge,
        "actions":actions,"rewards":rewards,
        "safe":safe,"predicted":predicted,
        "expected_correct_action":2 if condition=="A_returns" else 3,
        "candidate_cores":candidate.state()["cores"],
        "candidate_active_id":candidate.active_id,
        "candidate_old_A_preserved_after_B":intact_at_B,
        "candidate_old_A_recalled":recalled_original(candidate,marker,intact_at_B),
        "candidate_retrieval_switches":candidate.retrievals,
        "model_time_seconds":costs,
        "model_serialized_bytes":model_bytes,
        "oracle":{"action":oracle_action,"reward":oracle_result["reward"],
                  "posterior_A":oracle.q,
                  "decision_seconds":oracle_elapsed},
    }

def one_world(world,laws):
    started=time.perf_counter()
    after_A,after_B,marker,train,pre_cost=prehistory(world,laws)
    results={}
    for budget in BUDGETS:
        results[f"A_returns:{budget}"]=one_branch(world,laws,after_B,marker,"A_returns",budget)
        results[f"B_continues:{budget}"]=one_branch(world,laws,after_B,marker,"B_continues",budget)
        if budget==0:
            a=results["A_returns:0"]
            b=results["B_continues:0"]
            assert a["actions"]==b["actions"]
            assert a["predicted"]==b["predicted"]
            assert a["oracle"]["action"]==b["oracle"]["action"]
    assert len(results)==8
    return {
        "world":world,"prehistory":train,
        "A_checkpoint_candidate":json.loads(after_A["candidate"]),
        "B_checkpoint_candidate":json.loads(after_B["candidate"]),
        "A_origin":marker,"prehistory_model_seconds":pre_cost,
        "forks":results,
        "whole_process_seconds":time.perf_counter()-started
    }

def mean(v):
    assert v
    return sum(v)/len(v)

def paired_bootstrap(xs,ys,seed=BOOTSTRAP_SEED):
    assert len(xs)==len(ys) and xs
    differences=[x-y for x,y in zip(xs,ys)]
    n=len(differences)
    engine=random.Random(seed)
    draws=sorted(mean([differences[engine.randrange(n)] for _ in range(n)])
                 for _ in range(BOOTSTRAP_DRAWS))
    return [round(draws[51],9),round(draws[1996],9)]

def world_means(worlds,method,condition,budgets=PRIMARY_BUDGETS):
    return [mean([w["forks"][f"{condition}:{budget}"]["rewards"][method]
                  if method!="oracle" else w["forks"][f"{condition}:{budget}"]["oracle"]["reward"]
                  for budget in budgets]) for w in worlds]

def summary(worlds):
    by_cond={}
    for condition in CONDITIONS:
        by_cond[condition]={}
        for budget in BUDGETS:
            cases=[w["forks"][f"{condition}:{budget}"] for w in worlds]
            by_cond[condition][str(budget)]={}
            for name in (*NAMES,"oracle"):
                actions=[c["actions"][name] if name!="oracle" else c["oracle"]["action"]
                         for c in cases]
                rewards=[c["rewards"][name] if name!="oracle" else c["oracle"]["reward"]
                         for c in cases]
                by_cond[condition][str(budget)][name]={
                    "mean_reward":round(mean(rewards),9),
                    "correct_action_rate":round(mean([a==c["expected_correct_action"]
                                                      for a,c in zip(actions,cases)]),9),
                }
            by_cond[condition][str(budget)]["candidate_memory"]={
                "preserved_after_B_fraction":round(mean([c["candidate_old_A_preserved_after_B"] for c in cases]),9),
                "retrieved_at_decision_fraction":round(mean([c["candidate_old_A_recalled"] for c in cases]),9),
                "two_core_fraction":round(mean([len(c["candidate_cores"])==2 for c in cases]),9),
            }
    return by_cond

def negative_control(laws):
    rows=[]
    for world in NEGATIVE:
        _,after_B,marker,train,pre_cost=prehistory(world,laws)
        challenge=[]
        for i in range(4):
            obs=official_episode(laws["A"],seed_of(world,"negative","challenge",i),2)
            challenge.append(public_evidence(obs))
        proper=cold_restore({"candidate":after_B["candidate"]})["candidate"]
        for evidence in challenge:
            proper.learn(evidence["forward"])
        # Identical evidence quantity but destroy sequential association by shuffle;
        # experimenter phase labels never supplied.
        all_flags=[item["record"]["forward"] for item in train]+[item["forward"] for item in challenge]
        random.Random(seed_of(world,"negative","shuffle")).shuffle(all_flags)
        scrambled=ProtectedBank(2)
        for flag in all_flags:
            scrambled.learn(flag)
        reward={}
        decision={}
        for name,model in (("proper",proper),("shuffled",scrambled)):
            action=model.choose()
            sample=official_episode(laws["A"],seed_of(world,"negative","heldout"),action)
            decision[name]=action
            reward[name]=sample["reward"]
        rows.append({"world":world,"actions":decision,"rewards":reward})
    actual=[r["rewards"]["proper"] for r in rows]
    sham=[r["rewards"]["shuffled"] for r in rows]
    return rows,{"n":len(rows),"gain":round(mean(actual)-mean(sham),9),
                 "paired_CI95":paired_bootstrap(actual,sham)}

def omit_timings(obj):
    """Timing is diagnostic, never part of bit-for-bit scientific data SHA."""
    if isinstance(obj,dict):
        return {k:omit_timings(v) for k,v in obj.items()
                if k not in ("model_time_seconds","prehistory_model_seconds",
                             "whole_process_seconds","elapsed_seconds","decision_seconds")}
    if isinstance(obj,list):
        return [omit_timings(x) for x in obj]
    return obj

def first_use():
    """Authorized one-shot workflow entrypoint ONLY, guarded by exact source SHA."""
    started=time.perf_counter()
    assert [len(DEV),len(TRANSFER),len(NEGATIVE)]==[16,64,32]
    assert set(DEV).isdisjoint(TRANSFER) and set(DEV).isdisjoint(NEGATIVE)
    assert BUDGETS==(0,1,2,4)
    dev=[one_world(world,LAWS["dev"]) for world in DEV]
    transfer=[one_world(world,LAWS["transfer"]) for world in TRANSFER]
    negative_rows,negative_summary=negative_control(LAWS["transfer"])
    dev_stats=summary(dev)
    transfer_stats=summary(transfer)
    return_scores={name:world_means(transfer,name,"A_returns") for name in NAMES}
    hold_scores={name:world_means(transfer,name,"B_continues") for name in NAMES}
    strongest=max(MATCHED,key=lambda name:mean(return_scores[name]))
    gain=mean(return_scores["candidate"])-mean(return_scores[strongest])
    ablation=mean(return_scores["candidate"])-mean(return_scores["one_slot"])
    hold=mean(hold_scores["candidate"])-mean(hold_scores[strongest])
    gain_ci=paired_bootstrap(return_scores["candidate"],return_scores[strongest])
    ablation_ci=paired_bootstrap(return_scores["candidate"],return_scores["one_slot"])
    cases=[w["forks"][f"A_returns:{budget}"] for w in transfer
           for budget in PRIMARY_BUDGETS]
    return_accuracy=mean([case["actions"]["candidate"]==2 for case in cases])
    retrieval=mean([case["candidate_old_A_recalled"] for case in cases])
    cost_per_model={}
    for name in NAMES:
        training=mean([w["prehistory_model_seconds"][name] for w in transfer])
        challenge=mean([mean([c["model_time_seconds"][name] for c in
                           (w["forks"]["A_returns:2"],w["forks"]["A_returns:4"])])
                        for w in transfer])
        cost_per_model[name]=training+challenge
    fastest=min(cost_per_model[name] for name in MATCHED)
    cost_ratio=cost_per_model["candidate"]/max(1e-12,fastest)
    # Known-law oracle's return improvement is based on *actual held-out env
    # reward*, not merely the source-derived AAI-09P mathematical gain.
    prior_reward=world_means(transfer,"oracle","A_returns",(0,))
    oracle_current=world_means(transfer,"oracle","A_returns")
    oracle_gain=mean(oracle_current)-mean(prior_reward)
    oracle_gain_ci=paired_bootstrap(oracle_current,prior_reward)
    oracle_B0=world_means(transfer,"oracle","B_continues",(0,))
    oracle_B24=world_means(transfer,"oracle","B_continues")
    oracle_hold_loss=mean(oracle_B0)-mean(oracle_B24)
    no_probe=all(w["forks"]["A_returns:0"]["actions"]==
                 w["forks"]["B_continues:0"]["actions"] for w in transfer)
    benchmark_admitted=oracle_gain>=.20 and oracle_gain_ci[0]>0 and oracle_hold_loss<=.02
    checks={
        "official_oracle_empirical_headroom":benchmark_admitted,
        "candidate_better_than_strongest":gain>=.04 and gain_ci[0]>0,
        "non_degraded_B_continues":hold>=-.02,
        "A_return_accuracy":return_accuracy>=.80,
        "actual_old_A_memory_retrieval":retrieval>=.60,
        "improvement_over_single_core":ablation>=.04 and ablation_ci[0]>0,
        "shuffled_feedback_negative":negative_summary["gain"]>=.10 and negative_summary["paired_CI95"][0]>0,
        "cold_restore_and_zero_probe":no_probe,
        "learner_compute_le_2x":cost_ratio<=2.,
    }
    if not benchmark_admitted:
        classification="HEADROOM_INADEQUATE_NO_PROMOTION"
    elif all(checks.values()):
        classification="EXTERNAL_CANDIDATE_BENEFIT_REQUIRES_INDEPENDENT_NATIVE_SCIENCE"
    else:
        classification="VALID_NEGATIVE_NO_INTEGRATION"
    worlds={"dev":dev,"transfer":transfer,"negative":negative_rows}
    fingerprint=hashlib.sha256((canonical(omit_timings(worlds))+"\n").encode()).hexdigest()
    return {
        "schema":"yggdrasil.contrib.aai09a.frozen-external-first-use.v1",
        "original_prereg_commit":PREREG,
        "upstream_source_sha":UPSTREAM,
        "classification":classification,
        "strongest_matched_control":strongest,
        "cohort_counts":{"dev":len(dev),"transfer":len(transfer),"negative":len(negative_rows)},
        "dev":dev_stats,"transfer":transfer_stats,
        "primary_budgets":list(PRIMARY_BUDGETS),
        "gains":{
            "candidate_minus_strongest":round(gain,9),
            "candidate_minus_strongest_CI95":gain_ci,
            "candidate_minus_one_core":round(ablation,9),
            "candidate_minus_one_core_CI95":ablation_ci,
            "B_hold_candidate_minus_strongest":round(hold,9),
            "A_return_accuracy":round(return_accuracy,9),
            "preserved_A_retrieval_rate":round(retrieval,9),
            "candidate_model_compute_over_fastest":round(cost_ratio,6),
            "known_law_oracle_return_gain":round(oracle_gain,9),
            "known_law_oracle_return_gain_CI95":oracle_gain_ci,
            "known_law_oracle_B_hold_loss":round(oracle_hold_loss,9),
        },
        "model_seconds_per_world":cost_per_model,
        "negative":negative_summary,
        "checks":checks,
        "full_world_records_sha256":fingerprint,
        "world_records":worlds,
        "whole_process_seconds":round(time.perf_counter()-started,6),
        "science_limits":"External fixed-map NS-Gym with scripted action probes and known law family; no native Yggdrasil weights or general-intelligence evidence. Oracle holds privileged A/B likelihoods and prior, not matched.",
        "integration":"NONE",
    }

def source_only():
    """Pure no-NS-Gym structural check for mechanical workflow."""
    bank=ProtectedBank(2)
    for x in [True]*32:
        bank.learn(x)
    marker=origin_marker(bank)
    for x in [False]*32:
        bank.learn(x)
    intact=preserved_original(bank,marker)
    saved=checkpoint({"candidate":bank})
    copy=cold_restore(saved)["candidate"]
    assert saved==checkpoint({"candidate":copy})
    for x in (True,True):
        copy.learn(x)
    assert checkpoint({"candidate":bank})==saved
    return {"phase":"SOURCE_ONLY","prereg":PREREG,
            "intact_A_after_B":intact,
            "candidate_copy_decision_after_two_A":copy.choose(),
            "scientific_first_use":False}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-only",action="store_true")
    parser.add_argument("--mechanical",action="store_true")
    parser.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if sum(map(bool,(args.source_only,args.mechanical,args.primary)))!=1:
        parser.error("select exactly one test mode")
    if args.primary:
        parser.error("AAI-09A SCIENTIFIC FIRST USE DISARMED: separate explicit owner authorization needed")
    print(json.dumps(source_only() if args.source_only else official_mechanical(),
                     sort_keys=True,indent=2))
