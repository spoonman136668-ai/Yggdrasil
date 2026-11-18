#!/usr/bin/env python3
"""ENERGY-26 frozen comparative causal-factor projection on disjoint interventions.

No native Yggdrasil checkpoint, source first use, or external actor. True source
relations never enter learner fit; no held labels enter selection or training.
"""
import argparse
import hashlib
import itertools
import json
import math
import platform
import time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PARENTS = tuple(itertools.combinations(range(5), 3))
ACTIONS = tuple(itertools.product((-1, 1), repeat=5))
HYPOTHESES = tuple((p, sign) for p in PARENTS for sign in (-1, 1))
ARMS = ("pairwise_energy", "cubic_energy", "projected_energy", "capacity_matched_projected_conventional", "exact_fixed_noise_bayes", "exact_unknown_noise_beta_bayes")

def order(seed, parent, sign, noise):
    namespace = f"energy26/split-v1/seed={seed}/parents={parent}/sign={sign}/noise={noise}"
    arr = sorted(ACTIONS, key=lambda a: hashlib.sha256((namespace+"/a="+str(a)).encode()).digest())
    train, held = arr[:16], arr[16:]
    return train, held

def corrupted_labels(seed, parent, sign, flips, train):
    true = np.asarray([sign*math.prod(a[j] for j in parent) for a in train], dtype=int)
    namespace = f"energy26/corrupt-v1/seed={seed}/parents={parent}/sign={sign}/noise={flips}"
    keyed = sorted(range(len(train)), key=lambda idx: hashlib.sha256((namespace+"/a="+str(train[idx])).encode()).digest())
    observed = true.copy()
    for idx in keyed[:flips]:observed[idx] *= -1
    return observed, keyed[:flips]

def matrix(rows, cubic):
    return np.asarray([[1, *a, *(math.prod(a[j] for j in parent) for parent in PARENTS)] if cubic else [1, *a] for a in rows], dtype=float)

def fit(X, Y, ridge):
    return np.linalg.solve(X.T@X+ridge*np.eye(X.shape[1]), X.T@Y)

def linear_predict(X, W):
    return np.where(X@W >= 0, 1, -1)

def rule_predict(actions):
    return np.asarray([[sign*math.prod(a[j] for j in parents) for a in actions] for parents,sign in HYPOTHESES], dtype=int)

def bayesian_predictions(train, observed, held, fixed_error, prior):
    table_train = rule_predict(train)
    miss = (table_train != np.asarray(observed)).sum(axis=1).astype(int)
    n = len(train)
    htest = rule_predict(held)
    a0=time.perf_counter_ns()
    fixed = miss*np.log(fixed_error)+(n-miss)*np.log1p(-fixed_error)
    p=np.exp(fixed-np.max(fixed));p/=sum(p)
    fixed_result = (np.where(p@htest>=0,1,-1).astype(int), float(np.max(p)),int(np.argmax(p)))
    a1=time.perf_counter_ns()
    alpha,beta = prior
    robust = np.asarray([math.lgamma(int(m)+alpha)+math.lgamma(int(n-m)+beta)-math.lgamma(n+alpha+beta) for m in miss])
    p=np.exp(robust-np.max(robust));p/=sum(p)
    robust_result = (np.where(p@htest>=0,1,-1).astype(int),float(np.max(p)),int(np.argmax(p)))
    a2=time.perf_counter_ns()
    return (fixed_result,robust_result), miss.tolist(), (a1-a0,a2-a1)

def one(seed, parents, sign, flipped, protocol):
    train, held = order(seed, parents, sign, flipped)
    yobs, corrupt_indices = corrupted_labels(seed, parents, sign, flipped, train)
    truth=np.asarray([sign*math.prod(a[j] for j in parents) for a in held],dtype=int)
    ridge=protocol['ridge_lambda']
    timestamps=[time.perf_counter_ns()]
    low=fit(matrix(train,False), yobs, ridge)
    low_pred=linear_predict(matrix(held,False), low)
    timestamps.append(time.perf_counter_ns())
    high=fit(matrix(train,True), yobs, ridge)
    high_pred=linear_predict(matrix(held,True), high)
    timestamps.append(time.perf_counter_ns())
    best=int(np.argmax(np.abs(high[6:])))
    selected=PARENTS[best];polarity=1 if high[6+best]>=0 else -1
    projected=np.asarray([polarity*math.prod(a[j] for j in selected) for a in held],dtype=int)
    timestamps.append(time.perf_counter_ns())
    conventional=fit(matrix(train,True),yobs,ridge)
    ci=int(np.argmax(np.abs(conventional[6:])))
    cs=PARENTS[ci];cp=1 if conventional[6+ci]>=0 else -1
    matched=np.asarray([cp*math.prod(a[j] for j in cs) for a in held],dtype=int)
    timestamps.append(time.perf_counter_ns())
    (fixed,robust), mistakes, bayes_ns=bayesian_predictions(train,yobs,held,protocol['bayesian_fixed_epsilon'], protocol['robust_beta_noise_prior'])
    pred=dict(zip(ARMS,(low_pred,high_pred,projected,matched,fixed[0],robust[0])))
    assert all(arr.size ==16 for arr in pred.values())
    assert np.array_equal(projected, matched)
    elapsed = dict(zip(ARMS,(timestamps[1]-timestamps[0],timestamps[2]-timestamps[1],timestamps[3]-timestamps[1],timestamps[4]-timestamps[3],bayes_ns[0],bayes_ns[1])))
    return dict(seed=seed,source_parent=list(parents),source_sign=sign,source_flip_count=flipped,
      training_actions=[list(a) for a in train], training_observed=yobs.tolist(),train_corruption_indices=corrupt_indices,
      held_actions=[list(a) for a in held],held_truth=truth.tolist(),
      predictions={k:v.tolist() for k,v in pred.items()},selected_parent=list(selected),selected_sign=polarity,
      weight_high=high.tolist(),bayes_fixed={'posterior_max':fixed[1],'map_index':fixed[2]},
      bayes_robust={'posterior_max':robust[1],'map_index':robust[2]},
      hypothesis_mistakes=mistakes, fit_predict_ns=elapsed)

def run(protocol, seeds):
    cases=[one(seed,parents,sign,flips,protocol) for seed in seeds for flips in protocol['noise_flips_in_16_training_observations'] for parents in PARENTS for sign in (-1,1)]
    results={}
    for noise in protocol['noise_flips_in_16_training_observations']:
        subset=[c for c in cases if c['source_flip_count']==noise]
        results[str(noise)]={
         'worlds':len(subset),'held_per_arm':sum(len(c['held_truth']) for c in subset),
         'correct':{k:sum(int(p==t) for c in subset for p,t in zip(c['predictions'][k],c['held_truth'])) for k in ARMS},
         'parent_correct':sum(c['selected_parent']==c['source_parent'] and c['selected_sign']==c['source_sign'] for c in subset),
         'fit_plus_predict_ms':{k:sum(c['fit_predict_ns'][k] for c in subset)/1e6 for k in ARMS}}
    return {'schema':'energy26.structural-projection.scored.v1','protocol':protocol,'environment':{'python':platform.python_version(),'numpy':np.__version__},'results':results,'cases':cases,'scientific_pass':False,'native_execution':False,'deployment':'NONE'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');ap.add_argument('--out',type=Path);args=ap.parse_args()
    protocol=json.loads((HERE/'protocol.json').read_text())
    seeds=[protocol['smoke_seed']] if args.smoke else protocol['primary_seeds']
    a=run(protocol,seeds)
    if not args.smoke:(args.out or HERE/'scored.json').write_text(json.dumps(a,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(a['results'],sort_keys=True,indent=2))
if __name__=='__main__':main()
