"""WSP97 exact-source paired-SCM first-use protocol.

The model never sees SCM regime, hidden U, source truth function or the
evaluated majority do outcomes. All model predictions are first frozen
with their source digests; only THEN does the evaluator inspect hidden truth.
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
from world import PairedSCM,REGIMES,DO_BUDGET
from weights import (DirectHypothesisWeights,IndependentSymbolicBayes,
                     ConventionalTabularBayes,original_random_probe,
                     passive_only_prediction,swapped_do_observation,canonical,sha)

PROTOCOL=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
F=PROTOCOL["frozen"]
METHODS=("direct_active","independent_symbolic","fully_trained_conventional",
         "direct_random_probes","passive_only_causal","shuffled_do_effect",
         "oracle_true_regime")

def original_world(seed:int,regime:str)->dict:
    begin=time.process_time_ns()
    source=PairedSCM(seed,regime)
    passive=source.passive()
    source_sha=sha(passive)
    t=time.process_time_ns()
    direct=DirectHypothesisWeights()
    direct.fit_passive(passive)
    numeric_passive_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    symbolic=IndependentSymbolicBayes()
    symbolic.fit_passive(passive)
    symbolic_passive_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    conventional=ConventionalTabularBayes()
    conventional.fit_passive(passive)
    ordinary_passive_cpu=time.process_time_ns()-t
    random=DirectHypothesisWeights()
    random.fit_passive(passive)
    flipped=DirectHypothesisWeights()
    flipped.fit_passive(passive)
    # All arms start from exactly the same complete passive source.
    training_fit_direct=sum(direct.f(r["context_id"],r["setting"],r["action"])
                            ==r["observed_y"] for r in passive)
    if len(passive)!=32:
        raise AssertionError("original passive source not complete")
    do_active=[];do_random=[];queries_active=[];queries_random=[]
    t=time.process_time_ns()
    for index in range(DO_BUDGET):
        query=direct.choose_probe(index)
        # This selection uses ONLY already-learned passive source table.
        row=source.randomized_do("active",query,index)
        queries_active.append(query);do_active.append(row)
        direct.observe_do(row)
        symbolic.observe_do(row)
        conventional.observe_do(row)
        flipped.observe_do(swapped_do_observation(row))
    active_do_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    for index in range(DO_BUDGET):
        query=original_random_probe(seed,index)
        row=source.randomized_do("random",query,index)
        queries_random.append(query);do_random.append(row)
        random.observe_do(row)
    random_do_cpu=time.process_time_ns()-t
    query_source=tuple(q.as_input() for q in source.eval_queries())
    all_methods={
        "direct_active":direct.predict,
        "independent_symbolic":symbolic.predict,
        "fully_trained_conventional":conventional.predict,
        "direct_random_probes":random.predict,
        "passive_only_causal":lambda r:passive_only_prediction(direct.cells,r),
        "shuffled_do_effect":flipped.predict,
    }
    t=time.process_time_ns()
    predictions={name:tuple(fn(req) for req in query_source)
                 for name,fn in all_methods.items()}
    inference_cpu=time.process_time_ns()-t
    pre_score_sha=sha({
        "pair_seed":seed,"passive_records_sha256":source_sha,
        "active_do_sha256":sha(do_active),"random_do_sha256":sha(do_random),
        "eval_queries_sha256":sha(query_source),
        "all_model_predictions":predictions,
    })
    snapshot=direct.snapshot()
    reloaded=DirectHypothesisWeights.restore(snapshot)
    cold_identical=(reloaded.snapshot()==snapshot and
                    tuple(reloaded.predict(q) for q in query_source)==
                    predictions["direct_active"])
    tampered=json.loads(snapshot)
    cell=next(iter(tampered["data"]["cells"]))
    tampered["data"]["cells"][cell]=1.0-tampered["data"]["cells"][cell]
    tamper_rejected=False
    try:DirectHypothesisWeights.restore(json.dumps(tampered))
    except ValueError:tamper_rejected=True
    unknown=direct.predict({"context_id":99,"setting":0,"action":1}) is None
    replay_rejected=False
    try:direct.observe_do(do_active[0])
    except ValueError:replay_rejected=True
    # No hidden regime is read until all original methods' outputs and source
    # trial digests have been frozen and model snapshots audited.
    true_outcomes=tuple(source.majority_do_result(q)
                        for q in source.eval_queries())
    diagnostic=tuple(source.diagnostic(q) for q in source.eval_queries())
    if len(true_outcomes)!=24 or sum(diagnostic)!=6:
        raise AssertionError("original hidden do-diagnostic target count")
    audit=source.audit()
    predictions["oracle_true_regime"]=true_outcomes
    diagnostic_true_outcomes=tuple(y for y,flag in zip(true_outcomes,diagnostic) if flag)
    scores={
        name:{
            "full":sum(a==b for a,b in zip(p,true_outcomes)),
            "diagnostic":sum(a==b for a,b,flag in
                             zip(p,true_outcomes,diagnostic) if flag),
        }
        for name,p in predictions.items()
    }
    return {
        "pair_seed":seed,"regime_audit":audit["regime"],
        "hidden_fingerprint_after_predictions":audit["private_function_fingerprint"],
        "passive_sha256":source_sha,
        "active_do_sha256":sha(do_active),"random_do_sha256":sha(do_random),
        "original_active_probe_requests_sha256":sha(queries_active),
        "original_random_probe_requests_sha256":sha(queries_random),
        "original_eval_requests_sha256":sha(query_source),
        "all_model_predictions_before_scoring_sha256":pre_score_sha,
        "do_probes_active":len(do_active),"do_probes_random":len(do_random),
        "original_passive_training_rows":len(passive),
        "training_fit_direct":training_fit_direct,
        "training_fit_conventional":conventional.train_fit,
        "learned_regimes":{
            "direct":direct.regime(),
            "symbolic":symbolic.regime(),
            "conventional":conventional.regime(),
            "random_source":random.regime(),
        },
        "scores":scores,
        "diagnostic_true_outcomes_after_scoring":diagnostic_true_outcomes,
        "cold_snapshot":snapshot,
        "cold_restore":cold_identical,
        "tamper_rejected":tamper_rejected,
        "unknown_context_abstained":unknown,
        "uncertain_effect_replay_rejected":replay_rejected,
        "numeric_weight_slots":len(direct.cells)+1,
        "cpu_ns":{
            "numeric_source_fit":numeric_passive_cpu,
            "ordinary_source_fit":ordinary_passive_cpu,
            "symbolic_source_fit":symbolic_passive_cpu,
            "active_do_updates":active_do_cpu,
            "random_do_updates":random_do_cpu,
            "all_original_inference":inference_cpu,
            "whole_world":time.process_time_ns()-begin,
        },
    }

def evaluate(*,reserved:bool)->dict:
    begin=time.process_time_ns()
    seeds=(PROTOCOL["world"]["reserved_pair_seeds"] if reserved
           else PROTOCOL["world"]["public_pair_seeds"])
    if len(set(seeds))!=len(seeds):
        raise ValueError("original pre-registered pair source reused")
    pairs=[]
    for seed in seeds:
        worlds=[original_world(seed,mode) for mode in REGIMES]
        if worlds[0]["passive_sha256"]!=worlds[1]["passive_sha256"]:
            raise AssertionError("observationally indistinguishable SCM source differs")
        if worlds[0]["hidden_fingerprint_after_predictions"]!=worlds[1]["hidden_fingerprint_after_predictions"]:
            raise AssertionError("pair SCM function source does not match")
        if not all(a!=b for a,b in zip(
            worlds[0]["diagnostic_true_outcomes_after_scoring"],
            worlds[1]["diagnostic_true_outcomes_after_scoring"])):
            raise AssertionError("paired observational twins must diverge on every diagnostic do query")
        pairs.append(tuple(worlds))
    rows=[row for pair in pairs for row in pair]
    # A's cold memory must remain valid after all unrelated world/SCM updates.
    first_snapshot=rows[0]["cold_snapshot"]
    after_other_worlds=DirectHypothesisWeights.restore(first_snapshot).snapshot()==first_snapshot
    summary={
        name:{
            metric:sum(row["scores"][name][metric] for row in rows)
            for metric in ("full","diagnostic")}
        for name in METHODS}
    return {
        "schema":"wsp97.observational-equivalence-do-first-use.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_ORIGINAL_DEV",
        "pair_seeds":list(seeds),"pairs":len(pairs),"worlds":len(rows),
        "passive_observations":sum(r["original_passive_training_rows"] for r in rows),
        "randomized_do_probes_active":sum(r["do_probes_active"] for r in rows),
        "randomized_do_probes_random":sum(r["do_probes_random"] for r in rows),
        "total_eval_requests":len(rows)*24,
        "diagnostic_eval_requests":len(rows)*6,
        "correct":summary,
        "source_fit_direct":sum(r["training_fit_direct"] for r in rows),
        "source_fit_conventional":sum(r["training_fit_conventional"] for r in rows),
        "equal_passive_source_pairs":sum(
            pair[0]["passive_sha256"]==pair[1]["passive_sha256"] for pair in pairs),
        "paired_do_disagreement_pairs":sum(
            all(a!=b for a,b in zip(
                pair[0]["diagnostic_true_outcomes_after_scoring"],
                pair[1]["diagnostic_true_outcomes_after_scoring"]))
            for pair in pairs),
        "correct_world_regime_direct":sum(r["learned_regimes"]["direct"]==r["regime_audit"] for r in rows),
        "correct_world_regime_ordinary":sum(r["learned_regimes"]["conventional"]==r["regime_audit"] for r in rows),
        "cold_restored_worlds":sum(r["cold_restore"] for r in rows),
        "interference_restoration":after_other_worlds,
        "tamper_rejections":sum(r["tamper_rejected"] for r in rows),
        "unknown_context_abstentions":sum(r["unknown_context_abstained"] for r in rows),
        "replay_rejections":sum(r["uncertain_effect_replay_rejected"] for r in rows),
        "numeric_slots":sum(r["numeric_weight_slots"] for r in rows),
        "cpu_ns":{name:sum(r["cpu_ns"][name] for r in rows)
                  for name in rows[0]["cpu_ns"]},
        "whole_process_cpu_ns":time.process_time_ns()-begin,
        "world_receipts":[{
            "pair_seed":r["pair_seed"],"mode_only_after_model_predictions":r["regime_audit"],
            "passive_sha256":r["passive_sha256"],
            "active_do_sha256":r["active_do_sha256"],
            "random_do_sha256":r["random_do_sha256"],
            "original_unseen_queries_sha256":r["original_eval_requests_sha256"],
            "plans_sha256_before_eval":r["all_model_predictions_before_scoring_sha256"],
            "original_score":r["scores"],
            "trained_passive_fit":[r["training_fit_direct"],r["training_fit_conventional"]],
        } for r in rows],
        "scientific_limit":"A=U observationally yields indistinguishable paired SCM data. A 3-action DO experiment identifies the GLOBAL mode transferable to source-known but DO-unprobed contexts. Uses handcoded two-SCM Bayesian likelihood and observable passive 32-cell table; no original causal-program invention or real-world intelligence advantage."
    }

def classify(r:dict,*,reserved:bool)->dict:
    f=F;pair_count=f["reserved_pairs"] if reserved else f["public_pairs"]
    world_count=f["reserved_worlds"] if reserved else f["public_worlds"]
    diag_count=f["reserved_diagnostic_queries"] if reserved else f["public_diagnostic_queries"]
    full_count=f["reserved_total_queries"] if reserved else f["public_total_queries"]
    s=r["correct"]
    checks={
        "exact_original_worlds_and_cohorts":r["pairs"]==pair_count and r["worlds"]==world_count,
        "strictly_identical_paired_observational_sources":r["equal_passive_source_pairs"]==pair_count,
        "paired_intervention_nonidentifiability_proved":r["paired_do_disagreement_pairs"]==pair_count,
        "all_source_rows_and_unseen_eval_targets":r["passive_observations"]==world_count*32 and
            r["total_eval_requests"]==full_count and r["diagnostic_eval_requests"]==diag_count,
        "identical_three_action_probe_budgets":r["randomized_do_probes_active"]==world_count*3 and
            r["randomized_do_probes_random"]==world_count*3,
        "direct_source_passive_training_fit":r["source_fit_direct"]==world_count*32,
        "fully_gradient_trained_conventional_passive_fit":r["source_fit_conventional"]==world_count*32,
        "independent_symbolic_exact_parity":s["direct_active"]==s["independent_symbolic"],
        "conventional_not_better_accuracy":s["fully_trained_conventional"]["diagnostic"]<=
            s["direct_active"]["diagnostic"],
        "hidden_truth_oracle_all":s["oracle_true_regime"]=={"full":full_count,"diagnostic":diag_count},
        "exact_cold_memory_after_other_worlds":r["cold_restored_worlds"]==world_count and
            r["interference_restoration"],
        "tamper_and_unknown_refuse":r["tamper_rejections"]==world_count and
            r["unknown_context_abstentions"]==world_count,
        "no_replay_of_uncertain_effects":r["replay_rejections"]==world_count,
        "original_source_and_pre_scoring_prediction_receipts":len(r["world_receipts"])==world_count and
            all(len(x["plans_sha256_before_eval"])==64 for x in r["world_receipts"]),
        "whole_process_cost_and_numeric_memory":r["whole_process_cpu_ns"]>0 and
            r["numeric_slots"]==world_count*33 and
            all(x>=0 for x in r["cpu_ns"].values()),
    }
    if reserved:
        checks.update({
            "reserved_original_diagnostic_transfer":
                s["direct_active"]["diagnostic"]>=f["reserved_min_candidate_diagnostic_correct"],
            "reserved_advantage_over_random_do_choice":
                s["direct_active"]["diagnostic"]-
                s["direct_random_probes"]["diagnostic"]>=f["reserved_min_active_advantage_over_random"],
            "reserved_advantage_over_observation_only":
                s["direct_active"]["diagnostic"]-
                s["passive_only_causal"]["diagnostic"]>=f["reserved_min_active_advantage_over_passive"],
            "reserved_gap_to_fully_trained_conventional":
                s["fully_trained_conventional"]["diagnostic"]-
                s["direct_active"]["diagnostic"]<=f["reserved_max_gap_to_conventional"],
        })
    else:
        checks.update({
            "public_original_diagnostic_transfer":
                s["direct_active"]["diagnostic"]>=f["public_min_candidate_diagnostic_correct"],
            "public_advantage_over_random_do_choice":
                s["direct_active"]["diagnostic"]-
                s["direct_random_probes"]["diagnostic"]>=f["public_min_active_advantage_over_random"],
            "public_advantage_over_observation_only":
                s["direct_active"]["diagnostic"]-
                s["passive_only_causal"]["diagnostic"]>=f["public_min_active_advantage_over_passive"],
            "public_gap_to_fully_trained_conventional":
                s["fully_trained_conventional"]["diagnostic"]-
                s["direct_active"]["diagnostic"]<=f["public_max_gap_to_strong_conventional"],
        })
    classification=(f["dev_positive"] if reserved else f["public_positive"]) if all(checks.values()) else (
        f["dev_negative"] if reserved else f["public_negative"])
    return {**r,"checks":checks,"passed_checks":sum(checks.values()),
            "total_checks":len(checks),"classification":classification,
            "scientific_acceptance":"UNVERIFIED",
            "causal_program_discovery_without_hypothesis_catalog":False,
            "learned_language_or_general_intelligence":False,
            "superiority_over_strong_controls":False,"deployment":"NONE"}

def main()->None:
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--public-only",action="store_true")
    g.add_argument("--reserved-dev-first-use",action="store_true")
    opt=ap.parse_args()
    result=classify(evaluate(reserved=opt.reserved_dev_first_use),
                    reserved=opt.reserved_dev_first_use)
    print("WSP97_RESULT="+canonical(result),flush=True)

if __name__=="__main__":
    main()
