#!/usr/bin/env python3
"""ENERGY-26 independent deterministic data and numerical audit.

This is an after-score auditor; it does not import the scoring module.
Full Bayesian votes are evaluated with integer weights, not the scoring floats.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
FIVE=tuple(itertools.product([-1,1],repeat=5))
TRIPLES=tuple(itertools.combinations(range(5),3))
RULES=tuple((p,s) for p in TRIPLES for s in (-1,1))
ARMS=['pairwise_energy','cubic_energy','projected_energy','capacity_matched_projected_conventional','exact_fixed_noise_bayes','exact_unknown_noise_beta_bayes']


def re_order(seed,parent,sign,noise):
    scope=f'energy26/split-v1/seed={seed}/parents={parent}/sign={sign}/noise={noise}'
    # Intentionally uses (digest, action) tuple-sort instead of key-sort.
    return [a for _,a in sorted((hashlib.sha256((scope+'/a='+str(a)).encode()).digest(),a) for a in FIVE)]


def features(actions,high):
    arr=[]
    for x in actions:
        arr.append([1,*x, *[math.prod(x[i] for i in p) for p in TRIPLES]] if high else [1,*x])
    return np.array(arr,dtype=float)


def independent_ridge(x,y,lambda_):
    # Different numerical algorithm from scorer: augmented least squares,
    # rather than normal equation inversion.
    n=x.shape[1]
    X=np.concatenate((x,np.sqrt(lambda_)*np.eye(n)),axis=0)
    Y=np.concatenate((y,np.zeros(n)),axis=0)
    return np.linalg.lstsq(X,Y,rcond=None)[0]


def verify(case, protocol):
    count=0
    seed=int(case['seed']);parent=tuple(case['source_parent']);sign=int(case['source_sign']);flips=int(case['source_flip_count'])
    assert parent in TRIPLES and sign in (-1,1) and flips in (0,2,4)
    seq=re_order(seed,parent,sign,flips)
    tr=[tuple(x) for x in case['training_actions']];held=[tuple(x) for x in case['held_actions']]
    assert tr==seq[:16] and held==seq[16:] and len(set(tr))==16 and len(set(held))==16
    scope=f'energy26/corrupt-v1/seed={seed}/parents={parent}/sign={sign}/noise={flips}'
    ranked=sorted(range(16),key=lambda i:hashlib.sha256((scope+'/a='+str(tr[i])).encode()).digest())
    assert case['train_corruption_indices']==ranked[:flips]
    ytrue=[sign*math.prod(a[i] for i in parent) for a in tr]
    obs=ytrue.copy()
    for idx in ranked[:flips]:obs[idx]*=-1
    assert obs==case['training_observed'];count+=16
    truth=[sign*math.prod(a[i] for i in parent) for a in held]
    assert truth==case['held_truth'];count+=16
    # Refit without sharing implementation or calling the scorer.
    low=independent_ridge(features(tr,False),np.asarray(obs,dtype=float),protocol['ridge_lambda'])
    hi=independent_ridge(features(tr,True),np.asarray(obs,dtype=float),protocol['ridge_lambda'])
    original=np.asarray(case['weight_high'])
    assert np.max(np.abs(hi-original))<1e-8
    assert tuple(TRIPLES[int(np.argmax(np.abs(hi[6:])))])==tuple(case['selected_parent'])
    sign_pred=1 if hi[6+TRIPLES.index(tuple(case['selected_parent']))]>=0 else -1
    assert sign_pred==case['selected_sign']
    projected=[sign_pred*math.prod(a[i] for i in case['selected_parent']) for a in held]
    assert projected==case['predictions']['projected_energy']==case['predictions']['capacity_matched_projected_conventional'];count+=32
    near_zero={'pairwise_energy':0,'cubic_energy':0}
    for arm,coeff,design in [('pairwise_energy',low,features(held,False)),('cubic_energy',hi,features(held,True))]:
        raw=design@coeff
        for score,guess in zip(raw,case['predictions'][arm]):
            if abs(score)<=1e-8:near_zero[arm]+=1
            else:assert (1 if score>=0 else -1)==guess
            count+=1
    m=[]
    for p,s in RULES:
        predicted=[s*math.prod(a[i] for i in p) for a in tr]
        m.append(sum(pred!=actual for pred,actual in zip(predicted,obs)))
    assert m==case['hypothesis_mistakes']
    fixed=[19**(16-x) for x in m]
    # Beta(1,4) integrated noise prior: weights proportional to B(1+m,4+n-m)
    robust=[math.factorial(x)*math.factorial(16-x+3) for x in m]
    tie={'fixed':0,'robust':0}
    for method,weights,key in [('fixed',fixed,'exact_fixed_noise_bayes'),('robust',robust,'exact_unknown_noise_beta_bayes')]:
        if weights.index(max(weights)) != case['bayes_'+method]['map_index']:raise AssertionError('MAP_INDEX '+key)
        for action,guess in zip(held,case['predictions'][key]):
            vote=sum(w*s*math.prod(action[i] for i in p) for w,(p,s) in zip(weights,RULES))
            if vote==0:tie[method]+=1
            else:assert (1 if vote>=0 else -1)==guess, (key,seed,parent,flips,vote,guess)
            count+=1
    return count,near_zero,tie


def main():
    p=json.loads((HERE/'protocol.json').read_text())
    freeze=json.loads((HERE/'freeze.json').read_text())
    assert hashlib.sha256((HERE/'experiment.py').read_bytes()).hexdigest()==freeze['source_code_sha256']
    assert hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest()==freeze['protocol_sha256']
    j=json.loads((HERE/'scored.json').read_text())
    assert j['protocol']==p
    assert len(j['cases'])==240
    asserts=0;near_zero={'pairwise_energy':0,'cubic_energy':0};tie={'fixed':0,'robust':0}
    for case in j['cases']:
        checks,near,bt=verify(case,p)
        asserts+=checks
        for k in near_zero:near_zero[k]+=near[k]
        for k in tie:tie[k]+=bt[k]
    for n in p['noise_flips_in_16_training_observations']:
        subset=[c for c in j['cases'] if c['source_flip_count']==n]
        m=j['results'][str(n)]
        assert len(subset)==m['worlds']==80
        assert m['held_per_arm']==1280
        for a in ARMS:
            correct=sum(c['predictions'][a][i]==c['held_truth'][i] for c in subset for i in range(16))
            assert correct==m['correct'][a]
            asserts+=1280
        assert sum(c['selected_parent']==c['source_parent'] and c['selected_sign']==c['source_sign'] for c in subset)==m['parent_correct']
    verdict={'schema':'energy26.independent_audit.v1','status':'PASS','predictive_certificates_and_invariants':asserts,'worlds':len(j['cases']),'held_per_arm':3840,'source_pins':{'experiment_sha256':freeze['source_code_sha256'],'protocol_sha256':freeze['protocol_sha256'],'scored_sha256':hashlib.sha256((HERE/'scored.json').read_bytes()).hexdigest()},'near_zero_linear_margins':near_zero,'exact_bayesian_zero_votes':tie,'scores':j['results'],'native_checkpoint_evaluated':False,'scientific_pass':False}
    (HERE/'audit_result.json').write_text(json.dumps(verdict,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in verdict.items() if k!='scores'},indent=2,sort_keys=True))

if __name__=='__main__':main()
