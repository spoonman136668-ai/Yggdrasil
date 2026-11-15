"""AAI-11H mechanical source-only admission for novel changepoint learner.

Follows frozen AAI-11G actual reward, attainable-goal recovery, impossible-goal
regret, A/B cold retention and resource-aware sequential stop. --primary forbidden.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
for folder in ("AAI-11P","AAI-11A","AAI-11D","AAI-11F","AAI-11G"):
    sys.path.insert(0,str(HERE.parent/folder))
sys.path.insert(0,str(HERE))
import world,controls,admission
import learner as graph
import fixture as original_fixture
import calibration as old_posterior
import audit as original_oracle
import admit as G_benchmark
import causal

ARMS=("graph_recent8","posterior_planner",*causal.ARMS)
NEW=causal.ARMS[1]
ABLATION=causal.ARMS[0]
OLD_POSTERIOR="posterior_planner"
STRONGEST="graph_recent8"
ORIGINAL_STRONGEST_REWARD=2.134027778
ORIGINAL_OLD_POSTERIOR_REWARD=2.189756944
ORIGINAL_STRONGEST_GOAL_RECOVERY=.75
ORIGINAL_OLD_POSTERIOR_GOAL_RECOVERY=.8125


def make(name):
    if name==STRONGEST:
        return graph.GraphWindow(STRONGEST)
    if name==OLD_POSTERIOR:
        return old_posterior.PosteriorCausalModel(name)
    return causal.RunLengthCausalPosterior(name)


def frozen(name,actor):
    if name==STRONGEST:
        return graph.checkpoint(name,actor)
    if name==OLD_POSTERIOR:
        return old_posterior.checkpoint(actor)
    return causal.checkpoint(actor)


def restored(name,payload):
    if name==STRONGEST:
        return graph.restore(name,payload)
    if name==OLD_POSTERIOR:
        return old_posterior.restore(name,payload)
    return causal.restore(name,payload)


def train(key):
    world.fixture(key)
    actors={name:make(name) for name in ARMS}
    data=[]
    elapsed={name:0. for name in ARMS}
    for law,phase in (("A","train-initial"),("B","train-next")):
        for i in range(16):
            for event in world.pair(law,key,phase,i):
                data.append(event)
                for name,actor in actors.items():
                    mark=time.perf_counter()
                    actor.observe(world.copy_public(event))
                    elapsed[name]+=time.perf_counter()-mark
    if len(data)!=64 or any(set(e)!=world.PUBLIC_KEYS for e in data):
        raise AssertionError("original common public data budget changed")
    saved={}
    for name,actor in actors.items():
        mark=time.perf_counter()
        saved[name]=frozen(name,actor)
        if frozen(name,restored(name,saved[name]))!=saved[name]:
            raise AssertionError("source public cold checkpoint drift")
        elapsed[name]+=time.perf_counter()-mark
    if actors[ABLATION].rows!=actors[NEW].rows or len(actors[NEW].rows)!=16:
        raise AssertionError("candidate and ablation public memory inequivalent")
    old_source,old_rows,_=original_fixture.common_training(
        key,names=(STRONGEST,))
    if old_rows!=tuple(data) or old_source[STRONGEST]!=saved[STRONGEST]:
        raise AssertionError("original strongest public training/provenance changed")
    return saved,tuple(data),elapsed


def challenge(name,afterB,law,key,n):
    if law not in (*world.TRAIN,*world.TRANSFER) or type(n) is not int or n not in (2,4):
        raise ValueError("unapproved challenge scope")
    actor=restored(name,afterB)
    for i in range(n):
        for event in world.pair(law,key,f"challenge-{law}-{n}",i):
            actor.observe(world.copy_public(event))
    checkpoint=frozen(name,actor)
    if frozen(name,restored(name,checkpoint))!=checkpoint:
        raise AssertionError("challenge cold restore changed")
    return checkpoint


def episode(name,source,law,x,goal):
    actor=restored(name,source)
    row=world.copy_public(world.start(law,x,goal))
    actor.observe(world.copy_public(row))
    actions=[]
    for _ in range(2):
        action=actor.choose(world.copy_public(row))
        if action is None:
            break
        if action not in world.ACTIONS:
            raise AssertionError("illegal public causal action")
        row=world.copy_public(world.do(law,row,action))
        actions.append(world.ACTIONS.index(action))
        actor.observe(world.copy_public(row))
    if len(actions)!=row["actions_taken"]:
        raise AssertionError("action budget drift")
    return row["reward"],int(tuple(row["mediators"])==tuple(goal)),tuple(actions)


def _mean(xs):
    if not xs:raise ValueError("empty metric")
    return sum(xs)/len(xs)


def run_fixture():
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (p["id"]!="AAI-11H" or p["science"]["used"] or
        p["science"]["first_use_authorized"]):
        raise PermissionError("AAI11H SCIENTIFIC FIRST USE DISARMED")
    if ARMS!=(STRONGEST,OLD_POSTERIOR,*causal.ARMS) or len(world.FIXTURES)!=3:
        raise AssertionError("original frozen comparative methods changed")
    screen=p["frozen_trial"]["preregistered_screen"]
    totals={name:[] for name in ARMS}
    retain={name:[] for name in ARMS}
    trace=[]
    cold_receipts=[]
    spent={name:0. for name in ARMS}
    source_rows=0
    for key in world.FIXTURES:
        saved,public,training_times=train(key)
        source_rows+=len(public)
        for name in ARMS:
            spent[name]+=training_times[name]
        cold_receipts.append([key,*[hashlib.sha256(saved[name].encode()).hexdigest() for name in ARMS]])
        for law in world.TRANSFER:
            original_contexts=admission.contexts(key,law,12)
            privileged=[(int(tuple(goal) in original_oracle.closure(law,x)[1]),
                         world.exact_oracle(law,x,goal))
                        for x,goal in original_contexts]
            for n in (2,4):
                snaps={}
                for name in ARMS:
                    tick=time.perf_counter()
                    snaps[name]=challenge(name,saved[name],law,key,n)
                    spent[name]+=time.perf_counter()-tick
                if restored(NEW,snaps[NEW]).rows!=restored(ABLATION,snaps[ABLATION]).rows:
                    raise AssertionError("matched candidate/ablation challenge evidence drift")
                for name in ARMS:
                    for (x,goal),(possible,oracle_reward) in zip(original_contexts,privileged):
                        tick=time.perf_counter()
                        reward,success,actions=episode(name,snaps[name],law,x,goal)
                        spent[name]+=time.perf_counter()-tick
                        totals[name].append({"law":law,"reward":reward,
                                             "goal_correct":success,"oracle_reachable":possible,
                                             "oracle_reward":oracle_reward,"actions":len(actions)})
                        trace.append([key,law,n,name,list(x),list(goal),
                                      int(possible),round(reward,9),success,list(actions)])
        # Frozen A/B retention from exact cold post-B source, separate diagnostic.
        for law in world.TRAIN:
            positions=admission.contexts(key,law,12)
            for n in (2,4):
                for name in ARMS:
                    tick=time.perf_counter()
                    snap=challenge(name,saved[name],law,key,n)
                    for x,goal in positions:
                        r,_,_=episode(name,snap,law,x,goal)
                        retain[name].append(r)
                    spent[name]+=time.perf_counter()-tick
        for name in ARMS:
            if frozen(name,restored(name,saved[name]))!=saved[name]:
                raise AssertionError("A/B source changed after independent episodes")
    if source_rows!=3*64 or any(len(totals[name])!=288 for name in ARMS):
        raise AssertionError("unfrozen development episode count")
    metrics={name:G_benchmark.finalize_method(totals[name],144,144) for name in ARMS}
    familiar={name:round(_mean(retain[name]),9) for name in ARMS}
    if (abs(metrics[STRONGEST]["reward"]-ORIGINAL_STRONGEST_REWARD)>1e-6 or
        abs(metrics[OLD_POSTERIOR]["reward"]-ORIGINAL_OLD_POSTERIOR_REWARD)>1e-6 or
        abs(metrics[STRONGEST]["oracle_normalized_reachable_goal_recovery"]-.75)>1e-9 or
        abs(metrics[OLD_POSTERIOR]["oracle_normalized_reachable_goal_recovery"]-.8125)>1e-9):
        raise AssertionError("original qualified strongest or previous posterior scores drifted")
    candidate=metrics[NEW]
    tests={
        "candidate_reward_ge_strongest_plus_0_08":
            candidate["reward"]>=screen["candidate_actual_reward_min"]-1e-10,
        "candidate_reachable_goal_recovery_ge_0_80":
            candidate["oracle_normalized_reachable_goal_recovery"]>=
            screen["candidate_oracle_reachable_recovery_min"]-1e-10,
        "adaptive_runlength_reward_ge_fixed16_plus_0_03":
            candidate["reward"]-metrics[ABLATION]["reward"]>=
            screen["candidate_gain_over_same_memory_fixed16_min"]-1e-10,
        "adaptive_reward_ge_posterior8_plus_0_03":
            candidate["reward"]-metrics[OLD_POSTERIOR]["reward"]>=
            screen["candidate_gain_over_original_posterior8_min"]-1e-10,
        "unreachable_goals_regret_safe":
            candidate["unreachable_regret"]<=screen["candidate_unreachable_regret_max"]+1e-10,
        "A_B_return_retention_safe":
            familiar[NEW]>=screen["candidate_familiar_AB_return_min"]-1e-10
    }
    eligible=all(tests.values())
    result={
        "schema":"yggdrasil.contrib.aai11h.source-mechanical-dev.v1",
        "status":"DEV_FIRST_SCREEN_PASS_REQUIRES_FULL_MATCHED_COST" if eligible
                 else "DEV_NO_GO_NO_SCIENCE",
        "checks":tests,
        "metrics":metrics,"familiar_AB_reward":familiar,
        "candidate_minus_strongest_reward":round(candidate["reward"]-
                                                    metrics[STRONGEST]["reward"],9),
        "candidate_minus_fixed16_reward":round(candidate["reward"]-
                                                  metrics[ABLATION]["reward"],9),
        "candidate_minus_posterior8_reward":round(candidate["reward"]-
                                                    metrics[OLD_POSTERIOR]["reward"],9),
        "candidate_exact_goal_recovered":candidate["reachable_goals_hit"],
        "oracle_reachable_denominator":144,
        "source_fixture_train_challenge_restore_action_seconds":{
            name:round(spent[name],6) for name in ARMS},
        "trace_sha256":G_benchmark.digest(trace),
        "cold_training_snapshot_sha256":G_benchmark.digest(cold_receipts),
        "evaluations_per_arm":288,
        "familiar_episodes_per_arm":144,
        "scientific_cohorts_used":0,
        "new_native_model_changed":False,
        "all_11_conventional_new_run":False
    }
    if eligible:
        full=G_benchmark.run_benchmark()
        if full["classification"]!="BENCHMARK_QUALIFIED_FOR_PROSPECTIVE_SOURCE_DEV":
            raise AssertionError("G baseline no longer source qualified")
        fastest=full["fastest_measured_conventional"]
        original_time=full["source_fixture_training_plus_cold_execution_seconds"][fastest]
        ratio=spent[NEW]/max(original_time,1e-9)
        ok_ratio=ratio<=2.
        result["all_11_conventional_new_run"]=True
        result["final_matched"]={
            "strongest_reward":full["strongest_reward_control"],
            "best_recovery":full["best_conditional_success_control"],
            "fastest_control":fastest,
            "cost_ratio_candidate_to_fastest":round(ratio,6),
            "full_process_cost_le_2x":ok_ratio
        }
        result["status"]="DEV_ADMITTED_SCIENCE_UNVERIFIED" if ok_ratio else "DEV_NO_GO_NO_SCIENCE"
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture-admission",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("AAI11H SCIENTIFIC FIRST USE DISARMED")
    if not args.fixture_admission:
        p.error("only original three frozen mechanical source fixture names allowed")
    print("AAI11H_DEV="+json.dumps(run_fixture(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
