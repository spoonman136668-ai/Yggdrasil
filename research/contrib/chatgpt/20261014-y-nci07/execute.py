"""Y-NCI07: native Torch graph-local learned retention on bounded StatePool.

Uses a four-parameter learned edge preference based on the at-most-eight public
candidate relationships at each seven-edge overflow (including new input).
Development labels are future relevance, never supplied in sealed inference.
Compares exact same stream and learned native join to frozen Y-NCI06, FIFO, LRU.
"""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import torch
from torch import nn
P=Path(__file__).resolve().parent.parent/"20261014-y-nci06"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci06_frozen",P)
assert S and S.loader
previous=importlib.util.module_from_spec(S);S.loader.exec_module(previous)
nci02=previous.nci02
nci01=previous.nci01
torch.set_num_threads(1)
SEEDS=range(27680,27704)
def features(fact,considered):
    a,b=fact["edge"]
    degree=sum(1 for other in considered
        if other["edge"]!=fact["edge"] and
        (b==other["edge"][0] or a==other["edge"][1]))
    return [fact["exposure"]/4,fact["time"]/12,degree/3]
def train():
    torch.manual_seed(1707)
    x=[];y=[]
    for seed in range(27344,27504):
        for family in range(4):
            _,facts,chain=previous.fixture(seed,family)
            for t in range(7,12):
                visible=facts[t-7:t+1]
                for fact in visible:
                    x.append(features(fact,visible))
                    y.append([float(fact["edge"] in chain)])
    assert len(x)==160*4*5*8
    xx=torch.tensor(x,dtype=torch.float32)
    yy=torch.tensor(y,dtype=torch.float32)
    model=nn.Linear(3,1)
    opt=torch.optim.Adam(model.parameters(),lr=.06)
    for _ in range(180):
        opt.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(model(xx),yy)
        loss.backward()
        opt.step()
    right=total=0
    with torch.no_grad():
        for seed in range(27504,27536):
            for family in range(4):
                _,facts,chain=previous.fixture(seed,family)
                for t in range(7,12):
                    candidates=facts[t-7:t+1]
                    for fact in candidates:
                        v=torch.tensor(features(fact,candidates),dtype=torch.float32)
                        guess=bool(torch.sigmoid(model(v)).item()>=.5)
                        right+=int(guess==(fact["edge"] in chain));total+=1
    return model,len(x),right/total
def retain(stream,model):
    pool=nci01.new_native_pool()
    stored=[];score_muls=rejections=0
    for fact in stream:
        if len(stored)<7:
            stored.append(fact)
        else:
            options=stored+[fact]
            x=torch.tensor([features(f,options) for f in options],dtype=torch.float32)
            with torch.no_grad():
                probs=torch.sigmoid(model(x)).view(-1).tolist()
            score_muls+=len(options)*3
            # Index as final tie break: deterministic first least-valued loss.
            evict=min(range(len(options)),key=lambda i:(probs[i],i))
            if evict==7:rejections+=1
            else:stored=[v for i,v in enumerate(options) if i!=evict]
        state=torch.zeros_like(pool.state_dict()["storage"])
        for idx,f in enumerate(stored):
            row,col=divmod(idx,nci01.GRID)
            a,b=f["edge"]
            state[0,0,row,col]=float(a+1)
            state[0,1,row,col]=float(b+1)
            state[0,2,row,col]=1.
        pool.update(torch.tensor([0]),state)
    edges=nci02.memory_edges(pool)
    assert len(edges)==7 and pool.state_dict()["storage"].numel()*4==576
    return pool,edges,score_muls,rejections
def run(phase="development"):
    if phase not in ("development","sealed"):raise ValueError(phase)
    policy,ntrain,validation=train()
    result={"schema":"yggdrasil.nci07.graph-local-retention.v1",
      "phase":phase,"parent":"a0c890e74317870c7d310da533d989a532fc3089",
      "weights":[float(v) for v in policy.weight.detach().view(-1)],
      "bias":float(policy.bias.detach().item()),"development_examples":ntrain,
      "validation_accuracy":validation,"learned_retention_parameters":4,
      "prior_learned_retention_parameters":3,"capacity":7,"native_state_bytes":576,
      "sealed_seed_range":[27680,27704],"learned_graph_features":False,
      "learned_policy_choice":True,"learned_graph_search":False,
      "nci01_full_acceptance":False,
      "external_llm_calls":0,"accepted_ref_mutation":False,"verdict":"DEVELOPMENT_ONLY"}
    if phase=="development":return result
    prior_policy,_,_=previous.learner()
    join,bias,cut,_=nci02.join_training()
    admit,_,_=nci01.learned_admission()
    records=[]
    counts={}
    by_family={str(f):{"graph_four":0,"prior_four":0,"lru_four":0} for f in range(4)}
    operations={"graph":0,"prior":0,"fifo":0,"lru":0}
    admitted=missed=score_muls=rejections=0
    for seed in SEEDS:
        for family in range(4):
            nodes,raw,chain=previous.fixture(seed,family)
            stream=[]
            for fact in raw:
                a,b=fact["edge"]
                sentence=f"e{a} stores e{b}."
                with torch.no_grad():
                    accepted=bool(torch.sigmoid(admit(nci01.token_features(sentence))).item()>=.5)
                if accepted:stream.append(fact);admitted+=1
                else:missed+=1
            pool,graph,scored,reject=retain(stream,policy)
            score_muls+=scored;rejections+=reject
            old_edges={}
            for mode in ("learned","fifo","lru"):
                _,ed,_,_=previous.keep(stream,mode,prior_policy)
                old_edges[mode]=ed
            assert len(graph)==len(old_edges["learned"])==len(old_edges["fifo"])==len(old_edges["lru"])==7
            row={"seed":seed,"family":family,"graph_edges":len(graph),
                 "new_fact_rejections":reject}
            for mode,edges in (("graph",graph),("prior",old_edges["learned"]),
                               ("fifo",old_edges["fifo"]),("lru",old_edges["lru"])):
                ops={"join_candidate_evaluations":0}
                if mode in ("graph","prior"):
                    row[f"{mode}_two"]=nci02.reached(join,bias,cut,edges,nodes[0],nodes[2],2,ops)
                row[f"{mode}_four"]=nci02.reached(join,bias,cut,edges,nodes[0],nodes[4],4,ops)
                if mode=="graph":
                    snapshot=copy.deepcopy(pool.state_dict())
                    restored=nci01.new_native_pool()
                    restored.load_state_dict(snapshot)
                    row["graph_restored"]=nci02.reached(join,bias,cut,nci02.memory_edges(restored),
                         nodes[0],nodes[4],4,ops)
                operations[mode]+=ops["join_candidate_evaluations"]
            row["oracle_four"]=previous.exact_oracle(chain,nodes[0],nodes[4],4)
            for key in ("graph_two","graph_four","graph_restored","prior_two",
                        "prior_four","fifo_four","lru_four","oracle_four"):
                counts[key]=counts.get(key,0)+int(row[key])
            for mode in ("graph","prior","lru"):
                by_family[str(family)][f"{mode}_four"]+=int(row[f"{mode}_four"])
            records.append(row)
    assert len(records)==96
    accuracy={k:v/96 for k,v in counts.items()}
    for m in by_family.values():
        for k in m:m[k]/=24
    gain=accuracy.get("graph_four",0)-accuracy.get("prior_four",0)
    gain_lru=accuracy.get("graph_four",0)-accuracy.get("lru_four",0)
    safe=all(a["graph_four"]>=a["prior_four"]-.20 for a in by_family.values())
    label="NO_GRAPH_LOCAL_RETENTION_TRANSFER"
    if accuracy.get("graph_four",0)>=.60 and gain>=.15 and gain_lru>=.10 and safe:
        label="GRAPH_LOCAL_LEARNED_RETENTION_TRANSFER"
    elif gain>=.10:label="PARTIAL_GRAPH_LOCAL_RETENTION_GAIN"
    result.update({"records":records,"accuracy":accuracy,"by_family":by_family,
       "gain_vs_previous_learned":gain,"gain_vs_lru":gain_lru,
       "join_candidate_evaluations":operations,"score_feature_multiplies":score_muls,
       "new_fact_rejections":rejections,"checkpoint_restores":96,
       "native_admission_true_positive":admitted,
       "native_admission_false_negative":missed,"verdict":label})
    return result
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(run(parser.parse_args().phase),sort_keys=True,indent=2))
