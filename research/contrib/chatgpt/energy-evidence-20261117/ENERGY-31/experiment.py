#!/usr/bin/env python3
"""ENERGY-31: falsifiable bounded continuous causal-novelty retention experiment.

Source truth and held action patterns stay evaluator-side; all learners see only
selected public actions and their noisy experienced consequences. No native CKAD
model is imported. Prior candidate grammar is finite, NOT open-domain invention.
"""
import argparse
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import time
import numpy as np

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'protocol.json').read_text())
N_ACTIONS=64
ARMS=tuple(P['arms'])
SEEDS=tuple(P['source_seeds'])
SCENARIOS=tuple(P['scenarios'])
CHECKS=(8,16,24)

def hashint(*items):
    msg='/'.join(map(str,('energy31/v1',)+items)).encode('ascii')
    return int.from_bytes(hashlib.sha256(msg).digest(),'big')

def bank():
    masks=[];family=[];descriptions=[]
    for triple in combinations(range(6),3):
        remaining=tuple(i for i in range(6) if i not in triple)
        for sign in (0,1):
            rule=tuple(((sum((a>>j)&1 for j in triple)&1)^sign) for a in range(64))
            masks.append(rule);family.append('old');descriptions.append((triple,sign,None))
            for pair in combinations(remaining,2):
                extra=tuple(int(all((a>>j)&1 for j in pair)) for a in range(64))
                masks.append(tuple(x^y for x,y in zip(rule,extra)))
                family.append('novel');descriptions.append((triple,sign,pair))
    assert len(masks)==160 and len(set(masks))==160
    labels=np.asarray(masks,dtype=np.int8)
    indices_old=np.asarray([i for i,k in enumerate(family) if k=='old'],dtype=int)
    indices_new=np.asarray([i for i,k in enumerate(family) if k=='novel'],dtype=int)
    assert len(indices_old)==40 and len(indices_new)==120
    prior=np.zeros(160,dtype=float)
    prior[indices_old]=7/(8*40)
    prior[indices_new]=1/(8*120)
    assert abs(prior.sum()-1)<1e-12
    return labels,prior,indices_old,indices_new,descriptions

LABELS,PRIOR,OLD,NEW,DESCRIPTIONS=bank()

def choose_laws(seed,world,scenario):
    old_index=hashint('old-law',seed,world)%len(OLD)
    old=OLD[old_index].item()
    novel=NEW[hashint('novel-law',seed,world)%len(NEW)].item()
    # Ensure the known-world switch is to a genuinely different known rule.
    second=OLD[(old_index+1+hashint('second-law',seed,world)%(len(OLD)-1))%len(OLD)].item()
    assert second!=old
    if scenario=='familiar_return':return (old,novel,old)
    if scenario=='novel_persistent':return (old,novel,novel)
    if scenario=='stationary_null':return (old,old,old)
    if scenario=='known_rule_switch':return (old,second,old)
    raise ValueError(scenario)

def action_plan(seed,world,scenario):
    # The source chooses all actions before computing any hidden law/outcome.
    order=sorted(range(64),key=lambda a:hashint('held',seed,world,scenario,a))
    held=tuple(order[:12]);allowed=tuple(order[12:])
    plans=[]
    for phase in range(3):
        shuffled=sorted(allowed,key=lambda a:hashint('train',seed,world,scenario,phase,a))
        plans.append(tuple(shuffled[:24]))
    assert not (set(held)&set(sum((list(x) for x in plans),[])))
    assert all(len(set(x))==24 for x in plans)
    return held,plans

def noisy_label(seed,world,scenario,phase,index,law,action):
    truth=int(LABELS[law,action])
    corruption=int(hashint('noisy-label',seed,world,scenario,phase,index,action)%10==0)
    return truth^corruption,corruption

def likelihood(action,label):
    return np.where(LABELS[:,action]==label,0.9,0.1)

def normalize(w):
    total=float(np.sum(w,dtype=np.float64))
    if not math.isfinite(total) or total<=0:raise AssertionError('POSTERIOR_MASS')
    return w/total

class Learners:
    def __init__(self):
        self.state={arm:PRIOR.copy() for arm in ARMS}
        self.state['old_only'][NEW]=0
        self.state['old_only']=normalize(self.state['old_only'])
        self.receipts=[]
        self.evidence_hazard_triggers=0
    def transition(self,action,observed,phase_change=False):
        self.receipts.append((action,observed))
        evid=likelihood(action,observed)
        self.state['static_bayes']=normalize(self.state['static_bayes']*evid)
        recent=PRIOR.copy()
        for a,y in self.receipts[-24:]:
            recent=normalize(recent*likelihood(a,y))
        self.state['recent24_bayes']=recent
        self.state['fixed_hazard32']=normalize((self.state['fixed_hazard32']*(31/32)+PRIOR/32)*evid)
        old=self.state['evidence_hazard']
        surpr=float(np.dot(old,evid))
        hazard=(1/8 if surpr<1/4 else 1/96)
        self.evidence_hazard_triggers+=int(hazard==1/8)
        self.state['evidence_hazard']=normalize((old*(1-hazard)+PRIOR*hazard)*evid)
        if phase_change:self.state['oracle_boundary']=PRIOR.copy()
        self.state['oracle_boundary']=normalize(self.state['oracle_boundary']*evid)
        self.state['old_only']=normalize(self.state['old_only']*evid)
    def score(self,held,truth):
        results={}
        for arm,w in self.state.items():
            prob=w @ LABELS[:,held]
            correct=int(np.sum((prob>(0.5+1e-12))==truth))
            brier=float(np.sum((prob-truth)**2,dtype=np.float64))
            results[arm]={'correct':correct,'brier_sum':round(brier,12),
                          'novel_mass':round(float(np.sum(w[NEW])),12),
                          'pred':np.asarray(prob>(0.5+1e-12),dtype=int).tolist(),
                          'prob':np.round(prob,10).tolist()}
        return results

def case(seed,world,scenario):
    laws=choose_laws(seed,world,scenario)
    held,plan=action_plan(seed,world,scenario)
    model=Learners();events=[];scores=[];start=time.process_time()
    for phase,law in enumerate(laws):
        for index,action in enumerate(plan[phase]):
            actual,flip=noisy_label(seed,world,scenario,phase,index,law,action)
            model.transition(action,actual,phase_change=bool(phase>0 and index==0))
            events.append([action,actual,phase,index])
            if index+1 in CHECKS:
                true=LABELS[law,list(held)]
                scores.append({'phase':phase,'after':index+1,'truth':true.tolist(),
                               'arms':model.score(held,true)})
    return {'seed':seed,'world':world,'scenario':scenario,'laws':list(map(int,laws)),
            'held':list(held),'events':events,'scores':scores,
            'high_surprise_count':model.evidence_hazard_triggers,
            'cpu_seconds':round(time.process_time()-start,8)}

def aggregate(rows):
    groups={};gates={}
    for scenario in SCENARIOS:
        for phase in range(3):
            for after in CHECKS:
                pieces=[s for row in rows if row['scenario']==scenario for s in row['scores']
                        if s['phase']==phase and s['after']==after]
                count=len(pieces)*12
                groups[f'{scenario}/{phase}/{after}']={
                    'worlds':len(pieces),'held_per_arm':count,
                    'arms':{arm:{'correct':sum(z['arms'][arm]['correct'] for z in pieces),
                                'brier_sum':round(sum(z['arms'][arm]['brier_sum'] for z in pieces),9),
                                'novel_mass_mean':round(sum(z['arms'][arm]['novel_mass'] for z in pieces)/len(pieces),9)}
                            for arm in ARMS}}
    def g(name,phase,arm):return groups[f'{name}/{phase}/24']['arms'][arm]['correct']
    def acc(group,phase,arm):
        obj=groups[f'{group}/{phase}/24']
        return obj['arms'][arm]['correct']/obj['held_per_arm']
    novel=[acc(s,1,'evidence_hazard') for s in ('familiar_return','novel_persistent')]
    novel_fixed=[acc(s,1,'fixed_hazard32') for s in ('familiar_return','novel_persistent')]
    novel_window=[acc(s,1,'recent24_bayes') for s in ('familiar_return','novel_persistent')]
    novel_mean=sum(novel)/2;novel_ref=sum(novel_fixed)/2;novel_win=sum(novel_window)/2
    ret_scenarios=('familiar_return','known_rule_switch')
    ret_mean=sum(acc(s,2,'evidence_hazard') for s in ret_scenarios)/2
    ret_fixed=sum(acc(s,2,'fixed_hazard32') for s in ret_scenarios)/2
    stationary=acc('stationary_null',2,'evidence_hazard')
    stationary_static=acc('stationary_null',2,'static_bayes')
    stationary_novel=groups['stationary_null/2/24']['arms']['evidence_hazard']['novel_mass_mean']
    seed_gains={}
    for seed in sorted({row['seed'] for row in rows}):
        pool=[row for row in rows if row['seed']==seed and row['scenario'] in ret_scenarios]
        evidence=sum(s['arms']['evidence_hazard']['correct'] for row in pool for s in row['scores'] if s['phase']==2 and s['after']==24)
        fixed=sum(s['arms']['fixed_hazard32']['correct'] for row in pool for s in row['scores'] if s['phase']==2 and s['after']==24)
        seed_gains[str(seed)]=evidence-fixed
    gates={
      'novel_shift_gain':novel_mean>=novel_ref+0.02 and novel_mean>=novel_win-0.01,
      'returning_old_gain':ret_mean>=0.80 and ret_mean>=ret_fixed+0.02,
      'stationary_fidelity':stationary>=stationary_static-0.01 and stationary_novel<=0.25,
      'per_seed_robustness':sum(v>0 for v in seed_gains.values())>=2}
    metrics={'novel':{'evidence':novel_mean,'fixed':novel_ref,'recent24':novel_win},
             'return':{'evidence':ret_mean,'fixed':ret_fixed},
             'stationary':{'evidence':stationary,'static':stationary_static,'mean_novel_mass':stationary_novel},
             'seed_return_gains':seed_gains}
    return groups,gates,metrics

def semantic(result):
    return {k:v for k,v in result.items() if k not in ('whole_wall_seconds','total_cpu_seconds')}

def run(smoke=False):
    if smoke:seeds=(int(P['smoke_seed']),);worlds=range(int(P['smoke_world_indices']))
    else:seeds=SEEDS;worlds=range(int(P['world_indices_per_seed_and_scenario']))
    started=time.perf_counter();cstart=time.process_time()
    rows=[case(seed,w,s) for seed in seeds for w in worlds for s in SCENARIOS]
    groups,gates,metrics=aggregate(rows)
    return {'schema':'yggdrasil.energy31.continuous-novelty-result.v1',
            'kind':'smoke' if smoke else 'primary',
            'cases':rows,'groups':groups,'gates':gates,'metrics':metrics,
            'classification':'SMOKE_ONLY' if smoke else ('DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO'),
            'scientific_pass':False,'native_checkpoint_executed':False,'deployment':'NONE',
            'whole_wall_seconds':round(time.perf_counter()-started,6),
            'total_cpu_seconds':round(time.process_time()-cstart,6)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');ap.add_argument('--out',type=Path,default=ROOT/'scored.json')
    args=ap.parse_args();result=run(args.smoke)
    args.out.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'mode':result['kind'],'cases':len(result['cases']),'gates':result['gates'],
                      'metrics':result['metrics'],'class':result['classification'],'wall':result['whole_wall_seconds']},indent=2))
if __name__=='__main__':main()
