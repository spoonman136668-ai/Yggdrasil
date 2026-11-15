"""FKP-15 one-shot public native 16-step action-value learning science DEV.

Every training label is sourced from a real 16-step physical branch. Only
public PREFIX is visible when a model chooses ONE macro action at DEV;
nine future alternatives are evaluator-only and read AFTER choices frozen.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time
import numpy as np

import source
from learners import DirectValues,Retrieval,Ridge,context_data,mse
from baselines import fit_models,prediction

METHODS=("DIRECT","COUNTS","GRU","MLP","RIDGE","KNN",
         "PRIOR","RANDOM","SHUFFLED")
STRONG=("COUNTS","GRU","MLP","RIDGE","KNN","PRIOR","RANDOM","SHUFFLED")
BOOTSTRAPS=10000

def value_predictors(train,val):
    training=context_data(train)
    validation=context_data(val)
    if not training or not validation:raise ValueError("FKP15_NOT_ENOUGH_SOURCE")
    direct=DirectValues().fit(training)
    counts=DirectValues(two_keys=False).fit(training)
    shuffled=DirectValues(shuffled=True).fit(training)
    models={"DIRECT":direct,"COUNTS":counts,"SHUFFLED":shuffled}
    yval=np.stack([r["returns"] for r in validation])
    for typ,choices in (("RIDGE",(0.01,1.,100.)),("KNN",(1,5,15))):
        score=float("inf");selected=None;receipt=None
        for hyper in choices:
            model=(Ridge(float(hyper)) if typ=="RIDGE" else Retrieval(int(hyper))).fit(training)
            pred=model.predict(np.stack([r["context"] for r in validation]))
            loss=mse(pred,yval)
            if loss<score:
                selected=model;score=loss;receipt={"hyperparameter":hyper,"val_mse":loss}
        models[typ]=selected
        models[typ+"_receipt"]=receipt
    models["PRIOR"]=np.stack([r["returns"] for r in training]).mean(axis=0)
    torch,nets,fit_info=fit_models(training,validation)
    models["torch"]=torch
    models["GRU"]=nets["GRU"]
    models["MLP"]=nets["MLP"]
    models["fit_info"]=fit_info
    return models


def prior_seal(train,val,models):
    h=hashlib.sha256()
    h.update(source.cohort_digest(train).encode("ascii"))
    h.update(source.cohort_digest(val).encode("ascii"))
    for k in ("DIRECT","COUNTS","SHUFFLED"):h.update(models[k].snapshot())
    h.update(models["PRIOR"].astype("<f8").tobytes())
    for k in ("RIDGE","KNN"):
        mdl=models[k]
        for attr in ("coef","center","scale","x","y"):
            if hasattr(mdl,attr):h.update(np.asarray(getattr(mdl,attr),dtype="<f8").tobytes())
    for k in ("GRU","MLP"):
        for name,tensor in sorted(models[k].state_dict().items()):
            h.update(name.encode("ascii"))
            h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    h.update(json.dumps(models["fit_info"],sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def chosen_actions(public_row,models):
    summary=np.asarray(public_row["context"],dtype=np.float32)[None,:]
    pred={
      "DIRECT":models["DIRECT"].predict(summary)[0],
      "COUNTS":models["COUNTS"].predict(summary)[0],
      "SHUFFLED":models["SHUFFLED"].predict(summary)[0],
      "RIDGE":models["RIDGE"].predict(summary)[0],
      "KNN":models["KNN"].predict(summary)[0],
      "PRIOR":models["PRIOR"],
    }
    for k in ("GRU","MLP"):
        pred[k]=prediction(models[k],k,[public_row],models["torch"])[0]
    seed=public_row["seed"];anchor=public_row["anchor"]
    out={k:int(np.argmax(value)) for k,value in pred.items()}
    out["RANDOM"]=random.Random(seed^(anchor<<12)^0xF15B4).randrange(9)
    if set(out)!=set(METHODS):raise AssertionError("FKP15_MISSING_STRONG_CONTROL")
    return out


def dev_once(models):
    observations=[]
    actual_actions=0
    for seed in source.DEV:
        for anchor in source.ANCHORS:
            ref=source.real_prefix(seed,anchor,allow_dev=True)
            actual_actions+=ref["source_steps"]
            if not ref["valid"]:
                observations.append({"seed":seed,"anchor":anchor,"valid":False,
                                     "actual_source_actions":ref["source_steps"]})
                continue
            original_env=ref.pop("env")
            original_env.close()
            # Freeze all predictions from PUBLIC prefix before ANY held action return.
            selected=chosen_actions(ref,models)
            frozen_choice_sha=hashlib.sha256(
                json.dumps(selected,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            real=source.collect_one(seed,anchor,allow_dev=True)
            if not real["valid"] or real["prefix_sha256"]!=ref["prefix_sha256"] or not np.array_equal(real["sequence"],ref["sequence"]):
                raise AssertionError("FKP15_BLINDED_CHOICES_PREFIX_DIFFERENT")
            actual_actions+=real["physical_steps"]
            ret=real["returns"]
            reward={name:float(ret[index]) for name,index in selected.items()}
            positives={name:bool(ret[index]>0) for name,index in selected.items()}
            goals={name:int(real["goal_by_action"][index]) for name,index in selected.items()}
            observations.append({
                "valid":True,"seed":seed,"anchor":anchor,
                "prefix_sha256":ref["prefix_sha256"],
                "frozen_choices_sha256":frozen_choice_sha,
                "chosen_actions":selected,
                "earned_real_return":reward,
                "positive_return":positives,
                "goals_from_public_source":goals,
                "privileged_evaluator_max":float(ret.max()),
                "privileged_evaluator_min":float(ret.min()),
                "oracle_reward_spread":float(ret.max()-ret.min()),
                "actual_source_actions":ref["source_steps"]+real["physical_steps"],
                "branch_evaluator_public_receipts":real["branches_sha256"],
            })
    return observations,actual_actions


def paired_bootstrap(rows):
    complete=[r for r in rows if r["valid"]]
    world_mean={}
    for seed in source.DEV:
        x=[r for r in complete if r["seed"]==seed]
        if not x:continue
        world_mean[seed]={name:sum(r["earned_real_return"][name] for r in x)/len(x)
                          for name in METHODS}
    seeds=tuple(world_mean)
    if len(seeds)<24:raise ValueError("FKP15_INSUFFICIENT_DEV_WORLDS")
    mean={name:float(np.mean([world_mean[s][name] for s in seeds]))
          for name in METHODS}
    strongest=max(STRONG,key=lambda n:mean[n])
    rng=random.Random(1515)
    boot=[]
    for _ in range(BOOTSTRAPS):
        draw=[seeds[rng.randrange(len(seeds))] for _ in seeds]
        candidate=float(np.mean([world_mean[s]["DIRECT"] for s in draw]))
        best=max(float(np.mean([world_mean[s][k] for s in draw])) for k in STRONG)
        boot.append(candidate-best)
    boot.sort()
    return strongest,mean,[
        float(boot[249]),float(boot[9749])
    ],len(seeds)


def run(upstream:Path):
    start=time.perf_counter();cputime=time.process_time()
    custody=source.admit.source_custody(upstream)
    sys.path.insert(0,str(upstream))
    train=source.collect(source.TRAIN)
    val=source.collect(source.VAL)
    source_train=sum(r.get("physical_steps",r["source_steps"]) for r in train)
    source_val=sum(r.get("physical_steps",r["source_steps"]) for r in val)
    if len(train)!=256 or len(val)!=64:
        raise AssertionError("FKP15_TRAIN_VAL_ANCHOR_COUNT")
    began=time.perf_counter()
    models=value_predictors(train,val)
    fit_wall=time.perf_counter()-began
    seal=prior_seal(train,val,models)
    cold=models["DIRECT"].snapshot()
    restored=DirectValues.restore(cold)
    check=np.stack([r["context"] for r in context_data(val)])
    if cold!=restored.snapshot() or not np.array_equal(models["DIRECT"].predict(check),restored.predict(check)):
        raise AssertionError("FKP15_COLD_RESTORE_NOT_EXACT")
    tamper=bytearray(cold);tamper[101]^=1
    try:DirectValues.restore(bytes(tamper))
    except ValueError:tamper_rejected=True
    else:raise AssertionError("FKP15_UNSAFE_COLD_TAMPER")
    # No DEV original source env.reset occurred above.
    held,charged=dev_once(models)
    strongest,returns,ci,worlds=paired_bootstrap(held)
    valid=[r for r in held if r["valid"]]
    posrate={m:sum(r["positive_return"][m] for r in valid)/len(valid) for m in METHODS}
    goals={m:sum(r["goals_from_public_source"][m] for r in valid) for m in METHODS}
    oracle=np.mean([r["privileged_evaluator_max"] for r in valid])
    regret={m:float(oracle-returns[m]) for m in METHODS}
    oracle_adv=float(oracle-returns["RANDOM"])
    improvement=returns["DIRECT"]-returns[strongest]
    dev_signal=(improvement>=0.05 and ci[0]>0 and improvement>=0.10
                and posrate["DIRECT"]>=posrate[strongest]
                and worlds>=24 and oracle_adv>0.05
                and tamper_rejected)
    total=source_train+source_val+charged
    if total>source.MAX_ACTIONS:raise AssertionError("FKP15_SOURCE_ACTION_CAP_BREACHED")
    report={
       "schema":"fkp15.source-trained-16step-action-choice.dev.v1",
       "classification":"DEV_ACTION_VALUE_SIGNAL_ONLY" if dev_signal else
                        "DEV_MIXED_BEATS_WEAK_NOT_STRONG" if returns["DIRECT"]>returns["RANDOM"]
                        else "DEV_NO_GO_ACTION_VALUE_NOT_LEARNED",
       "scientific_pass":False,"native_model_modified":False,
       "protected_first_use":False,"reserved_transfer_opened":False,
       "original_public_dev_consumed":True,
       "official_source_reward_tested":False,
       "source_custody":custody,
       "source_action_budget":{"train":source_train,"validation":source_val,
                               "development":charged,"total":total,"limit":source.MAX_ACTIONS},
       "source_anchor_counts":{"train":len(train),"validation":len(val),
                               "development":len(held),"development_valid":len(valid),
                               "development_valid_worlds":worlds},
       "receipts":{"train_source":source.cohort_digest(train),
                   "validation_source":source.cohort_digest(val),
                   "held_public":hashlib.sha256(json.dumps(held,sort_keys=True).encode()).hexdigest(),
                   "pre_dev_learned_models":seal,
                   "direct_cold_bytes":hashlib.sha256(cold).hexdigest()},
       "candidate_direct_raw_weight_bytes":models["DIRECT"].count.nbytes+models["DIRECT"].sum_milli.nbytes,
       "candidate_cold_restored_bit_exact":True,
       "candidate_tamper_rejected":tamper_rejected,
       "trained_controls":models["fit_info"],
       "ridge_val_choice":models["RIDGE_receipt"],
       "knn_val_choice":models["KNN_receipt"],
       "best_return_control":strongest,
       "mean_real_16step_return":returns,
       "positive_return_action_choice_rate":posrate,
       "public_goal_events_by_method":goals,
       "privileged_unavailable_oracle_mean":float(oracle),
       "oracle_minus_random_headroom":oracle_adv,
       "regret_to_privileged_oracle":regret,
       "candidate_return_gain_over_best_control":improvement,
       "world_cluster_bootstrap_ci95":ci,
       "frozen_dev_signal":dev_signal,
       "times_seconds":{"all_wall":time.perf_counter()-start,
                         "all_cpu":time.process_time()-cputime,
                         "control_fit_wall":fit_wall},
       "full_process_compute_matched":False,
       "note":"Only source original action+outcomes, all nine DEV branches evaluator-only after frozen choice; no learner sees unchosen return labels; no on-policy multi-step planning beyond 16-step fixed macro."
    }
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--public-dev",action="store_true")
    p.add_argument("--upstream-root",type=Path)
    p.add_argument("--protected",action="store_true")
    args=p.parse_args()
    if args.protected or not args.public_dev or not args.upstream_root:
        p.error("FKP15_ONLY_FROZEN_PUBLIC_DEVELOPMENT; OWNER_PRIMARY_DISARMED")
    print(json.dumps(run(args.upstream_root.resolve()),sort_keys=True))
