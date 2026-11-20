#!/usr/bin/env python3
"""ENERGY-30: falsify likelihood-evidence gate for causal rule-family novelty.

This is an isolated synthetic CPU experiment.  It reuses the immutable
ENERGY-29 law definitions as a documented source dependency. It neither
imports native Yggdrasil model/checkpoints nor uses protected first-use.
"""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from parent_source_energy29 import OLD, ALL, BASE_PRIOR, BITS, FEATURES, X, hash_int, source_law, N, M

ROOT=Path(__file__).resolve().parent
SEEDS=(3041,3061,3083,3109)
SMOKE_SEED=9091
FAMILIES=('old','novel_in_basis','outside_basis')
CORRUPTION=(0,2,4)
N_WORLDS=20
N_TRAIN=24
N_HELD=24
ARMS=('old_bayes','mismatch_gate','evidence_gate','soft_mixture','full_anf_bayes','conventional_ridge','conventional_forest','conventional_tree')
# Fixed *before* any held evaluation.  Bayes ratio from posterior evidence:
# P(general family)=1/8, P(old family)=7/8.
NOVEL_PRIOR=0.125
ERROR_ODDS=1/3
GATE_POSTERIOR=0.5


def hash_order(label, items):
    return sorted(items,key=lambda item: hash_int(f'energy30/{label}/{item}'))


def action_split(seed, world_index, family, corruption):
    # Crucial source privacy: the training/held split is chosen by evaluator;
    # no learner receives the source law, family or seed.
    cohort=f'{seed}/{family}/{world_index}/{corruption}'
    order=hash_order('split/'+cohort,range(64))
    return tuple(order[:N_TRAIN]),tuple(order[N_TRAIN:N_TRAIN+N_HELD]),tuple(order[N_TRAIN+N_HELD:])


def source_sample(seed,family,world_index,corruption):
    train,held,unused=action_split(seed,world_index,family,corruption)
    truth,kind,sign=source_law(seed,family,world_index)
    observed=int(truth)
    flip=hash_order(f'flip/{seed}/{family}/{world_index}/{corruption}',range(len(train)))[:corruption]
    for pos in flip:observed^=1<<train[pos]
    return train,held,truth,observed,flip,kind


def fit_bank(bank,base,observed,seen_mask):
    mismatch=np.bitwise_count(np.bitwise_and(bank^np.uint64(observed),np.uint64(seen_mask))).astype(np.int16)
    weights=base*np.power(ERROR_ODDS,mismatch,dtype=np.float64)
    z=float(weights.sum(dtype=np.float64))
    if not z>0 or not np.isfinite(z):raise AssertionError('NONPOSITIVE_BANK_EVIDENCE')
    return weights,z,int(np.min(mismatch))


def predictions(held,bank,weights,z):
    return [int(float(weights[((bank>>np.uint64(a))&np.uint64(1))==1].sum(dtype=np.float64))/z>0.5)
            for a in held]


def sigmoid_family_posterior(z_old,z_new):
    return (NOVEL_PRIOR*z_new)/((1-NOVEL_PRIOR)*z_old+NOVEL_PRIOR*z_new)


def test_case(seed,family,world_index,corruption):
    train,held,truth,observed,flipped,kind=source_sample(seed,family,world_index,corruption)
    old_prior=np.full(len(OLD),1/len(OLD),dtype=np.float64)
    masks12=sum(1<<a for a in train[:12]);mask24=sum(1<<a for a in train)
    old12,zold12,min12=fit_bank(OLD,old_prior,observed,masks12)
    new12,znew12,_=fit_bank(ALL,BASE_PRIOR,observed,masks12)
    old24,zold24,min24=fit_bank(OLD,old_prior,observed,mask24)
    new24,znew24,_=fit_bank(ALL,BASE_PRIOR,observed,mask24)
    p12=sigmoid_family_posterior(zold12,znew12)
    p24=sigmoid_family_posterior(zold24,znew24)
    mismatch_birth=bool(min12>=2 or min24>=3)
    evidence_birth=bool(p12>=GATE_POSTERIOR or p24>=GATE_POSTERIOR)
    pred_old=predictions(held,OLD,old24,zold24)
    pred_new=predictions(held,ALL,new24,znew24)
    # Marginalize both families, not select the maximum-probability witness.
    soft=[]
    z_mix=(1-NOVEL_PRIOR)*zold24+NOVEL_PRIOR*znew24
    for a in held:
        on_old=float(old24[((OLD>>np.uint64(a))&1)==1].sum(dtype=np.float64))
        on_new=float(new24[((ALL>>np.uint64(a))&1)==1].sum(dtype=np.float64))
        soft.append(int(((1-NOVEL_PRIOR)*on_old+NOVEL_PRIOR*on_new)/z_mix>0.5))
    labels=np.asarray([((observed>>a)&1)*2-1 for a in train],dtype=np.float64)
    features=X[list(train)];held_features=X[list(held)]
    alpha=np.linalg.solve(features@features.T+np.eye(len(train)),labels)
    ridge_scores=held_features@(features.T@alpha)
    ridge=[int(score>0) for score in ridge_scores]
    observed_y=np.asarray([(observed>>a)&1 for a in train],dtype=np.int8)
    tree=DecisionTreeClassifier(max_depth=6,min_samples_leaf=1,random_state=seed)
    tree.fit(BITS[list(train)],observed_y)
    tree_predict=list(map(int,tree.predict(BITS[list(held)])))
    forest=ExtraTreesClassifier(n_estimators=31,max_depth=6,min_samples_leaf=1,
        max_features=None,bootstrap=False,n_jobs=1,
        random_state=hash_int(f'energy30/forest/{seed}/{family}/{world_index}/{corruption}')%(2**32))
    forest.fit(BITS[list(train)],observed_y)
    forest_predict=list(map(int,forest.predict(BITS[list(held)])))
    actual=[(truth>>a)&1 for a in held]
    arms={'old_bayes':pred_old,'mismatch_gate':pred_new if mismatch_birth else pred_old,
          'evidence_gate':pred_new if evidence_birth else pred_old,
          'soft_mixture':soft,'full_anf_bayes':pred_new,'conventional_ridge':ridge,
          'conventional_forest':forest_predict,'conventional_tree':tree_predict}
    assert len(arms)==len(ARMS) and all(len(a)==N_HELD for a in arms.values())
    return {'seed':seed,'family':family,'world_index':world_index,'corruption':corruption,
       'source_kind':kind,'truth_mask':hex(truth),
       'train_actions':list(train),'held_actions':list(held),
       'observed_train':[(observed>>a)&1 for a in train],
       'flipped_positions':list(flipped),
       'held_truth':actual,'min_old_mismatch12':min12,'min_old_mismatch24':min24,
       'posterior_novel_12':p12,'posterior_novel_24':p24,
       'birth_mismatch':mismatch_birth,'birth_evidence':evidence_birth,
       'predictions':arms,'correct':{k:sum(int(p==t) for p,t in zip(v,actual)) for k,v in arms.items()}}


def summarize(rows):
    groups={}
    for family in FAMILIES:
      for corrupt in CORRUPTION:
        sub=[r for r in rows if r['family']==family and r['corruption']==corrupt]
        if not sub: continue
        groups[f'{family}/noise{corrupt}']={'cases':len(sub),'held_per_arm':N_HELD*len(sub),
         'birth_mismatch':sum(r['birth_mismatch'] for r in sub),
         'birth_evidence':sum(r['birth_evidence'] for r in sub),
         'correct':{k:sum(r['correct'][k] for r in sub) for k in ARMS},
         'birth_disagreement':sum(r['birth_mismatch']!=r['birth_evidence'] for r in sub),
         'posterior_novel_24_mean':sum(r['posterior_novel_24'] for r in sub)/len(sub)}
    return {'cases':len(rows),'held_per_arm':len(rows)*N_HELD,'strata':groups}


def run(smoke):
    seeds=(SMOKE_SEED,) if smoke else SEEDS
    world_count=2 if smoke else N_WORLDS
    cases=[];start=time.perf_counter()
    for seed in seeds:
      for family in FAMILIES:
       for world_index in range(world_count):
        for corruption in CORRUPTION:
         cases.append(test_case(seed,family,world_index,corruption))
    return {'schema':'yggdrasil.energy30.novelty-versus-noise.v1','mode':'smoke' if smoke else 'scored',
       'models':list(ARMS),'source_dependency_sha256':'9dde0d8dbc70262d35404957a29b0405861b88caeaea7001767dbe9021443001',
       'cases':cases,'summary':summarize(cases),'wall_seconds_all_arms':time.perf_counter()-start,
       'native_checkpoint_tested':False,'scientific_pass':False,'deployment':'NONE'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'scored.json')
    args=parser.parse_args()
    obj=run(args.smoke)
    args.output.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'cases':obj['summary']['cases'],'seconds':obj['wall_seconds_all_arms'],
      'strata':obj['summary']['strata']},indent=2))

if __name__=='__main__':main()
