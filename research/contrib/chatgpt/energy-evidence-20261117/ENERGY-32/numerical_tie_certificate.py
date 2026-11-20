#!/usr/bin/env python3
"""POST-SCORE mathematical tie certificate, not a preregistered model change.

Uses integer likelihood products in the original finite hypothesis class to
identify posterior probabilities exactly equal to 1/2. No source imports.
"""
import itertools, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
R=[]
for tri in itertools.combinations(range(6),3):
    for sign in (0,1):R.append((tri,(),sign))
for tri in itertools.combinations(range(6),3):
    remain=tuple(x for x in range(6) if x not in tri)
    for pair in itertools.combinations(remain,2):
        for sign in (0,1):R.append((tri,pair,sign))
def label(i,a):
    t,p,s=R[i]
    return (sum((a>>j)&1 for j in t)&1) ^ (int(all((a>>j)&1 for j in p)) if p else 0) ^ s

def posterior(rows):
    # All priors put on a common denominator 960: familiar 21/960,
    # novel 1/960. Bernoulli observation likelihood 17/20 or 3/20.
    # Omit the common likelihood denominator 20**len(rows).
    weights=[]
    for i in range(160):
        weight=21 if i<40 else 1
        for a,y in rows:weight*=17 if label(i,a)==y else 3
        weights.append(weight)
    return weights

def selected_rows(case,arm):
    if arm=='no_reset' or (arm=='privileged_phase_oracle' and case['scenario']=='stationary_null'):
        return case['prefix']+case['stream']
    if arm in ('recent16','privileged_phase_oracle'):return case['stream']
    if arm=='single_surprise':return case['stream'] if case['single_alarm'] is not None else case['prefix']+case['stream']
    if arm=='paired_confirmation':return case['stream'] if case['paired_alarm'] is not None else case['prefix']+case['stream']
    raise ValueError('No integer closed form implemented for fixed-hazard arm')

def certificate(case,arm,action):
    weights=posterior(selected_rows(case,arm)); den=sum(weights)
    num=sum(w for i,w in enumerate(weights) if label(i,action))
    return {'numerator':str(num),'denominator':str(den),'exact_twice_numerator_minus_denominator':str(2*num-den), 'exact_half':2*num==den}

if __name__=='__main__':
    j=json.loads((HERE/'scored.json').read_text());
    # This post-score diagnostic does not decide which method should win.
    # Detect all exactly tied readouts for five non-hazard Bayesian arms.
    pairs=[]; all_ties=[]
    for c in j['cases']:
        for arm in ('no_reset','single_surprise','paired_confirmation','recent16','privileged_phase_oracle'):
            weights=posterior(selected_rows(c,arm));den=sum(weights)
            for k,a in enumerate(c['held']):
                num=sum(w for i,w in enumerate(weights) if label(i,a))
                if 2*num==den:
                    all_ties.append({'seed':c['seed'],'old':c['old'],'scenario':c['scenario'],'arm':arm,'held_index':k,'action':a,'source_decision':c['predictions'][arm][k],'correct':int(c['predictions'][arm][k]==label(c['true_rule'],a))})
    result={'schema':'energy32.postscore.exact-tie-certificate.v1','exact_tied_predictions':len(all_ties),'tie_records':all_ties,'frozen_score_changed':False,'source_changed':False}
    (HERE/'numerical_ties.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('Exact ties:',len(all_ties));print('Source-original decisions for tied cases:',{str(k):sum(rec['source_decision']==k for rec in all_ties) for k in (0,1)})
