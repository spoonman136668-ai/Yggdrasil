"""AAI-12Q one prespecified development screen: real do outcomes, cold forks.

New causal invariant vs the independently qualified strongest conventional
and an identical-eight-public-event ablation, on exactly original AAI-12P
mechanical fixtures. All actual actions and observations are matched.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-12P"))
sys.path.insert(0,str(HERE))
import world,controls,admit
import invariants

BEST="causal_structure_recent8"
ARMS=(BEST,*invariants.ARMS)


def model(name):
    if name==BEST:return controls.Control(name)
    return invariants.CausalInvariantModel(name)


def checkpoint(name,actor):
    if name==BEST:return controls.checkpoint(actor)
    return invariants.checkpoint(actor)


def restore(name,source):
    if name==BEST:return controls.restore(name,source)
    return invariants.restore(name,source)


def train(key):
    world.fixture(key)
    actors={n:model(n) for n in ARMS}
    elapsed={n:0. for n in ARMS}
    public=[]
    for law in world.FIT:
        for i in range(8):
            for event in world.pair(law,key,"fit",i):
                public.append(event)
                for name,actor in actors.items():
                    tic=time.perf_counter()
                    actor.observe(world.copy_public(event))
                    elapsed[name]+=time.perf_counter()-tic
    if len(public)!=64 or any(set(r)!=world.PUBLIC_KEYS for r in public):
        raise AssertionError("unchanged common public source training budget")
    snapshots={}
    for name,actor in actors.items():
        tic=time.perf_counter()
        actor.fit_checkpoint()
        snapshots[name]=checkpoint(name,actor)
        if checkpoint(name,restore(name,snapshots[name]))!=snapshots[name]:
            raise AssertionError("public cold A/B source different on restore")
        elapsed[name]+=time.perf_counter()-tic
    if not(actors[BEST].rows==actors[invariants.ABLATION].rows==
           actors[invariants.CANDIDATE].rows):
        raise AssertionError("candidate/ablation/strong baseline used unequal x-m observations")
    if actors[invariants.ABLATION].events!=actors[invariants.CANDIDATE].events:
        raise AssertionError("candidate and equal-memory ablation have different public data")
    return snapshots,tuple(public),elapsed


def challenge(name,after_fit,law,key,corrupt=False):
    world.fixture(key);world.law_name(law)
    actor=restore(name,after_fit)
    pairs=[world.pair(law,key,"challenge",i) for i in range(4)]
    if corrupt:
        labels=[tuple(p[1]["mediators"]) for p in pairs]
        translated=labels[1:]+labels[:1]
        if sorted(translated)!=sorted(labels):
            raise AssertionError("negative changed source mediator marginal")
        pairs=[(first,{**second,"mediators":list(fake),
                      "reward":world.reward(fake,second["goal"],1)})
               for (first,second),fake in zip(pairs,translated)]
    tic=time.perf_counter()
    for before,after in pairs:
        actor.observe(world.copy_public(before))
        actor.observe(world.copy_public(after))
    actor.fit_checkpoint()
    source=checkpoint(name,actor)
    if checkpoint(name,restore(name,source))!=source:
        raise AssertionError("challenge source didn't cold restore")
    return source,time.perf_counter()-tic


def episode(name,source,law,x,goal):
    actor=restore(name,source)
    current=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(current))
    actions=[]
    for _ in range(2):
        selected=actor.choose(world.copy_public(current))
        if selected is None:break
        if selected not in world.ACTIONS:
            raise AssertionError("unapproved causal do action")
        current=world.copy_public(world.do(law,current,selected))
        actions.append(world.ACTIONS.index(selected))
        actor.observe(world.copy_public(current))
    if len(actions)!=current["actions_taken"]:
        raise AssertionError("unaligned real consequential action budget")
    return current["reward"],int(tuple(current["mediators"])==tuple(goal)),actions


def source_screen():
    prereg=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (prereg["id"]!="AAI-12Q" or not prereg["safety"]["no_primary_first_use"]
        or prereg["safety"]["science_cohorts_used"]!=0):
        raise PermissionError("AAI12Q SCIENTIFIC FIRST USE DISARMED")
    criteria=prereg["evaluation"]["prespecified_go_no_go"]
    source_means=prereg["evaluation"]["source_baseline"]
    if (ARMS!=(BEST,invariants.ABLATION,invariants.CANDIDATE)
        or source_means["strongest"]!=BEST
        or source_means["total_reachable"]!=97
        or criteria["minimum_integer_reachable_hits"]!=48):
        raise AssertionError("not the frozen eight-bit four-mediator benchmark")
    totals={n:[] for n in ARMS}
    familiar={n:[] for n in ARMS}
    elapsed={n:0. for n in ARMS}
    trace=[]
    cold=[]
    for key in world.FIXTURES:
        saved,public,times=train(key)
        for n in ARMS:elapsed[n]+=times[n]
        cold.append([key,*[hashlib.sha256(saved[n].encode()).hexdigest() for n in ARMS]])
        for law in world.TRANSFER:
            positions=world.contexts(key,law)
            privileged=admit.source_oracle(law,positions)
            snapshots={}
            for n in ARMS:
                snaps,cost=challenge(n,saved[n],law,key)
                snapshots[n]=snaps
                elapsed[n]+=cost
            if (restore(invariants.ABLATION,snapshots[invariants.ABLATION]).events!=
                restore(invariants.CANDIDATE,snapshots[invariants.CANDIDATE]).events):
                raise AssertionError("candidate and equal-memory ablation challenge differ")
            for (x,goal),(optimal,reachable) in zip(positions,privileged):
                for n in ARMS:
                    tic=time.perf_counter()
                    score,hit,actions=episode(n,snapshots[n],law,x,goal)
                    elapsed[n]+=time.perf_counter()-tic
                    totals[n].append({"reward":score,"hit":hit,"actions":actions,
                                      "oracle":optimal,"reachable":reachable,"law":law})
                    trace.append([key,law,n,list(x),list(goal),
                                  round(score,9),hit,actions,reachable])
        for law in world.FIT:
            positions=world.contexts(key,law)
            for n in ARMS:
                snap,cost=challenge(n,saved[n],law,key)
                elapsed[n]+=cost
                for x,goal in positions:
                    tic=time.perf_counter()
                    score,_,_=episode(n,snap,law,x,goal)
                    elapsed[n]+=time.perf_counter()-tic
                    familiar[n].append(score)
        for n in ARMS:
            if checkpoint(n,restore(n,saved[n]))!=saved[n]:
                raise AssertionError("transfer or familiar episodes contaminated fit state")
    if (any(len(totals[n])!=192 or len(familiar[n])!=64 for n in ARMS)
        or len(cold)!=2):
        raise AssertionError("unfrozen source DEV event totals")
    scores={n:admit._flatten(totals[n]) for n in ARMS}
    returns={n:round(admit.mean(familiar[n]),9) for n in ARMS}
    original=scores[BEST]
    target=scores[invariants.CANDIDATE]
    equal=scores[invariants.ABLATION]
    if (abs(original["mean_reward"]-source_means["reward"])>1e-6
        or original["exact_goals_reached"]!=source_means["reachable"]
        or original["oracle_reachable_goals"]!=source_means["total_reachable"]
        or abs(original["oracle_unreachable_goal_regret"]-
               source_means["unreachable_regret"])>1e-6
        or abs(returns[BEST]-source_means["familiar_return"])>1e-6):
        raise AssertionError("the independently qualified strongest conventional source has drifted")
    checks={
        "actual_reward_improves_strongest_by_0_08":
            target["mean_reward"]>=criteria["candidate_mean_reward_min"]-1e-10,
        "attainable_goal_recovery_improves_0_05":
            target["exact_goals_reached"]>=criteria["minimum_integer_reachable_hits"]
            and target["oracle_relative_goal_recovery"]>=
            criteria["candidate_reachable_goal_recovery_min"]-1e-10,
        "causal_effect_contrast_beats_equal_public_memory_ablation_0_03":
            target["mean_reward"]-equal["mean_reward"]>=
            criteria["contrastive_effect_reward_gain_vs_same_8row_pointwise_min"]-1e-10,
        "oracle_unreachable_goal_regret_noninferior":
            target["oracle_unreachable_goal_regret"]<=criteria["max_unreachable_regret"]+1e-10,
        "familiar_cold_return_noninferior":
            returns[invariants.CANDIDATE]>=criteria["min_familiar_A_B_cold_reward"]-1e-10
    }
    pass_gate=all(checks.values())
    result={
        "schema":"yggdrasil.aai12q.source-mechanical-development.v1",
        "classification":"DEV_FIRST_SCREEN_PASS_COST_AND_NEGATIVE_PENDING" if pass_gate
                         else "DEV_NO_GO_NO_SCIENCE",
        "frozen_checks":checks,
        "scores":scores,"familiar_cold_reward":returns,
        "candidate_minus_strongest_actual_reward":round(
            target["mean_reward"]-original["mean_reward"],9),
        "candidate_minus_equal_data_ablation_reward":round(
            target["mean_reward"]-equal["mean_reward"],9),
        "per_method_full_source_training_challenge_cold_action_seconds":{
            n:round(elapsed[n],6) for n in ARMS},
        "all_eight_controls_rerun":False,
        "real_action_reward_trace_sha256":admit.digest(trace),
        "cold_training_snapshots_sha256":admit.digest(cold),
        "actual_unfamiliar_episodes_per_arm":192,
        "actual_familiar_episodes_per_arm":64,
        "source_only_no_science":True,
        "scientific_cohorts_used":0,
        "native_model_modified":False
    }
    if pass_gate:
        # Only after first source screen all PASS; don't rerun expensive eight
        # fully fitted controls on a failed hypothesis.
        whole=admit.admission()
        if whole["classification"]!="BENCHMARK_ADMITTED_FOR_NEW_PROSPECTIVE_SOURCE_DEVELOPMENT":
            raise AssertionError("source qualified eight controls benchmark changed")
        fastest=min(controls.METHODS,key=lambda name:
                    whole["measured_source_train_fit_challenge_cold_actual_action_seconds_by_method"][name])
        fastest_time=whole["measured_source_train_fit_challenge_cold_actual_action_seconds_by_method"][fastest]
        ratio=elapsed[invariants.CANDIDATE]/max(fastest_time,1e-10)
        negatives=[]
        for key in world.FIXTURES:
            snap,_,_=train(key)
            for law in world.TRANSFER:
                damaged,_=challenge(invariants.CANDIDATE,snap[invariants.CANDIDATE],law,key,True)
                for x,goal in world.contexts(key,law):
                    score,_,_=episode(invariants.CANDIDATE,damaged,law,x,goal)
                    negatives.append(score)
        corrupt=admit.mean(negatives)
        negative_pass=target["mean_reward"]>=corrupt-1e-10
        cost_pass=ratio<=criteria["max_candidate_full_process_seconds_ratio_to_fastest_conventional"]
        result["full_source_comparator"]={
            "fastest_control":fastest,"fastest_control_source_seconds":round(fastest_time,6),
            "whole_process_candidate_to_fastest_ratio":round(ratio,6),
            "whole_process_cost_gate":cost_pass,
            "corrupted_do_association_actual_reward":round(corrupt,9),
            "negative_control_gate":negative_pass
        }
        result["all_eight_controls_rerun"]=True
        result["classification"]=("DEV_ADMITTED_SCIENCE_UNVERIFIED" if
                                 cost_pass and negative_pass
                                 else "DEV_NO_GO_NO_SCIENCE")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dev",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("AAI12Q SCIENTIFIC FIRST USE DISARMED")
    if not args.source_dev:
        p.error("only frozen source-only dev on alpha/beta; no scientific worlds")
    print("AAI12Q_DEV="+json.dumps(source_screen(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
