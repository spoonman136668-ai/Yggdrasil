#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PREREG="626476e479cd8283625c6d45d36a28a994f61135"
PARENT_CLOSURE="f32f387b2048c7c2423346f4d509f2e44774637b"
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

ALLOWED=torch.tensor(
    [[v for v in range(VALUES) if (k+v)%4 != 0] for k in range(KEYS)],
    dtype=torch.long,
)
HELDOUT=torch.tensor(
    [[v for v in range(VALUES) if (k+v)%4 == 0] for k in range(KEYS)],
    dtype=torch.long,
)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def distinct_keys(g,n):
    scores=torch.rand((n,KEYS),generator=g)
    return torch.argsort(scores,dim=1)[:,:PAIRS]

def training_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+1)
    keys=distinct_keys(g,n)
    choice=torch.randint(0,ALLOWED.shape[1],(n,PAIRS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,choice]
    qi=torch.randint(0,PAIRS,(n,),generator=g,dtype=torch.long)
    qk=torch.gather(keys,1,qi[:,None]).squeeze(1)
    target=torch.gather(vals,1,qi[:,None]).squeeze(1)

    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(PAIRS):
        x[:,2*i]=keys[:,i]
        x[:,2*i+1]=KEYS+vals[:,i]
    x[:,-1]=KEYS+VALUES+qk
    return x,target,keys,vals,qi

def evaluation_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+2)
    keys=distinct_keys(g,n)
    choice=torch.randint(0,ALLOWED.shape[1],(n,PAIRS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,choice]
    qi=torch.randint(0,PAIRS,(n,),generator=g,dtype=torch.long)

    rows=torch.arange(n,dtype=torch.long)
    qk=keys[rows,qi]
    hchoice=torch.randint(0,HELDOUT.shape[1],(n,),generator=g,dtype=torch.long)
    target=HELDOUT[qk,hchoice]
    vals[rows,qi]=target

    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(PAIRS):
        x[:,2*i]=keys[:,i]
        x[:,2*i+1]=KEYS+vals[:,i]
    x[:,-1]=KEYS+VALUES+qk
    return x,target,keys,vals,qi

def holdout_pair_count(keys,vals,qi):
    rows=torch.arange(keys.shape[0],dtype=torch.long)
    qk=keys[rows,qi]
    qv=vals[rows,qi]
    pairs=set((int(k),int(v)) for k,v in zip(qk.tolist(),qv.tolist()))
    return len(pairs)

def holdout_bindings_present(keys,vals):
    return int((((keys+vals)%4)==0).sum().item())

def shuffled_bindings(x,seed):
    # Exact YGG-B4 control construction.
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

    xtr,ytr,ktr,vtr,qitr=training_data(seed,TRAIN_N)
    xev,yev,kev,vev,qiev=evaluation_data(seed,EVAL_N)

    train_holdout_bindings=holdout_bindings_present(ktr,vtr)
    eval_heldout_pairs=holdout_pair_count(kev,vev,qiev)
    if train_holdout_bindings != 0:
        raise AssertionError("held-out pair leaked into training")
    if torch.any(((kev[torch.arange(EVAL_N),qiev]+yev)%4)!=0):
        raise AssertionError("evaluation target not held out")

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
        "persistent_ood_accuracy":persistent,
        "reset_accuracy":reset,
        "binding_shuffle_accuracy":shuffled,
        "persistent_reset_gap":persistent-reset,
        "binding_shuffle_degradation":persistent-shuffled,
        "causal_direction":bool(persistent>reset and persistent>shuffled),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_holdout_bindings":train_holdout_bindings,
        "eval_distinct_heldout_pairs":eval_heldout_pairs,
        "max_abs_offdiag_key_cosine":max_abs_offdiag,
    }

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    persistent=[r["persistent_ood_accuracy"] for r in rows]
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
        "parameter_count_exactly_88":all(r["parameter_count"]==88 for r in rows),
        "no_holdout_pair_in_training":all(r["train_holdout_bindings"]==0 for r in rows),
        "all_16_holdout_pairs_scored":all(r["eval_distinct_heldout_pairs"]==16 for r in rows),
    }
    q["YGG_B5_CARTESIAN_HOLDOUT_COMPOSITION"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B5",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]:
        raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
