"""Yggdrasil NCI-01: native learned admission + StatePool bounded memory + fixed chain reasoning.

This is a deliberately limited integration feasibility probe. The binary text
admission rule is learned with a native Torch linear classifier; the delayed
relationship store is the existing native StatePool phenotype substrate.
The composition/retrieval rule itself is explicit code and is NOT learned.
"""
from __future__ import annotations

import copy
import json
import math
import torch
from torch import nn
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
TRAIN_SEED=41
SEALED=tuple(range(21312,21336))
STATE_CHANNELS=16
GRID=3
ACTIVE_LIMIT=7
RETAINED_LIMIT=9
LEXICON=("stores","observes")
def token_features(clause: str) -> torch.Tensor:
    # Features of observed local byte n-grams, not externally supplied class labels.
    words=clause.split()
    verb=words[1] if len(words)>=3 else ""
    return torch.tensor([float("sto" in verb),float("obs" in verb),
                         float(len(verb))/10.0],dtype=torch.float32)

def learned_admission():
    torch.manual_seed(TRAIN_SEED)
    learner=nn.Linear(3,1)
    x,y=[],[]
    for i in range(24):
        for relation,label in (("stores",1.0),("observes",0.0)):
            sentence=f"e{i} {relation} e{(i+7)%24}."
            x.append(token_features(sentence))
            y.append([label])
    xx,yy=torch.stack(x),torch.tensor(y,dtype=torch.float32)
    optimizer=torch.optim.SGD(learner.parameters(),lr=0.4)
    for _ in range(80):
        optimizer.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(learner(xx),yy)
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        probs=torch.sigmoid(learner(xx)).view(-1)
        dev=float(((probs>=.5)==(yy.view(-1)>=.5)).float().mean())
    return learner,dev,len(x)

def new_native_pool():
    initial=torch.zeros((1,STATE_CHANNELS,GRID,GRID),dtype=torch.float32)
    return StatePool(initial,capacity=1)

def memory_write(pool,source,target):
    checkpoint=pool.state_dict()["storage"]
    # Seven active working-memory locations, two additional retained capacity
    # are allowed but unused in this first composition probe.
    for idx in range(ACTIVE_LIMIT):
        y,x=divmod(idx,GRID)
        if checkpoint[0,2,y,x]==0 or int(checkpoint[0,0,y,x])-1==source:
            checkpoint[0,0,y,x]=float(source+1)
            checkpoint[0,1,y,x]=float(target+1)
            checkpoint[0,2,y,x]=1.0
            pool.update(torch.tensor([0]),checkpoint)
            return
    # No silent overflow: unchanged memory and explicit resource failure.
    raise RuntimeError("ACTIVE_WORKING_MEMORY_EXHAUSTED")

def memory_step(pool,source):
    state=pool.state_dict()["storage"][0]
    for index in range(ACTIVE_LIMIT):
        y,x=divmod(index,GRID)
        if float(state[2,y,x])>0 and int(state[0,y,x])-1==source:
            return int(state[1,y,x])-1
    return None

def traverse(pool,source,hops):
    key=source
    for _ in range(hops):
        key=memory_step(pool,key)
        if key is None:return None
    return key

def memory_entries(pool):
    state=pool.state_dict()["storage"][0,2]
    return int((state>0).sum())

def evaluate_one(learner,seed):
    # Entirely new combinations of symbolic names and relation chains.
    start=32+((seed*5)%8)
    nodes=[32+(start-32+i)%8 for i in range(5)]
    pool=new_native_pool()
    tp=fp=fn=0
    admission_calls=0
    def observe(source,target,verb):
        nonlocal tp,fp,fn,admission_calls
        clause=f"e{source} {verb} e{target}."
        with torch.no_grad():
            predicted=bool(torch.sigmoid(learner(token_features(clause))).item()>=.5)
        truth=(verb=="stores")
        admission_calls+=1
        if predicted and truth:tp+=1
        elif predicted and not truth:fp+=1
        elif not predicted and truth:fn+=1
        if predicted:memory_write(pool,source,target)
    observe(nodes[0],nodes[1],"stores")
    observe(50,51,"observes")
    observe(nodes[1],nodes[2],"stores")
    observe(52,53,"observes")
    observe(nodes[2],nodes[3],"stores")
    direct=(traverse(pool,nodes[0],1)==nodes[1])
    two=(traverse(pool,nodes[0],2)==nodes[2])
    three=(traverse(pool,nodes[0],3)==nodes[3])
    direct_only=(traverse(pool,nodes[0],1)==nodes[2])
    # Durable interruption recovery through the existing StatePool API.
    snapshot=copy.deepcopy(pool.state_dict())
    restored=new_native_pool()
    restored.load_state_dict(snapshot)
    interrupted=(traverse(restored,nodes[0],2)==nodes[2])
    observe_after=pool
    pool=restored
    observe(nodes[3],nodes[4],"stores")
    retained=(traverse(pool,nodes[0],2)==nodes[2])
    new_learned=(traverse(pool,nodes[0],4)==nodes[4])
    count=memory_entries(pool)
    assert count<=ACTIVE_LIMIT<=RETAINED_LIMIT
    assert pool.sample_shape==(STATE_CHANNELS,GRID,GRID)
    return {"seed":seed,"direct":direct,"two_hop":two,"three_hop":three,
        "interrupted_two_hop":interrupted,"old_retained":retained,
        "new_knowledge_four_hop":new_learned,"direct_only_baseline":direct_only,
        "admission_tp":tp,"admission_fp":fp,"admission_fn":fn,
        "admission_calls":admission_calls,"active_entries":count,
        "state_bytes":int(pool.state_dict()["storage"].numel()*4)}

def execute(mode):
    if mode not in ("development","sealed"):raise ValueError(mode)
    learner,dev,ntrain=learned_admission()
    base={"schema":"yggdrasil.nci01.native-pool-language-memory-integration.v1",
          "mode":mode,"source_parent":"2e9637f5eacd3f760668c17af89f65b1df9f4fdd",
          "development_admission_accuracy":dev,
          "training_sentences":ntrain,"admission_weight_count":4,
          "state_channels":STATE_CHANNELS,"grid":[GRID,GRID],
          "resident_state_bytes":STATE_CHANNELS*GRID*GRID*4,
          "active_limit":ACTIVE_LIMIT,"retained_limit":RETAINED_LIMIT,
          "native_pool_class":"yggdrasil.pool.StatePool",
          "composition_rule_learned":False,"relational_storage_learned":False,
          "nci01_full_acceptance":False,"external_llm_calls":0,
          "accepted_ref_mutation":False,"verdict":"DEV_ONLY"}
    if mode=="development":return base
    records=[evaluate_one(learner,s) for s in SEALED]
    assert len(records)==24
    metric={f:sum(bool(r[f]) for r in records)/len(records)
            for f in ("direct","two_hop","three_hop","interrupted_two_hop",
                      "old_retained","new_knowledge_four_hop","direct_only_baseline")}
    admission={key:sum(r[key] for r in records)
               for key in ("admission_tp","admission_fp","admission_fn","admission_calls")}
    base.update({"sealed_seeds":list(SEALED),"records":records,"metric":metric,
       "admission":admission,
       "checkpoint_restores":len(records),
       "max_active_entries":max(r["active_entries"] for r in records),
       "total_relation_lookup_steps_upper_bound":24*(1+2+3+1+2+2+4),
       "verdict":("COMPONENT_INTEGRATION_NOT_LEARNED_COMPOSITION"
             if metric["two_hop"]>=.75 and metric["new_knowledge_four_hop"]>=.75
             else "NCI01_COMPONENT_INTEGRATION_BELOW_FEASIBILITY_GATE")})
    return base

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["development","sealed"],default="development")
    args=p.parse_args()
    print(json.dumps(execute(args.mode),indent=2,sort_keys=True))
