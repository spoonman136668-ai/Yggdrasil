"""WSP96 prospective confounded observation vs randomized do(action) evaluation.

All model plans/source digests are hashed BEFORE the simulator's hidden
common cause, action effects, or true causal goal outcome are inspected.
No public fixture instantiates reserved world seeds.
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
from world import HiddenConfoundedWorld,BITS,DO_PER_ACTION,OBS_COUNT
from weights import (DirectDoWeights,ConventionalLogistic,IndependentSymbolic,
                     ObservationalNaive,WrongActionAssociation,
                     DeterministicRandomPlan,choose_plan,canonical,sha)

SPEC=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
C=SPEC["frozen"]
METHODS=("direct_do","fully_trained_logistic_do","independent_symbolic_do",
         "naive_observational_only","shuffled_action_mapping","random_plan",
         "oracle_upper_bound")

def world_result(seed:int)->dict:
    started=time.process_time_ns()
    world=HiddenConfoundedWorld(seed)
    do_source=world.randomized_interventions()
    observational_source=world.biased_observational_log()
    if len(do_source)!=OBS_COUNT or len(observational_source)!=OBS_COUNT:
        raise AssertionError("original do/logged record budget mismatch")
    for source in (do_source,observational_source):
        if any(set(row)!={"action_id","trial","observed_outcome"} for row in source):
            raise AssertionError("latent confounder leaked to learner interface")
    do_sha=sha(do_source);observational_sha=sha(observational_source)
    direct=DirectDoWeights(world.actions)
    t=time.process_time_ns()
    for row in do_source:direct.observe(row)
    numeric_fit_ns=time.process_time_ns()-t
    t=time.process_time_ns()
    ordinary=ConventionalLogistic(world.actions)
    ordinary.fit(do_source)
    ordinary_fit_ns=time.process_time_ns()-t
    t=time.process_time_ns()
    symbolic=IndependentSymbolic(world.actions)
    for row in do_source:symbolic.observe(row)
    symbolic_fit_ns=time.process_time_ns()-t
    t=time.process_time_ns()
    naive=ObservationalNaive(world.actions)
    for row in observational_source:naive.observe(row)
    naive_fit_ns=time.process_time_ns()-t
    shifted=WrongActionAssociation(direct,world.control_id)
    random=DeterministicRandomPlan(seed)
    # No candidate/control can access world._effects, latent U, assignment
    # probabilities, or the action subset that formed these 20 targets.
    goals=world.goals()
    if len(goals)!=20:raise AssertionError("frozen goal count")
    requests=tuple(g.request() for g in goals)
    named={
        "direct_do":direct,
        "fully_trained_logistic_do":ordinary,
        "independent_symbolic_do":symbolic,
        "naive_observational_only":naive,
        "shuffled_action_mapping":shifted,
        "random_plan":random,
    }
    plans={}
    plan_cpu={}
    for name,method in named.items():
        t=time.process_time_ns()
        if name=="random_plan":
            plans[name]=tuple(method.plan(world.actions,q["start"],q["target"],
                            q["max_actions"],goal_index=i)
                         for i,q in enumerate(requests))
        else:
            plans[name]=tuple(method.plan(world.actions,q["start"],q["target"],
                            q["max_actions"]) for q in requests)
        plan_cpu[name]=time.process_time_ns()-t
    preexecution_sha=sha({
        "world_seed":seed,"do_observations_sha256":do_sha,
        "endogenous_observations_sha256":observational_sha,
        "goal_requests_sha256":sha(requests),
        "model_output_plans":plans,
    })
    # Preserve cold numerical source with proof of no replay or world-B edits.
    cold_snapshot=direct.snapshot()
    clone=DirectDoWeights.restore(cold_snapshot)
    cold_exact=(clone.snapshot()==cold_snapshot and
                tuple(clone.plan(world.actions,q["start"],q["target"],3)
                      for q in requests)==plans["direct_do"])
    tampered=json.loads(cold_snapshot)
    a=world.actions[0]
    tampered["body"]["ones"][a][0]+=1
    tamper=False
    try:DirectDoWeights.restore(json.dumps(tampered))
    except ValueError:tamper=True
    unknown="f"*16
    while unknown in world.actions:unknown="e"*16
    unknown_abstains=direct.plan(tuple(world.actions[:-1])+(unknown,),0,1) is None

    # From here on, evaluator ONLY; no model output / weights are changed.
    audit=world.audit_after_scoring()
    truth=audit["true_effects"]
    oracle=tuple(choose_plan(truth,world.actions,q["start"],q["target"],3)
                 for q in requests)
    plans["oracle_upper_bound"]=oracle
    plan_cpu["oracle_upper_bound"]=0
    correct={name:sum(world.execute(g.start,p)==g.target
                      for g,p in zip(goals,proposed))
             for name,proposed in plans.items()}
    def bits_correct(guess:dict[str,int]):
        return sum(1 for action in world.actions for bit in range(BITS)
                   if (guess.get(action,-1)>>bit)&1 == (truth[action]>>bit)&1)
    # Different fit source semantics for the observation-only control.
    naive_effect=naive.effects()
    favorite=audit["favorite"];latent_mask=audit["latent_mask"]
    favorite_wrong_latent=sum(1 for bit in range(BITS) if (latent_mask>>bit)&1
                           and ((naive_effect.get(favorite,-1)^truth[favorite])>>bit)&1)
    return {
        "seed":seed,"do_observations_sha256":do_sha,
        "observational_logs_sha256":observational_sha,
        "preexecution_model_plans_sha256":preexecution_sha,
        "world_audit_sha256":audit["hidden_fingerprint"],
        "original_goals":len(goals),
        "do_interventions":len(do_source),
        "observational_logged_rows":len(observational_source),
        "do_action_counts":dict(direct.n),
        "observed_log_action_counts":dict(naive.n),
        "scores":correct,
        "true_effect_bits_correct":{
            "direct_do":bits_correct(direct.effects()),
            "fully_trained_logistic_do":bits_correct(ordinary.effects()),
            "naive_observational_only":bits_correct(naive.effects()),
        },
        "source_bits_total":len(world.actions)*BITS,
        "confounding_exists":audit["genuine_common_cause_observed"],
        "observational_favorite_wrong_latent_effect":favorite_wrong_latent>0,
        "hidden_assignment_probability_difference_for_audit":
            audit["observed_prevalence_u_favorite"]-
            audit["observed_prevalence_u_others"],
        "cold_restore":cold_exact,
        "tamper_rejected":tamper,
        "unknown_action_abstained":unknown_abstains,
        "numeric_weight_slots":len(world.actions)*BITS*2,
        "numeric_snapshot":cold_snapshot,
        "resource_ns":{
            "direct_fit":numeric_fit_ns,
            "ordinary_fit":ordinary_fit_ns,
            "symbolic_fit":symbolic_fit_ns,
            "observational_fit":naive_fit_ns,
            "plans":plan_cpu,
            "whole":time.process_time_ns()-started,
        },
    }

def evaluate(*,reserved:bool)->dict:
    start=time.process_time_ns()
    seeds=(SPEC["source"]["reserved_dev_seeds"] if reserved
           else SPEC["source"]["public_seeds"])
    if len(set(seeds))!=len(seeds):raise ValueError("duplicated original seed")
    rows=[world_result(seed) for seed in seeds]
    # Cold retention of first environment AFTER new independent worlds:
    # reload A's immutable snapshot; no replay of earlier do-source.
    original_snapshot=rows[0]["numeric_snapshot"]
    cold_after_other_worlds=(DirectDoWeights.restore(original_snapshot).snapshot()
                             ==original_snapshot)
    scores={k:sum(row["scores"][k] for row in rows) for k in METHODS}
    fit_cpu={name:sum(q["resource_ns"][name] for q in rows)
             for name in ("direct_fit","ordinary_fit","symbolic_fit","observational_fit")}
    plan_cpu={name:sum(q["resource_ns"]["plans"][name] for q in rows) for name in METHODS}
    # Public reports have no hidden effects, hidden U or private masks. Only
    # audited metrics / hashes are retained after all methods were frozen.
    return {
        "schema":"wsp96.confounded-causal-do-vs-observational-dev.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_ORIGINAL_DEV",
        "worlds":len(rows),"world_seeds":list(seeds),
        "goals":sum(x["original_goals"] for x in rows),
        "real_randomized_do_interventions":sum(x["do_interventions"] for x in rows),
        "passively_logged_observations":sum(x["observational_logged_rows"] for x in rows),
        "correct":scores,
        "true_do_effect_bits_correct":sum(x["true_effect_bits_correct"]["direct_do"] for x in rows),
        "ordinary_do_effect_bits_correct":sum(x["true_effect_bits_correct"]["fully_trained_logistic_do"] for x in rows),
        "naive_observational_bits_correct":sum(x["true_effect_bits_correct"]["naive_observational_only"] for x in rows),
        "true_effect_bits_total":sum(x["source_bits_total"] for x in rows),
        "latent_action_assignment_shift_worlds":sum(x["confounding_exists"] for x in rows),
        "naive_favorite_misbound_worlds":sum(x["observational_favorite_wrong_latent_effect"] for x in rows),
        "cold_world_restored":sum(x["cold_restore"] for x in rows),
        "cold_after_interference":cold_after_other_worlds,
        "tamper_rejected":sum(x["tamper_rejected"] for x in rows),
        "unknown_action_abstention":sum(x["unknown_action_abstained"] for x in rows),
        "numeric_weight_slots_total":sum(x["numeric_weight_slots"] for x in rows),
        "model_fit_cpu_ns":fit_cpu,
        "model_planning_cpu_ns":plan_cpu,
        "whole_process_cpu_ns":time.process_time_ns()-start,
        "world_receipts":[{
            "seed":x["seed"],
            "do_sha256":x["do_observations_sha256"],
            "observational_sha256":x["observational_logs_sha256"],
            "plans_sha256_before_scoring":x["preexecution_model_plans_sha256"],
            "world_audit_sha256_after_scoring":x["world_audit_sha256"],
            "confounding_audit_difference":x["hidden_assignment_probability_difference_for_audit"],
            "score":x["scores"],
            "original_do_action_counts":x["do_action_counts"],
            "observed_action_counts":x["observed_log_action_counts"],
        } for x in rows],
        "scientific_limit":"U truly affects observational A and Y, but do(action) randomization plus known p(U)<0.5 and XOR effect family renders causal effects majority-identifiable. No general causal discovery; logistic and symbolic ties expected."
    }

def classify(v:dict,*,reserved:bool)->dict:
    t=SPEC["frozen"];n=v["worlds"];c=v["correct"]
    checks={
        "exact_original_frozen_cohort":(n==t["dev_world_count" if reserved else "public_world_count"] and
            v["goals"]==t["dev_goals" if reserved else "public_goals"]),
        "randomized_do_action_budget":v["real_randomized_do_interventions"]==n*144,
        "equal_observational_record_count":v["passively_logged_observations"]==n*144,
        "symbolic_matched_source_parity":c["direct_do"]==c["independent_symbolic_do"],
        "strong_fully_trained_conventional_not_better":
            c["fully_trained_logistic_do"]<=c["direct_do"],
        "all_true_source_goals_reachable":c["oracle_upper_bound"]==v["goals"],
        "cold_numeric_memory":v["cold_world_restored"]==n and v["cold_after_interference"],
        "corruption_refusal":v["tamper_rejected"]==n,
        "unknown_action_abstention":v["unknown_action_abstention"]==n,
        "source_and_blinded_plan_receipts":len(v["world_receipts"])==n and
            all(len(x["plans_sha256_before_scoring"])==64 for x in v["world_receipts"]),
        "full_process_CPU_and_numeric_source_size":
            v["whole_process_cpu_ns"]>0 and v["numeric_weight_slots_total"]==n*60 and
            all(x>=0 for x in v["model_fit_cpu_ns"].values()) and
            all(x>=0 for x in v["model_planning_cpu_ns"].values()),
    }
    if reserved:
        checks.update({
            "reserved_original_causal_goal_success":c["direct_do"]>=t["min_dev_candidate_goals"],
            "reserved_gap_over_endogenous_logging":c["direct_do"]-c["naive_observational_only"]>=t["min_dev_advantage_vs_observational"],
            "reserved_gap_over_shuffled_action":c["direct_do"]-c["shuffled_action_mapping"]>=t["min_dev_advantage_vs_shuffled"],
        })
    else:
        checks.update({
            "public_original_do_goal_transfer":c["direct_do"]>=t["min_public_candidate_goals"],
            "public_fully_trained_model_qualified":c["fully_trained_logistic_do"]>=t["min_public_conventional_goals"],
            "public_direct_correct_effect_bits":v["true_do_effect_bits_correct"]/v["true_effect_bits_total"]>=t["min_public_true_effect_bits_fraction"],
            "public_trained_correct_effect_bits":v["ordinary_do_effect_bits_correct"]/v["true_effect_bits_total"]>=t["min_public_conventional_effect_bits_fraction"],
            "genuine_unobserved_common_cause_audited":v["latent_action_assignment_shift_worlds"]>=t["min_public_latent_assignment_correlation_worlds"],
            "endogenous_favorite_confounded_wrong_bits":v["naive_favorite_misbound_worlds"]>=t["min_public_observational_favorite_binding_errors_worlds"],
            "public_do_gain_over_observational":c["direct_do"]-c["naive_observational_only"]>=t["min_public_candidate_advantage_vs_observational"],
            "public_do_gain_over_shuffled":c["direct_do"]-c["shuffled_action_mapping"]>=t["min_public_candidate_advantage_vs_shuffled"],
        })
    result=(t["dev_positive"] if reserved else t["public_positive"]) if all(checks.values()) else (
            t["dev_negative"] if reserved else t["public_negative"])
    return {**v,"classification":result,"checks":checks,
            "passed_checks":sum(bool(a) for a in checks.values()),
            "total_checks":len(checks),
            "independent_scientific_acceptance":"UNVERIFIED",
            "fully_observational_nonparametric_causal_identification":False,
            "causal_superiority_over_symbolic_or_conventional":False,
            "general_intelligence":False,
            "deployment":"NONE"}

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--public-worlds-only",action="store_true")
    group.add_argument("--reserved-dev-first-use",action="store_true")
    args=parser.parse_args()
    x=classify(evaluate(reserved=args.reserved_dev_first_use),
               reserved=args.reserved_dev_first_use)
    print("WSP96_RESULT="+canonical(x),flush=True)

if __name__=="__main__":
    main()
