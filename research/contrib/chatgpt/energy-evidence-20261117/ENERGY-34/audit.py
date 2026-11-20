#!/usr/bin/env python3
"""ENERGY-34 independent receipt and generative-world auditor, not model-retraining proof.

Rebuilds action splits, hidden causal functions and noise by scalar Python without
importing experiment.py or using its feature matrix; checks all primary case receipts.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys

SOURCE_SHA='716f090f935184763f2d882a1aa6743867af0e2f3422946e789839b3ff3a0419'
SEEDS=(7117,7129,7151)
FAMILIES=('parity3','mixed','extended4')
SCENARIOS=('iid','shift_x0','heavy_noise')
ARMS=('sparse_energy','omp12','logistic','ridge','rbf_svm','decision_tree','shuffled_energy','majority')
CONTROLS=('omp12','logistic','ridge','rbf_svm','decision_tree')

def h(*parts):
    return sha256('/'.join(map(str,('energy34-v1',*parts))).encode('ascii')).digest()
def pick(*parts,limit):
    return int.from_bytes(h(*parts)[:8],'big')%limit

def reconstruct(seed,world,family,scenario):
    universe=[]
    for degree in (1,2,3,4):
        universe.extend([('parity',x) for x in combinations(range(8),degree)])
    universe.extend([('and',x) for x in combinations(range(8),2)])
    pool={k:[p for p,c in enumerate(universe) if c[0]=='parity' and len(c[1])==k] for k in (2,3,4)}
    ands=[p for p,c in enumerate(universe) if c[0]=='and']
    source_pools=([pool[3]]*3 if family=='parity3' else
                  [pool[3],pool[2],ands] if family=='mixed' else
                  [pool[4],pool[3],ands])
    chosen=[]
    for i,bank in enumerate(source_pools):
        k=pick('factor',seed,world,family,i,limit=len(bank))
        while bank[k] in chosen: k=(k+1)%len(bank)
        chosen.append(bank[k])
    signs=[1 if pick('sign',seed,world,family,i,limit=2) else -1 for i in range(3)]
    def bit(x,j):return (x>>j)&1
    def score(x):
        total=0
        for i,sign in zip(chosen,signs):
            kind,coords=universe[i]
            if kind=='parity':
                value=1
                for j in coords:value*=2*bit(x,j)-1
            else:value=2*(bit(x,coords[0])&bit(x,coords[1]))-1
            total+=sign*value
        return 1 if total>0 else -1
    if scenario=='shift_x0':
        trainpool=[i for i in range(256) if bit(i,0)==0]
        holdpool=[i for i in range(256) if bit(i,0)==1]
    else:
        mixed=sorted(range(256),key=lambda i:h('split',seed,world,family,scenario,i))
        trainpool=mixed[:96];holdpool=mixed[96:160]
    train=sorted(trainpool,key=lambda i:h('train_order',seed,world,family,scenario,i))[:96]
    hold=sorted(holdpool,key=lambda i:h('held_order',seed,world,family,scenario,i))[:64]
    flip_prob=.30 if scenario=='heavy_noise' else .10
    noisy=[]
    for j in train:
        flip=int.from_bytes(h('noise',seed,world,family,scenario,j)[:8],'big')/2**64<flip_prob
        noisy.append(score(j)*(-1 if flip else 1))
    return train,hold,noisy,[score(j) for j in hold],universe,chosen

def audit(filename):
    raw=Path(filename).read_bytes();d=json.loads(raw);checks=0
    def ok(pred,msg):
        nonlocal checks
        checks+=1
        if not pred:raise AssertionError(msg)
    ok(d['mode']=='primary','mode')
    ok(d['source_sha256']==SOURCE_SHA,'source')
    ok(d['schema']=='yggdrasil.energy34.score.v1','schema')
    ok(d['seeds']==list(SEEDS),'primary seeds')
    ok(d['world_count']==len(d['details'])==216,'world count')
    ok(d['feature_count']==190,'feature count')
    ok(d['observations_per_world']==96 and d['held_per_world']==64,'budgets')
    seen=set();totals={s:{a:0 for a in ARMS} for s in SCENARIOS}
    seed_tot={str(s):{c:{a:0 for a in ARMS} for c in SCENARIOS} for s in SEEDS}
    timings={a:0. for a in ARMS}
    for c in d['details']:
        seed,world,family,scenario=[c[k] for k in ('seed','world','family','scenario')]
        key=(seed,world,family,scenario)
        ok(key not in seen,'duplicate');seen.add(key)
        ok(seed in SEEDS and world in range(8) and family in FAMILIES and scenario in SCENARIOS,'identity')
        train,held,noisy,truth,universe,selected=reconstruct(seed,world,family,scenario)
        ok(len(universe)==190 and len(set(selected))==3,'independent source structure')
        ok(len(train)==96 and len(set(train))==96,'train intervention count')
        ok(len(held)==64 and len(set(held))==64,'held intervention count')
        ok(set(train).isdisjoint(held),'held contamination')
        ok(len(noisy)==96 and all(t in (-1,1) for t in noisy),'noise reconstruction')
        ok(len(truth)==64 and all(t in (-1,1) for t in truth),'target reconstruction')
        if scenario=='shift_x0':
            ok(all((i&1)==0 for i in train),'fit shift boundary')
            ok(all((i&1)==1 for i in held),'held shift boundary')
        for arm in ARMS:
            correct=c['correct'][arm]
            ok(isinstance(correct,int) and 0<=correct<=64,'correctness bounds')
            ok(c['fit_inference_seconds'][arm]>=0,'time bounds')
            totals[scenario][arm]+=correct
            seed_tot[str(seed)][scenario][arm]+=correct
            timings[arm]+=c['fit_inference_seconds'][arm]
        ok(c['active']['sparse_energy']<=12 and c['active']['omp12']<=12,'capacity')
        ok(c['active']['shuffled_energy']<=12,'sham capacity')
    ok(seen=={(s,w,f,c) for s in SEEDS for w in range(8) for f in FAMILIES for c in SCENARIOS},'full grid')
    ok(totals==d['scenario_totals'],'aggregates')
    ok(seed_tot==d['per_seed'],'per seed')
    ok(d['denominators']=={c:4608 for c in SCENARIOS},'denominators')
    ok(all(abs(timings[a]-d['fit_inference_seconds'][a])<1e-8 for a in ARMS),'time aggregation')
    n=4608
    gates={
      'iid_accuracy_vs_strongest':(totals['iid']['sparse_energy']-max(totals['iid'][a] for a in CONTROLS))/n>=.03,
      'shift_accuracy_vs_strongest':(totals['shift_x0']['sparse_energy']-max(totals['shift_x0'][a] for a in CONTROLS))/n>=.03,
      'heavy_noise_nonregression':(totals['heavy_noise']['sparse_energy']-max(totals['heavy_noise'][a] for a in CONTROLS))/n>=-.01,
      'seed_stability':sum(all(seed_tot[str(s)][c]['sparse_energy']>max(seed_tot[str(s)][c][a] for a in CONTROLS) for c in ('iid','shift_x0')) for s in SEEDS)>=2,
      'learned_vs_shuffled':all(totals[c]['sparse_energy']>totals[c]['shuffled_energy'] for c in SCENARIOS),
      'efficiency_vs_fastest_control':timings['sparse_energy']<=.5*min(timings[a] for a in CONTROLS)
    }
    ok(gates==d['gates'],'frozen gates')
    ok(d['classification']==('DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO'),'verdict')
    ok(d['scientific_pass'] is False and d['native_checkpoint_run'] is False and d['deployment']=='NONE','authority')
    return {'status':'PASS','checks':checks,'original_scored_json_sha256':sha256(raw).hexdigest(),'cases':len(seen),
            'scenario_totals':totals,'gates':gates,'source_reconstruction':'scalar source + intervention split, no model implementation imported',
            'limitations':'Does not independently retrain or verify each per-arm prediction; local cross-platform full regression unverified.'}

if __name__=='__main__':
    result=audit(sys.argv[1] if len(sys.argv)>1 else 'scored.json')
    Path('audit_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='scenario_totals'},sort_keys=True,indent=2))
