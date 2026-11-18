#!/usr/bin/env python3
"""ENERGY-32, preregistered repeated-intervention causal-change diagnosis.

All outcomes are revealed only after the chosen public action; no held data fits a model.
This is a source-free finite-Bayes comparison, not native Yggdrasil training.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time
import numpy as np

HERE=Path(__file__).resolve().parent
PRIOR_OLD=7/8
ERR=.15
ARMS=('no_reset','single_surprise','paired_confirmation','fixed_hazard','recent16','privileged_phase_oracle')
SCENARIOS=('stationary_null','novel_change','familiar_switch')
RULES=[]
for triple in combinations(range(6),3):
    for sign in (0,1):RULES.append((triple,None,sign))
for triple in combinations(range(6),3):
    remain=tuple(x for x in range(6) if x not in triple)
    for pair in combinations(remain,2):
        for sign in (0,1):RULES.append((triple,pair,sign))
assert len(RULES)==160
ACTIONS=[tuple((a>>i)&1 for i in range(6)) for a in range(64)]
TRUTH=np.array([[sum(a[x] for x in rule[0])%2 ^ (a[rule[1][0]]&a[rule[1][1]] if rule[1] else 0) ^ rule[2]
                 for a in ACTIONS] for rule in RULES],dtype=np.uint8)
PRIOR=np.array([PRIOR_OLD/40]*40+[(1-PRIOR_OLD)/120]*120,dtype=float)

def h(*items):return sha256('/'.join(map(str,('energy32-v1',*items))).encode('ascii')).digest()
def index(*items,n):return int.from_bytes(h(*items)[:8],'big')%n
# Identical public evidence for every arm and hidden action labels only for evaluator.
def build(seed,old,scenario):
    keys=sorted(range(64), key=lambda a:h('split',seed,old,scenario,a))
    old_actions=keys[:24]; distinct=keys[24:32]; held=keys[32:44]
    challenge=sorted(distinct,key=lambda a:h('order',seed,old,scenario,a))
    target=old if scenario=='stationary_null' else (40+index('new',seed,old,n=120) if scenario=='novel_change' else (old+2+2*index('switch',seed,old,n=19))%40)
    # Old starts from even signed rule ids, and the switch chooses a different even id.
    assert scenario=='stationary_null' or target!=old
    prefix=[]; stream=[]
    def row(a,rule,stage,ordinal):
        flip=int.from_bytes(h('noise',seed,old,scenario,stage,ordinal,a)[:8],'big')/2**64 < ERR
        return [a,int(TRUTH[rule,a])^int(flip)]
    for k,a in enumerate(old_actions): prefix.append(row(a,old,'old',k))
    for k,a in enumerate(challenge):
        stream.append(row(a,target,'new',2*k));stream.append(row(a,target,'new',2*k+1))
    return {'seed':seed,'old':old,'scenario':scenario,'target_family':'novel' if target>=40 else 'familiar', 'prefix':prefix,'stream':stream,'held':held},target

def update(w,a,y):
    likelihood=np.where(TRUTH[:,a]==y,1-ERR,ERR)
    z=w*likelihood
    return z/z.sum()

def predict(w,a):return float(w@TRUTH[:,a])

def fit(rows,prior=None):
    w=PRIOR.copy() if prior is None else prior.copy()
    for a,y in rows:w=update(w,a,y)
    return w

def fit_case(case):
    prefix,stream=case['prefix'],case['stream']
    models={}
    models['no_reset']=fit(prefix+stream)
    models['recent16']=fit(stream)
    models['privileged_phase_oracle']=fit(stream) if case['scenario']!='stationary_null' else models['no_reset'].copy()
    w=PRIOR.copy()
    for a,y in prefix:
        w=update((47/48)*w+(1/48)*PRIOR,a,y)
    for a,y in stream:
        w=update((47/48)*w+(1/48)*PRIOR,a,y)
    models['fixed_hazard']=w
    w=fit(prefix); single_alarm=None
    for i,(a,y) in enumerate(stream):
        if single_alarm is None:
            p=predict(w,a)
            likelihood=p if y else 1-p
            if likelihood < .18:
                single_alarm=i+1
                w=fit(stream[:i+1])
                continue
        w=update(w,a,y)
    models['single_surprise']=w
    w=fit(prefix); paired_alarm=None
    for k in range(0,len(stream),2):
        (a,y),(b,z)=stream[k:k+2]
        assert a==b
        if paired_alarm is None:
            p=predict(w,a)
            if (p>=.80 and y==z==0) or (p<=.20 and y==z==1):
                paired_alarm=k+2
                w=fit(stream[:k+2]);continue
        w=update(update(w,a,y),b,z)
    models['paired_confirmation']=w
    scores={arm:sum((predict(w,a)>.5)==bool(TRUTH[case['true_rule'],a]) for a in case['held']) for arm,w in models.items()}
    predictions={arm:[int(predict(w,a)>.5) for a in case['held']] for arm,w in models.items()}
    return {'correct':scores,'predictions':predictions,'single_alarm':single_alarm,'paired_alarm':paired_alarm,
            'belief_novel':{arm:round(float(w[40:].sum()),12) for arm,w in models.items()}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--out',default='scored.json');args=p.parse_args()
    protocol=json.loads((HERE/'protocol.json').read_text())
    if not args.smoke:assert protocol['seeds']==[5021,5039,5051,5059]
    seeds=[99991] if args.smoke else protocol['seeds'];old_ids=[0,2] if args.smoke else list(range(0,40,2))
    started=time.perf_counter();cases=[];agg=defaultdict(lambda:defaultdict(int));count=defaultdict(int);per_seed=defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    for seed in seeds:
      for old in old_ids:
       for scenario in SCENARIOS:
        case,target=build(seed,old,scenario);case['true_rule']=target
        data=fit_case(case)
        for arm in ARMS:
            agg[scenario][arm]+=data['correct'][arm]
            per_seed[str(seed)][scenario][arm]+=data['correct'][arm]
        count[scenario]+=1
        cases.append({**case,**data})
    totals={s:{a:int(agg[s][a]) for a in ARMS} for s in SCENARIOS}
    n={s:count[s]*12 for s in SCENARIOS}
    paired_fp=sum(c['paired_alarm'] is not None for c in cases if c['scenario']=='stationary_null')
    single_fp=sum(c['single_alarm'] is not None for c in cases if c['scenario']=='stationary_null')
    gates={'new_change_vs_single':all((totals[s]['paired_confirmation']-totals[s]['single_surprise'])/n[s]>=.03 for s in ('novel_change','familiar_switch')),
       'false_alarm':paired_fp/count['stationary_null']<=.10,
       'full_bayes':all(totals[s]['paired_confirmation']>=totals[s]['fixed_hazard'] for s in SCENARIOS),
       'stationary_retention':totals['stationary_null']['paired_confirmation']/n['stationary_null']>=.95}
    result={'schema':'yggdrasil.energy32.score.v1','classification':'DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO',
        'mode':'smoke' if args.smoke else 'primary','seeds':seeds,'cases':cases,'case_count':len(cases),'held_per_case':12,'observations_per_case':40,
        'source_structure_count':160,'scenario_totals':totals,'scenario_denominators':n,'false_alarms':{'paired':paired_fp,'single':single_fp},
        'gates':gates,'per_seed':{s:dict(v) for s,v in per_seed.items()},'wall_seconds':time.perf_counter()-started,
        'scientific_pass':False,'native_checkpoint_run':False,'deployment':'NONE'}
    (HERE/args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','per_seed')},sort_keys=True,indent=2))
if __name__=='__main__':main()
