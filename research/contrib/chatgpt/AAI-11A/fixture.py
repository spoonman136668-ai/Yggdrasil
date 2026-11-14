"""AAI-11A disarmed synthetic-only causal transfer source admission.

No reserved DEV/TRANSFER/NEGATIVE seeds are accepted or generated. This is a
single preregistered exploratory development gate, never a science result.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world, controls, learner


def common_training(key,names=learner.NAMES):
    world.fixture(key)
    actors={name:learner.make(name) for name in names}
    evidence=[]
    for law,scope in (("A","train-initial"),("B","train-next")):
        for trial in range(16):
            pair=world.pair(law,key,scope,trial)
            evidence.extend(pair)
            for name,actor in actors.items():
                for observed in pair:
                    actor.observe(world.copy_public(observed))
    for actor in actors.values():
        actor.fit_checkpoint()
    if len(evidence)!=64 or any(frozenset(event)!=world.PUBLIC_KEYS for event in evidence):
        raise AssertionError("unequal public evidence or private field")
    saved={name:learner.checkpoint(name,actor) for name,actor in actors.items()}
    for name,blob in saved.items():
        if learner.checkpoint(name,learner.restore(name,blob))!=blob:
            raise AssertionError("bad frozen post-B checkpoint")
    return saved,tuple(evidence)


def challenge(name,initial,law,key,budget,corrupt=False):
    if type(budget) is not int or budget not in (2,4):
        raise ValueError("unfrozen actual challenge budget")
    actor=learner.restore(name,initial)
    original=[]
    for trial in range(budget):
        pair=world.pair(law,key,f"challenge-{law}-{budget}",trial)
        original.append(pair)
    if corrupt:
        if budget<2:raise ValueError("negative needs two trials")
        mediator_post=[tuple(pair[1]["mediators"]) for pair in original]
        corrupted=[]
        for index,(pre,post) in enumerate(original):
            post=dict(post)
            post["mediators"]=list(mediator_post[(index+1)%budget])
            post["reward"]=world.reward(post["mediators"],post["goal"],post["actions_taken"])
            corrupted.append((pre,post))
        if sorted(tuple(p[1]["mediators"]) for p in corrupted)!=sorted(mediator_post):
            raise AssertionError("negative changed post mediator output marginals")
        original=corrupted
    for pre,post in original:
        actor.observe(world.copy_public(pre))
        actor.observe(world.copy_public(post))
    actor.fit_checkpoint()
    result=learner.checkpoint(name,actor)
    if learner.checkpoint(name,learner.restore(name,result))!=result:
        raise AssertionError("invalid cold challenge")
    return result


def episode(name,checkpoint,law,x,goal):
    """Restore on every episode; execute only this learner's actual do-actions."""
    actor=learner.restore(name,checkpoint)
    current=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(current))
    actions=[]
    for _ in range(2):
        action=actor.choose(world.copy_public(current))
        if action is None:break
        if action not in world.ACTIONS:
            raise AssertionError("unknown intervention")
        current=world.copy_public(world.do(law,current,action))
        actions.append(world.ACTIONS.index(action))
        actor.observe(world.copy_public(current))
    if len(actions)!=current["actions_taken"]:
        raise AssertionError("action allowance exceeded")
    return current["reward"],int(tuple(current["mediators"])==tuple(goal)),actions


def score(name,postB,law,key,budget,corrupt=False):
    snap=challenge(name,postB,law,key,budget,corrupt)
    contexts=tuple(sorted(
        (x,g) for x,g in (
            (world.INPUTS[world.index(key,"evaluate-"+law,k,"x",64)],
             world.GOALS[world.index(key,"evaluate-"+law,k,"goal",8)])
            for k in range(512)
        )
    ))
    # Reuse the ORIGINAL qualified unique twelve contexts, not replacements.
    from admission import contexts as admitted_contexts
    contexts=admitted_contexts(key,law,12)
    obs=[episode(name,snap,law,x,g) for x,g in contexts]
    check=learner.checkpoint(name,learner.restore(name,postB))
    if check!=postB:
        raise AssertionError("post-B cold source changed after forks")
    return {"mean_reward":round(sum(r for r,_,_ in obs)/len(obs),9),
            "goal_correct":round(sum(ok for _,ok,_ in obs)/len(obs),9),
            "actions_sha256":hashlib.sha256(
                controls.canonical([acts for _,_,acts in obs]).encode()).hexdigest(),
            "cold_bytes":len(snap.encode())}


def fixture_admission():
    prereg=json.loads((HERE/"prereg.json").read_text("utf8"))
    if prereg["id"]!="AAI-11A" or prereg["future_science"]["consumed"] or prereg["future_science"]["first_use_authorized"]:
        raise PermissionError("science first-use unauthorized")
    scores={name:[] for name in learner.NAMES}
    goals={name:[] for name in learner.NAMES}
    familiar={name:[] for name in learner.NAMES}
    oracle=[]
    traces=[]
    times={name:0. for name in learner.NAMES}
    memory={name:0 for name in learner.NAMES}
    start=time.perf_counter()
    fixtures={}
    for key in world.FIXTURES:
        tick=time.perf_counter()
        saved,evidence=common_training(key)
        if len(evidence)!=64:
            raise AssertionError("public training mismatch")
        train_cost=time.perf_counter()-tick
        # Baseline initial common training measured jointly, report combined
        # but do NOT misallocate it to one learner.
        fixture_times={}
        per={name:[] for name in learner.NAMES}
        local_oracle=[]
        for law in (*world.TRANSFER,*world.TRAIN):
            from admission import contexts as admitted_contexts
            positions=admitted_contexts(key,law,12)
            for n in (2,4):
                if law in world.TRANSFER:
                    local_oracle.append(sum(world.exact_oracle(law,x,g)
                                            for x,g in positions)/len(positions))
                for name in learner.NAMES:
                    before=time.perf_counter()
                    result=score(name,saved[name],law,key,n)
                    times[name]+=time.perf_counter()-before
                    memory[name]=max(memory[name],result["cold_bytes"])
                    traces.append((key,law,n,name,result["mean_reward"],
                                   result["actions_sha256"]))
                    if law in world.TRANSFER:
                        scores[name].append(result["mean_reward"])
                        goals[name].append(result["goal_correct"])
                        per[name].append(result["mean_reward"])
                    else:
                        familiar[name].append(result["mean_reward"])
        oracle.extend(local_oracle)
        fixtures[key]={"mean_oracle":round(sum(local_oracle)/len(local_oracle),9),
                       "method_means":{name:round(sum(v)/len(v),9)
                                       for name,v in per.items()},
                       "common_train_wall_seconds_unallocated":round(train_cost,6)}
    means={name:round(sum(v)/len(v),9) for name,v in scores.items()}
    success={name:round(sum(v)/len(v),9) for name,v in goals.items()}
    a_b={name:round(sum(v)/len(v),9) for name,v in familiar.items()}
    oracle_mean=round(sum(oracle)/len(oracle),9)
    strongest=max(learner.MATCHED,key=lambda n:means[n])
    fastest=min(learner.MATCHED,key=lambda n:times[n])
    gain=round(means[learner.CANDIDATE]-means[strongest],9)
    ablation=round(means[learner.CANDIDATE]-means[learner.ABLATION],9)
    headroom=round(oracle_mean-means[strongest],9)
    baseline_keep=a_b[strongest]
    candidate_keep=a_b[learner.CANDIDATE]
    ratio=times[learner.CANDIDATE]/max(times[fastest],1e-9)
    gates={
        "candidate_gt_strongest_plus_008":gain>=.08,
        "headroom_over_strongest_ge_025":headroom>=.25,
        "protected_vs_full_budget_one_slot_ge_005":ablation>=.05,
        "goal_success_ge_060":success[learner.CANDIDATE]>=.60,
        "return_A_B_hold_noninferiority":candidate_keep>=baseline_keep-.03,
        "candidate_under_2x_fastest_matched_process":ratio<=2.0,
    }
    return {
        "schema":"yggdrasil.contrib.aai11a.fixture-admission.v1",
        "status":"DEV_ADMITTED_SCIENCE_UNVERIFIED" if all(gates.values())
                 else "DEV_NO_GO_NO_SCIENCE",
        "checks":gates,"fixture_ids":list(world.FIXTURES),
        "strongest_conventional":strongest,
        "fastest_conventional_by_scoring_walltime":fastest,
        "candidate":learner.CANDIDATE,
        "candidate_minus_strongest":gain,
        "candidate_minus_one_slot":ablation,
        "oracle_minus_strongest":headroom,
        "candidate_goal_success":success[learner.CANDIDATE],
        "candidate_familiar":candidate_keep,
        "strongest_familiar":baseline_keep,
        "all_method_reward":means,
        "all_method_goal_success":success,
        "all_method_familiar":a_b,
        "candidate_over_fastest_scoring_time":round(ratio,6),
        "scoring_wall_seconds_by_method":{name:round(v,5) for name,v in times.items()},
        "max_cold_checkpoint_bytes":memory,
        "oracle_mean":oracle_mean,
        "fixture_mean_results":fixtures,
        "policy_trace_sha256":hashlib.sha256(controls.canonical(traces).encode()).hexdigest(),
        "whole_fixture_wall_seconds":round(time.perf_counter()-start,4),
        "science_cohorts_consumed":0,
        "scientific_CI":None,"native_model_changed":False,
        "data_admission":"MECHANICAL_FIXTURES_ONLY",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture-admission",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:
        p.error("AAI11A SCIENTIFIC FIRST USE DISARMED")
    if not args.fixture_admission:
        p.error("only source-only frozen fixture admission is supported")
    print("AAI11A_ADMISSION="+json.dumps(fixture_admission(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
