#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

import torch
from torch import nn

PREREG="d210b0ea6f5d65fb7c8cca2551bcd7658de37899"
VOCAB=8
SEQ=16
LAG=8
HIDDEN=16
EMBED=8
TRAIN_N=4096
EVAL_N=2048
BATCH=256
EPOCHS=50
LR=0.01
SEEDS=(101,202,303,404,505)

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def make_data(seed,n,salt):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+salt)
    x=torch.randint(0,VOCAB,(n,SEQ),generator=g,dtype=torch.long)
    y=x[:,SEQ-1-LAG].clone()
    return x,y

class CellMemory(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb=nn.Embedding(VOCAB,EMBED)
        width=EMBED+1+HIDDEN
        self.candidate=nn.Linear(width,HIDDEN)
        self.gate=nn.Linear(width,HIDDEN)
        self.readout=nn.Linear(HIDDEN,VOCAB)

    def encode(self,x,reset_each=False):
        n=x.shape[0]
        h=torch.zeros((n,HIDDEN),dtype=torch.float32)
        for t in range(SEQ):
            if reset_each:
                h=torch.zeros_like(h)
            e=self.emb(x[:,t])
            pos=torch.full((n,1),float(t)/(SEQ-1),dtype=torch.float32)
            z=torch.cat((e,pos,h),dim=1)
            c=torch.tanh(self.candidate(z))
            g=torch.sigmoid(self.gate(z))
            h=g*h+(1.0-g)*c
        return h

    def forward(self,x,reset_each=False):
        return self.readout(self.encode(x,reset_each=reset_each))

def shuffled_prefix(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9000000+seed)
    keys=torch.rand((x.shape[0],SEQ-1),generator=g)
    order=torch.argsort(keys,dim=1)
    out=x.clone()
    out[:,:SEQ-1]=torch.gather(x[:,:SEQ-1],1,order)
    return out

def accuracy(model,x,y,reset=False):
    model.eval()
    with torch.no_grad():
        pred=model(x,reset_each=reset).argmax(dim=1)
    return float((pred==y).float().mean().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=CellMemory()
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
    shuffled=accuracy(model,shuffled_prefix(xev,seed),yev,False)
    return {
        "seed":seed,
        "persistent_accuracy":intact,
        "reset_accuracy":reset,
        "shuffle_accuracy":shuffled,
        "persistent_reset_gap":intact-reset,
        "shuffle_degradation":intact-shuffled,
        "causal_direction":bool(intact>reset and intact>shuffled),
        "parameter_count":sum(p.numel() for p in model.parameters()),
    }

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    persistent=[r["persistent_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    drop=[r["shuffle_degradation"] for r in rows]
    qualification={
        "min_persistent_ge_090":min(persistent)>=0.90,
        "max_reset_le_070":max(reset)<=0.70,
        "min_gap_ge_020":min(gap)>=0.20,
        "min_shuffle_drop_ge_015":min(drop)>=0.15,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "median_persistent_ge_095":statistics.median(persistent)>=0.95,
    }
    qualification["YGG_B1_PERSISTENT_SEQUENCE_MEMORY"]=all(qualification.values())
    return {"rows":rows,"qualification":qualification}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B1",
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
