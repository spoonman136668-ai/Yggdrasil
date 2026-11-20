#!/usr/bin/env python3
"""Independent exact-integer verification of ENERGY-28 scored causal evidence.

Does not import experiment.py, and regenerates hidden source laws and outcomes
from an independently authored implementation. Read-only; no new training.
"""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.linalg import solve

ROOT=Path(__file__).resolve().parent
SOURCE=json.loads((ROOT/'scored.json').read_text())
FREEZE=json.loads((ROOT/'freeze.json').read_text())
COUNT=0
NEAR_ZERO=0
DIFF_NEAR_ZERO=0


def check(q,msg):
    global COUNT
    COUNT+=1
    if not q:
        raise AssertionError(f'{msg}: failed check #{COUNT}')


def bank():
    triples=list(itertools.combinations(range(6),3))
    base=[]; extended=[]
    for t in triples:
        unused=tuple(v for v in range(6) if v not in t)
        for sign in (0,1):
            base.append((t,(),sign))
            for pair in itertools.combinations(unused,2):
                extended.append((t,pair,sign))
    return base+extended


LAWS=bank()
check(len(LAWS)==160,'exact grammar count')
OUT=[]
for parents,interaction,sign in LAWS:
    row=[]
    for intervention in range(64):
        values=tuple((intervention>>k)&1 for k in range(6))
        parent_bit=sum(values[k] for k in parents)&1
        and_bit=values[interaction[0]]&values[interaction[1]] if interaction else 0
        row.append(parent_bit^and_bit^sign)
    OUT.append(tuple(row))


def source_actions(seed,rid):
    return [a for _,a in sorted((hashlib.sha256(
        f'energy28/split-v1/{seed}/{rid}/{a}'.encode()).digest(),a) for a in range(64))]


def changed_positions(seed,rid):
    return [i for _,i in sorted((hashlib.sha256(
        f'energy28/corruption-v1/{seed}/{rid}/{i}'.encode()).digest(),i) for i in range(16))]


def exact_posterior(train,labels,novel=False):
    limit=160 if novel else 40
    out=[]
    for rid in range(limit):
        errors=sum(OUT[rid][action]!=observed for action,observed in zip(train,labels))
        mass=pow(7,len(train)-errors)
        if novel and rid<40:
            mass*=21
        out.append(mass)
    return out


def predict(weights,held):
    denominator=sum(weights)
    return [int(2*sum(weight*OUT[rid][a] for rid,weight in enumerate(weights))>denominator)
            for a in held]


def conventional(train,labels,held):
    # Separate SciPy pivoted-system implementation of a fully trained kernel
    # ridge learner, distinct from scorer's np.linalg.solve.
    features=np.array([[2*OUT[law][action]-1 for law in range(160)] for action in train],dtype=float)
    matrix=features@features.T+np.eye(len(train))
    weights=solve(matrix,np.array([2*y-1 for y in labels],dtype=float),assume_a='pos')
    check(np.max(abs(matrix@weights -np.array([2*y-1 for y in labels])))<1e-8,'conventional residual')
    test=np.array([[2*OUT[law][action]-1 for law in range(160)] for action in held],dtype=float)
    score=test@(features.T@weights)
    return (score>0).astype(int).tolist(),score


for filename,expected in FREEZE['sha256'].items():
    check(hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==expected,'frozen '+filename)
check(SOURCE['schema']=='yggdrasil.energy28.causal-hypothesis-birth.v1','score schema')
check(SOURCE['mode']=='score','not smoke')
check(len(SOURCE['cases'])==960,'960 scored original models')
check(SOURCE['candidate_bank']=={'initial':40,'generated_interaction':120,'full':160},'same grammar size')
seen=set();aggregates={}
for case in SOURCE['cases']:
    seed,rid,err=case['seed'],case['rule_index'],case['corrupted']
    k=(seed,rid,err)
    check(k not in seen,'duplicate case key')
    seen.add(k)
    check(seed in (1811,1823,1831) and 0<=rid<160 and err in (0,2),'qualified source cohort')
    check(case['family']==('base' if rid<40 else 'novel'),'blind source family representation')
    split=source_actions(seed,rid)
    train,held=split[:16],split[16:32]
    check(train==case['train_actions'] and held==case['held_actions'],'independent SHA split')
    check(len(set(train+held))==32,'no overlap')
    flips=changed_positions(seed,rid)[:err]
    check(flips==case['flips'],'corruption evidence indices')
    outcomes=[OUT[rid][a] for a in train]
    for i in flips: outcomes[i]^=1
    check(outcomes==case['train_observed'],'only source revealed outcomes')
    truth=[OUT[rid][a] for a in held]
    check(truth==case['held_truth'],'unseen causal source outcomes')
    mismatch8=min(sum(OUT[j][a]!=y for a,y in zip(train[:8],outcomes[:8])) for j in range(40))
    mismatch16=min(sum(OUT[j][a]!=y for a,y in zip(train,outcomes)) for j in range(40))
    birth=mismatch8>=2 or mismatch16>=3
    check(case['old_min_mismatch8']==mismatch8,'8 observation trigger threshold')
    check(case['old_min_mismatch16']==mismatch16,'16 observation trigger threshold')
    check(case['born']==birth,'birth only after witnessed contradictions')
    old=exact_posterior(train,outcomes)
    full=exact_posterior(train,outcomes,True)
    old_pred=predict(old,held)
    birth_pred=predict(full,held) if birth else old_pred
    full_pred=predict(full,held)
    selected=full if birth else old
    top=max(range(len(selected)),key=lambda i:selected[i])
    hard=[OUT[top][a] for a in held]
    check(top==case['posterior_winner_index'],'posterior MAP winner')
    check(case['generated_new_rule']==(birth and top>=40),'created rule recognized without hidden labels')
    models={'old_bank':old_pred,'birth':birth_pred,'full_grammar':full_pred,'birth_hard_map':hard}
    for arm,preds in models.items():
        check(case['predictions'][arm]==preds,arm+' exact rule-level predictions')
    conventional_preds,scores=conventional(train,outcomes,held)
    for i,(scored_pred,recomputed,margin) in enumerate(zip(case['predictions']['conventional_ridge'],conventional_preds,scores)):
        if abs(margin)<=1e-8:
            NEAR_ZERO+=1
            if scored_pred!=recomputed:DIFF_NEAR_ZERO+=1
        else:
            check(scored_pred==recomputed,'material conventional prediction disagreement')
    for arm,preds in {**models,'conventional_ridge':case['predictions']['conventional_ridge']}.items():
        check(sum(x==y for x,y in zip(preds,truth))==case['correct'][arm],'correct count '+arm)
    agg=aggregates.setdefault(f"{case['family']}/corrupt{err}",{'worlds':0,'held_predictions_per_arm':0,'born':0,'generated_new_rule':0,'correct':{k:0 for k in case['correct']}})
    agg['worlds']+=1;agg['held_predictions_per_arm']+=len(held);agg['born']+=int(birth);agg['generated_new_rule']+=int(case['generated_new_rule'])
    for arm,c in case['correct'].items():agg['correct'][arm]+=c
check(len(seen)==960,'exact complete score cohorts')
for label,aggregate in aggregates.items():
    check(aggregate==SOURCE['aggregate']['strata'][label],'full independent reaggregate '+label)
for name,expected in [('base/corrupt0',120),('base/corrupt2',120),('novel/corrupt0',360),('novel/corrupt2',360)]:
    check(aggregates[name]['worlds']==expected,'balanced trials')
result={'schema':'yggdrasil.energy28.independent-audit.v1','status':'PASS','checked_assertions':COUNT,'source_scored_sha256':hashlib.sha256((ROOT/'scored.json').read_bytes()).hexdigest(),'training_cases':len(seen),'exact_source_outcomes':len(seen)*32,'held_predictions_checked_arms':len(seen)*16*5,'conventional_nearzero_margins':NEAR_ZERO,'different_conventional_nearzero_classifications':DIFF_NEAR_ZERO,'strata':aggregates,'native_checkpoint_executed':False,'scientific_pass':False}
(ROOT/'audit_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='strata'},indent=2))
