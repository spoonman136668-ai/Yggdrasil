#!/usr/bin/env python3
"""ENERGY-34: sparse margin-energy factor learning vs trained conventional controls.

Independent synthetic research only; never mutates native Yggdrasil learner.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path
import time
import warnings

import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit, LogisticRegression, Ridge
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).resolve().parent
SEEDS = (7117, 7129, 7151)
FAMILIES = ('parity3', 'mixed', 'extended4')
SCENARIOS = ('iid', 'shift_x0', 'heavy_noise')
ARMS = ('sparse_energy', 'omp12', 'logistic', 'ridge', 'rbf_svm', 'decision_tree', 'shuffled_energy', 'majority')
BITS = np.array([[(i >> j) & 1 for j in range(8)] for i in range(256)], dtype=np.int8)
SPINS = 2 * BITS - 1
FACTORS = {}
COLS = []
for degree in (1,2,3,4):
    for indices in combinations(range(8),degree):
        FACTORS[('parity',indices)] = len(COLS)
        COLS.append(np.prod(SPINS[:,indices],axis=1))
for indices in combinations(range(8),2):
    FACTORS[('and',indices)] = len(COLS)
    COLS.append(2 * (BITS[:,indices[0]] * BITS[:,indices[1]]) - 1)
PHI = np.array(COLS,dtype=np.float64).T
assert PHI.shape == (256,190)
IDX = {kind:[v for (k,_),v in FACTORS.items() if k==kind] for kind in ('and','parity')}
BY_DEGREE = {k:[v for (kind,coord),v in FACTORS.items() if kind=='parity' and len(coord)==k] for k in (1,2,3,4)}

def h(*parts):
    return sha256('/'.join(map(str,('energy34-v1',*parts))).encode('ascii')).digest()

def pick(*parts,limit):
    return int.from_bytes(h(*parts)[:8], 'big') % limit

def make_case(seed, world, family, scenario):
    pools = ([BY_DEGREE[3]] * 3 if family == 'parity3' else
             [BY_DEGREE[3],BY_DEGREE[2],IDX['and']] if family == 'mixed' else
             [BY_DEGREE[4],BY_DEGREE[3],IDX['and']])
    selected = []
    for j,pool in enumerate(pools):
        position=pick('factor',seed,world,family,j,limit=len(pool))
        while pool[position] in selected: position=(position+1)%len(pool)
        selected.append(pool[position])
    signs=[1 if pick('sign',seed,world,family,j,limit=2) else -1 for j in range(3)]
    truth=np.where(sum(sign*PHI[:,f] for sign,f in zip(signs,selected))>0,1,-1)
    if scenario=='shift_x0':
        trainpool=[i for i in range(256) if BITS[i,0]==0]
        heldpool=[i for i in range(256) if BITS[i,0]==1]
    else:
        pool=sorted(range(256),key=lambda i:h('split',seed,world,family,scenario,i))
        trainpool=pool[:96]
        heldpool=pool[96:160]
    train=sorted(trainpool,key=lambda i:h('train_order',seed,world,family,scenario,i))[:96]
    held=sorted(heldpool,key=lambda i:h('held_order',seed,world,family,scenario,i))[:64]
    assert len(set(train))==96 and len(set(held))==64 and not set(train).intersection(held)
    flip_prob=.30 if scenario=='heavy_noise' else .10
    observed=np.array([truth[i]*(-1 if int.from_bytes(h('noise',seed,world,family,scenario,i)[:8],'big')/2**64<flip_prob else 1) for i in train],dtype=int)
    return train,held,observed,truth,selected

def fit_energy(x,y):
    """Learn E(y|x)=-y*w·phi(x) by structured max-margin contrastive updates.
    Non-convex hard support pruning and top-gradient coordinates distinguish this
    method from conventional penalized logistic posterior fitting.
    """
    w=np.zeros(x.shape[1])
    for epoch in range(64):
        margin=y*(x@w)
        bad=margin<1
        if not np.any(bad):break
        grad=(y[bad,None]*x[bad]).mean(axis=0)
        picked=np.argsort(-np.abs(grad),kind='stable')[:8]
        w[picked]+=.045*grad[picked]
        keep=np.argsort(-np.abs(w),kind='stable')[:12]
        mask=np.zeros(len(w),dtype=bool);mask[keep]=True
        w[~mask]=0
    return w

def run_arm(arm, x, y, hold, raw_train, raw_held, negative_seed):
    start=time.perf_counter()
    if arm in ('sparse_energy','shuffled_energy'):
        if arm=='shuffled_energy':
            y=np.random.default_rng(negative_seed).permutation(y)
        weight=fit_energy(x,y)
        scores=hold@weight
        active=int(np.count_nonzero(weight))
    elif arm=='omp12':
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning)
            model=OrthogonalMatchingPursuit(n_nonzero_coefs=12,fit_intercept=True)
            model.fit(x,y)
        scores=model.predict(hold);active=int(np.count_nonzero(model.coef_))
    elif arm=='logistic':
        model=LogisticRegression(C=1.0,max_iter=500,tol=1e-8,solver='lbfgs')
        model.fit(x,y)
        scores=model.decision_function(hold);active=int(np.count_nonzero(model.coef_))
    elif arm=='ridge':
        model=Ridge(alpha=3.0)
        model.fit(x,y)
        scores=model.predict(hold);active=int(np.count_nonzero(model.coef_))
    elif arm=='rbf_svm':
        model=SVC(C=2.0,kernel='rbf',gamma='scale')
        model.fit(raw_train,y)
        scores=model.decision_function(raw_held);active=-1
    elif arm=='decision_tree':
        model=DecisionTreeClassifier(max_depth=8,random_state=19)
        model.fit(raw_train,y)
        scores=2*model.predict_proba(raw_held)[:,list(model.classes_).index(1)]-1 if len(model.classes_)>1 else np.full(len(raw_held),model.classes_[0])
        active=int(model.tree_.node_count)
    else:
        scores=np.full(len(hold),1 if y.mean()>0 else -1);active=1
    secs=time.perf_counter()-start
    return (np.where(scores>0,1,-1),secs,active)

def run_case(seed,world,family,scenario):
    train,held,observed,truth,source_factors=make_case(seed,world,family,scenario)
    x=PHI[train];hold=PHI[held]
    raw_train=BITS[train];raw_hold=BITS[held]
    accuracy={};timing={};active={}
    for arm in ARMS:
        pred,t,a=run_arm(arm,x,observed,hold,raw_train,raw_hold,
                         pick('sham',seed,world,family,scenario,limit=2**32))
        accuracy[arm]=int((pred==truth[held]).sum());timing[arm]=t;active[arm]=a
    return {'seed':seed,'world':world,'family':family,'scenario':scenario,
            'correct':accuracy,'fit_inference_seconds':timing,'active':active}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--out',required=True)
    args=p.parse_args()
    seeds=(99059,) if args.smoke else SEEDS
    worlds=range(2) if args.smoke else range(8)
    started=time.perf_counter()
    cases=[run_case(s,w,f,c) for s in seeds for w in worlds for f in FAMILIES for c in SCENARIOS]
    totals={scenario:{a:sum(x['correct'][a] for x in cases if x['scenario']==scenario) for a in ARMS} for scenario in SCENARIOS}
    n={scenario:sum(x['scenario']==scenario for x in cases)*64 for scenario in SCENARIOS}
    per_seed={str(s):{scenario:{a:sum(x['correct'][a] for x in cases if x['seed']==s and x['scenario']==scenario)
                      for a in ARMS} for scenario in SCENARIOS} for s in seeds}
    controls=('omp12','logistic','ridge','rbf_svm','decision_tree')
    gates={
      'iid_accuracy_vs_strongest': (totals['iid']['sparse_energy']-max(totals['iid'][a] for a in controls))/n['iid']>=.03,
      'shift_accuracy_vs_strongest': (totals['shift_x0']['sparse_energy']-max(totals['shift_x0'][a] for a in controls))/n['shift_x0']>=.03,
      'heavy_noise_nonregression':(totals['heavy_noise']['sparse_energy']-max(totals['heavy_noise'][a] for a in controls))/n['heavy_noise']>=-.01,
      'seed_stability':sum(all((per_seed[str(s)][c]['sparse_energy']-max(per_seed[str(s)][c][a] for a in controls))>0
                               for c in ('iid','shift_x0')) for s in seeds)>=2 if not args.smoke else False,
      'learned_vs_shuffled':all(totals[c]['sparse_energy']>totals[c]['shuffled_energy'] for c in SCENARIOS),
    }
    durations={a:sum(x['fit_inference_seconds'][a] for x in cases) for a in ARMS}
    gates['efficiency_vs_fastest_control']=durations['sparse_energy'] <= .5*min(durations[a] for a in controls)
    result={'schema':'yggdrasil.energy34.score.v1','mode':'smoke' if args.smoke else 'primary',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'seeds':list(seeds),'world_count':len(cases),'observations_per_world':96,'held_per_world':64,
            'feature_count':PHI.shape[1], 'training_data_class':'public interventions with witnessed noisy action consequences',
            'scenario_totals':totals,'denominators':n,'per_seed':per_seed,'gates':gates,
            'fit_inference_seconds':durations,'wall_seconds':time.perf_counter()-started,
            'classification':'DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO',
            'scientific_pass':False,'native_checkpoint_run':False,'deployment':'NONE','details':cases}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True,indent=2))

if __name__=='__main__': main()
