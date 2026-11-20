#!/usr/bin/env python3
"""ENERGY-27: actively identify unknown causal rule with action-conditioned noise.

Synthetic source exposes public 5-bit interventions and observed action outcomes;
true hidden law is accessed only by the source oracle and the held evaluator.
Logically identical Bayesian and normalized Boltzmann energy controls (no gain claim).
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, math, time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
RULES=[(comb,sign) for comb in itertools.combinations(range(5),3) for sign in (0,1)]
ACTIONS=list(itertools.product((0,1),repeat=5))
assert len(RULES)==20 and len(ACTIONS)==32
RULE_PRED=np.asarray([[sum(a[k] for k in comb)%2^sign for a in ACTIONS] for comb,sign in RULES], dtype=np.int8)
PHI=np.asarray([[1,*[2*v-1 for v in a],*[math.prod((2*a[t]-1 for t in comb)) for comb in itertools.combinations(range(5),3)]] for a in ACTIONS],dtype=float)
assert PHI.shape==(32,16)

def digest(*parts):
    return hashlib.sha256('/'.join(map(str,parts)).encode('ascii')).digest()

def permutations(seed):
    return sorted(range(32),key=lambda x:digest('energy27/holdout-v1',seed,x))

def noise_rate(a,regime):
    if regime=='homogeneous':return 0.1
    if regime=='heterogeneous':return 0.02 if ACTIONS[a][0]==0 else 0.35
    raise ValueError(regime)

def source_observe(seed,rule,regime,step,action):
    # Private source randomness: same U per step across arms, public flip rate set by action.
    d=digest('energy27/noise-v1',seed,rule,regime,step)
    u=int.from_bytes(d[:8],'big')/2**64
    return int(RULE_PRED[rule,action]) ^ int(u<noise_rate(action,regime))

def softmax(logw):
    b=np.exp(logw-max(logw));return b/b.sum()

def entropy(p):
    p=min(1.0-1e-15,max(1e-15,float(p)))
    return -p*math.log2(p)-(1-p)*math.log2(1-p)

# Regime is explicitly supplied to action selector; no hidden source law.
def select(posterior,remaining,regime,arm,seed,step):
    if arm=='uniform_random':
        u=int.from_bytes(digest('energy27/random-v2',seed,regime,step)[:8],'big')
        return remaining[u%len(remaining)]
    rules=RULE_PRED[:,remaining]
    e=np.array([noise_rate(a,regime) for a in remaining],dtype=float)
    q=posterior@rules
    p=e+(1-2*e)*q
    v=(1-2*e)**2*q*(1-q)
    if arm=='variance':score=v
    elif arm=='information_gain':score=np.array([entropy(x)-entropy(y) for x,y in zip(p,e)])
    else:raise ValueError(arm)
    # Resolve floating ties to same action according to native method's tie convention.
    highest=max(score)
    tied=np.where(score>=highest-1e-12)[0]
    if len(tied)>1:
        u=np.abs(p[tied]-0.5)
        tied=tied[np.where(u<=min(u)+1e-12)[0]]
    return int(remaining[int(tied[0])])

def choose_posterior(logw,readout_actions):
    w=softmax(logw)
    q=w@RULE_PRED[:,readout_actions]
    return w,q

def cubic_fit(xs,ys,held):
    if not xs:
        return np.full(len(held),.5)
    x=PHI[xs];y=np.array(ys,dtype=float)*2-1
    # Same cubic features as ENERGY-25/26; conventional fitted ridge, not a causal oracle.
    beta=np.linalg.solve(x.T@x+.25*np.eye(PHI.shape[1]), x.T@y)
    return np.clip((PHI[held]@beta+1)/2,0,1)

def world(seed,rule,regime,arm,probes):
    held=permutations(seed)[:8]
    remaining=sorted(set(range(32))-set(held))
    seen=[];obs=[];logs=[];logw=np.zeros(20,dtype=float)
    start=time.perf_counter()
    for step in range(probes):
        w=softmax(logw)
        action=select(w,remaining,regime,arm,seed,step)
        assert action not in seen and action not in held
        y=source_observe(seed,rule,regime,step,action)
        e=noise_rate(action,regime)
        pred=RULE_PRED[:,action]
        likelihood=np.where(pred==y,1-e,e)
        logw+=np.log(likelihood)
        seen.append(action);obs.append(y)
        logs.append({'step':step,'action':action,'observed_y':y,'noise_rate':e})
        remaining.remove(action)
    post,q=choose_posterior(logw,held)
    true=RULE_PRED[rule,held].astype(int)
    best=float(np.max(post));hard=int(np.flatnonzero(post>=best-1e-12)[0]);map_pred=RULE_PRED[hard,held]
    ridge=cubic_fit(seen,obs,held)
    elapsed=time.perf_counter()-start
    acc=int(np.sum((q>0.5+1e-12).astype(int)==true))
    map_acc=int(np.sum(map_pred==true))
    ridge_acc=int(np.sum((ridge>0.5+1e-12).astype(int)==true))
    return {'seed':seed,'hidden_rule':rule,'regime':regime,'arm':arm,'held_actions':held,
            'observations':logs,'held_truth':true.tolist(),
            'held_soft_prob':np.round(q,13).tolist(),'held_ridge_prob':np.round(ridge,13).tolist(),
            'posterior':np.round(post,13).tolist(), 'identified_rule':hard,
            'correct':acc,'map_correct':map_acc,'ridge_correct':ridge_acc,
            'true_rule_identified':int(hard==rule),'brier':float(np.mean((q-true)**2)),
            'elapsed_seconds':elapsed}

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--out',type=Path,default=HERE/'scored.json');args=p.parse_args()
    protocol=json.loads((HERE/'protocol.json').read_text())
    if not args.smoke:
        freeze=json.loads((HERE/'freeze.json').read_text())
        assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==freeze['source_sha256'], 'SOURCE_DRIFT'
        assert hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest()==freeze['protocol_sha256'], 'PROTOCOL_DRIFT'
    seeds=protocol['primary_seeds'] if not args.smoke else [protocol['smoke_seed']]
    n=protocol['causal_rules'] if not args.smoke else 3
    cases=[];started=time.perf_counter()
    for seed in seeds:
        for rule in range(n):
            for regime in protocol['regimes']:
                for arm in protocol['arms']:
                    cases.append(world(seed,rule,regime,arm,protocol['training_budget']))
    totals={}
    for regime in protocol['regimes']:
        rows=[x for x in cases if x['regime']==regime]
        totals[regime]={a:{'held_correct':sum(x['correct'] for x in rows if x['arm']==a),
                           'held_total':len([x for x in rows if x['arm']==a])*8,
                           'map_correct':sum(x['map_correct'] for x in rows if x['arm']==a),
                           'ridge_correct':sum(x['ridge_correct'] for x in rows if x['arm']==a),
                           'true_rule_identified':sum(x['true_rule_identified'] for x in rows if x['arm']==a),
                           'wall_seconds':sum(x['elapsed_seconds'] for x in rows if x['arm']==a),
                           'mean_brier':sum(x['brier'] for x in rows if x['arm']==a)/len([x for x in rows if x['arm']==a])}
                       for a in protocol['arms']}
    homogeneous=[(x,y) for x,y in zip([v for v in cases if v['regime']=='homogeneous' and v['arm']=='variance'],[v for v in cases if v['regime']=='homogeneous' and v['arm']=='information_gain'])]
    homo_action_ties=sum([q['action'] for q in x['observations']]==[q['action'] for q in y['observations']] for x,y in homogeneous)
    het=[(x,y) for x,y in zip([v for v in cases if v['regime']=='heterogeneous' and v['arm']=='variance'],[v for v in cases if v['regime']=='heterogeneous' and v['arm']=='information_gain'])]
    differences=sum([z['action'] for z in x['observations']] != [z['action'] for z in y['observations']] for x,y in het)
    per_seed={seed:{'delta':sum(x['correct']-y['correct'] for x,y in het if x['seed']==seed),
                    'different_action_cases':sum([a['action'] for a in x['observations']] != [a['action'] for a in y['observations']] for x,y in het if x['seed']==seed)} for seed in seeds}
    gain=totals['heterogeneous']['information_gain']['held_correct']-totals['heterogeneous']['variance']['held_correct']
    gate=(gain>=29 and sum(v['delta']>0 for v in per_seed.values())>=4 and
          all(v['delta']>=-8 for v in per_seed.values()) and
          homo_action_ties==len(homogeneous))
    result={'schema':'energy27.scored.v1','classification':'DEVELOPMENT_GO' if gate else 'DEVELOPMENT_NO_GO',
            'scientific_pass':False,'native_checkpoint_executed':False,'deployment':'NONE',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'primary':not args.smoke,
            'seeds':seeds,'rules_per_seed':n,'cases':cases,'totals':totals,
            'homogeneous_variance_and_eig_action_sequence_matches':homo_action_ties,
            'homogeneous_worlds':len(homogeneous),'heterogeneous_action_sequence_disagreements':differences,
            'heterogeneous_worlds':len(het),'per_seed_heterogeneous':per_seed,
            'heterogeneous_gain':gain,'frozen_gate_pass':bool(gate),'whole_scoring_wall_seconds':time.perf_counter()-started}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','totals')},indent=2))
    print('totals',json.dumps(totals,indent=2))

if __name__=='__main__':main()
