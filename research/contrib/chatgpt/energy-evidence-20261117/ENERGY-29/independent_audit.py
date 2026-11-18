#!/usr/bin/env python3
"""Independent ENERGY-29 source, model and negative-control audit.

No import of experiment.py. Rebuilds causal truth tables and candidate structures
from mathematical definitions, refits conventional learners, and on a frozen
stratified sample uses exact Python integer posterior voting.
"""
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import lstsq
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier

HOME=Path(__file__).resolve().parent
ROOT_SPACE=(1<<64)-1
SEEDS=(2399,2411,2423,2441)
FAMILIES=('old','novel_in_basis','outside_basis')
ARMS=('old_bayes','constructive','full_anf_bayes','conventional_poly_ridge','conventional_tree','conventional_forest','hard_map')

def assert_sha(file,expected):
    assert hashlib.sha256((HOME/file).read_bytes()).hexdigest()==expected, 'SOURCE_DRIFT '+file

def digest_integer(record):
    return int(hashlib.sha256(record.encode('ascii')).hexdigest(),16)

def monomials():
    return [sum(1<<j for j in indexes)
            for size in (1,2,3) for indexes in combinations(range(6),size)]

def eval_product(indices,action):
    return int((action&indices)==indices)

def output_bitmap(fn):
    return sum(int(fn(a))<<a for a in range(64))

def old_rules():
    old=[]
    for group in combinations(range(6),3):
        rest=[i for i in range(6) if i not in group]
        for sign in (0,1):
            old.append(output_bitmap(lambda a,s=sign,g=group:(sum(a>>i&1 for i in g)+s)%2))
            for pair in combinations(rest,2):
                old.append(output_bitmap(lambda a,s=sign,g=group,p=pair:
                         (sum(a>>i&1 for i in g)+s+((a>>p[0]&1)&(a>>p[1]&1)))%2))
    assert len(old)==160 and len(set(old))==160
    return old

def candidate_rules(features):
    base=[output_bitmap(lambda a,s=s:eval_product(s,a)) for s in features]
    rules=[];priors=[];weights_int=[]
    tiers=(1,12,27,60)
    # LCM of C(41,0..3) equals 10660, denominators 2*100*10660.
    for degree in range(4):
        denom=math.comb(41,degree)
        v=tiers[degree]/(200*denom)
        iw=tiers[degree]*10660//denom
        assert iw>0 and v>0
        for selected in combinations(range(41),degree):
            bits=0
            for s in selected:bits ^=base[s]
            rules.extend([bits,ROOT_SPACE^bits]);priors.extend([v,v]);weights_int.extend([iw,iw])
    assert len(rules)==23044 and len(set(rules))==23044
    return np.asarray(rules,dtype=np.uint64),np.asarray(priors,dtype=np.float64),np.asarray(weights_int,dtype=np.int64)

def source_law(seed,family,i,old,feature_dict):
    if family=='old':
        return old[digest_integer(f'energy29/oldchoice/{seed}/{i}')%160]
    if family=='novel_in_basis':
        ordering=sorted(feature_dict,key=lambda s:digest_integer(f'energy29/newlaw-v1/{seed}/{i}/{s}'))
        for index in range(17):
            terms=ordering[index:index+3]
            if len(terms)!=3 or 3 not in [x.bit_count() for x in terms] or 2 not in [x.bit_count() for x in terms]:
                continue
            bits=0
            for feature in terms:bits ^=feature_dict[feature]
            if digest_integer(f'energy29/newsig-v1/{seed}/{i}')&1:bits^=ROOT_SPACE
            if bits not in old:return bits
        raise AssertionError('MISSING_NEW_SOURCE_LAW')
    ordering=sorted(range(6),key=lambda j:digest_integer(f'energy29/outsidevar/{seed}/{i}/{j}'))
    if i&1:
        c=ordering[:5]
        truth=output_bitmap(lambda a:sum(a>>j&1 for j in c)>=3)
    else:
        four=sum(1<<j for j in ordering[:4]);two=sum(1<<j for j in ordering[4:]);one=1<<ordering[0]
        truth=output_bitmap(lambda a:eval_product(four,a)^eval_product(two,a)^eval_product(one,a))
    if digest_integer(f'energy29/outside_sign/{seed}/{i}')&1:truth ^=ROOT_SPACE
    return truth


def split(seed):
    order=sorted(range(64),key=lambda a:digest_integer(f'energy29/disjoint-split-v1/{seed}/{a}'))
    assert len(set(order))==64
    return order[:24],order[24:48],order[48:]

def model_predictions(masks,prior,training,held,observed):
    use=sum(1<<j for j in training)
    err=np.bitwise_count((masks^np.uint64(observed))&np.uint64(use)).astype(np.int32)
    # Alternative stable likelihood: P(evidence|hyp)=0.75^(n-errors)*0.25^errors.
    # Common factor 0.75^n cancels; one mismatch costs 1/3.
    unnorm=prior*np.exp2(-np.float64(np.log2(3))*err)
    den=unnorm.sum(dtype=np.float64)
    assert den>0
    preds=[]
    for action in held:
        positive=unnorm[np.bitwise_and(np.right_shift(masks,np.uint64(action)),np.uint64(1))==1].sum(dtype=np.float64)
        preds.append(int(positive*2>den))
    return preds,err,unnorm


def exact_votes(masks,base_int,training,held,observed):
    errs=np.bitwise_count((masks^np.uint64(observed))&np.uint64(sum(1<<j for j in training))).astype(np.int8)
    # Exact integer normalized posterior with tier prior fractions: no floating-roundoff.
    weights=(base_int.astype(object)*np.fromiter((3**(24-int(e)) for e in errs),dtype=object,count=len(errs)))
    total=sum(int(v) for v in weights)
    pred=[]
    for action in held:
        subset=weights[np.bitwise_and(np.right_shift(masks,np.uint64(action)),np.uint64(1))==1]
        pos=sum(int(v) for v in subset)
        pred.append(int(pos*2>total))
    return pred


def main():
    freeze=json.loads((HOME/'freeze.json').read_text());protocol=json.loads((HOME/'protocol.json').read_text())
    assert freeze['schema']=='energy29.frozen-source-before-scoring.v1'
    assert freeze['freeze_created_without_scored_file'] is True
    for f,key in [('experiment.py','source_sha256'),('protocol.json','protocol_sha256'),('smoke.json','smoke_sha256')]:assert_sha(f,freeze[key])
    assert protocol['source_design']['seeds']==list(SEEDS)
    assert protocol['source_design']['total_scored_cases']==480
    j=json.loads((HOME/'scored.json').read_text())
    assert j['mode']=='scored' and j['summary']['cases']==len(j['cases'])==480
    assert j['candidate_bank']['old']==160 and j['candidate_bank']['composed']==23044
    assert len(j['cases'])==len({(r['seed'],r['family'],r['world_index'],r['corrupt_count']) for r in j['cases']})
    expected_keys={(seed,fam,i,flip) for seed in SEEDS for fam in FAMILIES for i in range(20) for flip in (0,2)}
    assert {(r['seed'],r['family'],r['world_index'],r['corrupt_count']) for r in j['cases']}==expected_keys
    features=monomials();feature_dict={v:output_bitmap(lambda a,s=v:eval_product(s,a)) for v in features}
    old_list=old_rules();old_np=np.asarray(old_list,dtype=np.uint64)
    full_np,priors,priors_int=candidate_rules(features)
    full_set=set(map(int,full_np))
    assert np.isclose(sum(priors),1.0,atol=1e-13)
    input_features=np.asarray([[eval_product(f,a) for f in features] for a in range(64)],dtype=np.float64)
    bits=np.asarray([[(a>>k)&1 for k in range(6)] for a in range(64)],dtype=np.int64)
    tally=defaultdict(lambda:defaultdict(int))
    near_zero_regression=0;predictions_checked=0;causal_truth_checked=0;exact_vote_audits=0;all_invariants=0
    novel_in_old=0;outside_in_new=0
    for row in j['cases']:
        seed, fam, i, noise = row['seed'],row['family'],row['world_index'],row['corrupt_count']
        stage=f'{fam}/noise{noise}'
        train,held,unused=split(seed)
        assert row['train_actions']==train and row['held_actions']==held
        assert len(unused)==16 and not (set(train)&set(held))
        true=source_law(seed,fam,i,old_list,feature_dict)
        assert row['truth_mask_hex']==hex(true)
        if fam=='novel_in_basis':assert true in full_set and true not in old_list
        if fam=='outside_basis':assert true not in full_set and true not in old_list
        flips=sorted(range(24),key=lambda k:digest_integer(f'energy29/corrupt-v1/{seed}/{fam}/{i}/{k}'))[:noise]
        assert row['flipped_training_positions']==flips
        observed=true
        for k in flips:observed ^= 1<<train[k]
        assert row['train_observed']==[(observed>>a)&1 for a in train]
        truth=[(true>>a)&1 for a in held]
        assert row['held_truth']==truth
        causal_truth_checked+=len(held)
        given=np.uint64(observed)
        min12=min(int(x.bit_count()) for x in [int((int(guess)^observed)&sum(1<<z for z in train[:12])) for guess in old_list])
        min24=min(int(x.bit_count()) for x in [int((int(guess)^observed)&sum(1<<z for z in train)) for guess in old_list])
        born=bool(min12>=2 or min24>=3)
        assert row['old_min_mismatch12']==min12 and row['old_min_mismatch24']==min24
        assert row['birth']==born
        old_pred,old_errors,old_w=model_predictions(old_np,np.full(160,1/160),train,held,observed)
        full_pred,full_errors,full_w=model_predictions(full_np,priors,train,held,observed)
        construct=full_pred if born else old_pred
        hardest=full_np if born else old_np;weight=full_w if born else old_w
        winner=int(np.argmax(weight));assert winner==row['winner_hypothesis_index']
        map_preds=[(int(hardest[winner])>>a)&1 for a in held]
        # Distinct matrix-algebra refit: augmented least squares versus scorer's kernel solve.
        feat=input_features[train];y=np.asarray([(observed>>a&1)*2-1 for a in train],dtype=float)
        augmented=np.vstack([feat,np.eye(len(features))]);rhs=np.r_[y,np.zeros(len(features))]
        beta=lstsq(augmented,rhs,lapack_driver='gelsy')[0]
        ridges=input_features[held]@beta
        ridge_preds=[int(q>0) for q in ridges]
        assert all((abs(q)>1e-8 or q==0) for q in ridges)  # sanity and near-zero tracking
        near_zero_regression+=sum(abs(q)<=1e-8 for q in ridges)
        yy=np.asarray([(observed>>a)&1 for a in train],dtype=np.uint8)
        tree=DecisionTreeClassifier(max_depth=6,min_samples_leaf=1,random_state=seed).fit(bits[train],yy)
        tree_preds=list(map(int,tree.predict(bits[held])))
        rf_seed=digest_integer(f'energy29/forest-v1/{seed}/{i}')%(2**32)
        rf=ExtraTreesClassifier(n_estimators=31,max_depth=6,min_samples_leaf=1,max_features=None,
                       bootstrap=False,n_jobs=1,random_state=rf_seed).fit(bits[train],yy)
        forest_preds=list(map(int,rf.predict(bits[held])))
        generated={'old_bayes':old_pred,'constructive':construct,'full_anf_bayes':full_pred,
           'conventional_poly_ridge':ridge_preds,'conventional_tree':tree_preds,
           'conventional_forest':forest_preds,'hard_map':map_preds}
        for arm,values in generated.items():
            if values!=row['outputs'][arm]:
                divergent=[(k,v,row['outputs'][arm][k]) for k,v in enumerate(values) if v!=row['outputs'][arm][k]]
                raise AssertionError(f'SCORE_DISAGREEMENT {seed}/{fam}/{i}/{noise}/{arm}: {divergent[:10]}')
            correct=sum(p==t for p,t in zip(values,truth))
            assert correct==row['correct'][arm]
            tally[stage][arm]+=correct
            predictions_checked+=len(held)
        tally[stage]['births']+=int(born)
        tally[stage]['cases']+=1
        # Fully exact posterior independent check, stratified before seeing outcomes.
        if i in (0,10):
            exact=exact_votes(full_np,priors_int,train,held,observed)
            if exact!=full_pred:raise AssertionError('EXACT_POSTERIOR_ROUNDING_SEED')
            exact_vote_audits+=len(held)
        all_invariants+=22
    assert predictions_checked==480*7*24
    assert causal_truth_checked==480*24
    assert exact_vote_audits==4*3*2*2*24
    for stage,summary in j['summary']['strata'].items():
        assert summary['worlds']==tally[stage]['cases']==80
        assert summary['births']==tally[stage]['births']
        for arm in ARMS:assert summary['correct'][arm]==tally[stage][arm]
    audit={'schema':'energy29.independent-reconstruction.v1','status':'PASS','score_rows':len(j['cases']),
       'per_arm_held_truths':480*24,'individual_predictions_independently_verified':predictions_checked,
       'causal_outcomes_independently_reconstructed':causal_truth_checked,
       'exact_big_integer_held_posterior_votes_verified':exact_vote_audits,
       'structural_invariants_checked':all_invariants,
       'total_assertion_bearing_checks':predictions_checked+causal_truth_checked+exact_vote_audits+all_invariants,
       'source_sha256':freeze['source_sha256'],'protocol_sha256':freeze['protocol_sha256'],
       'numeric_ridge_near_zero_held_margins':near_zero_regression,
       'method_notes':'Reconstructed all causal truth tables, source masks/splits, forest and tree fits, augmented-LS ridge vs source kernel solve, independent Bayes posterior, and exact integer votes on 48 stratified cases; no import of experiment.py.',
       'strata':{k:dict(v) for k,v in tally.items()},'scientific_pass':False,'deployment':'NONE'}
    (HOME/'audit_result.json').write_text(json.dumps(audit,sort_keys=True,indent=2,default=int)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('strata','method_notes')},indent=2,default=int))

if __name__=='__main__':main()
