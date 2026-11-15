"""FKP-12 frozen original public DEV causal-outcome learning.

No protected or reserved transfer first-use. Models fully fit and validation
selected before opening DEV source. All learner outcomes are PUBLIC development,
never independent science, native model admission or model-guided RL policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

import numpy as np

import source
from model import DirectMemory,prior_probs,brier,logloss
from baselines import train_all,predict as predict_torch,aggregate_brier

METHODS=("DIRECT","COUNTS","GRU","MLP","LOGISTIC","SHUFFLED","NO_ACTION","PRIOR")
DEV_EXPECTED=source.DEV


def fingerprint(rows):
    h=hashlib.sha256()
    for row in rows:
        h.update(row["seed"].to_bytes(4,"little"))
        h.update(row["policy"].encode("ascii"))
        h.update(row["source_receipt_sha256"].encode("ascii"))
        h.update(row["x"].astype("<f4",copy=False).tobytes())
        h.update(row["y"].astype("<i8",copy=False).tobytes())
    return h.hexdigest()


def cohort_counts(rows):
    y=np.concatenate([r["y"] for r in rows])
    return {"negative":int(np.sum(y==0)),
            "zero":int(np.sum(y==1)),
            "positive":int(np.sum(y==2)),
            "steps":len(y),
            "episodes":len(rows)}


def bootstrap_paired_gain(rows,candidate,reference):
    """Episode pairs nested within eight original independent DEV worlds."""
    pairs=[]
    for seed in DEV_EXPECTED:
        vals=[]
        for i,e in enumerate(rows):
            if e["seed"]==seed:
                vals.append(brier(reference[i],e["y"])-brier(candidate[i],e["y"]))
        if len(vals)!=2:raise AssertionError("FKP12_DEV_WORLD_PAIR_INCOMPLETE")
        pairs.append(sum(vals)/len(vals))
    rng=random.Random(1212)
    sims=sorted(sum(pairs[rng.randrange(len(pairs))] for _ in pairs)/len(pairs)
                for _ in range(10000))
    return [float(sims[249]),float(sims[9749])]


def evaluate(rows,estimates):
    results={}
    for name,p in estimates.items():
        if len(p)!=len(rows):raise ValueError("FKP12_MISSING_HELD_EPISODE")
        totals={"steps":0,"wrong":0,"sum_brier":0.,"sum_log":0.}
        by_policy={}
        for episode,pred in zip(rows,p):
            y=episode["y"]
            n=len(y)
            score=brier(pred,y)
            log=logloss(pred,y)
            error=int(np.sum(np.argmax(pred,axis=1)!=y))
            totals["steps"]+=n
            totals["wrong"]+=error
            totals["sum_brier"]+=score*n
            totals["sum_log"]+=log*n
            pol=episode["policy"]
            record=by_policy.setdefault(pol,{"steps":0,"weighted_brier":0.})
            record["steps"]+=n
            record["weighted_brier"]+=score*n
        results[name]={
            "brier":totals["sum_brier"]/totals["steps"],
            "log_loss":totals["sum_log"]/totals["steps"],
            "accuracy":1-totals["wrong"]/totals["steps"],
            "by_policy_brier":{k:v["weighted_brier"]/v["steps"]
                               for k,v in by_policy.items()}}
    return results


def replay_only(upstream:Path):
    # The original public episodes have already been consumed on another OS.
    source.source_custody(upstream)
    import sys
    sys.path.insert(0,str(upstream))
    train=source.collect(source.TRAIN)
    valid=source.collect(source.VALIDATION)
    dev=source.collect(source.DEV,allow_dev=True)
    mem=DirectMemory().fit(train)
    return {"schema":"fkp12.public-source-replay.v1",
            "classification":"CONSUMED_PUBLIC_DEV_REPLAY_ONLY",
            "split_receipts":{"train":fingerprint(train),
                              "validation":fingerprint(valid),
                              "development":fingerprint(dev)},
            "train_counts":cohort_counts(train),
            "validation_counts":cohort_counts(valid),
            "development_counts":cohort_counts(dev),
            "direct_programmed_snapshot_sha256":hashlib.sha256(mem.snapshot()).hexdigest(),
            "source_sha":source.SOURCE_SHA,
            "protected_first_use":False,"transfer_first_use":False,
            "scientific_pass":False}


def run(upstream:Path):
    started=time.perf_counter();cpu_start=time.process_time()
    custody=source.source_custody(upstream)
    import sys
    sys.path.insert(0,str(upstream))
    train=source.collect(source.TRAIN)
    valid=source.collect(source.VALIDATION)
    # Source training and validation only; no DEV seen, normalization trained
    # independently from DEV and every conventional model is fully fitted.
    direct=DirectMemory().fit(train)
    counts=DirectMemory(two_hash=False).fit(train)
    shuffled=DirectMemory().fit(train,shuffle_labels=True)
    no_action=DirectMemory(ignore_action=True).fit(train)
    global_prior=prior_probs(train)
    started_models=time.perf_counter()
    torch, conventional,trained=train_all(train,valid)
    train_wall=time.perf_counter()-started_models

    # Seal all source & model/validation metadata BEFORE any DEV source access.
    before_dev=hashlib.sha256()
    for rows in (train,valid):
        before_dev.update(fingerprint(rows).encode())
    for m in (direct,counts,shuffled,no_action):
        before_dev.update(m.snapshot())
    for name in sorted(conventional):
        before_dev.update(name.encode("ascii"))
        for key,tensor in sorted(conventional[name].state_dict().items()):
            before_dev.update(key.encode("ascii"))
            before_dev.update(tensor.detach().cpu().contiguous().numpy().tobytes())
        before_dev.update(json.dumps(trained[name],sort_keys=True).encode())
    model_seal=before_dev.hexdigest()
    train_validation_counts={
        "train":cohort_counts(train),
        "validation":cohort_counts(valid),
    }

    # The sole original public DEV first-use is at this point, after sealing.
    dev=source.collect(source.DEV,allow_dev=True)
    cold=direct.snapshot()
    restored=DirectMemory.restore(cold)
    direct_preds=[direct.predict(e["x"]) for e in dev]
    if not all(np.array_equal(x,restored.predict(e["x"])) for x,e in zip(direct_preds,dev)):
        raise AssertionError("FKP12_COLD_RETENTION_NOT_EXACT")
    tamper=bytearray(cold);tamper[56]^=1
    try:DirectMemory.restore(bytes(tamper))
    except ValueError:tamper_rejected=True
    else:raise AssertionError("FKP12_TAMPER_NOT_REJECTED")
    estimates={
        "DIRECT":direct_preds,
        "COUNTS":[counts.predict(e["x"]) for e in dev],
        "SHUFFLED":[shuffled.predict(e["x"]) for e in dev],
        "NO_ACTION":[no_action.predict(e["x"]) for e in dev],
        "PRIOR":[np.tile(global_prior,(len(e["y"]),1)) for e in dev],
    }
    for name,m in conventional.items():
        estimates[name]=predict_torch(m,name,dev,torch)
    scores=evaluate(dev,estimates)
    strongest=min(["GRU","MLP","LOGISTIC","COUNTS"],
                  key=lambda n:scores[n]["brier"])
    gain=scores[strongest]["brier"]-scores["DIRECT"]["brier"]
    ci=bootstrap_paired_gain(dev,estimates["DIRECT"],estimates[strongest])
    has_events=cohort_counts(dev)["negative"]>0 and cohort_counts(dev)["positive"]>0
    no_policy_regression=all(
        scores["DIRECT"]["by_policy_brier"][policy] <=
        min(scores[name]["by_policy_brier"][policy] for name in
            ("GRU","MLP","LOGISTIC","COUNTS"))+0.01
        for policy in source.POLICIES
    )
    signal=(gain>=0.02 and ci[0]>0 and has_events and no_policy_regression
            and tamper_rejected)
    result={
        "schema":"fkp12.public-dev-direct-reward-learning.v1",
        "classification":"DEV_SIGNAL_ONLY_NOT_INDEPENDENT_SCIENCE" if signal else
                         "DEV_NO_GO_NO_REAL_EVENT_SOURCE" if not has_events else
                         "DEV_NO_GO_STRONG_CONVENTIONAL_NOT_BEATEN",
        "engineering_source_custody":custody,
        "pre_dev_model_seal_sha256":model_seal,
        "source_receipts":{"train":fingerprint(train),
                           "validation":fingerprint(valid),
                           "development":fingerprint(dev)},
        "source_cohorts":{**train_validation_counts,"development":cohort_counts(dev)},
        "original_public_dev_consumed":True,
        "transfer_first_use":False,
        "protected_first_use":False,
        "source_reward_modified_from_official_benchmark":True,
        "learner_trained":True,
        "native_yggdrasil_modified":False,
        "scientific_pass":False,
        "raw_direct_weights_bytes":direct.weights.nbytes,
        "direct_cold_snapshot_sha256":hashlib.sha256(cold).hexdigest(),
        "direct_cold_prediction_bit_exact":True,
        "direct_cold_tamper_rejected":tamper_rejected,
        "best_full_conventional":strongest,
        "paired_dev_gain_over_strongest_brier":gain,
        "paired_dev_gain_bootstrap_ci95":ci,
        "preregistered_dev_signal":signal,
        "per_policy_nonregression":no_policy_regression,
        "scores":scores,
        "conventional_training":trained,
        "training_only_wall_seconds":train_wall,
        "total_wall_seconds":time.perf_counter()-started,
        "total_cpu_seconds":time.process_time()-cpu_start,
        "whole_process_compute_matched":False
    }
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--public-dev",action="store_true")
    p.add_argument("--replay-consumed-public-source",action="store_true")
    p.add_argument("--upstream-root",type=Path)
    p.add_argument("--primary",action="store_true")
    a=p.parse_args()
    if a.primary or a.upstream_root is None or a.public_dev==a.replay_consumed_public_source:
        p.error("FKP12_FROZEN_PUBLIC_DEV_OR_REPLAY_ONLY; PROTECTED_DISARMED")
    value=(run if a.public_dev else replay_only)(a.upstream_root.resolve())
    print(json.dumps(value,sort_keys=True,indent=2))
