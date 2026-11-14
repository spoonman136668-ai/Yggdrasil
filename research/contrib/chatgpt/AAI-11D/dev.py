"""AAI-11D predeclared source-only posterior-vs-risk screen.

Only three frozen synthetic public fixtures, no primary science cohorts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE))
import world,controls,admission
import fixture as original_fixture
import learner as graph
import calibration as candidate

PREVIOUS_STRONGEST=2.134027778
FIRST_MIN=2.214027778
GOAL_MIN=.60
RISK_VS_POSTERIOR=.03
ARMS=("graph_recent8",*candidate.ARMS)


def train(key):
    world.fixture(key)
    actors={name: graph.GraphWindow(name) if name=="graph_recent8"
            else candidate.PosteriorCausalModel(name) for name in ARMS}
    public=[]
    times={name:0. for name in ARMS}
    for law,phase in (("A","train-initial"),("B","train-next")):
        for i in range(16):
            for row in world.pair(law,key,phase,i):
                public.append(row)
                for name,actor in actors.items():
                    tick=time.perf_counter()
                    actor.observe(world.copy_public(row))
                    times[name]+=time.perf_counter()-tick
    if len(public)!=64 or any(set(row)!=world.PUBLIC_KEYS for row in public):
        raise AssertionError("public initial A/B training evidence mismatch")
    outputs={}
    for name,actor in actors.items():
        tick=time.perf_counter()
        outputs[name]=(graph.checkpoint(name,actor) if name=="graph_recent8"
                       else candidate.checkpoint(actor))
        times[name]+=time.perf_counter()-tick
    return outputs,tuple(public),times


def restored(name,payload):
    return graph.restore(name,payload) if name=="graph_recent8" else candidate.restore(name,payload)


def frozen(name,actor):
    return graph.checkpoint(name,actor) if name=="graph_recent8" else candidate.checkpoint(actor)


def challenge(name,postB,law,key,n):
    if law not in (*world.TRANSFER,*world.TRAIN) or type(n) is not int or n not in (2,4):
        raise ValueError("unfrozen common do-action challenge")
    actor=restored(name,postB)
    for i in range(n):
        for row in world.pair(law,key,f"challenge-{law}-{n}",i):
            actor.observe(world.copy_public(row))
    output=frozen(name,actor)
    if frozen(name,restored(name,output))!=output:
        raise AssertionError("cold challenge checkpoint changed")
    return output


def episode(name,payload,law,x,goal):
    actor=restored(name,payload)
    current=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(current))
    actions=[]
    for _ in range(2):
        a=actor.choose(world.copy_public(current))
        if a is None:break
        if a not in world.ACTIONS:raise AssertionError("unknown do-action")
        current=world.copy_public(world.do(law,current,a))
        actions.append(world.ACTIONS.index(a))
        actor.observe(world.copy_public(current))
    if len(actions)!=current["actions_taken"]:
        raise AssertionError("action budget violated")
    if current["reward"]>world.exact_oracle(law,x,goal)+1e-9:
        raise AssertionError("candidate exceeded optimal two-action policy")
    return current["reward"],int(tuple(current["mediators"])==tuple(goal)),actions


def score(name,postB,law,key,n):
    snap=challenge(name,postB,law,key,n)
    samples=admission.contexts(key,law,12)
    outcomes=[episode(name,snap,law,x,goal) for x,goal in samples]
    if frozen(name,restored(name,postB))!=postB:
        raise AssertionError("after-B checkpoint contaminated by evaluation")
    return {"reward":sum(v for v,_,_ in outcomes)/len(outcomes),
            "goal":sum(g for _,g,_ in outcomes)/len(outcomes),
            "action_trace_sha256":hashlib.sha256(
                controls.canonical([acts for _,_,acts in outcomes]).encode()
            ).hexdigest(),
            "checkpoint_bytes":len(snap.encode())}


def _mean(xs):
    if not xs:raise ValueError("empty metric")
    return sum(xs)/len(xs)


def run_fixture():
    prereg=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
    if (prereg["id"]!="AAI-11D" or prereg["science"]["used"] or
        prereg["science"]["first_use_authorized"]):
        raise PermissionError("AAI11D SCIENTIFIC FIRST USE DISARMED")
    ts={name:0. for name in ARMS}
    rewards={name:[] for name in ARMS}
    goals={name:[] for name in ARMS}
    traces=[]
    cold=[]
    start=time.perf_counter()
    for key in world.FIXTURES:
        saved,public,training_seconds=train(key)
        for name in ARMS:
            ts[name]+=training_seconds[name]
            if frozen(name,restored(name,saved[name]))!=saved[name]:
                raise AssertionError("training source changed")
        # Independent original qualified training generator must agree.
        original_post,original_rows,_=original_fixture.common_training(
            key,names=("graph_recent8",))
        if original_rows!=public or saved["graph_recent8"]!=original_post["graph_recent8"]:
            raise AssertionError("original strongest training conditions drifted")
        cold.append([key,*[hashlib.sha256(saved[name].encode()).hexdigest()
                            for name in ARMS]])
        for law in world.TRANSFER:
            for n in (2,4):
                for name in ARMS:
                    tick=time.perf_counter()
                    result=score(name,saved[name],law,key,n)
                    ts[name]+=time.perf_counter()-tick
                    rewards[name].append(result["reward"])
                    goals[name].append(result["goal"])
                    traces.append((key,law,n,name,result["action_trace_sha256"],
                                   round(result["reward"],9)))
    means={name:round(_mean(xs),9) for name,xs in rewards.items()}
    completion={name:round(_mean(xs),9) for name,xs in goals.items()}
    if abs(means["graph_recent8"]-PREVIOUS_STRONGEST)>1e-6:
        raise AssertionError("immutable strongest qualified baseline NOT reproduced")
    if len(traces)!=len(world.FIXTURES)*len(world.TRANSFER)*2*len(ARMS):
        raise AssertionError("incomplete public condition grid")
    gain=means["risk_calibrated_planner"]-means["graph_recent8"]
    risk_effect=means["risk_calibrated_planner"]-means["posterior_planner"]
    screen=(means["risk_calibrated_planner"]>=FIRST_MIN-1e-10 and
            completion["risk_calibrated_planner"]>=GOAL_MIN-1e-10 and
            risk_effect>=RISK_VS_POSTERIOR-1e-10)
    evidence={
        "schema":"yggdrasil.contrib.aai11d.source-fixture.v1",
        "phase":"MECHANICAL_ONLY_NO_SCIENTIFIC_COHORT",
        "status":"DEV_FIRST_SCREEN_PASS_REQUIRES_FULL_MATCHED_QUALIFICATION" if screen
                 else "DEV_NO_GO_NO_SCIENCE",
        "results":means,"exact_three_goal_success":completion,
        "historical_best":PREVIOUS_STRONGEST,
        "risk_vs_historical_best":round(gain,9),
        "risk_vs_posterior_ablation":round(risk_effect,9),
        "risk_gain_gate_0_08":gain>=.08-1e-10,
        "risk_goals_gate_0_60":completion["risk_calibrated_planner"]>=.60-1e-10,
        "risk_specific_gain_gate_0_03":risk_effect>=.03-1e-10,
        "condition_groups":len(traces)//len(ARMS),
        "episodes_per_arm":len(world.FIXTURES)*len(world.TRANSFER)*2*12,
        "fixture_names":list(world.FIXTURES),
        "public_training_rows_per_arm_per_fixture":64,
        "cost_train_plus_challenge_episodes_seconds":{k:round(v,6) for k,v in ts.items()},
        "source_checkpoint_sha256":hashlib.sha256(controls.canonical(cold).encode()).hexdigest(),
        "policy_trace_sha256":hashlib.sha256(controls.canonical(traces).encode()).hexdigest(),
        "science_cohorts_consumed":0,"native_model_changed":False,
        "qualified_full_11_controls":False
    }
    if screen:
        # After passing *all* cheap prereg gates, fully requalify original
        # 11 matched controls and A/B retention on same immutable fixtures.
        full=original_fixture.fixture_admission()
        best=max(graph.MATCHED,key=lambda k:full["all_method_reward"][k])
        strongest=full["all_method_reward"][best]
        fastest=min(graph.MATCHED,key=lambda k:
                    full["training_checkpoint_challenge_action_restore_wall_seconds_by_method"][k])
        benchmark_time=full["training_checkpoint_challenge_action_restore_wall_seconds_by_method"][fastest]
        time_ratio=ts["risk_calibrated_planner"]/max(benchmark_time,1e-12)
        familiar=[]
        for key in world.FIXTURES:
            saved,_,_=train(key)
            for law in world.TRAIN:
                for n in (2,4):
                    familiar.append(score("risk_calibrated_planner",saved["risk_calibrated_planner"],law,key,n)["reward"])
        result_familiar=_mean(familiar)
        secondary={
            "strongest_all_11_gain":means["risk_calibrated_planner"]>=strongest+.08-1e-10,
            "return_AB_noninferiority":result_familiar>=full["all_method_familiar"][best]-.03-1e-10,
            "two_x_whole_process":time_ratio<=2.
        }
        evidence["qualified_full_11_controls"]=True
        evidence["secondary"]={"strongest":best,"strongest_reward":strongest,
                                "fastest":fastest,"risk_over_fastest_process":round(time_ratio,6),
                                "candidate_familiar":round(result_familiar,9),
                                "baseline_familiar":full["all_method_familiar"][best],
                                "gates":secondary}
        evidence["status"]="DEV_ADMITTED_SCIENCE_UNVERIFIED" if all(secondary.values()) else "DEV_NO_GO_NO_SCIENCE"
    evidence["total_source_fixture_wall_seconds"]=round(time.perf_counter()-start,4)
    return evidence


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture-admission",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:
        p.error("AAI11D SCIENTIFIC FIRST USE DISARMED")
    if not args.fixture_admission:
        p.error("AAI-11D only three frozen mechanical fixture names are allowed")
    print("AAI11D_DEV="+json.dumps(run_fixture(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
