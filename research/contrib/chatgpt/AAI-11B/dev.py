"""AAI-11B frozen sequential early-falsification DEV: no scientific first use.

First screen the new intervention-contrast candidate against the *previously*
qualified identical-source graph_recent8 result. If below that reference,
DO NOT rerun eleven baselines or spend untouched science cohorts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE))
import world,controls,admission
import fixture as prior
import contrast

REFERENCE=2.134027778
REQUIRED_GAIN=.08
GOAL_MIN=.60


def train(key):
    world.fixture(key)
    m=contrast.InterventionTournament()
    t=time.perf_counter()
    rows=[]
    for law,phase in (("A","train-initial"),("B","train-next")):
        for trial in range(16):
            pair=world.pair(law,key,phase,trial)
            for row in pair:
                rows.append(row)
                m.observe(world.copy_public(row))
    if len(rows)!=64:
        raise AssertionError("unmatched initial public training rows")
    source=contrast.checkpoint(m)
    if contrast.checkpoint(contrast.restore(source))!=source:
        raise AssertionError("post-B cold snapshot invalid")
    seconds=time.perf_counter()-t
    return source,tuple(rows),seconds


def challenge(postB,law,key,budget,corrupt=False):
    world.fixture(key)
    if type(budget) is not int or budget not in (2,4):
        raise ValueError("unregistered challenge budget")
    m=contrast.restore(postB)
    pairs=[world.pair(law,key,f"challenge-{law}-{budget}",i) for i in range(budget)]
    if corrupt:
        orig=[tuple(pair[1]["mediators"]) for pair in pairs]
        revised=[]
        for i,(pre,post) in enumerate(pairs):
            new=dict(post)
            new["mediators"]=list(orig[(i+1)%len(orig)])
            new["reward"]=world.reward(new["mediators"],new["goal"],new["actions_taken"])
            revised.append((pre,new))
        if sorted(tuple(post["mediators"]) for _,post in revised)!=sorted(orig):
            raise AssertionError("negative public mediator marginals changed")
        pairs=revised
    for before,after in pairs:
        m.observe(world.copy_public(before))
        m.observe(world.copy_public(after))
    result=contrast.checkpoint(m)
    if contrast.checkpoint(contrast.restore(result))!=result:
        raise AssertionError("challenge cold snapshot changed")
    return result


def episode(snapshot,law,x,goal):
    m=contrast.restore(snapshot)
    row=world.copy_public(world.start(law,x,goal))
    m.observe(world.copy_public(row))
    actions=[]
    for _ in range(2):
        action=m.choose(world.copy_public(row))
        if action is None:break
        if action not in world.ACTIONS:
            raise AssertionError("illegal action")
        row=world.copy_public(world.do(law,row,action))
        actions.append(world.ACTIONS.index(action))
        m.observe(world.copy_public(row))
    if len(actions)!=row["actions_taken"]:
        raise AssertionError("actual action count mismatch")
    return row["reward"],int(tuple(row["mediators"])==tuple(goal)),tuple(actions)


def score_condition(postB,law,key,budget,corrupt=False):
    snapshot=challenge(postB,law,key,budget,corrupt)
    contexts=admission.contexts(key,law,12)
    trials=[episode(snapshot,law,x,g) for x,g in contexts]
    if contrast.checkpoint(contrast.restore(postB))!=postB:
        raise AssertionError("original frozen training state mutated")
    return {"mean_reward":sum(reward for reward,_,_ in trials)/len(trials),
            "mean_goal_success":sum(correct for _,correct,_ in trials)/len(trials),
            "trace":hashlib.sha256(controls.canonical([actions for _,_,actions in trials]).encode()).hexdigest()}


def measure_fixture():
    locked=json.loads((HERE/"prereg.json").read_text("utf8"))
    if locked["id"]!="AAI-11B" or locked["authority"]["cohort_consumption"] or locked["authority"]["scientific_first_use"]:
        raise PermissionError("AAI11B SCIENTIFIC FIRST USE DISARMED")
    if locked["source_development"]["historical_mean_reward"]!=REFERENCE:
        raise ValueError("historical strongest source comparison changed")
    tstart=time.perf_counter()
    rewards=[];goals=[];traces=[];timing=0.
    saved_sha=[]
    for key in world.FIXTURES:
        checkpoint,evidence,secs=train(key)
        timing+=secs
        saved_sha.append(hashlib.sha256(checkpoint.encode()).hexdigest())
        if len(evidence)!=64:
            raise AssertionError("wrong fixture rows")
        for law in world.TRANSFER:
            for budget in (2,4):
                tick=time.perf_counter()
                result=score_condition(checkpoint,law,key,budget)
                timing+=time.perf_counter()-tick
                rewards.append(result["mean_reward"])
                goals.append(result["mean_goal_success"])
                traces.append((key,law,budget,result["trace"],
                               round(result["mean_reward"],9)))
    mean=sum(rewards)/len(rewards)
    completion=sum(goals)/len(goals)
    diff=mean-REFERENCE
    first=diff+1e-10>=REQUIRED_GAIN and completion+1e-10>=GOAL_MIN
    summary={
        "schema":"yggdrasil.contrib.aai11b.source-development.v1",
        "status":"DEV_FIRST_SCREEN_PASS_REQUIRES_FULL_MATCHED_QUALIFICATION" if first
                 else "DEV_NO_GO_NO_SCIENCE",
        "candidate_mean_reward":round(mean,9),
        "candidate_three_goal_success":round(completion,9),
        "historical_qualified_graph_recent8_mean":REFERENCE,
        "candidate_minus_historical_best":round(diff,9),
        "fixed_minimum_gain":REQUIRED_GAIN,
        "fixed_goal_success":GOAL_MIN,
        "first_screen_pass":first,
        "fixture_count":len(world.FIXTURES),"condition_count":len(traces),
        "public_training_rows_per_fixture":64,
        "training_checkpoint_challenge_episodes_seconds":round(timing,6),
        "frozen_training_checkpoint_sha256":saved_sha,
        "trace_sha256":hashlib.sha256(controls.canonical(traces).encode()).hexdigest(),
        "science_cohorts_consumed":0,"new_firstuse_allowed":False,
        "native_model_edited":False,
        "full_requalified_controls":None,
    }
    if first:
        # Trigger only after passing the pre-frozen cheap stop rule. Reuse
        # original AAI-11A source to requalify ALL 11 eligible strong controls.
        # This execution is still development-only with NO scientific cohorts.
        full=prior.fixture_admission()
        strongest=max(prior.learner.MATCHED,key=lambda name:full["all_method_reward"][name])
        competitor=full["all_method_reward"][strongest]
        fastest=min(prior.learner.MATCHED,key=lambda name:
                    full["training_checkpoint_challenge_action_restore_wall_seconds_by_method"][name])
        besttime=full["training_checkpoint_challenge_action_restore_wall_seconds_by_method"][fastest]
        ratio=timing/max(besttime,1e-12)
        candidate_familiar=[]
        for key in world.FIXTURES:
            postB,_,_=train(key)
            for law in world.TRAIN:
                for budget in (2,4):
                    candidate_familiar.append(score_condition(postB,law,key,budget)["mean_reward"])
        familiar=sum(candidate_familiar)/len(candidate_familiar)
        final_gates={
            "best_of_11_gain":mean-competitor>=REQUIRED_GAIN,
            "goal_success":completion>=GOAL_MIN,
            "familiar_noninferiority":familiar>=full["all_method_familiar"][strongest]-.03,
            "two_x_whole_process":ratio<=2.,
        }
        summary["full_requalified_controls"]={
            "strongest":strongest,"strongest_reward":competitor,
            "fastest":fastest,"candidate_over_fastest_whole_ratio":round(ratio,6),
            "candidate_familiar":round(familiar,9),
            "strongest_familiar":full["all_method_familiar"][strongest],
            "frozen_secondary_gates":final_gates}
        summary["status"]=("DEV_ADMITTED_SCIENCE_UNVERIFIED" if all(final_gates.values())
                           else "DEV_NO_GO_NO_SCIENCE")
    summary["fixture_wall_seconds_including_controls_if_needed"]=round(time.perf_counter()-tstart,4)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture-admission",action="store_true")
    p.add_argument("--primary",action="store_true")
    options=p.parse_args()
    if options.primary:
        p.error("AAI11B SCIENTIFIC FIRST USE DISARMED")
    if not options.fixture_admission:
        p.error("only mechanical fixture-only development permitted")
    print("AAI11B_DEV="+json.dumps(measure_fixture(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
