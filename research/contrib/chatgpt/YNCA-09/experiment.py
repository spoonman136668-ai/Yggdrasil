"""YNCA-09: learned causal incidence atlas from interventions; external development.

Each world has four binary vertex intervention variables, four anonymous response
channels, unknown XOR edge endpoints and unknown edge offsets. We infer the
causal wiring from noisy intervention-consequence observations. Source-free.
"""
from __future__ import annotations
from itertools import combinations, permutations
import argparse
import hashlib
import json
import math
import random

VERTICES = tuple(range(4))
ACTIONS = tuple(range(16))
EDGES = tuple(combinations(VERTICES, 2))
TOPOLOGIES = tuple(combinations(EDGES, 4))
CYCLES = tuple(t for t in TOPOLOGIES if all(sum(v in e for e in t)==2 for v in VERTICES))
NONCYCLES = tuple(t for t in TOPOLOGIES if t not in CYCLES)
SAMPLES = 8
NOISE = .10
A_SEEDS=range(410001,410065)
B_SEEDS=range(420001,420129)
SHIFT_SEEDS=range(430001,430065)
OPPOSITE=(0,1)


def rng(*tags):
    h=hashlib.sha256(':'.join(map(str,tags)).encode()).digest()
    return random.Random(int.from_bytes(h[:16],'big'))


def xor_edge(action, edge):
    return ((action >> edge[0]) & 1) ^ ((action >> edge[1]) & 1)


def world(seed,split):
    r=rng('world',split,seed)
    topo=r.choice(NONCYCLES if split=='SHIFT' else CYCLES)
    pairs=list(topo)
    r.shuffle(pairs)
    offsets=tuple(r.randrange(2) for _ in range(4))
    observations=[]
    for j in range(SAMPLES):
        action=r.randrange(16)
        outcomes=tuple(xor_edge(action,e)^b^int(r.random()<NOISE)
                       for e,b in zip(pairs,offsets))
        observations.append((action,outcomes))
    return {'pairs':tuple(pairs),'offsets':offsets,'observations':tuple(observations)}


def tables(w):
    # Output truth tables of unseen interventions, never passed into policy.
    return tuple(tuple(xor_edge(a,e)^b for e,b in zip(w['pairs'],w['offsets']))
                 for a in ACTIONS)


def likelihoods(observations):
    # Per-channel likelihoods for all six pairs and both offsets.
    result=[]
    for c in range(4):
        channel={}
        for e in EDGES:
            for bit in OPPOSITE:
                err=sum((xor_edge(a,e)^bit)!=out[c] for a,out in observations)
                channel[(e,bit)]=(1-NOISE)**(SAMPLES-err)*NOISE**err
        result.append(channel)
    return result


def independent_map(likes):
    return tuple(max(like,key=lambda x:(like[x],-EDGES.index(x[0]),-x[1])) for like in likes)


def independent_bayes(likes):
    return tuple({k:v/sum(row.values()) for k,v in row.items()} for row in likes)


def cycle_map(likes):
    # Pass B: one correction to independently fitted edges: impose global
    # consistency with a connected four-edge cycle; jointly infer offsets.
    best_score=-1
    best=None
    for topo in CYCLES:
        for assignment in permutations(topo):
            picks=tuple(max(((e,bit) for bit in OPPOSITE),key=lambda key:likes[i][key])
                        for i,e in enumerate(assignment))
            score=math.prod(likes[i][pair] for i,pair in enumerate(picks))
            if score>best_score:
                best_score=score
                best=picks
    assert best is not None
    return best


def joint_bayes(likes,topologies):
    # Exact same-observations Bayesian posterior under specified uniform graph prior.
    # Enumerate every ordered graph and analytically marginalize each channel's
    # independent offset (avoids 2^4 explicit offset tuples).
    channel_marginal=[]
    channel_conditional=[]
    for c in range(4):
        m={e:(likes[c][(e,0)]+likes[c][(e,1)])*.5 for e in EDGES}
        channel_marginal.append(m)
        channel_conditional.append({e:likes[c][(e,1)]/(likes[c][(e,0)]+likes[c][(e,1)])
                                    for e in EDGES})
    weights=[]
    for topo in topologies:
        for assn in permutations(topo):
            p=math.prod(channel_marginal[c][e] for c,e in enumerate(assn))
            weights.append((p,assn))
    z=sum(w for w,_ in weights)
    assert z>0
    probs=[[0.0]*4 for _ in ACTIONS]
    for w,assn in weights:
        w/=z
        for c,e in enumerate(assn):
            p_offset=channel_conditional[c][e]
            for a in ACTIONS:
                parity=xor_edge(a,e)
                probs[a][c]+=w*(p_offset if parity==0 else 1-p_offset)
    return tuple(tuple(row) for row in probs)


def from_map(pair_offsets):
    return tuple(tuple(xor_edge(a,e)^b for e,b in pair_offsets) for a in ACTIONS)


def metric(pred,truth):
    n=16*4
    brier=sum((pred[a][c]-truth[a][c])**2 for a in ACTIONS for c in range(4))/n
    accuracy=sum((pred[a][c]>=.5)==truth[a][c] for a in ACTIONS for c in range(4))/n
    return brier,accuracy


def eval_split(split):
    seeds={'A':A_SEEDS,'B':B_SEEDS,'SHIFT':SHIFT_SEEDS}[split]
    methods=('INDEPENDENT_MAP','INDEPENDENT_BAYES','JOINT_BAYES_CYCLE','JOINT_BAYES_UNRESTRICTED')
    if split!='A':methods=('INDEPENDENT_MAP','ATLAS_CYCLE_MAP','INDEPENDENT_BAYES','JOINT_BAYES_CYCLE','JOINT_BAYES_UNRESTRICTED')
    rows={m:[] for m in methods}
    structural={m:[] for m in ('INDEPENDENT_MAP','ATLAS_CYCLE_MAP') if m in methods}
    for seed in seeds:
        w=world(seed,split)
        like=likelihoods(w['observations'])
        truth=tables(w)
        a=independent_map(like)
        ib=independent_bayes(like)
        predictions={
            'INDEPENDENT_MAP':from_map(a),
            'INDEPENDENT_BAYES':tuple(tuple(sum(v*int(xor_edge(action,e)^b) for (e,b),v in ib[c].items()) for c in range(4)) for action in ACTIONS),
            'JOINT_BAYES_CYCLE':joint_bayes(like,CYCLES),
            'JOINT_BAYES_UNRESTRICTED':joint_bayes(like,TOPOLOGIES),
        }
        fitted={'INDEPENDENT_MAP':a}
        if 'ATLAS_CYCLE_MAP' in methods:
            b=cycle_map(like)
            fitted['ATLAS_CYCLE_MAP']=b
            predictions['ATLAS_CYCLE_MAP']=from_map(b)
        for m in methods:rows[m].append(metric(predictions[m],truth))
        for m,fit in fitted.items():structural[m].append(sum((e,b)==(we,wb) for (e,b),we,wb in zip(fit,w['pairs'],w['offsets']))/4)
    result={'split':split,'worlds':len(seeds),'noise':NOISE,'samples':SAMPLES,
            'structural_bases':{'candidate_pairs':len(EDGES),'cycle_topologies':len(CYCLES),'all_topologies':len(TOPOLOGIES)},
            'metrics':{m:{'brier':round(sum(x[0] for x in rows[m])/len(seeds),8),
                          'accuracy':round(sum(x[1] for x in rows[m])/len(seeds),8),
                          **({'edge_mapping_accuracy':round(sum(structural[m])/len(seeds),8)} if m in structural else {})} for m in methods}}
    if 'ATLAS_CYCLE_MAP' in methods:
        target=result['metrics']['ATLAS_CYCLE_MAP'];baseline=result['metrics']['INDEPENDENT_MAP'];oracle=result['metrics']['JOINT_BAYES_CYCLE'];
        relative=(baseline['brier']-target['brier'])/baseline['brier']
        ratio=target['brier']/oracle['brier']
        result.update({'relative_brier_gain_vs_independent_MAP':round(relative,8),
                       'brier_ratio_vs_exact_cycle_Bayes':round(ratio,8),
                       'decision':'DEVELOPMENT_SIGNAL' if split=='B' and relative>=.15 and ratio<=1.10 and target['edge_mapping_accuracy']>=baseline['edge_mapping_accuracy'] else 'NO_GO'})
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--split',required=True,choices=['A','B','SHIFT'])
    args=p.parse_args()
    print(json.dumps({'schema':'ynca09.learned-incidence-atlas.dev.v1','results':eval_split(args.split),
                      'claims':{'native_integration':False,'scientific_pass':False,'deployed':False}},indent=2,sort_keys=True))


if __name__=='__main__':main()
