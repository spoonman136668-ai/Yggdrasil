#!/usr/bin/env python3
"""Independent reconstructive audit of ENERGY-31. No import of experiment.py.

A separate pure-Python implementation reconstructs every causal law, source
noise draw, training/held partition, six fitted posteriors, and all prediction
probabilities at every checkpoint. No native or protected source accessed.
"""
import argparse
from collections import defaultdict
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'protocol.json').read_text())
RULES=[];IS_NOVEL=[]
for triple in combinations(range(6),3):
    rest=[i for i in range(6) if i not in triple]
    for parity_sign in range(2):
        old=[(sum((action>>v)&1 for v in triple)%2)^parity_sign for action in range(64)]
        RULES.append(old);IS_NOVEL.append(False)
        for pair in combinations(rest,2):
            RULES.append([o^int(((a>>pair[0])&1) and ((a>>pair[1])&1)) for a,o in enumerate(old)])
            IS_NOVEL.append(True)
assert len(RULES)==160 and len(set(map(tuple,RULES)))==160
OLD_IDS=[i for i,z in enumerate(IS_NOVEL) if not z]
NEW_IDS=[i for i,z in enumerate(IS_NOVEL) if z]
BASE=[7/(8*40) if not v else 1/(8*120) for v in IS_NOVEL]
ZERO=[1/40 if not v else 0 for v in IS_NOVEL]
ARMS=tuple(P['arms'])
CHECKS=(8,16,24)

def h(*args):
    b='/'.join(map(str,('energy31/v1',)+args)).encode('ascii')
    return int.from_bytes(hashlib.sha256(b).digest(),'big')

def source_laws(seed,world,scenario):
    i=h('old-law',seed,world)%40
    old=OLD_IDS[i]
    novel=NEW_IDS[h('novel-law',seed,world)%120]
    other=OLD_IDS[(i+1+h('second-law',seed,world)%39)%40]
    assert other!=old
    return {'familiar_return':[old,novel,old],
            'novel_persistent':[old,novel,novel],
            'stationary_null':[old,old,old],
            'known_rule_switch':[old,other,old]}[scenario]

def source_plan(seed,world,scenario):
    ordered=sorted(range(64),key=lambda a:h('held',seed,world,scenario,a))
    test=ordered[:12];allowed=ordered[12:]
    plans=[sorted(allowed,key=lambda a:h('train',seed,world,scenario,p,a))[:24] for p in range(3)]
    assert all(set(test).isdisjoint(p) for p in plans)
    return test,plans

def normalize(values):
    s=math.fsum(values)
    assert math.isfinite(s) and s>0
    return [w/s for w in values]

def emission(a,y):
    return [0.9 if v[a]==y else 0.1 for v in RULES]

def predict_prob(states,held):
    return [math.fsum(w*RULES[i][a] for i,w in enumerate(states)) for a in held]

def update(source_state,a,y,history,oracle_restart=False):
    factors=emission(a,y)
    update_by_product=lambda weights:normalize([w*f for w,f in zip(weights,factors)])
    source_state['static_bayes']=update_by_product(source_state['static_bayes'])
    # Independent from scorer's incremental window implementation:
    # recompute likelihood in log space from the last 24 public witnesses.
    retained=history[-24:]
    logits=[]
    for index,p in enumerate(BASE):
        z=math.log(p)
        for aa,yy in retained:
            z+=math.log(0.9 if RULES[index][aa]==yy else 0.1)
        logits.append(z)
    shift=max(logits)
    source_state['recent24_bayes']=normalize([math.exp(v-shift) for v in logits])
    source_state['fixed_hazard32']=update_by_product([(31/32)*w+(1/32)*base for w,base in zip(source_state['fixed_hazard32'],BASE)])
    existing=source_state['evidence_hazard']
    predicted=math.fsum(w*f for w,f in zip(existing,factors))
    hazard=1/8 if predicted<1/4 else 1/96
    source_state['evidence_hazard']=update_by_product([(1-hazard)*w+hazard*base for w,base in zip(existing,BASE)])
    if oracle_restart:source_state['oracle_boundary']=BASE[:]
    source_state['oracle_boundary']=update_by_product(source_state['oracle_boundary'])
    source_state['old_only']=update_by_product(source_state['old_only'])
    return int(hazard==1/8)

def verify_case(row):
    checks=0
    seed,world,scenario=(row['seed'],row['world'],row['scenario'])
    laws=source_laws(seed,world,scenario);assert laws==row['laws'];checks+=3
    held,plans=source_plan(seed,world,scenario)
    assert held==row['held'] and len(held)==12 and len(set(held))==12;checks+=3
    states={arm:BASE[:] for arm in ARMS}
    states['old_only']=ZERO[:]
    count_surprises=0
    current=0
    history=[]
    for p,law in enumerate(laws):
        for i,a in enumerate(plans[p]):
            record=row['events'][current]
            flip=int(h('noisy-label',seed,world,scenario,p,i,a)%10==0)
            actual=RULES[law][a]^flip
            assert record==[a,actual,p,i],(seed,world,scenario,current)
            checks+=4
            history.append((a,actual))
            count_surprises+=update(states,a,actual,history,oracle_restart=p>0 and i==0)
            current+=1
            if i+1 not in CHECKS:continue
            saved=row['scores'][p*3+CHECKS.index(i+1)]
            true=[RULES[law][t] for t in held]
            assert saved['phase']==p and saved['after']==i+1 and saved['truth']==true
            checks+=15
            for arm in ARMS:
                probs=predict_prob(states[arm],held)
                pred=[int(v>0.5+1e-12) for v in probs]
                correct=sum(int(x==y) for x,y in zip(pred,true))
                brier=math.fsum((v-t)**2 for v,t in zip(probs,true))
                novel=math.fsum(states[arm][i] for i in NEW_IDS)
                observed=saved['arms'][arm]
                assert observed['pred']==pred,(arm,seed,world,scenario,p,i)
                assert observed['correct']==correct
                assert abs(observed['brier_sum']-brier)<2e-9
                assert abs(observed['novel_mass']-novel)<3e-9
                for x,y in zip(probs,observed['prob']):
                    assert abs(x-y)<3e-9,(arm,seed,world,scenario,x,y)
                    checks+=1
                checks+=4
            for weights in states.values():
                assert abs(math.fsum(weights)-1)<1e-10
                assert all(-1e-12<=v<=1+1e-12 for v in weights)
                checks+=2
    assert count_surprises==row['high_surprise_count']
    assert len(row['events'])==72 and len(row['scores'])==9
    checks+=3
    return checks

def group_aggregate(rows):
    grouped={}
    for scenario in P['scenarios']:
        for phase in range(3):
            for after in CHECKS:
                entries=[s for r in rows if r['scenario']==scenario for s in r['scores'] if s['phase']==phase and s['after']==after]
                rec={'worlds':len(entries),'held_per_arm':len(entries)*12,'arms':{}}
                for arm in ARMS:
                    rec['arms'][arm]={
                      'correct':sum(s['arms'][arm]['correct'] for s in entries),
                      'brier_sum':round(sum(s['arms'][arm]['brier_sum'] for s in entries),9),
                      'novel_mass_mean':round(sum(s['arms'][arm]['novel_mass'] for s in entries)/len(entries),9)}
                grouped[f'{scenario}/{phase}/{after}']=rec
    return grouped

def audit(path):
    data=json.loads(path.read_text())
    rows=data['cases']
    if data['kind']=='primary':
        assert len(rows)==144
        assert {r['seed'] for r in rows}==set(P['source_seeds'])
        assert {r['scenario'] for r in rows}==set(P['scenarios'])
        assert len({(r['seed'],r['world'],r['scenario']) for r in rows})==len(rows)
    checks=0
    for row in rows:
        checks+=verify_case(row)
    groups=group_aggregate(rows)
    assert groups==data['groups'],'GROUP_AGGREGATION_DIFFERENCE'
    checks+=len(groups)*len(ARMS)*3
    # Recompute the pass/fail thresholds from the actual held receipts.
    def a(s,p,arm):
        z=groups[f'{s}/{p}/24']
        return z['arms'][arm]['correct']/z['held_per_arm']
    novel=sum(a(s,1,'evidence_hazard') for s in ('familiar_return','novel_persistent'))/2
    fixed=sum(a(s,1,'fixed_hazard32') for s in ('familiar_return','novel_persistent'))/2
    window=sum(a(s,1,'recent24_bayes') for s in ('familiar_return','novel_persistent'))/2
    returning=sum(a(s,2,'evidence_hazard') for s in ('familiar_return','known_rule_switch'))/2
    old_ref=sum(a(s,2,'fixed_hazard32') for s in ('familiar_return','known_rule_switch'))/2
    null=a('stationary_null',2,'evidence_hazard')
    null_old=a('stationary_null',2,'static_bayes')
    null_mass=groups['stationary_null/2/24']['arms']['evidence_hazard']['novel_mass_mean']
    per_seed={}
    for seed in sorted({r['seed'] for r in rows}):
        sampled=[r for r in rows if r['seed']==seed and r['scenario'] in ('familiar_return','known_rule_switch')]
        new=sum(s['arms']['evidence_hazard']['correct'] for r in sampled for s in r['scores'] if s['phase']==2 and s['after']==24)
        old=sum(s['arms']['fixed_hazard32']['correct'] for r in sampled for s in r['scores'] if s['phase']==2 and s['after']==24)
        per_seed[str(seed)]=new-old
    expected={
      'novel_shift_gain':novel>=fixed+0.02 and novel>=window-0.01,
      'returning_old_gain':returning>=.80 and returning>=old_ref+.02,
      'stationary_fidelity':null>=null_old-.01 and null_mass<=.25,
      'per_seed_robustness':sum(v>0 for v in per_seed.values())>=2}
    assert expected==data['gates'],'GATE_MISMATCH'
    assert data['classification']==('SMOKE_ONLY' if data['kind']=='smoke' else ('DEVELOPMENT_GO' if all(expected.values()) else 'DEVELOPMENT_NO_GO'))
    assert data['scientific_pass'] is False and data['native_checkpoint_executed'] is False and data['deployment']=='NONE'
    checks+=20
    return {'audit':'PASS','case_count':len(rows),'source_observations':72*len(rows),
            'held_prediction_checks':len(rows)*9*12*len(ARMS),
            'invariant_checks':checks,'gates':expected,'class':data['classification']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path,nargs='?',default=HERE/'scored.json')
    args=parser.parse_args();print(json.dumps(audit(args.source),sort_keys=True,indent=2))
