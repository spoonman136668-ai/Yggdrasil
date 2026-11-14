"""WSP95 frozen noisy causal sensor source learning and action planning.

All methods' plan outputs are SHA256-frozen BEFORE reading true hidden
channels/signatures or executing 2/3-action target goals. Public tests never
instantiate any reserved world.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import NoisyWorld,N_ACTIONS,N_CHANNELS,N_CAUSAL,seeded
from weights import (DirectCounts,SymbolicHistogram,FullyTrainedLogistic,
                     WrongActionAssociation,canonical,sha,plan_from_estimates)

PROTOCOL=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
FROZEN=PROTOCOL["frozen"]
METHODS=("direct_active","independent_symbolic","fully_trained_logistic",
         "direct_uniform","direct_random_probing","wrong_action_binding","oracle_ceiling")

def get_policy_observations(world:NoisyWorld, policy:str):
    actions=world.actions
    direct=DirectCounts(actions)
    observed=[]
    order_rng=seeded(f"WSP95/random-probe-order/{world.seed}")
    for trial in range(30):
        if policy=="active":
            action=direct.choose_action()
        elif policy=="uniform":
            action=actions[trial%N_ACTIONS]
        elif policy=="random":
            action=order_rng.choice(actions)
        else:
            raise ValueError("unregistered policy")
        # Potential observations are precommitted solely by
        # (world, action, within-action index), not influenced by allocation.
        sample=world.probe(action,direct.n[action])
        direct.observe(sample)
        observed.append(sample)
    if direct.interventions!=30:
        raise AssertionError("policy original action budget discrepancy")
    return direct,tuple(observed)

def original_world(seed:int)->dict:
    start=time.process_time_ns()
    world=NoisyWorld(seed)
    t=time.process_time_ns()
    active,source=get_policy_observations(world,"active")
    fit_direct_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    uniform,uniform_source=get_policy_observations(world,"uniform")
    fit_uniform_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    random_policy,random_source=get_policy_observations(world,"random")
    fit_random_cpu=time.process_time_ns()-t
    # Confirm paired common-random potential observations for identical
    # (action, probe index) across policies; no posthoc source substitution.
    active_map={(r["action_id"],r["probe_index"]):(r["sensor_before"],r["sensor_after"])
                for r in source}
    for row in uniform_source+random_source:
        key=(row["action_id"],row["probe_index"])
        if key in active_map and active_map[key]!=(row["sensor_before"],row["sensor_after"]):
            raise AssertionError("unpaired potential observation source")
    t=time.process_time_ns()
    symbolic=SymbolicHistogram(world.actions)
    for row in source:symbolic.observe(row)
    symbolic_fit_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    logistic=FullyTrainedLogistic(world.actions)
    logistic.fit(source)
    logistic_fit_cpu=time.process_time_ns()-t
    wrong=WrongActionAssociation(active)
    if active.stable_channels()!=symbolic.stable():
        raise AssertionError("independent symbolic's learned mask differs")
    # All 35 goals are fresh combinations. No method receives
    # hidden world mapping, hidden channel list or original generating subset.
    goals=world.goals()
    if len(goals)!=35:raise AssertionError("missing two/three-action goals")
    request_sha=sha([g.request() for g in goals])
    plan_methods={
        "direct_active":active,
        "independent_symbolic":symbolic,
        "fully_trained_logistic":logistic,
        "direct_uniform":uniform,
        "direct_random_probing":random_policy,
        "wrong_action_binding":wrong,
    }
    predictions={}
    planning_cpu={}
    for name,method in plan_methods.items():
        tick=time.process_time_ns()
        predictions[name]=tuple(method.plan(world.actions,req["start"],req["target"],
                                           req["max_actions"])
                                for req in (g.request() for g in goals))
        planning_cpu[name]=time.process_time_ns()-tick
    original_predictions_sha=sha({
        "world_seed":seed,
        "observations":{p:sha(rows) for p,rows in
                        (("active",source),("uniform",uniform_source),
                         ("random",random_source))},
        "goal_requests_sha256":request_sha,
        "predictions":predictions,
    })
    snap=active.snapshot()
    restored=DirectCounts.restore(snap)
    cold_exact=(snap==restored.snapshot() and
                tuple(restored.plan(world.actions,g.start,g.target,g.max_actions)
                      for g in goals)==predictions["direct_active"])
    tampered=json.loads(snap)
    a=next(iter(tampered["payload"]["counts"]))
    tampered["payload"]["counts"][a][0]=(
        tampered["payload"]["counts"][a][0]+1)%31
    try:
        DirectCounts.restore(json.dumps(tampered))
        tamper=False
    except ValueError:
        tamper=True
    unknown="f"*16
    while unknown in world.actions:unknown="e"*16
    unknown_abstains=(active.plan(world.actions[:-1]+(unknown,),0,1,3) is None)
    # The hidden truth is inspected ONLY AFTER all model plans were committed
    # above and cold restore/tamper checks are complete.
    causal_mask=world.actual_causal_channels()
    true_effects={a:world.actual_signature(a) for a in world.actions}
    oracle=tuple(plan_from_estimates(true_effects,world.actions,
                     g.start,g.target,g.max_actions) for g in goals)
    predictions["oracle_ceiling"]=oracle
    planning_cpu["oracle_ceiling"]=0
    scores={method:sum(
        world.execute(g.start,p)==g.target
        for g,p in zip(goals,plan))
        for method,plan in predictions.items()}
    per_action_bits=sum(
       sum(((estimated_effects.get(a,0)>>bit)&1)==((true_effects[a]>>bit)&1)
            for bit in range(N_CHANNELS))
       for a in world.actions
       for estimated_effects in (active.effects(),))
    conventional_bit_fit=sum(
       sum(((logistic.effects().get(a,0)>>bit)&1)==((true_effects[a]>>bit)&1)
           for bit in range(N_CHANNELS))
       for a in world.actions)
    mask_exact=set(active.stable_channels())==set(causal_mask)
    signal_noise={
        "stable_channel_count":N_CAUSAL,
        "stable_channels_inferred":list(active.stable_channels()),
        "stable_channels_true_audit":list(causal_mask),
        "noise_rate":PROTOCOL["world"]["noise_prob_12percent"],
    }
    return {
        "seed":seed,
        "world_audit_sha256":world.audit_fingerprint(),
        "sources_sha256":{
            "active":sha(source),
            "uniform":sha(uniform_source),
            "random":sha(random_source)},
        "goal_requests_sha256":request_sha,
        "model_predictions_pre_outcome_sha256":original_predictions_sha,
        "goals":len(goals),
        "actual_probes_by_policy":{
            "active":len(source),"uniform":len(uniform_source),
            "random":len(random_source)},
        "per_action_probe_counts":{
            "active":dict(active.n),"uniform":dict(uniform.n),
            "random":dict(random_policy.n)},
        "successes":scores,
        "true_signature_bits_correct":{
            "direct_active":per_action_bits,"conventional":conventional_bit_fit},
        "true_signature_bits_total":N_ACTIONS*N_CHANNELS,
        "stable_channel_exact":mask_exact,
        "model_cold_restore":cold_exact,
        "tamper_rejected":tamper,
        "unknown_action_abstention":unknown_abstains,
        "numeric_weight_slots":N_ACTIONS*N_CHANNELS*2,
        "resource_ns":{
            "direct_active_fit":fit_direct_cpu,
            "direct_uniform_fit":fit_uniform_cpu,
            "direct_random_fit":fit_random_cpu,
            "independent_symbolic_fit":symbolic_fit_cpu,
            "ordinary_trained_logistic_fit":logistic_fit_cpu,
            "plans":planning_cpu,
            "whole":time.process_time_ns()-start
        },
        "diagnostic_sensor_audit":signal_noise,
    }

def evaluate(*,reserved:bool)->dict:
    clock=time.process_time_ns()
    seeds=(PROTOCOL["world"]["reserved_dev_seeds"] if reserved
           else PROTOCOL["world"]["public_seeds"])
    if len(seeds)!=len(set(seeds)):
        raise ValueError("duplicate first-use world seed")
    results=tuple(original_world(seed) for seed in seeds)
    total={key:sum(x["successes"][key] for x in results) for key in METHODS}
    return {
        "schema":"wsp95.noisy-partial-sensor-causal-development.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_ORIGINAL_DEVELOPMENT",
        "protocol_sha":"5b9bf6780a2073ed3223892ca0582cfdc1288d8f",
        "world_count":len(seeds),
        "seed_list":list(seeds),
        "goals":sum(x["goals"] for x in results),
        "observed_interventions":{
            policy:sum(x["actual_probes_by_policy"][policy] for x in results)
            for policy in ("active","uniform","random")},
        "correct":total,
        "direct_true_effect_bits_correct":sum(
            x["true_signature_bits_correct"]["direct_active"] for x in results),
        "conventional_true_effect_bits_correct":sum(
            x["true_signature_bits_correct"]["conventional"] for x in results),
        "true_effect_bits_total":sum(x["true_signature_bits_total"] for x in results),
        "causal_channel_maps_correct":sum(x["stable_channel_exact"] for x in results),
        "cold_exact_count":sum(x["model_cold_restore"] for x in results),
        "tamper_rejection_count":sum(x["tamper_rejected"] for x in results),
        "unknown_action_abstention_count":sum(x["unknown_action_abstention"] for x in results),
        "whole_process_cpu_ns":time.process_time_ns()-clock,
        "fit_cpu_ns":{
            name:sum(x["resource_ns"][name] for x in results)
            for name in ("direct_active_fit","direct_uniform_fit","direct_random_fit",
                         "independent_symbolic_fit","ordinary_trained_logistic_fit")},
        "planning_cpu_ns":{
            name:sum(x["resource_ns"]["plans"][name] for x in results)
            for name in METHODS},
        "numeric_weight_slots_total":sum(x["numeric_weight_slots"] for x in results),
        "world_receipts":[{
            "seed":x["seed"],
            "world_fingerprint_after_predictions":x["world_audit_sha256"],
            "probe_sha256":x["sources_sha256"],
            "pre_outcome_predictions_sha256":x["model_predictions_pre_outcome_sha256"],
            "goal_requests_sha256":x["goal_requests_sha256"],
            "results":x["successes"],
            "causal_channel_exact":x["stable_channel_exact"],
            "effect_bits_correct":x["true_signature_bits_correct"],
            "action_probe_counts":x["per_action_probe_counts"],
        } for x in results],
        "caveat":"Unknown channel identification with noisy interventions. Nuisance drift is exogenous, NOT a real hidden confounder of treatment assignment. Direct count-based estimate plus hardcoded XOR planner; no general intelligence claim."
    }

def classify(r:dict,*,reserved:bool)->dict:
    t=FROZEN;c=r["correct"]
    n=r["world_count"]
    checks={
        "original_frozen_worlds_and_goals":
            n==t["dev_worlds" if reserved else "public_worlds"] and
            r["goals"]==t["dev_total_goals" if reserved else "public_total_goals"],
        "strict_same_action_budget_every_policy":
            all(x==n*30 for x in r["observed_interventions"].values()),
        "independent_symbolic_parity":c["direct_active"]==c["independent_symbolic"],
        "cold_restore":r["cold_exact_count"]==n,
        "checksum_tamper":r["tamper_rejection_count"]==n,
        "unknown_action_abstention":r["unknown_action_abstention_count"]==n,
        "source_prediction_receipts":len(r["world_receipts"])==n and
            all(len(x["pre_outcome_predictions_sha256"])==64
                for x in r["world_receipts"]),
        "whole_fit_planning_process_CPU_and_numeric_memory":
            r["whole_process_cpu_ns"]>0 and r["numeric_weight_slots_total"]==n*84 and
            all(v>=0 for v in r["fit_cpu_ns"].values()) and
            all(v>=0 for v in r["planning_cpu_ns"].values()),
        "oracle_all_goals_reachable":c["oracle_ceiling"]==r["goals"],
    }
    if reserved:
        checks.update({
            "reserved_original_goal_transfer":c["direct_active"]>=t["dev_min_direct_success"],
            "above_wrong_action_binding":c["direct_active"]-c["wrong_action_binding"]>=
                t["dev_min_advantage_over_wrong_binding"],
            "within_strong_conventional":c["fully_trained_logistic"]-c["direct_active"]<=
                t["dev_max_gap_to_conventional"],
        })
    else:
        checks.update({
            "public_original_goal_transfer":c["direct_active"]>=t["min_public_direct_success"],
            "public_correct_signature_fraction":r["direct_true_effect_bits_correct"]/
                r["true_effect_bits_total"]>=t["min_public_true_signature_bits_correct_fraction"],
            "unknown_causal_channel_detection":r["causal_channel_maps_correct"]>=
                t["min_public_stable_channel_identification_worlds"],
            "fully_trained_comparator_learning":c["fully_trained_logistic"]>=
                t["min_public_conventional_accuracy"],
            "matched_budget_random_policy_gap":c["direct_active"]-c["direct_random_probing"]>=
                t["minimum_public_advantage_over_random_policy"],
            "negative_wrong_action_association":c["direct_active"]-c["wrong_action_binding"]>=
                t["minimum_public_advantage_over_wrong_binding"],
            "within_ordinary_trained_comparator":c["fully_trained_logistic"]-c["direct_active"]<=
                t["maximum_public_gap_to_strong_conventional"],
        })
    classification=(t["positive_dev"] if all(checks.values()) else t["negative_dev"]
                    ) if reserved else (t["positive_public"] if all(checks.values())
                                        else t["negative_public"])
    return {
        **r,"checks":checks,
        "passed_checks":sum(bool(x) for x in checks.values()),
        "total_checks":len(checks),
        "classification":classification,
        "scientific_acceptance":"UNVERIFIED",
        "superiority_over_exact_symbolic":False,
        "claimed_adaptive_advantage_over_uniform":
            c["direct_active"]>c["direct_uniform"],
        "independent_hidden_confounder_identification":False,
        "general_intelligence":False,
        "deployment":"NONE"
    }

def main():
    arg=argparse.ArgumentParser()
    mode=arg.add_mutually_exclusive_group(required=True)
    mode.add_argument("--public-worlds-only",action="store_true")
    mode.add_argument("--reserved-dev-first-use",action="store_true")
    x=arg.parse_args()
    result=classify(evaluate(reserved=x.reserved_dev_first_use),
                    reserved=x.reserved_dev_first_use)
    print("WSP95_RESULT="+canonical(result),flush=True)

if __name__=="__main__":
    main()
