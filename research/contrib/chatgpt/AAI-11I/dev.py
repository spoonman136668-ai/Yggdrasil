"""AAI-11I one-shot disarmed source fixture test of causal feedback value.

The original eleven controls are already independently frozen and qualified.
This first screen evaluates actual independent do-outcomes for best graph_recent8,
identical-belief posterior8 ablation and novel outcome-conditioned planner.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
for p in ("AAI-11P","AAI-11A","AAI-11D","AAI-11F","AAI-11G"):
    sys.path.insert(0,str(HERE.parent/p))
sys.path.insert(0,str(HERE))
import world,controls,admission
import learner as graph
import fixture as original_fixture
import calibration as old_posterior
# The old and current evaluators are both named dev.py. Import the
# frozen predecessor under its *path*, never through ambiguous sys.path.
import importlib.util
_old_spec=importlib.util.spec_from_file_location(
    "_aai11d_frozen_source_dev",HERE.parent/"AAI-11D"/"dev.py")
old_dev=importlib.util.module_from_spec(_old_spec)
_old_spec.loader.exec_module(old_dev)
import audit
import admit as g_benchmark
import policy

GRAPH="graph_recent8"
POSTERIOR="posterior_planner"
CANDIDATE=policy.ARM
ARMS=(GRAPH,POSTERIOR,CANDIDATE)


def make(name):
    if name==GRAPH:return graph.GraphWindow(name)
    if name==POSTERIOR:return old_posterior.PosteriorCausalModel(name)
    if name==CANDIDATE:return policy.CausalFeedbackPlanner()
    raise ValueError("unregistered evidence-matched model")


def frozen(name,actor):
    if name==GRAPH:return graph.checkpoint(name,actor)
    if name==POSTERIOR:return old_posterior.checkpoint(actor)
    if name==CANDIDATE:return policy.checkpoint(actor)
    raise ValueError("bad frozen arm")


def restored(name,src):
    if name==GRAPH:return graph.restore(name,src)
    if name==POSTERIOR:return old_posterior.restore(name,src)
    if name==CANDIDATE:return policy.restore(src)
    raise ValueError("unknown public causal model")


def train(key):
    world.fixture(key)
    actors={name:make(name) for name in ARMS}
    evidence=[]
    times={name:0. for name in ARMS}
    for law,scope in (("A","train-initial"),("B","train-next")):
        for i in range(16):
            for row in world.pair(law,key,scope,i):
                evidence.append(row)
                for name,actor in actors.items():
                    tick=time.perf_counter()
                    actor.observe(world.copy_public(row))
                    times[name]+=time.perf_counter()-tick
    if len(evidence)!=64 or any(set(row)!=world.PUBLIC_KEYS for row in evidence):
        raise AssertionError("non-matched original public training")
    if actors[POSTERIOR].rows!=actors[CANDIDATE].rows:
        raise AssertionError("candidate or ablation observed different data")
    saved={}
    for name,actor in actors.items():
        tick=time.perf_counter()
        saved[name]=frozen(name,actor)
        if frozen(name,restored(name,saved[name]))!=saved[name]:
            raise AssertionError("public cold training changed")
        times[name]+=time.perf_counter()-tick
    verified,rows,_=old_dev.train(key)
    if (rows!=tuple(evidence) or
        saved[GRAPH]!=verified[GRAPH] or
        saved[POSTERIOR]!=verified[POSTERIOR]):
        raise AssertionError("original immutable conventional or posterior source drift")
    return saved,tuple(evidence),times


def challenge(name,postB,law,key,n):
    if law not in (*world.TRAIN,*world.TRANSFER) or type(n) is not int or n not in (2,4):
        raise ValueError("unfrozen common do-action challenge")
    actor=restored(name,postB)
    for i in range(n):
        for row in world.pair(law,key,f"challenge-{law}-{n}",i):
            actor.observe(world.copy_public(row))
    snap=frozen(name,actor)
    if frozen(name,restored(name,snap))!=snap:
        raise AssertionError("challenge checkpoint not cold reproducible")
    return snap


def episode(name,postChallenge,law,x,goal):
    actor=restored(name,postChallenge)
    row=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(row))
    actions=[]
    for _ in range(2):
        action=actor.choose(world.copy_public(row))
        if action is None:break
        if action not in world.ACTIONS:raise AssertionError("model invented do-action")
        row=world.copy_public(world.do(law,row,action))
        actions.append(world.ACTIONS.index(action))
        actor.observe(world.copy_public(row))
    if len(actions)!=row["actions_taken"]:
        raise AssertionError("unfrozen actual intervention count")
    if row["reward"]>world.exact_oracle(law,x,goal)+1e-9:
        raise AssertionError("model acted better than exact-law privileged oracle")
    return row["reward"],int(tuple(row["mediators"])==tuple(goal)),tuple(actions)


def mean(xs):
    if not xs:raise ValueError("empty model metric")
    return sum(xs)/len(xs)


def run_source_fixture():
    p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
    if (p["id"]!="AAI-11I" or p["science"]["used"]!=0 or
        p["science"]["first_use_authorized"]):
        raise PermissionError("AAI11I SCIENTIFIC FIRST USE DISARMED")
    screens=p["frozen_comparison"]["all_required_dev_gates"]
    if ARMS!=(GRAPH,POSTERIOR,policy.ARM):
        raise AssertionError("unfrozen comparison source")
    totals={name:[] for name in ARMS}
    familiar={name:[] for name in ARMS}
    elapsed={name:0. for name in ARMS}
    receipts=[]
    trace=[]
    for key in world.FIXTURES:
        saved,public,cost=train(key)
        for name in ARMS:
            elapsed[name]+=cost[name]
        receipts.append([key,*[hashlib.sha256(saved[name].encode()).hexdigest()
                                for name in ARMS]])
        for law in world.TRANSFER:
            positions=admission.contexts(key,law,12)
            # PRIVILEGED evaluator ONLY: never supplied to make/observe/choose.
            metadata=[(int(tuple(goal) in audit.closure(law,x)[1]),
                       world.exact_oracle(law,x,goal))
                      for x,goal in positions]
            for budget in (2,4):
                snap={}
                for name in ARMS:
                    t=time.perf_counter()
                    snap[name]=challenge(name,saved[name],law,key,budget)
                    elapsed[name]+=time.perf_counter()-t
                if restored(POSTERIOR,snap[POSTERIOR]).rows!=restored(CANDIDATE,snap[CANDIDATE]).rows:
                    raise AssertionError("matched public information changed after challenge")
                for name in ARMS:
                    for (x,goal),(reachable,oracle_reward) in zip(positions,metadata):
                        t=time.perf_counter()
                        reward,hit,actions=episode(name,snap[name],law,x,goal)
                        elapsed[name]+=time.perf_counter()-t
                        totals[name].append({"law":law,"reward":reward,
                                             "goal_correct":hit,"oracle_reachable":reachable,
                                             "oracle_reward":oracle_reward,"actions":len(actions)})
                        trace.append((key,law,budget,name,list(x),list(goal),
                                      reachable,round(reward,9),hit,list(actions)))
        # Familiar cold A/B retention, exactly source 11G same contexts.
        for law in world.TRAIN:
            positions=admission.contexts(key,law,12)
            for budget in (2,4):
                for name in ARMS:
                    t=time.perf_counter()
                    snap=challenge(name,saved[name],law,key,budget)
                    for x,goal in positions:
                        reward,_,_=episode(name,snap,law,x,goal)
                        familiar[name].append(reward)
                    elapsed[name]+=time.perf_counter()-t
        for name in ARMS:
            if frozen(name,restored(name,saved[name]))!=saved[name]:
                raise AssertionError("independent evaluation contaminated A/B source")
    if any(len(totals[n])!=288 or len(familiar[n])!=144 for n in ARMS):
        raise AssertionError("incomplete original transfer or familiar evaluations")
    metrics={name:g_benchmark.finalize_method(totals[name],144,144) for name in ARMS}
    familiar_means={name:round(mean(familiar[name]),9) for name in ARMS}
    if (abs(metrics[GRAPH]["reward"]-2.134027778)>1e-6 or
        abs(metrics[POSTERIOR]["reward"]-2.189756944)>1e-6 or
        metrics[GRAPH]["reachable_goals_hit"]!=108 or
        metrics[POSTERIOR]["reachable_goals_hit"]!=117 or
        abs(familiar_means[GRAPH]-2.210416667)>1e-6):
        raise AssertionError("previous fully matched eleven-control or posterior8 qualification drift")
    cand=metrics[CANDIDATE]
    tests={
        "reward_ge_original_strongest_plus_0_08":
            cand["reward"]>=screens["candidate_reward_min"]-1e-10,
        "reachable_goal_recovery_ge_0_80":
            cand["oracle_normalized_reachable_goal_recovery"]>=
            screens["candidate_reachable_goal_recovery_min"]-1e-10,
        "gain_vs_same_eight_row_posterior_ge_0_03":
            cand["reward"]-metrics[POSTERIOR]["reward"]>=
            screens["candidate_gain_vs_same_belief_open_loop_posterior_min"]-1e-10,
        "unreachable_oracle_regret_noninferior":
            cand["unreachable_regret"]<=screens["candidate_unreachable_regret_max"]+1e-10,
        "cold_familiar_AB_reward_noninferior":
            familiar_means[CANDIDATE]>=screens["candidate_familiar_return_min"]-1e-10
    }
    eligible=all(tests.values())
    out={
        "schema":"yggdrasil.contrib.aai11i.source-mechanical.v1",
        "classification":"DEV_FIRST_SCREEN_PASS_REQUIRES_FULL_MATCHED_COST" if eligible
                          else "DEV_NO_GO_NO_SCIENCE",
        "gates":tests,"scores":metrics,"familiar_AB_actual_return":familiar_means,
        "candidate_gain_vs_strongest":round(cand["reward"]-metrics[GRAPH]["reward"],9),
        "candidate_gain_vs_original_posterior":round(cand["reward"]-metrics[POSTERIOR]["reward"],9),
        "candidate_reachable_goals":cand["reachable_goals_hit"],
        "oracle_reachable_denominator":144,
        "whole_source_fixture_process_seconds":{name:round(elapsed[name],6)
                                                 for name in ARMS},
        "all_11_conventional_rerun":False,
        "actual_action_reward_trace_sha256":g_benchmark.digest(trace),
        "public_training_checkpoint_sha256":g_benchmark.digest(receipts),
        "real_transfer_episodes_per_arm":288,
        "real_familiar_episodes_per_arm":144,
        "science_cohorts_used":0,
        "native_model_changed":False
    }
    if eligible:
        full=g_benchmark.run_benchmark()
        if full["classification"]!="BENCHMARK_QUALIFIED_FOR_PROSPECTIVE_SOURCE_DEV":
            raise AssertionError("G conventional benchmark source drift")
        fastest=full["fastest_measured_conventional"]
        fastest_cost=full["source_fixture_training_plus_cold_execution_seconds"][fastest]
        ratio=elapsed[CANDIDATE]/max(fastest_cost,1e-9)
        passed=ratio<=2.
        out["all_11_conventional_rerun"]=True
        out["full_matched"]={"fastest_control":fastest,
                             "cost_ratio_to_fastest":round(ratio,6),
                             "max_cost_ratio":2.,"cost_gate_pass":passed}
        out["classification"]="DEV_ADMITTED_SCIENCE_UNVERIFIED" if passed else "DEV_NO_GO_NO_SCIENCE"
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--fixture-admission",action="store_true")
    a.add_argument("--primary",action="store_true")
    args=a.parse_args()
    if args.primary:a.error("AAI11I SCIENTIFIC FIRST USE DISARMED")
    if not args.fixture_admission:
        a.error("only the original three mechanical fixture names admitted")
    print("AAI11I_DEV="+json.dumps(run_source_fixture(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
