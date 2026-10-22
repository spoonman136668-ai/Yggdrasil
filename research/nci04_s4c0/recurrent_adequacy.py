"""NCI-04 S4C0: actual conventional recurrent training adequacy control.

No new Yggdrasil learner, no new source-input privilege, no retraining on
MR34F consumed held-development seeds. Fix a scientifically important
weak comparator by independently testing exact analytic BPTT gradients
and training using bias-corrected full-episode Adam under precommitted
TRAINING-ONLY checkpoint selection. The source engine and action policy
are the untouched independently authored originals.

This cannot prove cognitive transfer or resource equality. A well-trained
recurrent comparator is a PREREQUISITE for subsequent novel learner claims.
"""
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import psutil

from research.mr34f.prospective_controls import (
    SOURCES, INPUT, LATENT, TARGET, Logistic, Counts, Recurrent,
    episodes, verify_source, current_vector, score, canon, peak_rss
)
from research.mr27.natural_memory import source_guard

FROZEN=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.nci04.s4c0.independent-conventional-recurrent-adequacy.dev.v1"
TRAIN=(1613,1619,1621,1627,1637,1657,1663,1667,1669,1693,
       1697,1699,1709,1721,1723,1733,1741,1747,1753,1759)
EVAL=(1777,1783,1787,1789,1801,1811,1823,1831)
OPT=dict(train_only_epochs_max=65,lr=.03,betas=[.9,.999],
         epsilon=1e-8,l2=.0002,global_norm_clip=5,
         restart_seeds=[17,31])
FDMAP=((0,0),(7,2))
HDMAP=((2,2),(0,6))
YMAP=((3,1),)


def config():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["parent_exact_mr34f_head"]!="53fcafe5db83fbde30771cbd0a25f06d8af681b9" or
        p["new_source_train_only_development_reset_seeds"]!=list(TRAIN) or
        p["new_held_development_original_reset_seeds"]!=list(EVAL) or
        p["native_action_cap"]!=96 or
        p["recurrent_precommitted_optimizer"]["train_only_epochs_max"]!=OPT[
            "train_only_epochs_max"] or
        p["recurrent_precommitted_optimizer"]["lr"]!=OPT["lr"] or
        p["recurrent_precommitted_optimizer"]["betas"]!=OPT["betas"] or
        p["recurrent_precommitted_optimizer"]["epsilon"]!=OPT["epsilon"] or
        p["recurrent_precommitted_optimizer"]["l2"]!=OPT["l2"] or
        p["recurrent_precommitted_optimizer"]["global_norm_clip"]!=OPT[
            "global_norm_clip"] or
        p["recurrent_precommitted_optimizer"]["restart_seeds"]!=OPT[
            "restart_seeds"] or
        p["no_protected_scientific_first_use"] is not True or
        p["no_new_ygg_model_trained"] is not True or
        p["no_outcome_based_seeds_or_training_search"] is not True or
        any(p["original_engines"].get(s)!=v[0] for s,v in SOURCES.items())):
        raise ValueError("NCI04_S4C0_FROZEN_SOURCE_OR_MODEL_DRIFT")
    return p


def BPTT_gradient(model,ep):
    """Analytic derivative of source PUBLIC proper Bernoulli log likelihood.

    The known original-source next-public binary outcome y only enters
    after actual native transition in the frozen training records.
    """
    predictions,history=model.forward(ep)
    n=len(ep)
    if not n or predictions.shape!=(n,TARGET) or len(history)!=n+1:
        raise ValueError("NCI04_S4C0_RECURRENT_EPISODE_SHAPE")
    gradients=[np.zeros_like(w) for w in model.params()]
    dwx,dwh,dbh,dwy,dby=gradients
    future=np.zeros(LATENT)
    for t in reversed(range(n)):
        x,_,y=ep[t]
        err=(predictions[t]-y)/(n*TARGET)
        dwy[:]+=np.outer(history[t+1],err)
        dby[:]+=err
        delta=(err@model.wy.T+future)*(1-history[t+1]**2)
        dwx[:]+=np.outer(x,delta)
        dwh[:]+=np.outer(history[t],delta)
        dbh[:]+=delta
        future=delta@model.wh.T
    return gradients


def logistic_cross_entropy(model,ep):
    probs=model.forward(ep)[0]
    labels=np.vstack([row[2] for row in ep])
    p=np.clip(probs,1e-12,1-1e-12)
    return float(-np.mean(labels*np.log(p)+(1-labels)*np.log(1-p)))


def derivative_check(ep):
    model=Recurrent(17,{"recurrent_epochs":1,"recurrent_lr":.04,
                        "recurrent_gradient_clip":5})
    grads=BPTT_gradient(model,ep)
    coords=[(0,(0,0)),(0,(7,2)),(1,(2,2)),(1,(0,6)),
            (3,(3,1)),(2,(3,)),(4,(7,))]
    accuracy=[]
    delta=1e-5
    for group,index in coords:
        weight=model.params()[group]
        prior=float(weight[index])
        weight[index]=prior+delta
        plus=logistic_cross_entropy(model,ep)
        weight[index]=prior-delta
        minus=logistic_cross_entropy(model,ep)
        weight[index]=prior
        analytical=float(grads[group][index])
        numerical=(plus-minus)/(2*delta)
        accuracy.append({"parameter_group":group,"parameter_index":index,
                         "analytic":analytical,
                         "finite_difference":numerical,
                         "absolute_error":abs(analytical-numerical)})
    largest=max(x["absolute_error"] for x in accuracy)
    if largest>1e-5 or not math.isfinite(largest):
        raise ValueError("NCI04_S4C0_ANALYTIC_SOURCE_BPTT_WRONG")
    return {"max_absolute_gradient_error":largest,
            "coordinates":accuracy,"passed":True}


def train_source_recurrent(train,baseline_train_brier):
    cfg={"recurrent_epochs":1,"recurrent_lr":.04,
         "recurrent_gradient_clip":5}
    results=[]
    for seed in OPT["restart_seeds"]:
        m=Recurrent(seed,cfg)
        mean=[np.zeros_like(x) for x in m.params()]
        variance=[np.zeros_like(x) for x in m.params()]
        global_step=0
        best=None
        initial=None
        start=time.process_time_ns()
        for epoch in range(1,OPT["train_only_epochs_max"]+1):
            for ep in train:
                grads=BPTT_gradient(m,ep)
                # The Adam optimizer and L2 are applied only to frozen
                # ORIGINAL training episodes, never the held DEV outcomes.
                grads=[g+(OPT["l2"]*w if w.ndim>1 else 0)
                       for g,w in zip(grads,m.params())]
                magnitude=float(np.sqrt(sum(np.sum(g*g) for g in grads)))
                if not math.isfinite(magnitude):
                    raise ValueError("NCI04_S4C0_NONFINITE_GRADIENT")
                factor=min(1.,OPT["global_norm_clip"]/max(magnitude,1e-12))
                global_step+=1
                for index,(w,g) in enumerate(zip(m.params(),grads)):
                    g=g*factor
                    mean[index]=OPT["betas"][0]*mean[index]+(
                        1-OPT["betas"][0])*g
                    variance[index]=OPT["betas"][1]*variance[index]+(
                        1-OPT["betas"][1])*(g*g)
                    first=mean[index]/(1-OPT["betas"][0]**global_step)
                    second=variance[index]/(1-OPT["betas"][1]**global_step)
                    w-=OPT["lr"]*first/(np.sqrt(second)+OPT["epsilon"])
            trained=[m.forward(ep)[0] for ep in train]
            current,_=score(trained,train)
            if initial is None:
                initial=current
            if not math.isfinite(current):
                raise ValueError("NCI04_S4C0_NONFINITE_TRAINING_OBJECTIVE")
            snap=[np.array(w,copy=True) for w in m.params()]
            if best is None or current<best[0]:
                best=(current,epoch,snap)
            if current<=baseline_train_brier+.001:
                break
        best_score,best_epoch,weights=best
        for w,new in zip(m.params(),weights):
            w[:]=new
        results.append({"source_train_Brier":best_score,
                        "training_epoch_selected":best_epoch,
                        "training_epoch_run":epoch,
                        "initial_end_epoch_Brier":initial,
                        "train_CPU_ns":time.process_time_ns()-start,
                        "model":m,"seed":seed})
    selected=min(results,key=lambda z:(z["source_train_Brier"],z["seed"]))
    return selected,[{k:v for k,v in a.items() if k!="model"} for a in results]


def main(farama,pycolab):
    p=config()
    roots={key:verify_source(
        farama if key=="FaramaMiniGridDoorKey8" else pycolab,
        sha) for key,(sha,_,_) in SOURCES.items()}
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    source_guard(roots["FaramaMiniGridDoorKey8"])
    t0=time.process_time_ns()
    reports={}
    for family,root in roots.items():
        original_train,custody_train=episodes(root,family,TRAIN)
        original_eval,custody_eval=episodes(root,family,EVAL)
        if len(original_train)!=len(TRAIN) or len(original_eval)!=len(EVAL):
            raise ValueError("NCI04_S4C0_NOT_FULL_NATIVE_SOURCE_COHORT")
        shared_cfg={"logistic_epochs":100,"logistic_lr":.8,
                    "logistic_l2":.0002}
        baseline=Logistic(False,shared_cfg)
        baseline.fit(original_train)
        train_pred=[baseline.forecast(ep) for ep in original_train]
        train_brier,_=score(train_pred,original_train)
        baseline_pred=[baseline.forecast(ep) for ep in original_eval]
        baseline_eval,baseline_seeds=score(baseline_pred,original_eval)
        grad=derivative_check(original_train[0])
        trained,restarts=train_source_recurrent(original_train,train_brier)
        r=trained["model"]
        frozen_params=[w.tobytes() for w in r.params()]
        start=time.process_time_ns()
        recurrent_pred=[r.forward(ep)[0] for ep in original_eval]
        rec_eval,rec_seeds=score(recurrent_pred,original_eval)
        inference_cpu=time.process_time_ns()-start
        if frozen_params!=[w.tobytes() for w in r.params()]:
            raise ValueError("NCI04_S4C0_HELD_DEVELOPMENT_LEAK")
        bayesian=Counts(False)
        symbolic=Counts(True)
        bayesian.fit(original_train)
        symbolic.fit(original_train)
        bayes_eval,_=score([bayesian.forecast(ep)
                           for ep in original_eval],original_eval)
        symbol_eval,_=score([symbolic.forecast(ep)
                            for ep in original_eval],original_eval)
        reports[family]={
            "exact_original_source_git_sha":SOURCES[family][0],
            "authentic_train_steps":sum(len(e) for e in original_train),
            "authentic_eval_steps":sum(len(e) for e in original_eval),
            "source_train_native_event_sha256":sha256(
                canon(custody_train).encode()).hexdigest(),
            "source_eval_native_event_sha256":sha256(
                canon(custody_eval).encode()).hexdigest(),
            "central_finite_difference_original_source_gradient_check":grad,
            "fully_trained_current_public_training_brier":train_brier,
            "frozen_train_only_recurrent_restarts":restarts,
            "source_train_chosen_recurrent_brier":trained["source_train_Brier"],
            "source_train_chosen_recurrent_seed":trained["seed"],
            "prospective_eval_Brier":{
                "conventional_memoryless":baseline_eval,
                "newly_train_qualified_recurrent":rec_eval,
                "bounded_bayesian_counts":bayes_eval,
                "bounded_symbolic_history":symbol_eval
            },
            "held_original_independent_seed_clusters_recurrent_better_than_memoryless":
                sum(a<=b for a,b in zip(rec_seeds,baseline_seeds)),
            "per_frozen_original_eval_seed_proper_brier":{
                str(seed):{"recurrent":rec_seeds[i],
                           "memoryless":baseline_seeds[i]}
                for i,seed in enumerate(EVAL)
            },
            "frozen_recurrent_model_checkpoint_bytes":
                sum(w.nbytes for w in r.params())+LATENT*8,
            "whole_recurrent_native_training_cpu_ns":sum(x[
                "train_CPU_ns"] for x in restarts),
            "recurrent_held_dev_inference_cpu_ns":inference_cpu,
            "source_private_world_pose_reward_mission_to_model":False
        }
    conditions={}
    for family,z in reports.items():
        scores=z["prospective_eval_Brier"]
        conditions[family]={
            "native_analytic_gradient_certified":z[
                "central_finite_difference_original_source_gradient_check"]["passed"],
            "conventional_recurrent_training_only_competent":
                z["source_train_chosen_recurrent_brier"]<=z[
                    "fully_trained_current_public_training_brier"]+.001,
            "held_dev_recurrent_nonregression_vs_memoryless":
                scores["newly_train_qualified_recurrent"]<=scores[
                    "conventional_memoryless"],
            "held_dev_seed_cluster_nonregression_five_of_eight":
                z["held_original_independent_seed_clusters_recurrent_better_than_memoryless"]>=5,
        }
    print("NCI04_S4C0_INDEPENDENT_NATIVE_RECURRENT_ADEQUACY="+canon({
        "original_exact_source_git_shas":dict(
            (k,v[0]) for k,v in SOURCES.items()),
        "frozen_protocol_sha256":sha256(FROZEN.read_bytes()).hexdigest(),
        "original_true_source_control_receipts":reports,
        "predeclared_by_family_control_qualification":conditions,
        "all_control_adequacy_conditions_passed":
            all(all(x.values()) for x in conditions.values()),
        "original_trained_Yggdrasil_45_parameter_state_unchanged":True,
        "training_only_epoch_checkpoint_choice":True,
        "first_use_protected_science_data_consumed":False,
        "native_full_source_plus_training_cpu_ns":time.process_time_ns()-t0,
        "whole_source_process_peak_resident_bytes":peak_rss(),
        "all_in_resource_parity_against_original_Yggdrasil":"NOT_QUALIFIED",
        "new_learned_self_organizing_cognition":"NOT_TESTED",
        "source_G29_reviewed_semantic_atlas_and_final_regression":"BLOCKED",
        "source_redistribution_license_review":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    }))
    for family,root in roots.items():
        verify_source(root,SOURCES[family][0])


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit(
            "Usage: python -m research.nci04_s4c0.recurrent_adequacy ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(sys.argv[1],sys.argv[2])
