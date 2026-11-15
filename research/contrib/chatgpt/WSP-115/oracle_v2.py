"""Hidden synthetic WSP115 v2 intervention source. Evaluator ONLY.

This module must never be imported from native.py, independent controls, or
fabricated fixtures. All 16 new v2 64-node heldout worlds are first-use protected
until the entire transcript and all learner predictions have been hash-sealed.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"WSP-114"))
from native import grammar, effect_from_parameters

SEED="v2"

def _digest(*parts):
    return sha256("|".join(map(str,parts)).encode("ascii")).digest()

def hidden_coefficients(split,nodes,world,seed=SEED):
    if split not in ("train","transfer") or type(nodes) is not int or nodes not in (64,48,32):
        raise ValueError("invalid hidden world family")
    if type(world) is not int or not 0<=world<(32 if split=="train" else 16):
        raise ValueError("out of bounds world")
    coefficients=[]
    for node in range(nodes):
        terms=grammar(min(12,node))
        result=0
        for index,term in enumerate(terms):
            if split=="train" and len(term)==2:
                continue
            if _digest("WSP115","LAW",seed,split,nodes,world,node,index)[0]%4==0:
                result|=1<<index
        if split=="transfer":
            pairs=[i for i,term in enumerate(terms) if len(term)==2]
            if pairs and not any(result&(1<<i) for i in pairs):
                result|=1<<pairs[0]
        coefficients.append(result)
    return tuple(coefficients)

def hidden_effect(split,nodes,world,state,action,seed=SEED):
    weights=hidden_coefficients(split,nodes,world,seed)
    return effect_from_parameters(state,action,weights,nodes)

def _query(namespace,nodes,world,index,seed=SEED):
    d=_digest("WSP115",namespace,seed,nodes,world,index)
    return int.from_bytes(d[:8],"big")&((1<<nodes)-1),int.from_bytes(d[8:10],"big")%(2*nodes)

def common_training(nodes=64,seed=SEED):
    tables=[]
    for w in range(32):
        model=hidden_coefficients("train",nodes,w,seed)
        data=[]
        for i in range(256):
            s,a=_query("TRAIN",nodes,w,i,seed)
            data.append((s,a,effect_from_parameters(s,a,model,nodes)))
        tables.append(tuple(data))
    return tuple(tables)

def heldout_inputs(nodes,world,count=512,seed=SEED):
    return tuple(_query("HOLDOUT",nodes,world,i,seed) for i in range(count))

def transfer_effect(nodes,world,state,action,seed=SEED):
    return hidden_effect("transfer",nodes,world,state,action,seed)
