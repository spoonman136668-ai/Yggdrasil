"""Y-NCI11-R3: development-only native task-trained recurrent state mechanisms.

No sealed cohorts are selected, registered or opened in this experiment.
The trained state uses 144 float32 values (=576 resident bytes), separate
trainable model parameters, and no inference-time future question access.
"""
from __future__ import annotations
import argparse, json, time, importlib.util
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/"20261014-y-nci11-latent"/"execute.py"
spec=importlib.util.spec_from_file_location("nci11_frozen",P)
assert spec and spec.loader
previous=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
D=12
TRAIN_SEEDS=tuple(range(37024,37048))
VALID_SEEDS=tuple(range(37104,37116))
FAMILIES_TRAIN=(0,1,2)
FAMILIES_VALID=(4,5,6,7)

def public_encoded(seed,family,ca,cb,shift):
    edges,questions,truth,full=previous.fixture(seed,family,ca,cb)
    # Renaming is public and consistent within each graph, but hidden
    # task truth is not supplied to the state-former.
    ids=sorted(set([k for edge in edges for k in edge]+[k for q in questions for k in q]))
    g=torch.Generator().manual_seed(9871+seed*17+family*131)
    order=torch.randperm(len(ids),generator=g).tolist()
    replacements={value:shift+11*i+3 for value,i in zip(ids,order)}
    edges=[[replacements[a],replacements[b]] for a,b in edges]
    questions=[[replacements[a],replacements[b]] for a,b in questions]
    return edges,questions,truth

def data(seeds,families,shift):
    observed,questions,labels=[],[],[]
    for seed in seeds:
        for family in families:
            for ca in (False,True):
                for cb in (False,True):
                    e,q,y=public_encoded(seed,family,ca,cb,shift)
                    observed.append(e)
                    questions.append(q)
                    labels.append(y)
    e=previous.feature(torch.tensor(observed,dtype=torch.long))
    q=previous.feature(torch.tensor(questions,dtype=torch.long))
    truth=torch.tensor(labels,dtype=torch.float32)
    return e,q,truth

class NativePredictiveState(nn.Module):
    def __init__(self,kind):
        super().__init__()
        assert kind in ("gru_recurrent","bilinear_gated")
        self.kind=kind
        if kind=="gru_recurrent":
            self.cell=nn.GRUCell(2*D,D*D)
        else:
            self.src=nn.Linear(D,D,bias=False)
            self.dst=nn.Linear(D,D,bias=False)
            self.writer=nn.Sequential(nn.Linear(D*2,24),nn.Tanh(),nn.Linear(24,1))
            self.retention=nn.Parameter(torch.tensor(2.0))
        self.qsource=nn.Linear(D,D,bias=False)
        self.qtarget=nn.Linear(D,D,bias=False)
        self.readout=nn.Sequential(nn.Linear(D*D+2*D,40),nn.Tanh(),nn.Linear(40,1))
    def memory(self,edges):
        batch=edges.shape[0]
        state=torch.zeros((batch,D*D),dtype=edges.dtype,device=edges.device)
        for step in range(edges.shape[1]):
            pair=edges[:,step].reshape(batch,2*D)
            if self.kind=="gru_recurrent":
                state=self.cell(pair,state)
            else:
                a=F.normalize(self.src(pair[:,:D]),dim=-1)
                b=F.normalize(self.dst(pair[:,D:]),dim=-1)
                write=(a.unsqueeze(-1)*b.unsqueeze(-2)).reshape(batch,D*D)
                gate=torch.sigmoid(self.writer(pair))
                state=torch.tanh(torch.sigmoid(self.retention)*state + gate*write)
        return state
    def score(self,state,queries):
        q0=F.normalize(self.qsource(queries[:,:,0]),dim=-1)
        q1=F.normalize(self.qtarget(queries[:,:,1]),dim=-1)
        state_per_query=state.unsqueeze(1).expand(-1,queries.shape[1],-1)
        inp=torch.cat((state_per_query,q0,q1),dim=-1)
        return self.readout(inp).squeeze(-1)
    def forward(self,edges,queries):
        return self.score(self.memory(edges),queries)

def accuracy(logits,truth):
    return float(((logits>=0)==(truth>=.5)).float().mean().item())
def fit_one(kind,train,valid,seed):
    torch.manual_seed(seed)
    model=NativePredictiveState(kind)
    with torch.no_grad():
        initial_accuracy=accuracy(model(valid[0],valid[1]),valid[2])
    initial={k:v.detach().clone() for k,v in model.state_dict().items()}
    opt=torch.optim.Adam(model.parameters(),lr=.007)
    start=time.perf_counter()
    epochs=75
    for step in range(epochs):
        model.train()
        opt.zero_grad()
        loss=F.binary_cross_entropy_with_logits(model(train[0],train[1]),train[2])
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(),3.)
        opt.step()
    model.eval()
    with torch.no_grad():
        resident=model.memory(valid[0])
        trained_accuracy=accuracy(model.score(resident,valid[1]),valid[2])
        no_memory=accuracy(model.score(torch.zeros_like(resident),valid[1]),valid[2])
        native=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
        native.update(torch.tensor([0]),resident[:1].reshape(1,16,3,3).detach())
        restored=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
        restored.load_state_dict(native.state_dict())
        checkpoint_pass=torch.equal(native.state_dict()["storage"],restored.state_dict()["storage"])
        delta=sum((v-initial[k]).square().sum().item() for k,v in model.state_dict().items())**.5
    return {"kind":kind,"training_examples":len(train[0]),
        "validation_examples":len(valid[0]),
        "trained_validation_accuracy":trained_accuracy,
        "same_architecture_initial_accuracy":initial_accuracy,
        "trained_zero_memory_accuracy":no_memory,
        "training_minus_initialized":trained_accuracy-initial_accuracy,
        "training_minus_zero_memory":trained_accuracy-no_memory,
        "training_steps":epochs,"train_bce":float(loss.item()),
        "trained_parameter_l2_delta":delta,
        "native_checkpoint_pass":bool(checkpoint_pass),
        "resident_state_bytes":resident[0].numel()*resident.element_size(),
        "model_parameter_count":sum(p.numel() for p in model.parameters()),
        "model_parameters_bytes_fp32":sum(p.numel()*p.element_size() for p in model.parameters()),
        "training_wall_ms":round((time.perf_counter()-start)*1000)}

def main():
    train=data(TRAIN_SEEDS,FAMILIES_TRAIN,100)
    valid=data(VALID_SEEDS,FAMILIES_VALID,1400)
    records=[
       fit_one("gru_recurrent",train,valid,20231),
       fit_one("bilinear_gated",train,valid,20232)
    ]
    best=max(records,key=lambda r:(r["training_minus_initialized"],
                                   r["training_minus_zero_memory"],
                                   r["trained_validation_accuracy"]))
    qualified=(
        best["trained_validation_accuracy"]>=.70 and
        best["training_minus_initialized"]>=.10 and
        best["training_minus_zero_memory"]>=.10 and
        best["resident_state_bytes"]==576 and
        best["native_checkpoint_pass"] and
        best["trained_parameter_l2_delta"]>.01)
    print(json.dumps({
       "schema":"yggdrasil.nci11r3.predictive-native-memory-development.v1",
       "stage":"DEVELOPMENT_ONLY",
       "frozen_source_parent":"931144b5b5a984ea4523bad036ce5b92210d7a21",
       "training_seed_bounds":[37024,37048],
       "validation_seed_bounds":[37104,37116],
       "training_families":list(FAMILIES_TRAIN),
       "validation_families":list(FAMILIES_VALID),
       "unseen_validation_entity_ids":True,
       "selected":best["kind"],"candidates":records,
       "native_memory_bytes":576,
       "programmed_public_symbol_features":True,
       "fixed_test_queries_not_provided_to_memory":True,
       "full_nci01_acceptance":False,
       "qualification":{"min_accuracy":.70,"min_trained_minus_initialized":.10,
         "min_trained_minus_zero_memory":.10},
       "development_qualified":bool(qualified),
       "verdict":"NCI11R3_DEVELOPMENT_TRANSFER_QUALIFIED" if qualified else
         "NCI11R3_DEVELOPMENT_NO_GENERALIZABLE_TRAINED_STATE",
       "first_use_sealed":False,"sealed_cohort_reserved":False,
       "external_llm_calls":0,"accepted_ref_mutation":False
    },indent=2,sort_keys=True))
if __name__=="__main__":main()
