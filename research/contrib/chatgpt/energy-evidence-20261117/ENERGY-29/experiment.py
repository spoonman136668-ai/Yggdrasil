#!/usr/bin/env python3
"""ENERGY-29: construct previously absent Boolean causal interactions from public evidence.

Isolated synthetic development research. No native CKAD weights/episodes or
reserved first-use. This is a bounded universal ANF basis, NOT unrestricted
open-world causal invention or a distinctive energy architecture.
"""
import argparse
from collections import Counter
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier

ROOT=Path(__file__).resolve().parent
N=6
ACTIONS=64
M=(1<<ACTIONS)-1
FEATURES=tuple(sum(1<<j for j in c) for degree in (1,2,3) for c in combinations(range(N),degree))
TIERS=(0.01,0.12,0.27,0.60)
SEEDS=(2399,2411,2423,2441)
SMOKE_SEED=7001
FAMILIES=('old','novel_in_basis','outside_basis')
NOISE=(0,2)
ARMS=('old_bayes','constructive','full_anf_bayes','conventional_poly_ridge','conventional_tree','conventional_forest','hard_map')


def hash_int(text):
    return int.from_bytes(hashlib.sha256(text.encode('ascii')).digest(),'big')


def truthmask_monomial(support):
    return sum(1<<a for a in range(ACTIONS) if (a & support)==support)

TERMS={support:truthmask_monomial(support) for support in FEATURES}


def old_grammar():
    ans=[]
    for triple in combinations(range(N),3):
        triple_mask=sum(1<<j for j in triple)
        rest=[j for j in range(N) if j not in triple]
        def parity(a):return (a&triple_mask).bit_count()&1
        for sign in (0,1):
            for pair in [None,*combinations(rest,2)]:
                bits=sum((parity(a)^sign^int(pair is not None and all(a&(1<<j) for j in pair)))<<a for a in range(ACTIONS))
                ans.append(bits)
    assert len(ans)==160 and len(set(ans))==160
    return tuple(ans)

OLD=np.asarray(old_grammar(),dtype=np.uint64)


def build_hypotheses():
    masks=[];degrees=[];structures=[]
    for degree in range(4):
        for chosen in combinations(FEATURES,degree):
            base=0
            for j in chosen:base^=TERMS[j]
            masks.extend([base,M^base])
            degrees.extend([degree,degree])
            structures.extend([(chosen,0),(chosen,1)])
    assert len(masks)==23044
    w=np.array([TIERS[k]/(2*math.comb(len(FEATURES),k)) for k in degrees],dtype=np.float64)
    return np.asarray(masks,dtype=np.uint64),w,structures

ALL,BASE_PRIOR,STRUCT=build_hypotheses()
X=np.asarray([[(a&support)==support for support in FEATURES] for a in range(ACTIONS)],dtype=np.float64)
BITS=np.asarray([[(a>>j)&1 for j in range(N)] for a in range(ACTIONS)],dtype=np.int8)


def action_split(seed):
    order=sorted(range(ACTIONS),key=lambda a:hash_int(f'energy29/disjoint-split-v1/{seed}/{a}'))
    return tuple(order[:24]),tuple(order[24:48]),tuple(order[48:])


def _new_law(seed,world_index):
    # Source-side choice; not a learner's candidate rule lookup or a revealed label.
    # Always 3 genuinely distinct monomials and at least one cubic factor.
    ordered=sorted(FEATURES,key=lambda s:hash_int(f'energy29/newlaw-v1/{seed}/{world_index}/{s}'))
    for q in range(0,17):
        selected=ordered[q:q+3]
        if len(selected)!=3:continue
        if not any(s.bit_count()==3 for s in selected):continue
        if not any(s.bit_count()==2 for s in selected):continue
        mask=0
        for s in selected:mask^=TERMS[s]
        sign=hash_int(f'energy29/newsig-v1/{seed}/{world_index}')&1
        if sign:mask ^=M
        if mask in set(int(x) for x in OLD):continue
        return mask,tuple(selected),sign
    raise AssertionError('SOURCE_LAW_CONSTRUCTION')


def _outside_law(seed,world_index):
    # Two families well outside the original XOR3+AND2 and ANF <=3-term bank.
    bits=sorted(range(N),key=lambda j:hash_int(f'energy29/outsidevar/{seed}/{world_index}/{j}'))
    if world_index%2:
        # Majority vote of five inputs is a nonlinear degree-four ANF structure.
        chosen=bits[:5]
        mask=sum((int(sum((a>>j)&1 for j in chosen)>=3))<<a for a in range(ACTIONS))
        kind='majority5'
    else:
        four=sum(1<<j for j in bits[:4]);two=sum(1<<j for j in bits[4:])
        mask=TERMS.get(four,truthmask_monomial(four))^TERMS[two]^(sum(((a>>bits[0])&1)<<a for a in range(ACTIONS)))
        kind='degree4_interaction'
    sign=hash_int(f'energy29/outside_sign/{seed}/{world_index}')&1
    if sign:mask^=M
    return mask,kind,sign


def source_law(seed,family,world_index):
    if family=='old':return int(OLD[hash_int(f'energy29/oldchoice/{seed}/{world_index}')%len(OLD)]),'old_160',0
    if family=='novel_in_basis':
        bits,sel,sign=_new_law(seed,world_index)
        return bits,'novel_3term_anf',sign
    bits,kind,sign=_outside_law(seed,world_index)
    return bits,kind,sign


def corrupted(seed,family,world_index,train,flip_count,truth):
    observed=int(truth)
    order=sorted(range(len(train)),key=lambda i:hash_int(f'energy29/corrupt-v1/{seed}/{family}/{world_index}/{i}'))
    flipped=order[:flip_count]
    for i in flipped:observed^=1<<train[i]
    return observed,flipped


def posterior_predictions(hyp_masks,weights,train,held,seen_mask,observed):
    diff=np.bitwise_count((hyp_masks^np.uint64(observed))&np.uint64(seen_mask)).astype(np.int32)
    scaled=np.power(3.0,-diff,dtype=np.float64)*weights
    total=float(scaled.sum(dtype=np.float64))
    assert total>0.0 and math.isfinite(total)
    scores=[]
    for a in held:
        prob=float(scaled[((hyp_masks>>np.uint64(a))&np.uint64(1))==1].sum(dtype=np.float64))/total
        scores.append(int(prob>0.5))
    return scores,diff,scaled


def test_case(seed,family,world_index,flip_count):
    train,held,unused=action_split(seed)
    truth,truth_family,sign=source_law(seed,family,world_index)
    observed,flipped=corrupted(seed,family,world_index,train,flip_count,truth)
    seen_mask=sum(1<<a for a in train)
    # Old rule consistency is evaluated only on revealed public evidence.
    seen12=sum(1<<a for a in train[:12]);
    before12=np.bitwise_count((OLD^np.uint64(observed))&np.uint64(seen12)).min()
    before24=np.bitwise_count((OLD^np.uint64(observed))&np.uint64(seen_mask)).min()
    born=bool(before12>=2 or before24>=3)
    old_pred,old_diff,old_post=posterior_predictions(OLD,np.full(len(OLD),1/len(OLD)),train,held,seen_mask,observed)
    full_pred,full_diff,full_post=posterior_predictions(ALL,BASE_PRIOR,train,held,seen_mask,observed)
    constructive=full_pred if born else old_pred
    # Hard winner-take-all as an uncertainty ablation of the same candidate posterior.
    winner=int(np.argmax(full_post if born else old_post))
    map_truth=int(ALL[winner] if born else OLD[winner])
    hard_map=[(map_truth>>a)&1 for a in held]
    # Trained conventional regression on the same complete <=3 polynomial feature basis.
    feature_train=X[list(train),:];feature_held=X[list(held),:]
    labels=np.array([((observed>>a)&1)*2-1 for a in train],dtype=np.float64)
    kernel=feature_train@feature_train.T+np.eye(len(train),dtype=np.float64)
    alpha=np.linalg.solve(kernel,labels)
    ridge_scores=feature_held@(feature_train.T@alpha)
    ridge=[int(v>0) for v in ridge_scores]
    y=np.array([(observed>>a)&1 for a in train],dtype=np.uint8)
    tree=DecisionTreeClassifier(max_depth=6,min_samples_leaf=1,random_state=seed)
    tree.fit(BITS[list(train)],y)
    tree_pred=[int(z) for z in tree.predict(BITS[list(held)])]
    forest=ExtraTreesClassifier(n_estimators=31,max_depth=6,min_samples_leaf=1,max_features=None,
                               bootstrap=False,n_jobs=1,random_state=hash_int(f'energy29/forest-v1/{seed}/{world_index}')%(2**32))
    forest.fit(BITS[list(train)],y)
    forest_pred=[int(z) for z in forest.predict(BITS[list(held)])]
    targets=[(truth>>a)&1 for a in held]
    outputs=dict(old_bayes=old_pred,constructive=constructive,full_anf_bayes=full_pred,
                 conventional_poly_ridge=ridge,conventional_tree=tree_pred,
                 conventional_forest=forest_pred,hard_map=hard_map)
    if any(len(v)!=24 for v in outputs.values()):raise AssertionError('HELD_PRED_LENGTH')
    return {'seed':seed,'family':family,'world_index':world_index,'truth_kind':truth_family,'truth_mask_hex':hex(truth),
            'corrupt_count':flip_count,'train_actions':list(train),'held_actions':list(held),
            'train_observed':[int((observed>>a)&1) for a in train], 'flipped_training_positions':flipped,
            'held_truth':targets,'old_min_mismatch12':int(before12),'old_min_mismatch24':int(before24),
            'birth':born,'winner_hypothesis_index':winner,'outputs':outputs,
            'correct':{k:sum(p==t for p,t in zip(v,targets)) for k,v in outputs.items()}}


def run(smoke=False):
    seeds=(SMOKE_SEED,) if smoke else SEEDS
    laws=range(2) if smoke else range(20)
    records=[];t=time.perf_counter()
    for seed in seeds:
        for family in FAMILIES:
            for world_index in laws:
                for corrupt in NOISE:
                    records.append(test_case(seed,family,world_index,corrupt))
    strata={}
    for family in FAMILIES:
        for corruption in NOISE:
            sub=[x for x in records if x['family']==family and x['corrupt_count']==corruption]
            strata[f'{family}/noise{corruption}']={
                'worlds':len(sub),'held_per_arm':len(sub)*24,
                'births':sum(z['birth'] for z in sub),
                'correct':{k:sum(z['correct'][k] for z in sub) for k in ARMS},
                'hard_gains_over_old':sum(z['correct']['constructive']>z['correct']['old_bayes'] for z in sub),
                'hard_losses_against_old':sum(z['correct']['constructive']<z['correct']['old_bayes'] for z in sub),
            }
    return {'schema':'yggdrasil.energy29.open_anf_bounded_discovery.v1',
            'mode':'smoke' if smoke else 'scored','science':'isolated unprotected synthetic development',
            'source_unknown_to_inference':True,'candidate_bank':{'old':len(OLD),'composed':len(ALL),'degrees':list(TIERS)},
            'cases':records,'summary':{'cases':len(records),'held_per_arm':len(records)*24,
             'strata':strata,'wall_seconds_all_arms':time.perf_counter()-t}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'scored.json')
    args=parser.parse_args()
    obj=run(smoke=args.smoke)
    args.output.write_text(json.dumps(obj,separators=(',',':'),sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in obj['summary'].items() if k!='strata'}|{'strata':obj['summary']['strata']},indent=2))

if __name__=='__main__':main()
