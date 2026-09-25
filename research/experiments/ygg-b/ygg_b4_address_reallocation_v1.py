#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PREREG="f4a67d36b972efe2406c5323ae7f45ee45e0a57f"
KEYS=8
VALUES=8
PAIRS=4
SEQ=9
KEY_DIM=8
VALUE_DIM=1
PERSISTENT_SCALARS=16
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

def shuffled_bindings(x,seed):
    # Exact YGG-B2 control construction.
    g=torch.Generator(device="cpu")
    g.manual_seed(9100000+seed)
    out=x.clone()
    value_cols=torch.tensor([1,3,5,7],dtype=torch.long)
    vals=x[:,value_cols]
    order=torch.argsort(torch.rand((x.shape[0],PAIRS),generator=g),dim=1)
    out[:,value_cols]=torch.gather(vals,1,order)
    return out

class FactorizedBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(KEYS,KEY_DIM)
        self.value_emb=nn.Embedding(VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,VALUES)

    def key(self,ids):
        return F.normalize(self.key_emb(ids),p=2,dim=1,eps=1e-12)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,KEY_DIM),dtype=torch.float32)
        pending=torch.zeros((n,KEY_DIM),dtype=torch.float32)

        for t in range(SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)

            token=x[:,t]
            if t<8 and t%2==0:
                if torch.any((token<0)|(token>=KEYS)):
                    raise AssertionError("key token range")
                pending=self.key(token)
            elif t<8:
                value_id=token-KEYS
                if torch.any((value_id<0)|(value_id>=VALUES)):
                    raise AssertionError("value token range")
                value=self.value_emb(value_id)
                M=M+value.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            else:
                query_id=token-(KEYS+VALUES)
                if torch.any((query_id<0)|(query_id>=KEYS)):
                    raise AssertionError("query token range")
                query=self.key(query_id)
                read=torch.bmm(M,query.unsqueeze(2)).squeeze(2)
                return self.readout(read)

        raise AssertionError("missing query")

def accuracy(model,x,y,reset=False):
    model.eval()
    with torch.no_grad():
        pred=model(x,reset_each=reset).argmax(dim=1)
    return float((pred==y).float().mean().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=FactorizedBinding()
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

    persistent=accuracy(model,xev,yev,False)
    reset=accuracy(model,xev,yev,True)
    shuffled=accuracy(model,shuffled_bindings(xev,seed),yev,False)
    with torch.no_grad():
        keys=F.normalize(model.key_emb.weight,p=2,dim=1,eps=1e-12)
        gram=keys @ keys.T
        offdiag=gram - torch.eye(KEYS,dtype=gram.dtype)
        max_abs_offdiag=float(offdiag.abs().max().item())
    return {
        "seed":seed,
        "persistent_accuracy":persistent,
        "reset_accuracy":reset,
        "binding_shuffle_accuracy":shuffled,
        "persistent_reset_gap":persistent-reset,
        "binding_shuffle_degradation":persistent-shuffled,
        "causal_direction":bool(persistent>reset and persistent>shuffled),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "max_abs_offdiag_key_cosine":max_abs_offdiag,
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
        "state_exactly_16":all(r["persistent_state_scalars"]==16 for r in rows),
    }
    q["parameter_count_exactly_88"]=all(r["parameter_count"]==88 for r in rows)
    q["YGG_B4_ADDRESS_DIMENSION_REALLOCATION"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B4",
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
