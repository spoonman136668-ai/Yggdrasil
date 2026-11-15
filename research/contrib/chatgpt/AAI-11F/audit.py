"""AAI-11F independent exact two-intervention oracle feasibility audit.

EVALUATOR ONLY. Use exact frozen original AAI-11P world and source-selected
mechanical contexts, never a learner or reserved scientific cohort. Calculate
whether the frozen 60% exact THREE-bit success gate is even achievable.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world,admission
import controls

EXPECTED_UNIQUE=144
EXPECTED_POSITIVE_UNIQUE=72
EXPECTED_EPISODES=288
EXPECTED_POSITIVE_EPISODES=144
EXPECTED_ORACLE_MEAN=2.448263889
ORIGINAL_GOAL_SUCCESS_GATE=.60


def sequences(law,x,goal):
    """Exhaust all ordered 0/1/2 do-action sequences AND their actual costs."""
    x=world.bits(x,6)
    goal=world.bits(goal,3)
    candidates=[(x,0)]
    for first in world.ACTIONS:
        x1=world.setbit(x,first)
        candidates.append((x1,1))
        for second in world.ACTIONS:
            x2=world.setbit(x1,second)
            candidates.append((x2,2))
    if len(candidates)!=1+12+144:
        raise AssertionError("incorrect exhaustive action sequence space")
    result=set()
    reward_optimum=float("-inf")
    optimum_can_match_goal=False
    min_actions_for_goal=None
    for state,steps in candidates:
        mediator=world.intermediates(law,state)
        result.add(mediator)
        value=world.reward(mediator,goal,steps)
        achieved=(mediator==goal)
        if achieved and (min_actions_for_goal is None or steps<min_actions_for_goal):
            min_actions_for_goal=steps
        if value>reward_optimum+1e-12:
            reward_optimum=value
            optimum_can_match_goal=achieved
        elif abs(value-reward_optimum)<=1e-12 and achieved:
            optimum_can_match_goal=True
    return {
        "attainable":int(min_actions_for_goal is not None),
        "min_actions":min_actions_for_goal,
        "reward_best":reward_optimum,
        "best_reward_has_goal":int(optimum_can_match_goal),
        "reachable_outcomes":result,
    }


def closure(law,x):
    """Independent 0->1->2 bounded state-set BFS, not sequence-score logic."""
    x=world.bits(x,6)
    depths=[{x}]
    for depth in (1,2):
        newest=set()
        for previous in depths[depth-1]:
            for a in world.ACTIONS:
                newest.add(world.setbit(previous,a))
        depths.append(newest)
    outcomes=set()
    for depth_states in depths:
        for state in depth_states:
            outcomes.add(world.intermediates(law,state))
    if not depths[0] or any(not set(depths[i-1]).issubset(depths[i]) for i in (1,2)):
        raise AssertionError("bounded do-state reachability is not monotonic")
    return depths,outcomes


def independent_goal_rate(law):
    """Full 64 public inputs x 8 goals structural ceiling, not a science trial."""
    success=0
    for x in world.INPUTS:
        _,outcomes=closure(law,x)
        for goal in world.GOALS:
            success+=int(goal in outcomes)
    return success, len(world.INPUTS)*len(world.GOALS)


def mechanical_audit():
    p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
    if p["id"]!="AAI-11F" or p["science"]["used"]!=0 or p["science"]["first_use_authorized"]:
        raise PermissionError("AAI11F SCIENTIFIC FIRST USE DISARMED")
    if len(world.INPUTS)!=64 or len(world.GOALS)!=8 or len(world.ACTIONS)!=12:
        raise AssertionError("frozen world shape changed")
    if world.TRANSFER!=("C","D","E","F") or world.FIXTURES!=(
        "mechanical:alpha","mechanical:beta","mechanical:gamma"):
        raise AssertionError("original frozen transfer labels or fixture names changed")
    if p["prespecified_gate"]["original_threshold"]!=ORIGINAL_GOAL_SUCCESS_GATE:
        raise AssertionError("frozen original gate changed")

    contexts_unique=[]
    all_episodes=[]
    oracle_values=[]
    by_law=collections.defaultdict(lambda:{"n":0,"reachable":0})
    by_fixture=collections.defaultdict(lambda:{"n":0,"reachable":0})
    min_actions=collections.Counter()
    for key in world.FIXTURES:
        world.fixture(key)
        for law in world.TRANSFER:
            contexts=admission.contexts(key,law,12)
            if len(contexts)!=12 or len(set(contexts))!=12:
                raise AssertionError("original unique source contexts changed")
            for x,goal in contexts:
                exhaustive=sequences(law,x,goal)
                depths,reachable=closure(law,x)
                if exhaustive["reachable_outcomes"]!=reachable:
                    raise AssertionError("two independent do-action solvers disagree")
                if exhaustive["attainable"]!=int(goal in reachable):
                    raise AssertionError("exact-goal feasibility disagrees across solvers")
                if exhaustive["best_reward_has_goal"]!=exhaustive["attainable"]:
                    raise AssertionError("cost-sensitive optimal reward conflicts with exact attainable goal")
                original=world.exact_oracle(law,x,goal)
                if abs(exhaustive["reward_best"]-original)>1e-10:
                    raise AssertionError("original exact two-action reward oracle drifted")
                # Original AAI-11P selection has EXACT same public x,goal
                # for challenge budget 2 and 4. Neither gives more than two
                # do-actions in an independent evaluation episode.
                record=[key,law,list(x),list(goal),exhaustive["attainable"],
                        exhaustive["min_actions"],round(original,9)]
                contexts_unique.append(record)
                for n in (2,4):
                    all_episodes.append([key,law,n,list(x),list(goal),
                                         exhaustive["attainable"]])
                    oracle_values.append(original)
                by_law[law]["n"]+=1
                by_law[law]["reachable"]+=exhaustive["attainable"]
                by_fixture[key]["n"]+=1
                by_fixture[key]["reachable"]+=exhaustive["attainable"]
                min_actions["impossible" if exhaustive["min_actions"] is None
                            else str(exhaustive["min_actions"])]+=1

    reachable_unique=sum(z[4] for z in contexts_unique)
    reachable_episodes=sum(z[5] for z in all_episodes)
    oracle_mean=sum(oracle_values)/len(oracle_values)
    if len(contexts_unique)!=EXPECTED_UNIQUE or len(all_episodes)!=EXPECTED_EPISODES:
        raise AssertionError("original three-fixture evaluation budget drift")
    if reachable_unique!=EXPECTED_POSITIVE_UNIQUE or reachable_episodes!=EXPECTED_POSITIVE_EPISODES:
        raise AssertionError("pre-audit independent source enumeration not reproduced")
    if abs(oracle_mean-EXPECTED_ORACLE_MEAN)>1e-6:
        raise AssertionError("previously qualified original oracle reward not reproduced")
    if any(by_law[law]["n"]!=36 for law in world.TRANSFER):
        raise AssertionError("unfrozen law counts")
    if any(by_fixture[key]["n"]!=48 for key in world.FIXTURES):
        raise AssertionError("unfrozen fixture counts")

    full={law:independent_goal_rate(law) for law in world.TRANSFER}
    goal_fraction=reachable_episodes/len(all_episodes)
    min_pass_count=math.ceil(ORIGINAL_GOAL_SUCCESS_GATE*len(all_episodes)-1e-12)
    classification=("BENCHMARK_GOAL_GATE_IMPOSSIBLE" if goal_fraction<ORIGINAL_GOAL_SUCCESS_GATE
                    else "ORIGINAL_GOAL_GATE_FEASIBLE")
    return {
        "schema":"yggdrasil.contrib.aai11f.oracle-ceiling-audit.v1",
        "status":"ENGINEERING_DIAGNOSTIC_SOURCE_ONLY_NO_SCIENCE",
        "classification":classification,
        "original_goal_success_threshold":ORIGINAL_GOAL_SUCCESS_GATE,
        "exact_goal_oracle_upper_bound":round(goal_fraction,9),
        "total_original_evaluation_episodes":len(all_episodes),
        "unique_original_contexts":len(contexts_unique),
        "exact_goal_attainable_episodes":reachable_episodes,
        "exact_goal_unattainable_episodes":len(all_episodes)-reachable_episodes,
        "frozen_60_percent_minimum_successes":min_pass_count,
        "unattainable_required_additional_successes":max(0,min_pass_count-reachable_episodes),
        "original_exact_two_action_oracle_mean_reward":round(oracle_mean,9),
        "per_law_unique_contexts":dict(by_law),
        "per_fixture_unique_contexts":dict(by_fixture),
        "minimum_actions_to_exact_goal_for_unique_contexts":dict(sorted(min_actions.items())),
        "full_64x8_goal_structural_ceiling":{
            law:{"reachable":n,"total":total,"fraction":round(n/total,9)}
            for law,(n,total) in full.items()
        },
        "historical_goal_success":{"original_graph_recent8":.375,
                                   "AAI11D_posterior_only":.40625,
                                   "AAI11D_risk_policy":.388888889},
        "first_use_disarmed":True,
        "reserved_cohorts_consumed":0,
        "new_learners_trained":0,
        "source_only":True,
        "original_benchmark_oracle_reward_verified":True,
        "two_independent_reachability_algorithms_agree":True,
        "source_context_deterministic_digest_sha256":hashlib.sha256(
            controls.canonical(contexts_unique).encode("utf8")).hexdigest(),
        "full_episode_feasibility_digest_sha256":hashlib.sha256(
            controls.canonical(all_episodes).encode("utf8")).hexdigest()
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--mechanical-oracle-audit",action="store_true")
    a.add_argument("--primary",action="store_true")
    args=a.parse_args()
    if args.primary:
        a.error("AAI11F SCIENTIFIC FIRST USE DISARMED")
    if not args.mechanical_oracle_audit:
        a.error("only original three frozen source mechanical fixtures are supported")
    print("AAI11F_AUDIT="+json.dumps(mechanical_audit(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
