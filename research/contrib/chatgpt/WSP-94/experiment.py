"""WSP94 frozen genuine action-consequence source and planning comparison.

The five intervention probes precede any target goal. Planners receive only
the observed probes and explicit (start, target) goal request, never the
hidden world signatures or originating action subset. Scoring executes all
pre-frozen plans against the hidden world after their SHA256 is recorded.
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
from world import HiddenCausalWorld,ACTIONS,OUTPUT_BITS,NUISANCE_BITS
from weights import (DirectNumeric,FullyTrainedConventional,IndependentSymbolic,
                     WrongActionBinding,PassiveNoIdentity,DeterministicRandom,
                     effect_bits,canonical)

PROTOCOL=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
SPEC=PROTOCOL["frozen"]
ALGORITHMS=("direct_numeric","symbolic_exact","conventional_trained",
            "shuffled_action","passive_no_identity","random_plan")

def digest(x:object)->str:
    return hashlib.sha256(canonical(x).encode("ascii")).hexdigest()

def one_world(seed:int)->dict:
    start_cpu=time.process_time_ns()
    world=HiddenCausalWorld(seed)
    actions=tuple(world.action_ids)
    source=tuple(x.as_record() for x in world.probe_once_per_action())
    if len(source)!=ACTIONS or world.real_probe_action_count!=ACTIONS:
        raise AssertionError("probe action budget/source invariant")
    if any("signature" in x or "hidden_matrix" in x for x in source):
        raise AssertionError("hidden world effect must not be supplied to learner")
    src_sha=digest(source)
    # One source for all arms. The conventional model sees exactly the same
    # five observations, including action identity, output before/after and
    # nuisance inputs; only the representation/learning rule differs.
    direct=DirectNumeric()
    t=time.process_time_ns()
    for x in source:direct.observe(x)
    direct_fit_cpu=time.process_time_ns()-t
    symbolic=IndependentSymbolic()
    t=time.process_time_ns()
    for x in source:symbolic.observe(x)
    symbolic_fit_cpu=time.process_time_ns()-t
    logistic=FullyTrainedConventional()
    t=time.process_time_ns()
    logistic.fit(source)
    conventional_fit_cpu=time.process_time_ns()-t
    wrong=WrongActionBinding(source)
    passive=PassiveNoIdentity(source)
    random=DeterministicRandom(seed)

    direct_bit_fit=sum(
        (1 if (((direct.effect(obs["action_id"])^effect_bits(obs))>>bit)&1)==0 else 0)
        for obs in source for bit in range(OUTPUT_BITS))
    ordinary_bit_fit,ordinary_bit_total=logistic.fitted_bits(source)
    if ordinary_bit_total!=ACTIONS*OUTPUT_BITS:
        raise AssertionError("ordinary control source fit denominator wrong")

    goals=world.heldout_goals()
    if len(goals)!=20:
        raise AssertionError("unexpected held-out composition goal count")
    requests=tuple(g.for_model() for g in goals)
    goal_requests_sha=digest(requests)
    predicted={name:[] for name in ALGORITHMS}
    predicted_cpu={}
    arms={
        "direct_numeric":direct,
        "symbolic_exact":symbolic,
        "conventional_trained":logistic,
        "shuffled_action":wrong,
        "passive_no_identity":passive,
        "random_plan":random,
    }
    for name,model in arms.items():
        t=time.process_time_ns()
        for goal in goals:
            # The hidden originating action set and world signature map
            # remain private inside world and are never arguments here.
            request=goal.for_model()
            if name=="random_plan":
                answer=model.plan(actions,request["start"],request["target"],
                                  request["max_actions"],goal_id=goal.goal_id)
            else:
                answer=model.plan(actions,request["start"],request["target"],
                                  request["max_actions"])
            predicted[name].append(answer)
        predicted_cpu[name]=time.process_time_ns()-t
    predicted_hash=digest({
        "seed":seed,"probe_sha":src_sha,"goal_request_sha":goal_requests_sha,
        "proposed_plans":predicted,
    })
    # No model weight update is allowed after this frozen prediction hash.
    achieved={}
    results={}
    for name,plans in predicted.items():
        measured=tuple(world.execute(g.start,p,max_actions=g.max_actions)
                       for g,p in zip(goals,plans))
        achieved[name]=measured
        results[name]=sum(actual==g.target for actual,g in zip(measured,goals))
    # Full post-evaluation snapshot for cold/retention audit, not a new probe.
    state=direct.snapshot()
    cold=DirectNumeric.restore(state)
    cold_identical=(cold.snapshot()==state and
                    tuple(cold.plan(actions,r["start"],r["target"],r["max_actions"])
                          for r in requests)==tuple(predicted["direct_numeric"]))
    tampered=json.loads(state)
    name=next(iter(tampered["payload"]["weights"]))
    tampered["payload"]["weights"][name][0]=1.0-tampered["payload"]["weights"][name][0]
    tamper_rejected=False
    try:DirectNumeric.restore(json.dumps(tampered))
    except ValueError:tamper_rejected=True
    # Invalid action list must NOT be interpreted as an unknown causal effect.
    nonexistent="f"*16
    while nonexistent in actions:nonexistent="e"*16
    unknown=direct.plan(tuple(actions[:-1])+(nonexistent,),0,1,3)
    probe_nuisance_changes=sum(x["nuisance_before"]!=x["nuisance_after"]
                              for x in source)
    return {
        "seed":seed,"source_sha256":src_sha,
        "hidden_matrix_sha256_postscoring":world.hidden_fingerprint(),
        "goal_requests_sha256":goal_requests_sha,
        "predictions_frozen_before_outcome_sha256":predicted_hash,
        "intervention_actions_used":world.real_probe_action_count,
        "nuisance_channel_count":NUISANCE_BITS,
        "nuisance_channel_changes_observed":probe_nuisance_changes,
        "unseen_goal_count":len(goals),
        "two_step_count":10,"three_step_count":10,
        "result_correct":results,
        "direct_signature_bits_fit":[direct_bit_fit,ACTIONS*OUTPUT_BITS],
        "conventional_signature_bits_fit":[ordinary_bit_fit,ordinary_bit_total],
        "cold_restore":cold_identical,
        "tamper_rejected":tamper_rejected,
        "unknown_action_abstains":unknown is None,
        "direct_numeric_weights":len(direct.weights)*OUTPUT_BITS,
        "fit_cpu_ns":{
            "direct_numeric":direct_fit_cpu,
            "independent_symbolic":symbolic_fit_cpu,
            "fully_trained_conventional":conventional_fit_cpu,
        },
        "planning_cpu_ns":predicted_cpu,
        "world_whole_cpu_ns":time.process_time_ns()-start_cpu,
    }

def evaluate(*,reserved:bool)->dict:
    begin=time.process_time_ns()
    seeds=(PROTOCOL["scope"]["reserved_world_seeds"] if reserved
           else PROTOCOL["scope"]["public_world_seeds"])
    if len(set(seeds))!=len(seeds):
        raise ValueError("frozen world source contains duplicate seed")
    worlds=[]
    # In a public test, no reserved world is instantiated or scored.
    for seed in seeds:
        worlds.append(one_world(seed))
    totals={name:sum(x["result_correct"][name] for x in worlds) for name in ALGORITHMS}
    initial=worlds[0]
    # A's source state was locally restored immediately after learning,
    # while all subsequent worlds were learned in independent instances.
    # Cold retention is checked by retaining the original model prediction
    # receipt, not replaying a prior environment's single-use interventions.
    return {
        "schema":"wsp94.frozen-intervention-to-compositional-goals-result.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_UNREGISTERED_DEVELOPMENT",
        "source_protocol_prereg_sha":"195d2c6c284831a7019fd858dc0b972ca6fd83c3",
        "seed_count":len(seeds),
        "seeds":list(seeds),
        "actual_intervention_actions_total":sum(x["intervention_actions_used"] for x in worlds),
        "goal_questions_total":sum(x["unseen_goal_count"] for x in worlds),
        "two_action_goals":sum(x["two_step_count"] for x in worlds),
        "three_action_goals":sum(x["three_step_count"] for x in worlds),
        "correct":totals,
        "direct_signature_bits_correct":sum(x["direct_signature_bits_fit"][0] for x in worlds),
        "conventional_signature_bits_correct":sum(x["conventional_signature_bits_fit"][0] for x in worlds),
        "signature_bits_total":len(seeds)*ACTIONS*OUTPUT_BITS,
        "cold_worlds_restored_exact":sum(x["cold_restore"] for x in worlds),
        "tamper_rejections":sum(x["tamper_rejected"] for x in worlds),
        "unknown_action_abstentions":sum(x["unknown_action_abstains"] for x in worlds),
        "nuisance_transitions_seen":sum(x["nuisance_channel_changes_observed"] for x in worlds),
        "numeric_weights_total":sum(x["direct_numeric_weights"] for x in worlds),
        "model_fit_cpu_ns":{
            name:sum(x["fit_cpu_ns"][name] for x in worlds)
            for name in ("direct_numeric","independent_symbolic","fully_trained_conventional")},
        "plan_cpu_ns":{
            name:sum(x["planning_cpu_ns"][name] for x in worlds)
            for name in ALGORITHMS},
        "whole_process_cpu_ns":time.process_time_ns()-begin,
        "source_and_prediction_receipts":[{
            "world_seed":x["seed"],
            "observations_sha256":x["source_sha256"],
            "goal_requests_sha256":x["goal_requests_sha256"],
            "predictions_sha256_before_execution":x["predictions_frozen_before_outcome_sha256"],
            "world_fingerprint_postscoring":x["hidden_matrix_sha256_postscoring"],
            "result_correct":x["result_correct"],
        } for x in worlds],
        "novelty_limit":"Each world is re-probed five times. Only 2/3-action composition goals are novel; no zero-shot transfer to new unprobed physics.",
        "science_limit":"Source-visible XOR signatures plus a fixed GF(2) planner; ties with exact symbolic and trained conventional do not prove new intelligence."
    }

def classify(r:dict,*,reserved:bool)->dict:
    t=PROTOCOL["frozen"];n=r["goal_questions_total"];yes=r["correct"]
    checks={
        "cohort_seed_and_goal_count":(
            r["seed_count"]==t["dev_worlds" if reserved else "public_worlds"] and
            n==t["dev_total_goals" if reserved else "public_total_goals"]),
        "exact_probe_action_budget":r["actual_intervention_actions_total"]==r["seed_count"]*ACTIONS,
        "direct_real_probe_effect_learning":
            r["direct_signature_bits_correct"]==r["signature_bits_total"],
        "fully_trained_conventional_probe_fit":
            r["conventional_signature_bits_correct"]==r["signature_bits_total"],
        "exact_independent_symbolic_parity":yes["direct_numeric"]==yes["symbolic_exact"],
        "within_strong_trained_conventional":
            yes["conventional_trained"]-yes["direct_numeric"]<=t["max_direct_gap_to_conventional_success"],
        "cold_numeric_world_retention":
            r["cold_worlds_restored_exact"]==r["seed_count"],
        "checksum_tamper_rejection":r["tamper_rejections"]==r["seed_count"],
        "unknown_action_abstention":r["unknown_action_abstentions"]==r["seed_count"],
        "exogenous_nuisance_exercised":r["nuisance_transitions_seen"]>0,
        "whole_process_and_memory_costs":(
            r["whole_process_cpu_ns"]>0 and
            r["numeric_weights_total"]==r["seed_count"]*ACTIONS*OUTPUT_BITS and
            all(v>=0 for v in r["model_fit_cpu_ns"].values()) and
            all(v>=0 for v in r["plan_cpu_ns"].values())),
    }
    if reserved:
        checks.update({
            "dev_compositional_intervention_success":
                yes["direct_numeric"]>=t["min_dev_direct_success"],
            "dev_wrong_action_binding_negative":
                yes["direct_numeric"]-yes["shuffled_action"]>=t["minimum_dev_advantage_over_shuffled"],
        })
    else:
        checks.update({
            "public_compositional_intervention_success":
                yes["direct_numeric"]>=t["min_public_direct_success"],
            "wrong_binding_is_negative":
                yes["shuffled_action"]<=t["max_public_shuffled_success"],
            "passive_ablation_is_negative":
                yes["passive_no_identity"]<=t["max_public_passive_success"],
            "open_loop_random_is_negative":
                yes["random_plan"]<=t["max_public_random_success"],
            "action_binding_has_value":
                yes["direct_numeric"]-yes["shuffled_action"]>=t["minimum_public_advantage_over_shuffled"],
        })
    classification=(t["dev_positive"] if all(checks.values())
                    else t["dev_negative"]) if reserved else (
                    t["public_positive"] if all(checks.values())
                    else t["public_negative"])
    return {
        **r,"checks":checks,
        "passed_checks":sum(checks.values()),"total_checks":len(checks),
        "classification":classification,
        "independent_scientific_acceptance":"UNVERIFIED",
        "real_world_or_general_language_learning":False,
        "superiority_over_symbolic_or_trained_conventional":False,
        "accepted_model_integration":False,
        "deployment":"NONE",
    }

def main()->None:
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--public-worlds-only",action="store_true")
    group.add_argument("--reserved-dev-first-use",action="store_true")
    args=ap.parse_args()
    result=classify(evaluate(reserved=args.reserved_dev_first_use),
                    reserved=args.reserved_dev_first_use)
    print("WSP94_RESULT="+canonical(result),flush=True)

if __name__=="__main__":
    main()
