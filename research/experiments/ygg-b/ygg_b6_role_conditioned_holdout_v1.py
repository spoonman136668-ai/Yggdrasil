#!/usr/bin/env python3
import hashlib, json, statistics, sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PREREG="7667a338a63b16b3468f8e0e2b201b3725572151"
PARENT_CLOSURE="a40e007cf7b3bce6b2a88da78ee91a420f2fd532"
KEYS=8
ROLES=2
VALUES=8
PAIRS=4
SEQ=14
KEY_DIM=8
VALUE_DIM=1
PERSISTENT_SCALARS=16
TRAIN_N=8192
EVAL_N=4096
BATCH=256
EPOCHS=75
LR=0.005
SEEDS=(111,222,333,444,555)

ROLE_BASE=KEYS
VALUE_BASE=KEYS+ROLES
QUERY_KEY_BASE=KEYS+ROLES+VALUES
QUERY_ROLE_BASE=QUERY_KEY_BASE+KEYS

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

ALLOWED=torch.tensor(
    [[[v for v in range(VALUES) if (k+2*r+v)%4 != 0] for r in range(ROLES)] for k in range(KEYS)],
    dtype=torch.long,
)
HELDOUT=torch.tensor(
    [[[v for v in range(VALUES) if (k+2*r+v)%4 == 0] for r in range(ROLES)] for k in range(KEYS)],
    dtype=torch.long,
)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def distinct_two_keys(g,n):
    scores=torch.rand((n,KEYS),generator=g)
    return torch.argsort(scores,dim=1)[:,:2]

def structural_addresses(g,n):
    pair=distinct_two_keys(g,n)
    keys=torch.stack((pair[:,0],pair[:,0],pair[:,1],pair[:,1]),dim=1)
    roles=torch.tensor((0,1,0,1),dtype=torch.long).unsqueeze(0).expand(n,-1).clone()
    return keys,roles

def pack(keys,roles,vals,qi):
    n=keys.shape[0]
    rows=torch.arange(n,dtype=torch.long)
    qk=keys[rows,qi]
    qr=roles[rows,qi]
    target=vals[rows,qi]
    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(PAIRS):
        x[:,3*i]=keys[:,i]
        x[:,3*i+1]=ROLE_BASE+roles[:,i]
        x[:,3*i+2]=VALUE_BASE+vals[:,i]
    x[:,12]=QUERY_KEY_BASE+qk
    x[:,13]=QUERY_ROLE_BASE+qr
    return x,target,qk,qr

def training_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+1)
    keys,roles=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[2],(n,PAIRS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,choice]
    qi=torch.randint(0,PAIRS,(n,),generator=g,dtype=torch.long)
    x,target,qk,qr=pack(keys,roles,vals,qi)
    return x,target,keys,roles,vals,qi,qk,qr

def evaluation_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+2)
    keys,roles=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[2],(n,PAIRS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,choice]
    qi=torch.randint(0,PAIRS,(n,),generator=g,dtype=torch.long)
    rows=torch.arange(n,dtype=torch.long)
    qk=keys[rows,qi]
    qr=roles[rows,qi]
    hchoice=torch.randint(0,HELDOUT.shape[2],(n,),generator=g,dtype=torch.long)
    vals[rows,qi]=HELDOUT[qk,qr,hchoice]
    x,target,qk,qr=pack(keys,roles,vals,qi)
    return x,target,keys,roles,vals,qi,qk,qr

def holdout_triples_present(keys,roles,vals):
    return int((((keys+2*roles+vals)%4)==0).sum().item())

def queried_holdout_triple_count(qk,qr,target):
    triples=set((int(k),int(r),int(v)) for k,r,v in zip(qk.tolist(),qr.tolist(),target.tolist()))
    return len(triples)

def shuffled_values(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9100000+seed)
    out=x.clone()
    value_cols=torch.tensor([2,5,8,11],dtype=torch.long)
    vals=x[:,value_cols]
    order=torch.argsort(torch.rand((x.shape[0],PAIRS),generator=g),dim=1)
    out[:,value_cols]=torch.gather(vals,1,order)
    return out

def flipped_roles(x):
    out=x.clone()
    role_cols=torch.tensor([1,4,7,10],dtype=torch.long)
    roles=x[:,role_cols]-ROLE_BASE
    out[:,role_cols]=ROLE_BASE+(1-roles)
    return out

class RoleBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(KEYS,KEY_DIM)
        self.role_emb=nn.Embedding(ROLES,KEY_DIM)
        self.value_emb=nn.Embedding(VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,VALUES)

    def address(self,key_ids,role_ids):
        return F.normalize(self.key_emb(key_ids)+self.role_emb(role_ids),p=2,dim=1,eps=1e-12)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,KEY_DIM),dtype=torch.float32)
        pending=torch.zeros((n,KEY_DIM),dtype=torch.float32)

        for t in range(SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)

            token=x[:,t]
            if t in (0,3,6,9):
                if torch.any((token<0)|(token>=KEYS)):
                    raise AssertionError("key token range")
                pending=self.key_emb(token)
            elif t in (1,4,7,10):
                role_id=token-ROLE_BASE
                if torch.any((role_id<0)|(role_id>=ROLES)):
                    raise AssertionError("role token range")
                pending=F.normalize(pending+self.role_emb(role_id),p=2,dim=1,eps=1e-12)
            elif t in (2,5,8,11):
                value_id=token-VALUE_BASE
                if torch.any((value_id<0)|(value_id>=VALUES)):
                    raise AssertionError("value token range")
                value=self.value_emb(value_id)
                M=M+value.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            elif t==12:
                key_id=token-QUERY_KEY_BASE
                if torch.any((key_id<0)|(key_id>=KEYS)):
                    raise AssertionError("query key range")
                pending=self.key_emb(key_id)
            elif t==13:
                role_id=token-QUERY_ROLE_BASE
                if torch.any((role_id<0)|(role_id>=ROLES)):
                    raise AssertionError("query role range")
                query=F.normalize(pending+self.role_emb(role_id),p=2,dim=1,eps=1e-12)
                read=torch.bmm(M,query.unsqueeze(2)).squeeze(2)
                return self.readout(read)
            else:
                raise AssertionError("sequence position")

        raise AssertionError("missing query")

def accuracy(model,x,y,reset=False):
    model.eval()
    with torch.no_grad():
        pred=model(x,reset_each=reset).argmax(dim=1)
    return float((pred==y).float().mean().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=RoleBinding()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,ytr,ktr,rtr,vtr,qitr,qktr,qrtr=training_data(seed,TRAIN_N)
    xev,yev,kev,rev,vev,qiev,qkev,qrev=evaluation_data(seed,EVAL_N)

    train_holdout=holdout_triples_present(ktr,rtr,vtr)
    eval_count=queried_holdout_triple_count(qkev,qrev,yev)
    if train_holdout!=0:
        raise AssertionError("held-out triple leaked into training")
    if torch.any(((qkev+2*qrev+yev)%4)!=0):
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
    value_shuffle=accuracy(model,shuffled_values(xev,seed),yev,False)
    role_flip=accuracy(model,flipped_roles(xev),yev,False)

    with torch.no_grad():
        addr=[]
        for k in range(KEYS):
            for r in range(ROLES):
                addr.append(model.address(torch.tensor([k]),torch.tensor([r])).squeeze(0))
        addresses=torch.stack(addr,dim=0)
        gram=addresses@addresses.T
        offdiag=gram-torch.eye(KEYS*ROLES,dtype=gram.dtype)
        max_abs_offdiag=float(offdiag.abs().max().item())

    return {
        "seed":seed,
        "persistent_ood_accuracy":persistent,
        "reset_accuracy":reset,
        "value_shuffle_accuracy":value_shuffle,
        "role_flip_accuracy":role_flip,
        "persistent_reset_gap":persistent-reset,
        "value_shuffle_degradation":persistent-value_shuffle,
        "role_flip_degradation":persistent-role_flip,
        "causal_direction":bool(persistent>reset and persistent>value_shuffle and persistent>role_flip),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_holdout_triples":train_holdout,
        "eval_distinct_heldout_triples":eval_count,
        "max_abs_offdiag_address_cosine":max_abs_offdiag,
    }

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    persistent=[r["persistent_ood_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    value_drop=[r["value_shuffle_degradation"] for r in rows]
    role_drop=[r["role_flip_degradation"] for r in rows]
    q={
        "min_persistent_ge_090":min(persistent)>=0.90,
        "median_persistent_ge_095":statistics.median(persistent)>=0.95,
        "max_reset_le_035":max(reset)<=0.35,
        "min_gap_ge_050":min(gap)>=0.50,
        "min_value_shuffle_drop_ge_040":min(value_drop)>=0.40,
        "min_role_flip_drop_ge_040":min(role_drop)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_16":all(r["persistent_state_scalars"]==16 for r in rows),
        "parameter_count_exactly_104":all(r["parameter_count"]==104 for r in rows),
        "no_holdout_triple_in_training":all(r["train_holdout_triples"]==0 for r in rows),
        "all_32_holdout_triples_scored":all(r["eval_distinct_heldout_triples"]==32 for r in rows),
    }
    q["YGG_B6_ROLE_CONDITIONED_HOLDOUT"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B6",
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
