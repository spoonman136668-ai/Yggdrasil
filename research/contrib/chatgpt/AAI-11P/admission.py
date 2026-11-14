"""AAI-11P matched fully trained conventional benchmark pre-admission ONLY.

Compares actual public post-intervention rewards against a privileged oracle.
Fixture labels are not science cohort IDs and no new mechanism is tested.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import world
import controls


def contexts(fixture,law,n=12):
    world.fixture(fixture)
    if type(n) is not int or not 1<=n<=12:
        raise ValueError("invalid frozen context budget")
    candidates=((x,g) for x in world.INPUTS for g in world.GOALS)
    def rank(item):
        x,g=item
        payload=f"AAI11P|{fixture}|{law}|{''.join(map(str,x))}|{''.join(map(str,g))}".encode("ascii")
        return hashlib.sha256(payload).digest()
    return tuple(sorted(candidates,key=rank)[:n])


def common_training(fixture):
    world.fixture(fixture)
    models={name:controls.make(name) for name in controls.ALL}
    public_rows=[]
    for law,phase in (("A","train-initial"),("B","train-next")):
        for i in range(16):
            pair=world.pair(law,fixture,phase,i)
            public_rows.extend(pair)
            for model in models.values():
                for event in pair:
                    model.observe(world.copy_public(event))
    if len(public_rows)!=64:
        raise AssertionError("unequal 64 public rows")
    for model in models.values():
        model.fit_checkpoint()
    saved={name:controls.checkpoint(model) for name,model in models.items()}
    for name in models:
        if controls.checkpoint(controls.restore(saved[name],name))!=saved[name]:
            raise AssertionError("training snapshot not independent cold clone")
    return saved,tuple(public_rows)


def common_challenge(name,source,law,fixture,n):
    world.fixture(fixture)
    if type(n) is not int or n not in (2,4):
        raise ValueError("unfrozen challenge budget")
    actor=controls.restore(source,name)
    for i in range(n):
        for event in world.pair(law,fixture,f"challenge-{law}-{n}",i):
            actor.observe(world.copy_public(event))
    actor.fit_checkpoint()
    result=controls.checkpoint(actor)
    if controls.checkpoint(controls.restore(result,name))!=result:
        raise AssertionError("challenge cold snapshot invalid")
    return result


def episode(name,snapshot,law,x,goal):
    actor=controls.restore(snapshot,name)
    current=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(current))
    actions=[]
    for _ in range(2):
        chosen=actor.choose(world.copy_public(current))
        if chosen is None:break
        if chosen not in world.ACTIONS:
            raise ValueError("invalid control action")
        current=world.copy_public(world.do(law,current,chosen))
        actions.append(world.ACTIONS.index(chosen))
        actor.observe(world.copy_public(current))
    if current["actions_taken"]!=len(actions):
        raise AssertionError("policy exceeded action allowance")
    return {"reward":current["reward"],
            "goal_correct":int(tuple(current["mediators"])==goal),
            "actions":actions}


def score_condition(name,snapshot,law,fixture,n,context_count=12):
    challenge=common_challenge(name,snapshot,law,fixture,n)
    data=[episode(name,challenge,law,x,g) for x,g in contexts(fixture,law,context_count)]
    # Every episode starts from the identical frozen challenge snapshot.
    if controls.checkpoint(controls.restore(name= name,payload=challenge))!=challenge:
        raise AssertionError("condition snapshot contaminated")
    return {"mean_reward":round(sum(d["reward"] for d in data)/len(data),9),
            "mean_goal_success":round(sum(d["goal_correct"] for d in data)/len(data),9),
            "mean_actions":round(sum(len(d["actions"]) for d in data)/len(data),9),
            "action_trace":hashlib.sha256(controls.canonical([d["actions"] for d in data]).encode()).hexdigest(),
            "checkpoint_bytes":len(challenge.encode())}


def _mean(items):
    if not items:
        raise ValueError("empty score list")
    return sum(items)/len(items)


def admission():
    # Exactly the three preregistered string fixtures; no numerical seed.
    fixed=json.loads((Path(__file__).resolve().parent/"prereg.json").read_text("utf8"))
    if fixed["id"]!="AAI-11P" or fixed["future_science"]["used"]!=0 or fixed["future_science"]["primary_authorized"]:
        raise PermissionError("AAI11P scientific cohorts must remain untouched")
    engine=world.mechanics()
    checks=engine["checks"]
    if not all(checks.values()):
        return {"classification":"BENCHMARK_INADEQUATE_NO_SCIENCE",
                "reason":"mechanical causal identifiability or consequence FAIL",
                "mechanical":engine,"science_cohorts_used":0}
    # Deterministic fixed synthetic experiment, no peek/tune/seed search.
    transfer_laws=world.TRANSFER
    timing=time.perf_counter()
    per_fixture={}
    pooled={name:[] for name in controls.ALL}
    pooled_goal={name:[] for name in controls.ALL}
    oracle_pool=[]
    familiar_pool={name:[] for name in controls.ALL}
    method_trace=[]
    for key in world.FIXTURES:
        frozen,events=common_training(key)
        per={name:[] for name in controls.ALL}
        per_familiar={name:[] for name in controls.ALL}
        per_oracle=[]
        for law in (*transfer_laws,*world.TRAIN):
            for budget in (2,4):
                contexts_public=contexts(key,law)
                gold=_mean([world.exact_oracle(law,x,g) for x,g in contexts_public])
                if law in transfer_laws:
                    per_oracle.append(gold)
                    oracle_pool.append(gold)
                for name in controls.ALL:
                    output=score_condition(name,frozen[name],law,key,budget)
                    if law in transfer_laws:
                        per[name].append(output["mean_reward"])
                        pooled[name].append(output["mean_reward"])
                        pooled_goal[name].append(output["mean_goal_success"])
                    else:
                        per_familiar[name].append(output["mean_reward"])
                        familiar_pool[name].append(output["mean_reward"])
                    method_trace.append((key,law,budget,name,output["action_trace"],
                                         output["mean_reward"]))
        if len(events)!=64:
            raise AssertionError("fixture public evidence count")
        per_fixture[key]={"oracle_mean":round(_mean(per_oracle),9),
                          "controls":{n:round(_mean(v),9) for n,v in per.items()},
                          "familiar_control_mean":{n:round(_mean(v),9) for n,v in per_familiar.items()}}
        # Source checkpoints cannot mutate between independent forks.
        other,_=common_training(key)
        if frozen!=other:
            raise AssertionError("common training checkpoint mutated")
    means={n:round(_mean(v),9) for n,v in pooled.items()}
    matched=max(controls.METHODS,key=lambda n:means[n])
    strongest=means[matched]
    oracle=round(_mean(oracle_pool),9)
    gap=round(oracle-strongest,9)
    familiar_best=max(controls.METHODS,key=lambda n:_mean(familiar_pool[n]))
    familiar_reward=round(_mean(familiar_pool[familiar_best]),9)
    each_fixture_gap={key:round(item["oracle_mean"]-
                                    item["controls"][matched],9)
                      for key,item in per_fixture.items()}
    checks=dict(checks)
    checks["best_trained_conventional_familiar_floor"]=familiar_reward>=1.70
    checks["oracle_headroom_over_strongest_ge_025"]=gap>=.25
    checks["each_fixture_headroom_ge_010"]=all(v>=.10 for v in each_fixture_gap.values())
    trace=hashlib.sha256(controls.canonical(method_trace).encode()).hexdigest()
    result={
        "schema":"yggdrasil.contrib.aai11p.matched-control-admission.v1",
        "phase":"MECHANICAL_FIXTURE_ONLY_NO_SCIENCE",
        "classification":("BENCHMARK_ADMITTED_FOR_FUTURE_SCIENCE_DESIGN_ONLY"
                          if all(checks.values()) else "BENCHMARK_INADEQUATE_NO_SCIENCE"),
        "checks":checks,
        "strongest_conventional_transfer":matched,
        "strongest_transfer_reward":strongest,
        "privileged_oracle_transfer_reward":oracle,
        "oracle_headroom":gap,
        "strongest_familiar":familiar_best,
        "familiar_best_reward":familiar_reward,
        "per_fixture_headroom":each_fixture_gap,
        "matched_control_means":{n:means[n] for n in controls.METHODS},
        "matched_goal_success":{n:round(_mean(pooled_goal[n]),9) for n in controls.METHODS},
        "control_count":len(controls.METHODS),
        "public_observations_per_training":64,
        "challenges_per_transfer_law":[2,4],
        "distinct_laws":list(world.LAWS),
        "evaluation_contexts_per_law":12,
        "fixtures":list(world.FIXTURES),
        "trace_sha256":trace,
        "mechanical_trace_sha256":engine["trace_sha256"],
        "total_wall_seconds":round(time.perf_counter()-timing,4),
        "science_cohorts_consumed":0,
        "trained_new_candidate":False,
        "native_yggdrasil_edited":False
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture-admission",action="store_true")
    parser.add_argument("--mechanical",action="store_true")
    parser.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if args.primary:
        parser.error("AAI11P SCIENTIFIC FIRST USE DISARMED")
    if args.mechanical and not args.fixture_admission:
        output=world.mechanics()
        print("AAI11P_MECHANICAL="+json.dumps(output,sort_keys=True),flush=True)
        if not all(output["checks"].values()):
            raise SystemExit("AAI11P_MECHANICAL_INADEQUATE_NO_SCIENCE")
        return
    if not args.fixture_admission:
        parser.error("only frozen fixture admission is supported")
    out=admission()
    print("AAI11P_ADMISSION="+json.dumps(out,sort_keys=True),flush=True)
    # Fixture-admission NO-GO is a valid scientific-development diagnostic,
    # not a broken engineering test. Exit 0 so the immutable NO-GO is preserved.


if __name__=="__main__":
    main()
