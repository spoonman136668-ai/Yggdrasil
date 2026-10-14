"""Y-NCI06: native Torch supervised retention + bounded StatePool + frozen learned join.

A four-parameter Torch logistic policy learns future query relevance from
development-only public exposure/insert-time observations. No future relevance
label or task query is supplied during original sealed inference. Seven active
StatePool edges and 576 bytes for learned, FIFO and LRU baseline arms.
"""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import torch
from torch import nn
P=Path(__file__).resolve().parent.parent/"20261014-y-nci05"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci05_pinned",P)
assert S and S.loader
native=importlib.util.module_from_spec(S);S.loader.exec_module(native)
nci02=native.nci02
nci01=native.nci01
torch.set_num_threads(1)
CAP=7
SEEDS=range(26432,26456)
def fixture(seed,family):
    offsets=((0,1,2,3),(0,2,4,6),(1,3,5,7),(2,4,7,9))
    step=(1,3,5,7)[family]
    nodes=[64+(seed*7+family*3+i*step)%16 for i in range(5)]
    chain=[(nodes[i],nodes[i+1]) for i in range(4)]
    target_count=noise_count=0
    facts=[]
    for t in range(12):
        target=t in offsets[family]
        if target:
            edge=chain[target_count];target_count+=1
        else:
            edge=(96+2*noise_count+(seed+family)%2,
                  120+2*noise_count+(seed+2*family)%2)
            noise_count+=1
        repetitions=1
        if family==0 and target:repetitions=4
        if family==1:repetitions=3 if target else 1+(seed+t)%2
        if family==2 and not target:repetitions=4
        if family==3:repetitions=1+(seed*3+t*5)%4
        facts.append({"edge":edge,"exposure":repetitions,"time":t})
    assert target_count==4 and noise_count==8
    return nodes,facts,chain
def features(fact):
    return [float(fact["exposure"])/4,float(fact["time"])/12]
def learner():
    torch.manual_seed(1606)
    model=nn.Linear(2,1)
    rows=[];labels=[]
    for seed in range(25952,26112):
        for family in range(4):
            _,facts,chain=fixture(seed,family)
            for fact in facts:
                rows.append(features(fact))
                labels.append([float(fact["edge"] in chain)])
    x=torch.tensor(rows,dtype=torch.float32)
    y=torch.tensor(labels,dtype=torch.float32)
    optimizer=torch.optim.Adam(model.parameters(),lr=.06)
    for _ in range(180):
        optimizer.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(model(x),y)
        loss.backward();optimizer.step()
    right=total=0
    with torch.no_grad():
        for seed in range(26112,26144):
            for family in range(4):
                _,facts,chain=fixture(seed,family)
                for fact in facts:
                    pred=float(torch.sigmoid(model(torch.tensor(features(fact)))).item())>=.5
                    right+=int(pred==(fact["edge"] in chain));total+=1
    return model,len(rows),right/total
def score(mode,item,model):
    if mode=="fifo":return float(item["time"])
    if mode=="lru":return float(item["last"])
    with torch.no_grad():
        return float(torch.sigmoid(model(torch.tensor(features(item)))).item())
def keep(facts,mode,model):
    pool=nci01.new_native_pool()
    occupied=[]
    clock=evictions=multiplications=0
    for fact in facts:
        clock+=1
        incoming=dict(fact);incoming["last"]=clock
        if len(occupied)==CAP:
            victim=min(range(CAP),key=lambda i:(score(mode,occupied[i],model),i))
            if mode=="learned":multiplications+=2*CAP
            occupied.pop(victim);evictions+=1
        occupied.append(incoming)
        if fact["time"]==6:
            for v in occupied:
                if v["exposure"]>=3:
                    clock+=1;v["last"]=clock
        state=torch.zeros_like(pool.state_dict()["storage"])
        for idx,item in enumerate(occupied):
            yy,xx=divmod(idx,nci01.GRID)
            source,target=item["edge"]
            state[0,0,yy,xx]=float(source+1)
            state[0,1,yy,xx]=float(target+1)
            state[0,2,yy,xx]=1.0
        pool.update(torch.tensor([0]),state)
    edges=nci02.memory_edges(pool)
    assert len(edges)==CAP and pool.state_dict()["storage"].numel()*4==576
    return pool,edges,evictions,multiplications
def exact_oracle(edges,source,target,hops):
    frontier={source}
    for _ in range(hops):
        frontier={b for a,b in edges if a in frontier}
    return target in frontier
def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    model,ntrain,val=learner()
    result={"schema":"yggdrasil.nci06.native-trained-retention.v1",
       "phase":phase,"parent":"adee6983ab3a2d091da50bdf4b02c68b96df6edf",
       "retention_weights":[float(x) for x in model.weight.detach().view(-1)],
       "retention_bias":float(model.bias.detach()),
       "development_examples":ntrain,"development_validation_accuracy":val,
       "sealed_seed_range":[26432,26456],"native_memory_bytes":576,
       "learned_retention_parameters":3,
       "learned_join_parameters":6,"lexical_admission_parameters":4,
       "memory_cap":CAP,"learned_relational_storage":False,
       "learned_graph_search":False,"nci01_full_acceptance":False,
       "external_llm_calls":0,"accepted_ref_mutation":False,
       "verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    weights,bias,cut,_=nci02.join_training()
    admit,_,_=nci01.learned_admission()
    records=[];tallies={};ops={"learned":0,"fifo":0,"lru":0}
    total_evictions=score_muls=missed=admitted=0
    by_family={str(i):{"learned_four":0,"fifo_four":0,"lru_four":0} for i in range(4)}
    for seed in SEEDS:
        for family in range(4):
            nodes,all_facts,chain=fixture(seed,family)
            stream=[]
            for fact in all_facts:
                a,b=fact["edge"]
                clause=f"e{a} stores e{b}."
                with torch.no_grad():
                    prob=float(torch.sigmoid(admit(nci01.token_features(clause))).item())
                if prob>=.5:admitted+=1;stream.append(fact)
                else:missed+=1
            arms={}
            row={"seed":seed,"family":family}
            for mode in ("learned","fifo","lru"):
                pool,edges,evict,mults=keep(stream,mode,model)
                total_evictions+=evict;score_muls+=mults
                work={"join_candidate_evaluations":0}
                row[f"{mode}_two"]=nci02.reached(weights,bias,cut,edges,nodes[0],nodes[2],2,work)
                row[f"{mode}_four"]=nci02.reached(weights,bias,cut,edges,nodes[0],nodes[4],4,work)
                if mode=="learned":
                    snapshot=copy.deepcopy(pool.state_dict())
                    restored=nci01.new_native_pool()
                    restored.load_state_dict(snapshot)
                    recovered=nci02.memory_edges(restored)
                    row["learned_restored"]=nci02.reached(
                        weights,bias,cut,recovered,nodes[0],nodes[4],4,work)
                row[f"{mode}_edges"]=len(edges)
                ops[mode]+=work["join_candidate_evaluations"]
            row["oracle_two"]=exact_oracle(chain,nodes[0],nodes[2],2)
            row["oracle_four"]=exact_oracle(chain,nodes[0],nodes[4],4)
            for key in ("learned_two","learned_four","learned_restored",
                        "fifo_two","fifo_four","lru_two","lru_four",
                        "oracle_two","oracle_four"):
                tallies[key]=tallies.get(key,0)+int(row[key])
            for mode in ("learned","fifo","lru"):
                by_family[str(family)][f"{mode}_four"]+=int(row[f"{mode}_four"])
            records.append(row)
    assert len(records)==96 and all(row[f"{mode}_edges"]==CAP
        for row in records for mode in ("learned","fifo","lru"))
    accuracy={key:v/96 for key,v in tallies.items()}
    for v in by_family.values():
        for key in v:v[key]/=24
    delta_fifo=accuracy["learned_four"]-accuracy["fifo_four"]
    delta_lru=accuracy["learned_four"]-accuracy["lru_four"]
    no_family_collapse=all(g["learned_four"]>=g["lru_four"]-.20 for g in by_family.values())
    label="NO_TRANSFERABLE_LEARNED_RETENTION_GAIN"
    if (accuracy["learned_four"]>=.60 and delta_fifo>=.15
        and delta_lru>=.10 and no_family_collapse):
        label="LEARNED_BOUNDED_RETENTION_TRANSFER"
    elif delta_fifo>=.10:label="PARTIAL_RETENTION_GAIN_WITH_GENERALIZATION_COST"
    result.update({"records":records,"accuracy":accuracy,"by_family":by_family,
        "gain_vs_fifo_four":delta_fifo,"gain_vs_lru_four":delta_lru,
        "join_candidate_evaluations":ops,"total_evictions_all_arms":total_evictions,
        "retention_score_multiplications":score_muls,
        "checkpoint_restores":96,"native_admission_true_positive":admitted,
        "native_admission_false_negative":missed,"verdict":label})
    return result
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(parser.parse_args().phase),sort_keys=True,indent=2))
