"""WSP109 three-intervention partially identifiable synthetic causal transfer.

All original queried before/after labels remain unread until every model
prediction, intervention trace and cold-restoration result is SHA256 sealed.
No historical data, protected first use, model promotion or merged controls.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import (
    FIT_SEEDS, TRANSFER_SEEDS, FIXTURE_SEEDS,
    HYPOTHESES, N_RULES, ACTION_BUDGET, QUERIES_PER_WORLD,
    masked_feedback, private_law, private_query_truth,
    feature_bits, query_scene, path_features,
    random_action_sequence, validate_world_schedule,
)
from learners import (
    DirectWeightPosterior, SymbolicBayes, ConventionalLogistic,
)

ARMS = ("direct_greedy", "symbolic_greedy", "depth3_bayes",
        "random_bayes", "fixed_bayes", "conventional_logistic", "no_feedback")
POLICIES = ("greedy", "depth3", "random", "fixed")
MAX_WALL_SECONDS = 120


def anonymous_context(seed: int) -> str:
    # Opaque context key; no law/seed/index is given to learner methods.
    return "ctx-" + sha256(("WSP109-CONTEXT|"+str(seed)).encode("ascii")).hexdigest()[:24]


def train_one_world(seed: int, direct: DirectWeightPosterior,
                    direct_symbolic: SymbolicBayes,
                    optimize: SymbolicBayes, random_bayes: SymbolicBayes,
                    fixed_bayes: SymbolicBayes, conventional: ConventionalLogistic):
    context=anonymous_context(seed)
    direct.start(context)
    for model in (direct_symbolic,optimize,random_bayes,fixed_bayes):
        model.start(context)
    observed = {key: [] for key in POLICIES}
    random_sequence = random_action_sequence(seed)
    for index in range(ACTION_BUDGET):
        kind = direct.choose_greedy(context)
        result = masked_feedback(seed,kind)
        direct.program(context,kind,result)
        direct_symbolic.observe(context,kind,result)
        observed["greedy"].append((kind,result))

        kind_opt = optimize.choose_depth3(context)
        result_opt = masked_feedback(seed,kind_opt)
        optimize.observe(context,kind_opt,result_opt)
        observed["depth3"].append((kind_opt,result_opt))

        kind_rand = random_sequence[index]
        result_rand = masked_feedback(seed,kind_rand)
        random_bayes.observe(context,kind_rand,result_rand)
        observed["random"].append((kind_rand,result_rand))

        kind_fixed=index
        result_fixed=masked_feedback(seed,kind_fixed)
        fixed_bayes.observe(context,kind_fixed,result_fixed)
        observed["fixed"].append((kind_fixed,result_fixed))
    conventional.fit(context,observed["greedy"])

    supports = {key: {
        "count": model.posterior_count(context),
        "entropy_bits": math.log2(model.posterior_count(context)),
        "intervention_kinds": [kind for kind,_ in observed[name]],
        "feedback": [int(v) for _,v in observed[name]],
    } for key,model,name in (
        ("direct_greedy", direct, "greedy"),
        ("symbolic_greedy", direct_symbolic, "greedy"),
        ("depth3_bayes", optimize, "depth3"),
        ("random_bayes",random_bayes, "random"),
        ("fixed_bayes",fixed_bayes, "fixed"),
    )}
    if supports["direct_greedy"]["count"] != supports["symbolic_greedy"]["count"]:
        raise AssertionError("independent Bayes posterior size differs from direct weights")
    if any(len({kind for kind, _ in trace}) != ACTION_BUDGET
           for trace in observed.values()):
        raise AssertionError("duplicate or missing intervention in frozen action budget")
    return observed,supports


def predict_pair(context,scene, direct, direct_symbolic, optimal, random, fixed, conventional):
    before = path_features(scene.before,scene.source,scene.target)
    after = path_features(scene.after(),scene.source,scene.target)
    def preds(features):
        return {
            "direct_greedy": bool(direct.predict(context,features)),
            "symbolic_greedy": bool(direct_symbolic.predict(context,features)),
            "depth3_bayes": bool(optimal.predict(context,features)),
            "random_bayes": bool(random.predict(context,features)),
            "fixed_bayes": bool(fixed.predict(context,features)),
            "conventional_logistic": bool(conventional.predict(context,features)),
            "no_feedback": False,
        }
    return {"before":preds(before),"after":preds(after)}


def score_cohort(predictions):
    scores = {
        arm: {
            "total":0, "before_correct":0, "after_correct":0,
            "change_correct":0, "actually_changed":0,
            "changed_correct":0, "actually_unchanged":0,
            "unchanged_correct":0,
        } for arm in ARMS
    }
    real_changed=0
    real_unchanged=0
    actual_positive_before=0
    actual_positive_after=0
    for record in predictions:
        seed,index=record["seed"],record["index"]
        scene=query_scene(seed,index)
        x=path_features(scene.before,scene.source,scene.target)
        y=path_features(scene.after(),scene.source,scene.target)
        truth_before=private_query_truth(seed,x)
        truth_after=private_query_truth(seed,y)
        actual_positive_before+=int(truth_before)
        actual_positive_after+=int(truth_after)
        changed=truth_before!=truth_after
        real_changed+=int(changed)
        real_unchanged+=int(not changed)
        for arm in ARMS:
            pred_before=record["prediction"]["before"][arm]
            pred_after=record["prediction"]["after"][arm]
            if type(pred_before) is not bool or type(pred_after) is not bool:
                raise ValueError("invalid cached pre-oracle prediction")
            r=scores[arm]
            r["total"]+=1
            r["before_correct"]+=int(pred_before==truth_before)
            r["after_correct"]+=int(pred_after==truth_after)
            effect_correct=int((pred_before!=pred_after)==changed)
            r["change_correct"]+=effect_correct
            if changed:
                r["actually_changed"]+=1
                r["changed_correct"]+=effect_correct
            else:
                r["actually_unchanged"]+=1
                r["unchanged_correct"]+=effect_correct
    if real_changed < 30 or real_unchanged < 30:
        raise AssertionError("masked query transfer cohort lacks intervention headroom")
    n=len(predictions)
    for r in scores.values():
        r["before_accuracy"]=r["before_correct"]/n
        r["after_accuracy"]=r["after_correct"]/n
        r["action_change_accuracy"]=r["change_correct"]/n
        r["actual_changed_accuracy"]=r["changed_correct"]/r["actually_changed"]
        r["actual_unchanged_accuracy"]=r["unchanged_correct"]/r["actually_unchanged"]
    return {
        "query_count":n, "actual_positive_before":actual_positive_before,
        "actual_positive_after":actual_positive_after,
        "actual_changed_count":real_changed,
        "actual_unchanged_count":real_unchanged,"arms":scores,
    }


def run_development(*, cohorts=None, require_full=True):
    if require_full and cohorts is not None:
        raise ValueError("first-use world cohorts cannot be overridden")
    if require_full:
        validate_world_schedule()
        cohorts=(("fit",FIT_SEEDS),("transfer",TRANSFER_SEEDS))
    if cohorts is None:
        raise ValueError("one fixed frozen cohort or explicit fixture world required")
    start=time.monotonic()
    cpu=time.process_time()
    direct=DirectWeightPosterior()
    sym=SymbolicBayes()
    opt=SymbolicBayes()
    rand=SymbolicBayes()
    fixed=SymbolicBayes()
    conventional=ConventionalLogistic()
    predictions={}
    observed={}
    support={}
    distinct_entities=set()
    timing=defaultdict(int)
    for cohort_name,seeds in cohorts:
        if cohort_name in predictions:
            raise ValueError("duplicate cohort name")
        cohort_predictions=[]
        cohort_observations=[]
        cohort_support=[]
        for seed in seeds:
            begin=time.process_time_ns()
            obs,sizes=train_one_world(seed,direct,sym,opt,rand,fixed,conventional)
            timing["world_training_all_policies"]+=time.process_time_ns()-begin
            context=anonymous_context(seed)
            cohort_observations.append({
                "world_context":context,
                "observed_feedback":obs,
            })
            cohort_support.append({"world_context":context,**sizes})
            for index in range(QUERIES_PER_WORLD):
                if time.monotonic()-start > MAX_WALL_SECONDS:
                    raise TimeoutError("frozen synthetic learner/executor time limit exceeded")
                scene=query_scene(seed,index)
                names=(scene.source,scene.target)
                if any(name in distinct_entities for name in names):
                    raise AssertionError("unfamiliar-world entity alias across scenes")
                distinct_entities.update(names)
                tick=time.process_time_ns()
                paired=predict_pair(
                    context,scene,direct,sym,opt,rand,fixed,conventional)
                timing["all_arms_query_inference"]+=time.process_time_ns()-tick
                if (paired["before"]["direct_greedy"]!=
                    paired["before"]["symbolic_greedy"] or
                    paired["after"]["direct_greedy"]!=
                    paired["after"]["symbolic_greedy"]):
                    raise AssertionError("direct numerical and independent symbolic disagreement")
                cohort_predictions.append({
                    "seed":seed,"index":index,"prediction":paired,
                })
        predictions[cohort_name]=cohort_predictions
        observed[cohort_name]=cohort_observations
        support[cohort_name]=cohort_support

    # All world actions and all before/after predictions get sealed before any
    # heldout query truth is computed.
    receipts={}
    for name in predictions:
        payload={
            "observations": observed[name],
            "model_predictions": predictions[name],
            "posterior_support": support[name],
        }
        raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        receipts[name]=sha256(raw.encode("ascii")).hexdigest()

    # Persistence and interference: restore earliest world AFTER all subsequent
    # world-law training. No withheld query truth read yet.
    snapshot=direct.snapshot()
    cold=DirectWeightPosterior.restore(snapshot)
    cold_predictive_parity=True
    for name,records in predictions.items():
        for record in records:
            ctx=anonymous_context(record["seed"])
            scene=query_scene(record["seed"],record["index"])
            if (cold.predict(ctx,path_features(scene.before,scene.source,scene.target)) !=
                record["prediction"]["before"]["direct_greedy"] or
                cold.predict(ctx,path_features(scene.after(),scene.source,scene.target)) !=
                record["prediction"]["after"]["direct_greedy"]):
                cold_predictive_parity=False
                break
    if not cold_predictive_parity:
        raise AssertionError("cold direct weights lost knowledge after interference")

    tampered=json.loads(snapshot)
    first_context=sorted(tampered["payload"])[0]
    tampered["payload"][first_context]["weights"][0]=2
    tamper_rejected=False
    try:
        DirectWeightPosterior.restore(json.dumps(tampered))
    except ValueError:
        tamper_rejected=True
    if not tamper_rejected:
        raise AssertionError("modified direct-weight memory accepted")

    # Only now consult the world oracle for previously unseen query outcomes.
    metrics={name:score_cohort(predictions[name]) for name in predictions}
    for name in metrics:
        if (metrics[name]["arms"]["direct_greedy"] !=
            metrics[name]["arms"]["symbolic_greedy"]):
            raise AssertionError("direct weight prediction differs from independent exact Bayes")
    if require_full:
        transfer_laws={private_law(seed) for seed in TRANSFER_SEEDS}
        fit_laws={private_law(seed) for seed in FIT_SEEDS}
        novelty=len(transfer_laws-fit_laws)
        if novelty!=12:
            raise AssertionError("precommitted law classes must be disjoint")
    else:
        novelty=None
    posterior={
        cohort:{
            policy:{
                "mean_remaining_hypotheses":sum(w[policy]["count"]
                    for w in support[cohort])/len(support[cohort]),
                "mean_residual_entropy_bits":sum(w[policy]["entropy_bits"]
                    for w in support[cohort])/len(support[cohort]),
                "ambiguous_worlds":sum(w[policy]["count"]>1
                    for w in support[cohort]),
                "min_remaining_hypotheses":min(w[policy]["count"]
                    for w in support[cohort]),
                "max_remaining_hypotheses":max(w[policy]["count"]
                    for w in support[cohort]),
            } for policy in ("direct_greedy","depth3_bayes","random_bayes","fixed_bayes")
        } for cohort in support
    }
    if require_full and posterior["transfer"]["direct_greedy"]["ambiguous_worlds"]<6:
        raise AssertionError("frozen prior test has insufficient residual ambiguity")
    return {
        "schema":"wsp109.budget-three-causal-active-learning-transfer-dev.v1",
        "classification":"DEV_NONVIRGIN_TECHNICAL_REPLAY_PARTIALLY_IDENTIFIABLE_CAUSAL_INFERENCE_NOT_SCIENTIFIC_PASS",
        "original_first_use_aborted_job_id":132639008222,
        "dev_cohort_original_first_use":False,
        "precision_only_binary64_objective_repair":True,
        "scientific_pass":False,
        "novel_direct_weights_superior_to_bayes":False,
        "original_protected_first_use":False,
        "historical_wikidata_accessed":False,
        "official_validation_test_accessed":False,
        "candidate_hypotheses":len(HYPOTHESES),
        "possible_four_active_laws":126,
        "max_interventions_per_world":ACTION_BUDGET,
        "query_scenes_per_world":QUERIES_PER_WORLD,
        "fit_worlds":len(FIT_SEEDS) if require_full else len(cohorts[0][1]),
        "transfer_worlds":len(TRANSFER_SEEDS) if require_full else None,
        "transfer_law_templates_not_in_fit":novelty,
        "direct_numeric_parameter_count":len(direct.weights)*len(HYPOTHESES),
        "conventional_coefficient_count":len(conventional.theta)*(N_RULES+1),
        "conventional_max_gradient_inf_norm":max(conventional.gradients.values()),
        "conventional_max_newton_steps":max(conventional.steps.values()),
        "cold_retained_worlds":len(direct.weights),
        "cold_restore_predictions_identical":cold_predictive_parity,
        "tampered_snapshot_rejected":tamper_rejected,
        "actions_and_predictions_sha256_before_query_labels":receipts,
        "posterior_uncertainty":posterior,
        "metrics":metrics,
        "training_cpu_seconds_all_policies":timing["world_training_all_policies"]/1e9,
        "inference_cpu_seconds_all_arms":timing["all_arms_query_inference"]/1e9,
        "whole_process_cpu_seconds":time.process_time()-cpu,
        "whole_process_wall_seconds":time.monotonic()-start,
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--frozen-budget-three-causal-dev",action="store_true",required=True)
    a.parse_args()
    result=run_development()
    print("WSP109_BUDGETED_CAUSAL_DEV="+json.dumps(
        result,sort_keys=True,separators=(",",":")),flush=True)
