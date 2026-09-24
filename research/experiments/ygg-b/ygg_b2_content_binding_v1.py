#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

import torch
from torch import nn

PREREG="4713b8d26aa9328ee6a6cebaf0a9fa07169d4d49"
KEYS=8
VALUES=8
PAIRS=4
SEQ=9
HIDDEN=16
EMBED=8
TRAIN_N=8192
EVAL_N=4096
BATCH=256
EPOCHS=75
LR=0.005
SEEDS=(111,222,333,444,555)

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def make_data(seed,n,salt):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+salt)
    scores=torch.rand((n,KEYS),generator=g)
    keys=torch.argsort(scores,dim=1)[:,:PAIRS]
    vals=torch.randint(0,VALUES,(n,PAIRS),generator=g,dtype=torch.long)
    qi=torch.randint(0,PAIRS,(n,),generator=g,dtype=torch.long)
    qk=torch.gather(keys,1,qi[:,None]).squeeze(1)
    target=torch.gather(vals,1,qi[:,None]).squeeze(1)

    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(PAIRS):
        x[:,2*i]=keys[:,i]
        x[:,2*i+1]=KEYS+vals[:,i]
    x[:,-1]=KEYS+VALUES+qk
    return x,target

class BindingCell(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb=nn.Embedding(KEYS+VALUES+KEYS,EMBED)
        width=EMBED+HIDDEN
        self.candidate=nn.Linear(width,HIDDEN)
        self.gate=nn.Linear(width,HIDDEN)
        self.readout=nn.Linear(HIDDEN,VALUES)

    def encode(self,x,reset_each=False):
        h=torch.zeros((x.shape[0],HIDDEN),dtype=torch.float32)
        for t in range(SEQ):
            if reset_each:
                h=torch.zeros_like(h)
            e=self.emb(x[:,t])
            z=torch.cat((e,h),dim=1)
            c=torch.tanh(self.candidate(z))
            g=torch.sigmoid(self.gate(z))
            h=g*h+(1.0-g)*c
        return h

    def forward(self,x,reset_each=False):
        return self.readout(self.encode(x,reset_each=reset_each))

def shuffled_bindings(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9100000+seed)
    out=x.clone()
    value_cols=torch.tensor([1,3,5,7],dtype=torch.long)
    vals=x[:,value_cols]
    order=torch.argsort(torch.rand((x.shape[0],PAIRS),generator=g),dim=1)
    out[:,value_cols]=torch.gather(vals,1,order)
    return out

def accuracy(model,x,y,reset=False):
    model.eval()
    with torch.no_grad():
        pred=model(x,reset_each=reset).argmax(dim=1)
    return float((pred==y).float().mean().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=BindingCell()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=nn.CrossEntropyLoss()
    xtr,ytr=make_data(seed,TRAIN_N,1)
    xev,yev=make_data(seed,EVAL_N,2)
    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+3)

    for _ in range(EPOCHS):
        model.train()
        order=torch.randperm(TRAIN_N,generator=gen)
        for i in range(0,TRAIN_N,BATCH):
            idx=order[i:i+BATCH]
            opt.zero_grad(set_to_none=True)
            loss=loss_fn(model(xtr[idx]),ytr[idx])
            loss.backward()
            opt.step()

    intact=accuracy(model,xev,yev,False)
    reset=accuracy(model,xev,yev,True)
    shuffled=accuracy(model,shuffled_bindings(xev,seed),yev,False)
    return {
        "seed":seed,
        "persistent_accuracy":intact,
        "reset_accuracy":reset,
        "binding_shuffle_accuracy":shuffled,
        "persistent_reset_gap":intact-reset,
        "binding_shuffle_degradation":intact-shuffled,
        "causal_direction":bool(intact>reset and intact>shuffled),
        "parameter_count":sum(p.numel() for p in model.parameters()),
    }

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    persistent=[r["persistent_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    drop=[r["binding_shuffle_degradation"] for r in rows]
    q={
        "min_persistent_ge_090":min(persistent)>=0.90,
        "max_reset_le_035":max(reset)<=0.35,
        "min_gap_ge_050":min(gap)>=0.50,
        "min_shuffle_drop_ge_040":min(drop)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "median_persistent_ge_095":statistics.median(persistent)>=0.95,
    }
    q["YGG_B2_CONTENT_ADDRESSED_BINDING"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B2",
        "prereg":PREREG,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]:
        raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
