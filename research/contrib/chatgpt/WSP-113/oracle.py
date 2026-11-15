"""Evaluator-owned hidden graph generation and effect source.

Never imported by native.py, controls.py or fixture-only tests.
Every output is an actual downstream state transition following do(target,value).
"""
from __future__ import annotations
from hashlib import sha256

EDGES=((0,1),(0,2),(1,2),(0,3),(1,3),(2,3))

def _hash(*parts):
    return sha256("|".join(map(str,parts)).encode("ascii")).digest()

def graph_mask(split,world,seed="v1"):
    if split not in ("train","transfer") or type(world)!=int or not 0<=world<128:
        raise ValueError("unregistered hidden causal world")
    order=sorted(EDGES,key=lambda e:(_hash("WSP113","GRAPH",seed,split,world,*e),e))
    count=_hash("WSP113","COUNT",seed,split,world)[0]%(3 if split=="train" else 4)
    if split=="transfer":count+=3
    chosen=set(order[:count])
    return sum(int(edge in chosen)<<i for i,edge in enumerate(EDGES))

def effect_for_graph(state,action,mask):
    if not 0<=state<16 or not 0<=action<8 or not 0<=mask<64:
        raise ValueError("invalid test effect request")
    target=action//2
    forced=action%2
    bits=[0]*4
    for j in range(4):
        if j==target:bits[j]=forced
        else:
            value=(state>>j)&1
            for i in range(j):
                if (mask>>EDGES.index((i,j)))&1:
                    value ^= bits[i]
            bits[j]=value
    return sum(bit<<i for i,bit in enumerate(bits))

def training_observations(seed="v1"):
    return tuple(tuple((state,action,effect_for_graph(state,action,graph_mask("train",world,seed)))
                       for state in range(16) for action in range(8))
                 for world in range(128))

def transfer_effect(world,state,action,seed="v1"):
    return effect_for_graph(state,action,graph_mask("transfer",world,seed))
