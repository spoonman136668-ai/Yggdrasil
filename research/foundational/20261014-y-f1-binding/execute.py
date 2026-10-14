"""Y-F1: permutation-invariant relational binding diagnostic, DEVELOPMENT ONLY.

Tests whether learning structural transition likelihoods helps when entities
are renamed. Exact identifier equality and four-hop traversal are CODED, not
learned. Each physical state stores 12 packed endpoint pairs and 132 float32
off-diagonal link scores in a native 576-byte StatePool. No sealed cohort.
"""
from __future__ import annotations
import importlib.util, json, time
from pathlib import Path
import torch
from torch import nn
from yggdrasil.pool import StatePool

torch.set_num_threads(1)
HERE=Path(__file__).resolve().parent
p=HERE.parents[1]/"contrib"/"chatgpt"/"20261014-y-nci11-latent"/"execute.py"
spec=importlib.util.spec_from_file_location("y11_origin",p)
assert spec and spec.loader
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
TRAIN=tuple(range(38000,38024))
VALID=tuple(range(38112,38124))
N=12
MASK=~torch.eye(N,dtype=torch.bool)
FORMS=("exact_binding","identity_similarity","hybrid")
def relabel(v,seed,variant):
    # Distinct injective affine permutation of the same public entities.
    return (int(v)*[61,73,89][variant]+seed*[17,19,23][variant]+101)%60000
def fixture(seed,family,ca,cb,variant):
    edges,queries,_,_=old.fixture(seed,family,ca,cb)
    e=[(relabel(a,seed,variant),relabel(b,seed,variant)) for a,b in edges]
    q=[(relabel(a,seed,variant),relabel(b,seed,variant)) for a,b in queries]
    assert len(e)==12 and len(set(e))==12
    def path(start,end):
        reached={start}
        for _ in range(4):
            reached={b for a,b in e if a in reached}
        return end in reached
    return e,q,[path(*pair) for pair in q]
def dataset(seeds,families,variant):
    facts,qs,labels=[],[],[]
    for seed in seeds:
        for family in families:
            for ca in (False,True):
                for cb in (False,True):
                    e,q,y=fixture(seed,family,ca,cb,variant)
                    facts.append(e);qs.append(q);labels.append(y)
    return (torch.tensor(facts,dtype=torch.int32),
      torch.tensor(qs,dtype=torch.int32),
      torch.tensor(labels,dtype=torch.float32))
def signals(facts):
    src=facts[:,:,0];dst=facts[:,:,1]
    eq=(dst[:,:,None]==src[:,None,:]).float()
    left=old.feature(dst.long()) # B x 12 x 12
    right=old.feature(src.long())
    similarity=torch.einsum("bid,bjd->bij",left,right)
    return eq,similarity
class Gate(nn.Module):
    def __init__(self,form):
        super().__init__()
        assert form in FORMS
        self.form=form
        self.weights=nn.Parameter(torch.tensor([-.2,0.,-1.]))
    def make_state(self,facts):
        eq,sim=signals(facts)
        signal=sim if self.form=="identity_similarity" else eq
        secondary=sim if self.form=="hybrid" else torch.zeros_like(signal)
        p=torch.sigmoid(self.weights[0]*signal+self.weights[1]*secondary+self.weights[2])
        p=p*(~torch.eye(12,dtype=torch.bool)).to(p)
        # Pack source & destination as two uint16 in one float32 slot.
        src=facts[:,:,0];dst=facts[:,:,1]
        assert int(facts.min())>=0 and int(facts.max())<65536
        packed=((src<<16)|dst).to(torch.int32).view(torch.float32)
        state=torch.cat((packed,p[:,MASK]),dim=-1)
        assert state.shape[-1]==144 and state.element_size()==4
        return state
def answer(state,questions):
    packed=state[:,:12].contiguous().view(torch.int32).long()
    src=(packed>>16)&65535;dst=packed&65535
    scores=torch.zeros((state.shape[0],N,N),dtype=torch.float32)
    scores[:,MASK]=state[:,12:]
    # Four-edge query composition. Node equality and traversal are CODED.
    outputs=[]
    for j in range(2):
        a,b=questions[:,j,0],questions[:,j,1]
        dp=(src==a[:,None]).float()
        for _ in range(3):
            dp=1-torch.prod(1-dp.unsqueeze(-1)*scores,dim=1)
        hits=(dst==b[:,None]).float()
        pred=1-torch.prod(1-dp*hits,dim=1)
        outputs.append(pred)
    return torch.stack(outputs,dim=1)
def fixed_exact(facts,questions):
    # Same packed 576-byte schema, coded equality instead of trained gate.
    eq=(facts[:,:,1,None]==facts[:,None,:,0]).float()
    p=eq*.999+(1-eq)*.001
    p=p*(~torch.eye(12,dtype=torch.bool)).float()
    packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
    state=torch.cat((packed,p[:,MASK]),dim=-1)
    return answer(state,questions)
def qualify():
    train=dataset(TRAIN,(0,1,2),0)
    valid=dataset(VALID,(4,5,6,7),1)
    cases=[]
    saved={}
    for i,form in enumerate(FORMS):
        torch.manual_seed(600+i)
        m=Gate(form)
        with torch.no_grad():
            init=answer(m.make_state(valid[0]),valid[1])
            init_acc=float(((init>=.5)==valid[2].bool()).float().mean())
        opt=torch.optim.Adam(m.parameters(),lr=.07)
        begin=time.perf_counter()
        for epoch in range(130):
            opt.zero_grad()
            scores=answer(m.make_state(train[0]),train[1]).clamp(.0001,.9999)
            loss=nn.functional.binary_cross_entropy(scores,train[2])
            loss.backward();opt.step()
        with torch.no_grad():
            state=m.make_state(valid[0])
            outcome=answer(state,valid[1])
            acc=float(((outcome>=.5)==valid[2].bool()).float().mean())
            no_mem=float((valid[2]==0).float().mean())
            checkpoint=StatePool(torch.zeros((1,16,3,3)),capacity=1)
            checkpoint.update(torch.tensor([0]),state[0].reshape(1,16,3,3).detach())
            restored=StatePool(torch.zeros((1,16,3,3)),capacity=1)
            restored.load_state_dict(checkpoint.state_dict())
            exact=bool(torch.equal(checkpoint.state_dict()["storage"],restored.state_dict()["storage"]))
            renaming=dataset(VALID,(4,5,6,7),2)
            # Compare SAME case questions and graph structure after renaming.
            renamed=answer(m.make_state(renaming[0]),renaming[1])
            invariance=float(((renamed>=.5)==(outcome>=.5)).float().mean())
            weights=[float(w) for w in m.weights]
        cases.append({"form":form,"trained_accuracy":acc,"initialized_accuracy":init_acc,
          "train_bce":float(loss),"train_steps":130,"model_parameter_count":3,
          "model_weight_bytes_float32":12,"resident_state_bytes":576,
          "checkpoint_pass":exact,"weights":weights,
          "renaming_prediction_agreement":invariance,
          "no_memory_class_prior":no_mem,"training_wall_ms":round((time.perf_counter()-begin)*1000)})
        saved[form]=acc
    with torch.no_grad():
        fixed=fixed_exact(valid[0],valid[1])
        fixed_acc=float(((fixed>=.5)==valid[2].bool()).float().mean())
    winner=max(cases,key=lambda x:x["trained_accuracy"])
    # Structural alignment may be an essential CODED scaffolding, not a
    # learned key-binding algorithm; do not misclassify this success as one.
    useful=(saved["exact_binding"]>=.70 and
      saved["exact_binding"]-saved["identity_similarity"]>=.10 and
      cases[0]["renaming_prediction_agreement"]>=.99)
    return {"schema":"yggdrasil.foundation.f1-permutation-binding-dev.v1",
      "status":"DEVELOPMENT_ONLY",
      "source_parent":"2e54fa1842df59e3fc8c8a540af5eec9e7525c5f",
      "train_bounds":[38000,38024],"validation_bounds":[38112,38124],
      "train_families":[0,1,2],"validation_families":[4,5,6,7],
      "train_graphs":len(train[0]),"validation_graphs":len(valid[0]),
      "answers_per_graph":2,"renaming_variant_count":3,
      "candidate_results":cases,"strong_fixed_exact_binding_accuracy":fixed_acc,
      "frozen_gate_margins":{"structural_vs_identity":.10,"min_accuracy":.70,"min_renaming_agreement":.99},
      "selected_candidate":winner["form"],"diagnostic_useful":useful,
      "verdict":"CODED_EQUALITY_SCAFFOLD_EXPLAINS_TRANSFER" if useful else
        "EQUALITY_SCAFFOLD_TRANSFER_NOT_CONFIRMED",
      "coded_node_equality":True,"coded_four_hop_traversal":True,
      "actual_learned_component":"Three scalar edge-transition weights only",
      "model_cannot_learn_variable_identity_matching":True,
      "physical_memory_bytes":576,"first_use_sealed":False,
      "sealed_cohort_reserved":False,"external_llm_calls":0,
      "accepted_ref_mutation":False,"full_nci01_acceptance":False}
if __name__=="__main__":print(json.dumps(qualify(),indent=2,sort_keys=True))
