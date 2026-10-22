"""NCI-04 S4C1: honest original native source-trained predictive-state test.

Prerequisite S4C0 certified a strong conventional recurrent on both
independently authored original-source engines. Its prior DEV seeds are
CONSUMED; this experiment uses only NEW frozen source seeds, trains the
original 45 coefficient / 8 scalar Ygg native local model, and competes
against fully independently fitted recurrent, logistic, Bayesian and
symbolic history controls trained on the SAME new native source traces.

Our local cell receives a deterministic seven-value projection of the
23-value original public input provided to all conventional competitors;
it does not receive extra original source information or any private
world labels. The learned state is sourced from predicted future public
changes, NOT from answers or hidden world. No preassigned ring messaging.
Full episode BPTT in offline training requires additional scratch memory.

PROSPECTIVE evaluation: train-only weights, THEN new frozen DEV source.
Every genuine source action is independent of model forecasts. A held
source outcome is never used in the current prediction nor for optimizer
choice. A retrospective pooled-feature collision screen is explicitly
NOT the same as original full-public-image causal alias identification.
"""
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

from research.mr34f.prospective_controls import (
    SOURCES,Logistic,Counts,episodes,verify_source,score,peak_rss,canon
)
from research.nci04_s4c0.recurrent_adequacy import train_source_recurrent
from research.mr27.natural_memory import source_guard
from research.nci04_s4c1.native_predictive_quotient import (
    NativePredictiveQuotient45,PARAMETERS
)

FROZEN=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.nci04.s4c1.native-prediction-conditioned-state.dev.v1"
TRAIN=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)
EVAL=(2003,2011,2017,2027,2029,2039,2053,2063)
EPOCHS=40
LR=.035
BETAS=(.9,.999)
EPS=1e-8
L2=.0002
CLIP=5.


def protocol():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    q=p["training_algorithm"]
    if (p["schema"]!=SCHEMA or
        p["exact_qualified_parent"]!="f3751b15e8139a68f34fb695b8bf418492086dc5" or
        p["distinct_new_train_development_reset_seeds"]!=list(TRAIN) or
        p["distinct_new_held_development_reset_seeds"]!=list(EVAL) or
        set(TRAIN)&set(EVAL) or
        p["source_native_step_cap"]!=96 or
        p["original_native_runtime_production_changed"] is not False or
        p["scientific_first_use_protected"] is not False or
        q!={"epochs_max":EPOCHS,"learning_rate":LR,
            "adam_betas":list(BETAS),"adam_epsilon":EPS,"l2":L2,
            "global_gradient_clip":CLIP,
            "source_train_only_best_epoch_checkpoint":True,
            "no_held_dev_hyperparameter_selection":True,
            "no_held_dev_weight_updates":True} or
        any(p["source_original_commits"].get(k)!=v[0]
            for k,v in SOURCES.items())):
        raise ValueError("NCI04_S4C1_FROZEN_ORIGINAL_SOURCE_DRIFT")
    return p


def train_native(episodes_train):
    model=NativePredictiveQuotient45()
    gradients=model.source_gradient_finite_difference(episodes_train[0])
    a=[np.zeros_like(w) for w in model.params()]
    b=[np.zeros_like(w) for w in model.params()]
    t=0
    saved=None
    history=[]
    started=time.process_time_ns()
    for epoch in range(1,EPOCHS+1):
        for native in episodes_train:
            grads=list(model.analytic_bptt(native))
            grads=[g+(L2*w if w.ndim==2 else 0.)
                   for g,w in zip(grads,model.params())]
            norm=float(np.sqrt(sum(float(np.sum(g*g)) for g in grads)))
            if not math.isfinite(norm):
                raise ValueError("NCI04_S4C1_NONFINITE_SOURCE_TRAIN_GRADIENT")
            factor=min(1.,CLIP/max(norm,1e-12))
            t+=1
            for i,(w,g) in enumerate(zip(model.params(),grads)):
                g=g*factor
                a[i]=BETAS[0]*a[i]+(1.-BETAS[0])*g
                b[i]=BETAS[1]*b[i]+(1.-BETAS[1])*(g*g)
                m=a[i]/(1.-BETAS[0]**t)
                v=b[i]/(1.-BETAS[1]**t)
                w-=LR*m/(np.sqrt(v)+EPS)
            model.train_updates+=1
        train_scores=[model.forward(e) for e in episodes_train]
        total,_=score(train_scores,episodes_train)
        if not math.isfinite(total):
            raise ValueError("NCI04_S4C1_TRAINING_LOSS_NONFINITE")
        history.append(float(total))
        if saved is None or total<saved[0]:
            saved=(total,epoch,model.snapshot())
    best_brier,best_epoch,serialized=saved
    exact=NativePredictiveQuotient45.restore(serialized)
    if exact.snapshot()!=serialized:
        raise ValueError("NCI04_S4C1_NATIVE_WEIGHT_SNAPSHOT_DRIFT")
    return exact,{
        "source_native_training_first_last_best_Brier":
            [history[0],history[-1],best_brier],
        "TRAINING_ONLY_selected_epoch":best_epoch,
        "fully_executed_original_training_epochs":EPOCHS,
        "original_native_trainable_coefficient_count":PARAMETERS,
        "eight_native_retained_scalar_states":8,
        "finite_difference_analytic_public_source_BPTT":gradients,
        "training_cpu_ns_full_episode_45_coefficient_Adam":
            time.process_time_ns()-started,
        "checkpoint_bytes":len(serialized.encode()),
        "training_full_episode_public_state_cache_more_than_inference":True,
    }


def brier(pred,ep):
    yy=np.asarray([row[2] for row in ep])
    return np.mean((pred-yy)**2,axis=1)


def retrospective_pooled_aliases(held,by_name):
    """Honest pooled-23 feature collision, NOT full original public alias."""
    buckets=defaultdict(list)
    for i,ep in enumerate(held):
        for j,row in enumerate(ep):
            buckets[row[0].tobytes()].append((i,j,row[2].tobytes()))
    conflicts=set()
    groups=0
    for members in buckets.values():
        if (len({a for a,_,_ in members})<2 or
            len({t for _,_,t in members})<2):
            continue
        groups+=1
        for i,j,_ in members:
            conflicts.add((i,j))
    summaries={}
    for model, predictions in by_name.items():
        values=[float(brier(predictions[i],held[i])[j])
                for i,j in sorted(conflicts)]
        summaries[model]=float(np.mean(values)) if values else None
    return {
        "pooled_current_23feature_cross_reset_conflicting_label_groups":groups,
        "held_original_native_steps_in_retroactively_selected_pooled_conflicts":
            len(conflicts),
        "independent_native_eval_seed_clusters_with_context_conflict":
            len({i for i,_ in conflicts}),
        "held_conditional_Brier_by_competitor_if_qualified":summaries,
        "NOT_original_exact_full_public_board_match":True,
        "NO_privileged_world_or_future_target_in_forecast":True,
    }


def original_source_experiment(family,root):
    train,custody_train=episodes(root,family,TRAIN)
    held,custody_held=episodes(root,family,EVAL)
    if len(train)!=20 or len(held)!=8:
        raise ValueError("NCI04_S4C1_ORIGINAL_NATIVE_COHORT_INCOMPLETE")

    model,train_info=train_native(train)
    memoryless=Logistic(False,{"logistic_epochs":100,
                               "logistic_lr":.8,"logistic_l2":.0002})
    memoryless.fit(train)
    baseline_train,_=score([memoryless.forecast(e) for e in train],train)
    qualified,restarts=train_source_recurrent(train,baseline_train)
    recurrent=qualified["model"]
    bayesian=Counts(False)
    symbolic=Counts(True)
    bayesian.fit(train)
    symbolic.fit(train)

    original_native_checkpoint=model.snapshot()
    recurrent_bytes=[p.tobytes() for p in recurrent.params()]
    memoryless_bytes=[p.tobytes() for p in (memoryless.w,memoryless.b)]
    bayesian_count_bytes=bayesian.checkpoint_bytes()
    symbolic_count_bytes=symbolic.checkpoint_bytes()
    start=time.process_time_ns()

    sources={
        "native_45_local_predicted_state":
            [model.forward(e) for e in held],
        "same_45_weights_all_states_erased":
            [model.forward(e,zero_state=True) for e in held],
        "same_45_weights_roles_reassigned":
            [model.forward(e,permuted_roles=True) for e in held],
        "adequately_trained_8state_conventional_recurrent":
            [recurrent.forward(e)[0] for e in held],
        "fully_trained_current_public_memoryless":
            [memoryless.forecast(e) for e in held],
        "Bayesian_128context_control":
            [bayesian.forecast(e) for e in held],
        "symbolic_128context_history_control":
            [symbolic.forecast(e) for e in held],
    }
    overall={}
    by_seed={}
    for name,preds in sources.items():
        value,per=score(preds,held)
        overall[name]=float(value)
        by_seed[name]=per
    if (model.snapshot()!=original_native_checkpoint or
        recurrent_bytes!=[p.tobytes() for p in recurrent.params()] or
        memoryless_bytes!=[p.tobytes() for p in (
            memoryless.w,memoryless.b)] or
        bayesian_count_bytes!=bayesian.checkpoint_bytes() or
        symbolic_count_bytes!=symbolic.checkpoint_bytes()):
        raise ValueError("NCI04_S4C1_ORIGINAL_HELDOUT_WEIGHT_OR_COUNT_LEAK")
    inference_CPU=time.process_time_ns()-start
    alias=retrospective_pooled_aliases(held,sources)
    seedwins=sum(
        a+.0<b for a,b in zip(
            by_seed["native_45_local_predicted_state"],
            by_seed["same_45_weights_all_states_erased"]))
    held_raw_digest=sha256(canon(custody_held).encode()).hexdigest()
    return {
        "original_independently_authored_source_sha":SOURCES[family][0],
        "original_train_native_env_step_actions":sum(map(len,train)),
        "new_prospective_dev_original_native_env_step_actions":
            sum(map(len,held)),
        "original_source_train_public_event_digest":
            sha256(canon(custody_train).encode()).hexdigest(),
        "original_source_held_public_event_digest":held_raw_digest,
        "original_source_held_seed_episode_receipts":custody_held,
        "native_original_Ygg45_training":train_info,
        "fully_training_qualified_conventional_recurrent": {
            "source_train_brier":qualified["source_train_Brier"],
            "initialization_selected_from_training_only":qualified["seed"],
            "training_episodes_and_checkpoints":restarts,
            "model_checkpoint_bytes":recurrent.checkpoint_bytes()},
        "prospective_true_original_public_next_Brier_lower_better":overall,
        "held_independent_native_seed_own_state_needed_count":seedwins,
        "held_independent_source_seed_proper_Brier":{
            str(seed):{k:by_seed[k][i] for k in sources}
            for i,seed in enumerate(EVAL)},
        "retrospective_pooled_public_feature_ambiguity_not_source_world_identifiability":
            alias,
        "candidate_and_controls_held_inference_CPU_ns_shared_process":
            inference_CPU,
        "same_training_source_Bayesian_symbolic_checkpoint_bytes":{
            "bayesian":bayesian_count_bytes,
            "symbolic":symbolic_count_bytes},
        "native_45_state_uses_true_source_target_only_in_offline_training":
            True,
        "native_prediction_state_updates_during_eval_from_predictions_only":
            True,
        "same_full_23_common_public_source_values_available_to_controls":
            True,
        "candidate_7_local_projected_features_are_subset_of_public_not_more":
            True,
        "true_source_original_hidden_world_reward_to_any_predictor":False,
    }


def main(farama,pycolab):
    p=protocol()
    roots={k:verify_source(
        farama if k=="FaramaMiniGridDoorKey8" else pycolab,
        x[0]) for k,x in SOURCES.items()}
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    results={key:original_source_experiment(key,root)
             for key,root in roots.items()}
    criteria={}
    for name,report in results.items():
        s=report["prospective_true_original_public_next_Brier_lower_better"]
        candidate=s["native_45_local_predicted_state"]
        alternatives=("adequately_trained_8state_conventional_recurrent",
                      "fully_trained_current_public_memoryless",
                      "Bayesian_128context_control",
                      "symbolic_128context_history_control")
        criteria[name]={
            "native_45_cell_model_beats_all_strong_original_public_controls":
                all(candidate<s[k] for k in alternatives),
            "native_predicted_outcome_state_reduces_held_source_Brier_by_0_002":
                candidate+.002<=s["same_45_weights_all_states_erased"],
            "same_weights_local_state_necessary_on_6_of_8_native_seed_clusters":
                report["held_independent_native_seed_own_state_needed_count"]>=6,
            "local_learned_role_specificity_vs_role_reassignment":
                candidate<s["same_45_weights_roles_reassigned"],
            "native_exact_45_parameters_eight_retained_states":True,
            "equal_all_in_isolated_native_CPU_RSS_storage_message_resource":
                False,
            "protected_independent_scientific_first_use":False,
            "independent_unfamiliar_task_family_transfer":False
        }
    for family,root in roots.items():
        verify_source(root,SOURCES[family][0])
    print("NCI04_S4C1_ORIGINAL_NATIVE_LEARNED_PREDICTIVE_QUOTIENT="+canon({
        "frozen_precode_protocol_sha256":sha256(FROZEN.read_bytes()).hexdigest(),
        "actual_original_source_control_and_native_candidate_results":results,
        "original_source_prospective_development_decision":criteria,
        "narrow_frozen_dev_architectural_conditions_met":
            all(all(v for k,v in result.items() if k not in (
                "equal_all_in_isolated_native_CPU_RSS_storage_message_resource",
                "protected_independent_scientific_first_use",
                "independent_unfamiliar_task_family_transfer"))
                for result in criteria.values()),
        "source_engine_model_policy_and_training_total_CPU_ns_shared_process":
            time.process_time_ns()-start,
        "original_all_models_shared_worker_OS_peak_resident_bytes":
            peak_rss(),
        "parallel_model_memory_not_isolated_for_total_parity":True,
        "candidate_45_native_coefficient_count":45,
        "candidate_eight_native_inference_state_scalars":8,
        "candidate_no_preassigned_ring_messages":True,
        "candidate_training_full_episode_BPTT_extra_memory_unmatched":True,
        "original_native_execution_unchanged_training_and_eval":True,
        "scientific_first_use_consumed":False,
        "G29_source_atlas_and_full_final_regression":"BLOCKED",
        "independent_source_license_disagreement":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    }))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.nci04_s4c1.original_native_predictive_state SOURCE_FARAMA SOURCE_PYCOLAB")
    main(sys.argv[1],sys.argv[2])
