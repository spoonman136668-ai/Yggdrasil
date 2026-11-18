"""YNCA07: source-free structural Popperian falsifier, development only.

This is a bounded compositional symbolic-program prototype. It does not modify
Yggdrasil model weights or run protected science. Each agent receives the same
passive observations, permitted actions, and genuine probe outcomes.
"""
import argparse
import hashlib
import json
import random
import statistics
from dataclasses import dataclass
from itertools import combinations, permutations

N_ACTIONS=16
N_PROBES=4
PASSIVE=(0,15)
PROBE_COST=.02
SEEDS={'A':(171001,171129),'B':(172001,172129),'FRESH':(181001,181257)}
TRAIN_SEEDS=range(160001,160065)


def rng(*parts):
    return random.Random(int.from_bytes(hashlib.sha256(':'.join(map(str,parts)).encode()).digest()[:8],'big'))


def truth(fn): return tuple(int(fn(tuple((a>>i)&1 for i in range(4)))) for a in range(N_ACTIONS))


@dataclass(frozen=True)
class Program:
    name:str
    family:str
    complexity:int
    table:tuple


def grammar():
    programs={}
    def add(name,family,cost,fn):
        t=truth(fn)
        if t not in programs or (cost,name)<(programs[t].complexity,programs[t].name):
            programs[t]=Program(name,family,cost,t)
    for i in range(4):
        add('x'+str(i),'atom',1,lambda x,i=i:x[i])
        add('~x'+str(i),'not',2,lambda x,i=i:1-x[i])
    for i,j in combinations(range(4),2):
        add(f'AND({i},{j})','and',3,lambda x,i=i,j=j:x[i]&x[j])
        add(f'OR({i},{j})','or',3,lambda x,i=i,j=j:x[i]|x[j])
        add(f'XOR({i},{j})','xor',3,lambda x,i=i,j=j:x[i]^x[j])
    for i,j,k in combinations(range(4),3):
        add(f'MAJ({i},{j},{k})','majority',6,lambda x,i=i,j=j,k=k:int(x[i]+x[j]+x[k]>=2))
        add(f'XOR3({i},{j},{k})','xor3',5,lambda x,i=i,j=j,k=k:x[i]^x[j]^x[k])
    for sel,left,right in permutations(range(4),3):
        add(f'MUX({sel},{left},{right})','mux',6,lambda x,s=sel,a=left,b=right:x[a] if x[s] else x[b])
    add('XOR4','xor4',7,lambda x:x[0]^x[1]^x[2]^x[3])
    return tuple(sorted(programs.values(),key=lambda p:(p.complexity,p.name)))

PROGRAMS=grammar()
BY_FAMILY={f:tuple(p for p in PROGRAMS if p.family==f) for f in ('mux','majority','xor3','xor4')}


def world(seed,split):
    # Held-in-development distribution: compositional 3- and 4-way functions.
    pool=[p for family in BY_FAMILY.values() for p in family]
    p=rng('program',split,seed).choice(pool)
    # Noiseless outcomes are diagnostic of structural synthesis, sensor noise separate.
    return p


def survivors(obs):
    return tuple(p for p in PROGRAMS if all(p.table[action]==result for action,result in obs))


def learned_prior():
    counts={p.table:0.25 for p in PROGRAMS}
    for seed in TRAIN_SEEDS:
        p=world(seed,'TRAIN')
        counts[p.table]+=1.0
    return counts

PRIOR=learned_prior()


def choice(candidates):
    return min(candidates,key=lambda p:(p.complexity,p.name))


def score_falsifier(candidates,chosen,action,weights,balanced=False):
    # Build counterexample worlds by searching compositional programs that agree
    # with *all observed* facts but contradict the Minimalist at the action.
    alts=[p for p in candidates if p.table[action]!=chosen.table[action]]
    if not alts:return (-1.,None)
    counter=min(alts,key=lambda p:(p.complexity,p.name))
    # World novelty / topological capacity not assumed; this is real program search.
    diversity=len(alts)/len(candidates)
    if balanced:
        # Pass B correction, fixed before independent B development cohort.
        # Prevent the Falsifier from chasing large but lopsided counterworlds.
        score=4*diversity*(1-diversity)+.03*(weights.get(counter.family,1)-1)
    else:
        score=diversity*weights.get(counter.family,1)
    return (score - .003*action.bit_count(),counter)


def select(policy,candidates,seen,seed,step,weights):
    available=[a for a in range(N_ACTIONS) if a not in seen]
    if not available:return None,None
    if policy=='fixed':return available[0],None
    if policy=='random':return rng('random',seed,step).choice(available),None
    if policy in ('EIG','EIG_TRAINED'):
        prior=({p.table:1.0 for p in candidates} if policy=='EIG' else PRIOR)
        denominator=sum(prior[p.table] for p in candidates)
        best=max(available,key=lambda a:(
            entropy(sum(prior[p.table]*p.table[a] for p in candidates)/denominator),-a))
        return best,None
    if policy in ('IPFC_A','IPFC_B'):
        minimalist=choice(candidates)
        ranked=[(*score_falsifier(candidates,minimalist,a,weights,policy=='IPFC_B'),a) for a in available]
        ranked.sort(key=lambda k:(k[0],-k[2]),reverse=True)
        if ranked[0][1] is None:return None,None
        return ranked[0][2],ranked[0][1]
    raise ValueError(policy)


def entropy(p):
    if p<=0 or p>=1:return 0
    import math
    return -(p*math.log2(p)+(1-p)*math.log2(1-p))


def episode(truth_program,policy,seed):
    seen={a:truth_program.table[a] for a in PASSIVE}
    weights={}
    traces=[]
    for step in range(N_PROBES):
        candidates=survivors(seen.items())
        assert candidates and truth_program in candidates
        action,alternate=select(policy,candidates,seen,seed,step,weights)
        if action is None:break
        proposed=choice(candidates)
        observed=truth_program.table[action]
        # Update both surviving program family and falsifier preferences after
        # *real* feedback only, never after synthetic dreamed outcomes.
        if policy in ('IPFC_A','IPFC_B') and alternate is not None:
            family=alternate.family
            if proposed.table[action] != observed:
                weights[family]=min(3.,weights.get(family,1.)+.25)
            else:
                weights[family]=max(.5,weights.get(family,1.)-.10)
        seen[action]=observed
        traces.append((action, alternate.name if alternate else None,observed))
    final=survivors(seen.items())
    final_program=choice(final)
    # Universal diagnostic score over all 16 inputs (not training feedback).
    accuracy=sum(a==b for a,b in zip(final_program.table,truth_program.table))/N_ACTIONS
    # Bayesian mean prediction using same exact program library, deterministic.
    brier=sum((sum(p.table[a] for p in final)/len(final)-truth_program.table[a])**2
              for a in range(N_ACTIONS))/N_ACTIONS
    return {'brier':brier,'accuracy':accuracy,'exact':int(final_program.table==truth_program.table),
            'survivors':len(final),'probes':len(traces),'cost':len(traces)*PROBE_COST,
            'trace':traces}


def evaluate(split):
    start,end=SEEDS[split]
    policies=('IPFC_A','EIG','EIG_TRAINED','fixed','random') if split=='A' else ('IPFC_A','IPFC_B','EIG','EIG_TRAINED','fixed','random')
    results={policy:[] for policy in policies}
    for seed in range(start,end):
        p=world(seed,split)
        for policy in results:
            results[policy].append(episode(p,policy,seed))
    metrics={k:{field:round(statistics.mean(x[field] for x in rows),8)
                for field in ('brier','accuracy','exact','survivors','probes','cost')}
             for k,rows in results.items()}
    candidate='IPFC_A' if split=='A' else 'IPFC_B'
    best_control=min(('EIG','EIG_TRAINED','fixed','random'),key=lambda name:metrics[name]['brier'])
    gain=metrics[best_control]['brier']-metrics[candidate]['brier']
    relative=gain/max(1e-9,metrics[best_control]['brier'])
    return {'split':split,'n':end-start,'grammar_size':len(PROGRAMS),
            'family_counts':{k:len(v) for k,v in BY_FAMILY.items()},
            'metrics':metrics,'best_control':best_control,
            'primary_brier_gain_vs_best_control':round(gain,8),
            'primary_relative_gain_vs_best_control':round(relative,8),
            'decision':('PROMISING' if relative>=.05 and metrics[candidate]['accuracy']>=metrics[best_control]['accuracy']-.02 and metrics[candidate]['probes']<=metrics[best_control]['probes'] else 'NO_CLEAR_SIGNAL')}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--split',choices=['A','B','FRESH'],required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.split),indent=2,sort_keys=True))

if __name__=='__main__':main()
