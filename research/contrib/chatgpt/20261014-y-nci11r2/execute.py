"""NCI11-R2 development-only native gated memory falsification.

Two newly trained recurrent 12x12 float32 StatePool state-formers; no seeded
NCI11 original holdout is accessed here. Full-graph future-question labels
supervise training only. Test-time memory receives public edge sequence alone.
"""
from __future__ import annotations
import importlib.util, json, time
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
BASE=Path(__file__).resolve().parent.parent/"20261014-y-nci11-latent"/"execute.py"
S=importlib.util.spec_from_file_location("y_nci11_frozen",BASE)
assert S and S.loader
prior=importlib.util.module_from_spec(S); S.loader.exec_module(prior)
D=12
TRAIN=tuple(range(35104,35128))
VALID=tuple(range(35168,35180))
MODES=("recurrent_write_gate","predictive_forget_gate")

class LearnedRecurrentState(nn.Module):
    def __init__(self,mode):
        super().__init__()
        assert mode in MODES
        self.mode=mode
        self.source=nn.Linear(D,D,bias=False)
        self.target=nn.Linear(D,D,bias=False)
        self.query_source=nn.Linear(D,D,bias=False)
        self.query_target=nn.Linear(D,D,bias=False)
        self.write_gate=nn.Linear(4,1)
        self.keep_gate=nn.Linear(4,1)
        self.gain=nn.Parameter(torch.tensor(11.))
        self.bias=nn.Parameter(torch.tensor(0.))
        with torch.no_grad():
            for module in (self.source,self.target,self.query_source,self.query_target):
                module.weight.copy_(torch.eye(D)+.07*torch.randn(D,D))
            self.write_gate.weight.copy_(torch.tensor([[1.,1.,-.5,.0]]))
            self.write_gate.bias.fill_(0.)
            self.keep_gate.weight.copy_(torch.tensor([[-.3,0.,0.,1.]]))
            self.keep_gate.bias.fill_(2.)
    def memory(self,edges):
        # B x 12 observed facts x 2 public entity embeddings, nothing else.
        b,steps,_,_=edges.shape
        state=torch.zeros((b,D,D),device=edges.device,dtype=edges.dtype)
        for t in range(steps):
            a=F.normalize(self.source(edges[:,t,0,:]),dim=-1)
            z=F.normalize(self.target(edges[:,t,1,:]),dim=-1)
            dot=(a*z).sum(dim=-1,keepdim=True)
            features=torch.cat((dot, (a*a).mean(dim=-1,keepdim=True),
                (z*z).mean(dim=-1,keepdim=True),
                state.square().mean(dim=(-1,-2)).unsqueeze(-1)),dim=-1)
            add=torch.sigmoid(self.write_gate(features)).reshape(b,1,1)
            write=(a.unsqueeze(2)*z.unsqueeze(1))/4
            if self.mode=="recurrent_write_gate":
                state=torch.tanh(.91*state+add*write)
            else:
                retention=torch.sigmoid(self.keep_gate(features)).reshape(b,1,1)
                state=torch.tanh(retention*state+add*write)
        return state
    def logits(self,state,questions):
        a=F.normalize(self.query_source(questions[:,:,0,:]),dim=-1)
        dst=F.normalize(self.query_target(questions[:,:,1,:]),dim=-1)
        for _ in range(4):
            a=torch.einsum("bqi,bij->bqj",a,state)
        return self.gain*(a*dst).sum(dim=-1)+self.bias
    def forward(self,edges,questions):
        return self.logits(self.memory(edges),questions)

def accuracy(logits,truth):
    return float(((logits>=0)==truth.bool()).float().mean())

def benchmark():
    train=prior.dataset(TRAIN,(0,1))
    valid=prior.dataset(VALID,(2,3))
    source_budget_bytes=576
    cases=[]
    for i,mode in enumerate(MODES):
        torch.manual_seed(900+i)
        m=LearnedRecurrentState(mode)
        with torch.no_grad():
            initial=m(valid[0],valid[1])
            initial_acc=accuracy(initial,valid[2])
        start=time.perf_counter()
        opt=torch.optim.Adam(m.parameters(),lr=.018)
        for _ in range(100):
            opt.zero_grad()
            loss=F.binary_cross_entropy_with_logits(m(train[0],train[1]),train[2])
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(),max_norm=3)
            opt.step()
        with torch.no_grad():
            latent=m.memory(valid[0])
            after=m.logits(latent,valid[1])
            zero=m.logits(torch.zeros_like(latent),valid[1])
            # Also record a query-free readout, to detect fixed class priors.
            trained_acc=accuracy(after,valid[2])
            zero_acc=accuracy(zero,valid[2])
            native=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
            native.update(torch.tensor([0]),latent[:1].reshape(1,16,3,3).detach())
            regenerated=StatePool(torch.zeros((1,16,3,3),dtype=torch.float32),capacity=1)
            regenerated.load_state_dict(native.state_dict())
            assert torch.equal(native.state_dict()["storage"],regenerated.state_dict()["storage"])
            assert regenerated.state_dict()["storage"].numel()*4==576
        params=sum(p.numel() for p in m.parameters())
        cases.append({"architecture":mode,"validation_accuracy":trained_acc,
          "same_architecture_initial_accuracy":initial_acc,
          "trained_zero_memory_accuracy":zero_acc,
          "validation_memory_gain":trained_acc-zero_acc,
          "actual_training_steps":100,"gradient_clip":3,"parameter_count":params,
          "model_weight_bytes_fp32":params*4,"resident_state_bytes":source_budget_bytes,
          "training_wall_ms":int((time.perf_counter()-start)*1000),
          "training_loss":float(loss.item())})
    best=max(cases,key=lambda x:(x["validation_accuracy"]-
                x["same_architecture_initial_accuracy"],
                x["validation_accuracy"]-x["trained_zero_memory_accuracy"],
                x["validation_accuracy"]))
    qualified=(best["validation_accuracy"]>=.70
            and best["validation_accuracy"]-best["same_architecture_initial_accuracy"]>=.10
            and best["validation_memory_gain"]>=.10)
    return {"schema":"yggdrasil.nci11r2.gated-recurrent-dev.v1",
        "mode":"DEVELOPMENT_ONLY",
        "frozen_scientific_parent":"a3d6cc4ae68aee4621fc8f93f400277458b36e65",
        "train_seed_bounds":[35104,35128],"valid_seed_bounds":[35168,35180],
        "unreserved_future_sealed_cohort":None,
        "training_graphs":len(TRAIN)*2*4,
        "validation_graphs":len(VALID)*2*4,
        "training_objective":"native future-query BCE, public observations only during state formation",
        "candidate_results":cases,"selected_architecture":best["architecture"],
        "qualification_thresholds":{"min_accuracy":.70,
           "min_gain_above_identical_initial_state":.10,
           "min_gain_over_zero_memory":.10},
        "development_qualified":qualified,
        "verdict":"NCI11R2_DEV_NATIVE_LEARNING_QUALIFIED" if qualified else
            "NCI11R2_DEV_NO_RELIABLE_LEARNED_MEMORY_GAIN",
        "native_state_bytes":source_budget_bytes,
        "learned_state_formation":True,
        "programmed_outer_product_and_four_step_matrix_composition":True,
        "sealed_first_use_executed":False,
        "external_llm_calls":0,"accepted_ref_mutation":False,
        "full_nci01_acceptance":False}

if __name__=="__main__":
    print(json.dumps(benchmark(),sort_keys=True,indent=2))
