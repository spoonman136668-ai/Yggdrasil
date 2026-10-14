"""Y-NCI11: genuinely trainable bounded associative state and query readout.

The latent update is a 12x12 native StatePool tensor (576 bytes). Four distinct
12x12 learned projections encode public source/destination symbols and query
tokens. Supervised development future-question loss trains state formation
and readout; no future question is supplied during state formation at test.
Outer products and four matrix compositions are coded differentiable algebra,
not learned graph traversal or language understanding.
"""
from __future__ import annotations
import copy,importlib.util,json,math,time
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
D=12
TRAIN=tuple(range(32640,32664))
VALID=tuple(range(32704,32712))
SEALED=tuple(range(33840,33864))
MODELS=("additive_associative","leaky_associative")
def feature(ids):
    ids=ids.to(torch.float32).unsqueeze(-1)
    k=torch.arange(1,D+1,dtype=torch.float32)
    return F.normalize(torch.sin(ids*k*.119)+torch.cos(ids*k*k*.017),dim=-1)
def fixture(seed,family,cut_a,cut_b):
    a=[64+(seed*3+5*i)%16 for i in range(5)]
    b=[96+(seed*7+3*i)%16 for i in range(5)]
    x,y,z,w=[200+(seed%7)*4+i for i in range(4)]
    edges=[(nodes[i],nodes[i+1]) for nodes in (a,b) for i in range(4)]
    if cut_a:edges[2]=(a[2],300+seed%13)
    if cut_b:edges[6]=(b[2],320+seed%13)
    motifs=(
      [(a[1],x),(b[2],y),(z,a[2]),(w,b[1])],
      [(x,a[1]),(a[1],y),(z,b[2]),(b[2],w)],
      [(a[1],x),(a[2],y),(b[1],z),(b[2],w)],
      [(x,a[1]),(y,a[2]),(z,b[1]),(w,b[2])],
      [(a[1],x),(x,a[1]),(b[2],y),(y,b[2])],
      [(z,a[1]),(a[1],x),(w,b[2]),(b[2],y)],
      [(a[2],x),(a[2],y),(b[1],z),(b[1],w)],
      [(x,a[1]),(y,a[2]),(z,b[1]),(w,b[2])],
    )
    patterns=(
      (0,4,8,1,5,9,2,6,10,3,7,11),
      (8,0,9,4,1,10,5,2,11,6,3,7),
      (0,1,8,4,5,9,2,6,10,3,7,11),
      (8,4,0,9,5,1,10,6,2,11,7,3),
      (8,4,0,9,5,1,10,6,2,11,7,3),
      (0,4,8,1,5,9,2,6,10,3,7,11),
      (8,0,9,4,1,10,5,2,11,6,3,7),
      (0,1,8,4,5,9,2,6,10,3,7,11),
    )
    full=edges+motifs[family]
    assert len(full)==12 and len(set(full))==12
    observed=[full[i] for i in patterns[family]]
    queries=[(a[0],a[4]),(b[0],b[4])]
    labels=[not cut_a,not cut_b]
    return observed,queries,labels,full
def dataset(seeds,families):
    edges,queries,truth=[],[],[]
    for seed in seeds:
      for family in families:
       for ca in (False,True):
        for cb in (False,True):
         observed,q,labels,_=fixture(seed,family,ca,cb)
         edges.append(observed);queries.append(q);truth.append(labels)
    return feature(torch.tensor(edges)),feature(torch.tensor(queries)),torch.tensor(truth,dtype=torch.float32)

class AssociativeState(nn.Module):
    def __init__(self,mode):
        super().__init__()
        assert mode in MODELS
        self.mode=mode
        self.src=nn.Linear(D,D,bias=False)
        self.dst=nn.Linear(D,D,bias=False)
        self.qsrc=nn.Linear(D,D,bias=False)
        self.qdst=nn.Linear(D,D,bias=False)
        self.gain=nn.Parameter(torch.tensor(10.0))
        self.bias=nn.Parameter(torch.tensor(0.0))
        with torch.no_grad():
            for module in (self.src,self.dst,self.qsrc,self.qdst):
                module.weight.copy_(torch.eye(D)+.05*torch.randn(D,D))
    def memory(self,edges):
        a,b=edges[...,0,:],edges[...,1,:]
        src=F.normalize(self.src(a),dim=-1)
        dst=F.normalize(self.dst(b),dim=-1)
        products=src.unsqueeze(-1)*dst.unsqueeze(-2)/4
        if self.mode=="additive_associative":
            return torch.tanh(products.sum(dim=1))
        state=torch.zeros_like(products[:,0])
        for t in range(products.shape[1]):
            state=torch.tanh(.92*state+products[:,t])
        return state
    def readout(self,memory,query):
        a=F.normalize(self.qsrc(query[...,0,:]),dim=-1)
        b=F.normalize(self.qdst(query[...,1,:]),dim=-1)
        for _ in range(4):
            a=torch.einsum("bqi,bij->bqj",a,memory)
        return self.gain*(a*b).sum(dim=-1)+self.bias
    def forward(self,edges,queries):
        return self.readout(self.memory(edges),queries)

def fit():
    training=dataset(TRAIN,(0,1))
    validation=dataset(VALID,(2,3))
    candidates=[]
    for index,mode in enumerate(MODELS):
        torch.manual_seed(45+index)
        model=AssociativeState(mode)
        opt=torch.optim.Adam(model.parameters(),lr=.02)
        start=time.perf_counter()
        for _ in range(100):
            opt.zero_grad()
            logits=model(training[0],training[1])
            loss=F.binary_cross_entropy_with_logits(logits,training[2])
            loss.backward();opt.step()
        with torch.no_grad():
            a=model(validation[0],validation[1])
            val=float(((a>0)==validation[2]).float().mean())
            zero=torch.zeros((validation[0].shape[0],D,D))
            absent=float(((model.readout(zero,validation[1])>0)==validation[2]).float().mean())
        candidates.append((val,absent,mode,model,time.perf_counter()-start))
    winner=sorted(candidates,key=lambda z:(-z[0],z[4],z[2]))[0]
    return winner,candidates

def exact_reach(full,start,target,depth):
    nodes={start}
    for _ in range(depth):
        nodes={dst for src,dst in full if src in nodes}
    return target in nodes

def original(mode="development"):
    assert mode in ("development","sealed")
    (dev,zero,selected,model,elapsed),tested=fit()
    parameters=sum(x.numel() for x in model.parameters())
    result={
      "schema":"yggdrasil.nci11.native-learned-associative-state.v1",
      "mode":mode,
      "parent":"8498472bc050279fc0f203939ee45dcdaa58ddf3",
      "training_seeds":list(TRAIN),"validation_seeds":list(VALID),
      "sealed_heldout_seeds":list(SEALED),
      "training_families":[0,1],"validation_families":[2,3],
      "sealed_novel_families":[4,5,6,7],
      "selected_model":selected,"validation_accuracy":dev,
      "validation_zero_memory":zero,
      "training_candidates":[{"mode":m,"validation_accuracy":v,
        "zero_memory":z,"training_wall_ms":round(t*1000)}
         for v,z,m,_,t in tested],
      "trained_parameter_count":parameters,"trained_parameter_bytes":parameters*4,
      "native_state_bytes":D*D*4,"native_state_shape":[16,3,3],
      "state_encoding_learned":True,"query_projections_learned":True,
      "outer_product_update_programmed":True,
      "four_step_matrix_composition_programmed":True,
      "training_epochs_per_model":100,
      "training_graphs":len(TRAIN)*2*4,
      "validation_graphs":len(VALID)*2*4,
      "external_llm_calls":0,"accepted_ref_mutation":False,
      "nci01_full_acceptance":False,
      "verdict":"DEVELOPMENT_ONLY",
    }
    if mode=="development":return result
    selected_eval=dataset(SEALED,(4,5,6,7))
    with torch.no_grad():
        memories=model.memory(selected_eval[0])
        answers=model.readout(memories,selected_eval[1])
        zero_scores=model.readout(torch.zeros_like(memories),selected_eval[1])
    # Own native StatePool is used for persistence/checkpoint qualification.
    saved=0
    rows=[]
    native_start=time.perf_counter()
    for i,seed in enumerate(SEALED):
     for family in (4,5,6,7):
      for ca in (False,True):
       for cb in (False,True):
        ix=len(rows)
        observed,qs,labels,full=fixture(seed,family,ca,cb)
        oracle=[exact_reach(full,a,b,4) for a,b in qs]
        pool=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
        pool.update(torch.tensor([0]),memories[ix].reshape(1,16,3,3).detach())
        state=copy.deepcopy(pool.state_dict())
        recovered=StatePool(torch.zeros((1,16,3,3)),capacity=1)
        recovered.load_state_dict(state)
        assert torch.equal(recovered.state_dict()["storage"],pool.state_dict()["storage"])
        saved+=1
        row={"seed":seed,"family":family,"cut_a":ca,"cut_b":cb,
          "oracle":[bool(v) for v in oracle],"truth":[bool(v) for v in labels],
          "learned":[bool(v) for v in (answers[ix]>0).tolist()],
          "zero_memory":[bool(v) for v in (zero_scores[ix]>0).tolist()],
          "memory_bytes":pool.state_dict()["storage"].numel()*4}
        rows.append(row)
    assert len(rows)==len(SEALED)*4*4
    correct=sum(int(answer==label) for r in rows for answer,label in zip(r["learned"],r["truth"]))
    ablated=sum(int(answer==label) for r in rows for answer,label in zip(r["zero_memory"],r["truth"]))
    oracle_correct=sum(int(a==b) for r in rows for a,b in zip(r["oracle"],r["truth"]))
    grouped={str(f):sum(int(a==b) for r in rows if r["family"]==f for a,b in zip(r["learned"],r["truth"]))/(len(SEALED)*4*2)
             for f in (4,5,6,7)}
    pct=correct/(len(rows)*2)
    result.update({"original_records":rows,"sealed_question_count":len(rows)*2,
      "sealed_accuracy":pct,"zero_memory_accuracy":ablated/(len(rows)*2),
      "oracle_accuracy":oracle_correct/(len(rows)*2),
      "accuracy_by_structure":grouped,"checkpoint_restores":saved,
      "original_science_wall_ms":round((time.perf_counter()-native_start)*1000)})
    if oracle_correct!=len(rows)*2:
        result["verdict"]="NCI11_INVALID_ORACLE"
    elif pct>=.70 and pct-ablated/(len(rows)*2)>=.10 and all(v>=.60 for v in grouped.values()):
        result["verdict"]="NCI11_BOUNDED_LEARNED_LATENT_TRANSFER"
    else:result["verdict"]="NCI11_NO_ROBUST_LATENT_TRANSFER"
    return result

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--phase",choices=("development","sealed"),default="development")
    print(json.dumps(original(a.parse_args().phase),indent=2,sort_keys=True))
