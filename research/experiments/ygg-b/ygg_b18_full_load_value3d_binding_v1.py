#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PREREG="28dc1862e5347e661cf435d6482e122bb731adbc"
PARENT_CLOSURE="eb2d0192d36d22e423f8c5552e69e52d5363e079"

KEYS=8
ROLES=2
SLOTS=2
VALUES=8
BINDINGS=8
SEQ=35
ADDRESS_DIM=8
VALUE_DIM=3
PERSISTENT_SCALARS=32
PARAMETERS=120
TRAIN_N=8192
EVAL_N=4096
BATCH=256
EPOCHS=75
LR=0.005
SEEDS=(111,222,333,444,555)

ROLE_BASE=KEYS
SLOT_BASE=ROLE_BASE+ROLES
VALUE_BASE=SLOT_BASE+SLOTS
QUERY_KEY_BASE=VALUE_BASE+VALUES
QUERY_ROLE_BASE=QUERY_KEY_BASE+KEYS
QUERY_SLOT_BASE=QUERY_ROLE_BASE+ROLES

ROLE_MASK=torch.tensor([
    [1,1,1,1,1,1,1,1],
    [1,-1,1,-1,1,-1,1,-1],
],dtype=torch.float32)
SLOT_MASK=torch.tensor([
    [1,1,1,1,1,1,1,1],
    [1,1,-1,-1,1,1,-1,-1],
],dtype=torch.float32)

ALLOWED=torch.tensor(
    [[[[v for v in range(VALUES) if (k+2*r+3*s+v)%4 != 0]
        for s in range(SLOTS)] for r in range(ROLES)] for k in range(KEYS)],
    dtype=torch.long,
)
HELDOUT=torch.tensor(
    [[[[v for v in range(VALUES) if (k+2*r+3*s+v)%4 == 0]
        for s in range(SLOTS)] for r in range(ROLES)] for k in range(KEYS)],
    dtype=torch.long,
)

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def distinct_two_keys(g,n):
    scores=torch.rand((n,KEYS),generator=g)
    return torch.argsort(scores,dim=1)[:,:2]

def structural_addresses(g,n):
    pair=distinct_two_keys(g,n)
    pattern_roles=torch.tensor((0,0,1,1,0,0,1,1),dtype=torch.long)
    pattern_slots=torch.tensor((0,1,0,1,0,1,0,1),dtype=torch.long)
    keys=torch.stack((
        pair[:,0],pair[:,0],pair[:,0],pair[:,0],
        pair[:,1],pair[:,1],pair[:,1],pair[:,1],
    ),dim=1)
    roles=pattern_roles.unsqueeze(0).expand(n,-1).clone()
    slots=pattern_slots.unsqueeze(0).expand(n,-1).clone()
    return keys,roles,slots

def pack(keys,roles,slots,vals,qi):
    n=keys.shape[0]
    rows=torch.arange(n,dtype=torch.long)
    qk=keys[rows,qi]
    qr=roles[rows,qi]
    qs=slots[rows,qi]
    target=vals[rows,qi]
    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(BINDINGS):
        x[:,4*i]=keys[:,i]
        x[:,4*i+1]=ROLE_BASE+roles[:,i]
        x[:,4*i+2]=SLOT_BASE+slots[:,i]
        x[:,4*i+3]=VALUE_BASE+vals[:,i]
    x[:,32]=QUERY_KEY_BASE+qk
    x[:,33]=QUERY_ROLE_BASE+qr
    x[:,34]=QUERY_SLOT_BASE+qs
    return x,target,qk,qr,qs

def training_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+11)
    keys,roles,slots=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[3],(n,BINDINGS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,slots,choice]
    qi=torch.randint(0,BINDINGS,(n,),generator=g,dtype=torch.long)
    x,target,qk,qr,qs=pack(keys,roles,slots,vals,qi)
    return x,target,keys,roles,slots,vals,qi,qk,qr,qs

def evaluation_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+12)
    keys,roles,slots=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[3],(n,BINDINGS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,slots,choice]
    qi=torch.randint(0,BINDINGS,(n,),generator=g,dtype=torch.long)
    rows=torch.arange(n,dtype=torch.long)
    qk=keys[rows,qi]
    qr=roles[rows,qi]
    qs=slots[rows,qi]
    hchoice=torch.randint(0,HELDOUT.shape[3],(n,),generator=g,dtype=torch.long)
    vals[rows,qi]=HELDOUT[qk,qr,qs,hchoice]
    x,target,qk,qr,qs=pack(keys,roles,slots,vals,qi)
    return x,target,keys,roles,slots,vals,qi,qk,qr,qs

def holdout_quadruples_present(keys,roles,slots,vals):
    return int((((keys+2*roles+3*slots+vals)%4)==0).sum().item())

def queried_holdout_quadruple_count(qk,qr,qs,target):
    quads=set(
        (int(k),int(r),int(s),int(v))
        for k,r,s,v in zip(qk.tolist(),qr.tolist(),qs.tolist(),target.tolist())
    )
    return len(quads)

VALUE_COLS=torch.tensor([4*i+3 for i in range(BINDINGS)],dtype=torch.long)
ROLE_COLS=torch.tensor([4*i+1 for i in range(BINDINGS)],dtype=torch.long)
SLOT_COLS=torch.tensor([4*i+2 for i in range(BINDINGS)],dtype=torch.long)

def shuffled_values(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9200000+seed)
    out=x.clone()
    vals=x[:,VALUE_COLS]
    order=torch.argsort(torch.rand((x.shape[0],BINDINGS),generator=g),dim=1)
    out[:,VALUE_COLS]=torch.gather(vals,1,order)
    return out

def flipped_roles(x):
    out=x.clone()
    roles=x[:,ROLE_COLS]-ROLE_BASE
    out[:,ROLE_COLS]=ROLE_BASE+(1-roles)
    return out

def flipped_slots(x):
    out=x.clone()
    slots=x[:,SLOT_COLS]-SLOT_BASE
    out[:,SLOT_COLS]=SLOT_BASE+(1-slots)
    return out

class StructuralBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(KEYS,ADDRESS_DIM)
        self.value_emb=nn.Embedding(VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,VALUES)

    def bind_role(self,v,r):
        return F.normalize(v*ROLE_MASK[r],p=2,dim=1,eps=1e-12)

    def bind_slot(self,v,s):
        return F.normalize(v*SLOT_MASK[s],p=2,dim=1,eps=1e-12)

    def address(self,k,r,s):
        return self.bind_slot(self.bind_role(self.key_emb(k),r),s)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,ADDRESS_DIM),dtype=torch.float32)
        pending=torch.zeros((n,ADDRESS_DIM),dtype=torch.float32)
        for t in range(SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)
            token=x[:,t]
            mod=t%4
            if t<32 and mod==0:
                if torch.any((token<0)|(token>=KEYS)):
                    raise AssertionError("key token range")
                pending=self.key_emb(token)
            elif t<32 and mod==1:
                role=token-ROLE_BASE
                if torch.any((role<0)|(role>=ROLES)):
                    raise AssertionError("role token range")
                pending=self.bind_role(pending,role)
            elif t<32 and mod==2:
                slot=token-SLOT_BASE
                if torch.any((slot<0)|(slot>=SLOTS)):
                    raise AssertionError("slot token range")
                pending=self.bind_slot(pending,slot)
            elif t<32 and mod==3:
                value=token-VALUE_BASE
                if torch.any((value<0)|(value>=VALUES)):
                    raise AssertionError("value token range")
                vv=self.value_emb(value)
                M=M+vv.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            elif t==32:
                key=token-QUERY_KEY_BASE
                if torch.any((key<0)|(key>=KEYS)):
                    raise AssertionError("query key range")
                pending=self.key_emb(key)
            elif t==33:
                role=token-QUERY_ROLE_BASE
                if torch.any((role<0)|(role>=ROLES)):
                    raise AssertionError("query role range")
                pending=self.bind_role(pending,role)
            elif t==34:
                slot=token-QUERY_SLOT_BASE
                if torch.any((slot<0)|(slot>=SLOTS)):
                    raise AssertionError("query slot range")
                q=self.bind_slot(pending,slot)
                read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
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
    model=StructuralBinding()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,ytr,ktr,rtr,str_,vtr,qitr,qktr,qrtr,qstr=training_data(seed,TRAIN_N)
    xev,yev,kev,rev,sev,vev,qiev,qkev,qrev,qsev=evaluation_data(seed,EVAL_N)

    leaked=holdout_quadruples_present(ktr,rtr,str_,vtr)
    eval_count=queried_holdout_quadruple_count(qkev,qrev,qsev,yev)
    if leaked!=0:
        raise AssertionError("held-out quadruple leaked into training")
    if torch.any(((qkev+2*qrev+3*qsev+yev)%4)!=0):
        raise AssertionError("evaluation target not held out")

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+13)
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
    slot_flip=accuracy(model,flipped_slots(xev),yev,False)

    with torch.no_grad():
        addr=[]
        for k in range(KEYS):
            for r in range(ROLES):
                for s in range(SLOTS):
                    addr.append(model.address(
                        torch.tensor([k]),torch.tensor([r]),torch.tensor([s])
                    ).squeeze(0))
        addresses=torch.stack(addr,dim=0)
        gram=addresses@addresses.T
        off=gram-torch.eye(KEYS*ROLES*SLOTS,dtype=gram.dtype)
        max_cos=float(off.abs().max().item())

    return {
        "seed":seed,
        "persistent_ood_accuracy":persistent,
        "reset_accuracy":reset,
        "value_shuffle_accuracy":value_shuffle,
        "role_flip_accuracy":role_flip,
        "slot_flip_accuracy":slot_flip,
        "persistent_reset_gap":persistent-reset,
        "value_shuffle_degradation":persistent-value_shuffle,
        "role_flip_degradation":persistent-role_flip,
        "slot_flip_degradation":persistent-slot_flip,
        "causal_direction":bool(
            persistent>reset and persistent>value_shuffle
            and persistent>role_flip and persistent>slot_flip
        ),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_holdout_quadruples":leaked,
        "eval_distinct_heldout_quadruples":eval_count,
        "max_abs_offdiag_address_cosine":max_cos,
    }

def mechanical():
    torch.manual_seed(991)
    model=StructuralBinding()
    params=sum(p.numel() for p in model.parameters())
    products=[]
    for r in range(ROLES):
        for s in range(SLOTS):
            products.append(tuple((ROLE_MASK[r]*SLOT_MASK[s]).tolist()))
    g=torch.Generator(device="cpu")
    g.manual_seed(1)
    keys,roles,slots=structural_addresses(g,1)
    triples=set(zip(keys[0].tolist(),roles[0].tolist(),slots[0].tolist()))
    expected_role=torch.tensor([
        [1,1,1,1,1,1,1,1],
        [1,-1,1,-1,1,-1,1,-1],
    ],dtype=torch.float32)
    expected_slot=torch.tensor([
        [1,1,1,1,1,1,1,1],
        [1,1,-1,-1,1,1,-1,-1],
    ],dtype=torch.float32)
    checks={
        "role_masks_exact":torch.equal(ROLE_MASK,expected_role),
        "slot_masks_exact":torch.equal(SLOT_MASK,expected_slot),
        "four_structural_mask_products_distinct":len(set(products))==4,
        "value_dimension_exactly_3":model.value_emb.weight.shape==(VALUES,3),
        "memory_shape_3x8":VALUE_DIM==3 and ADDRESS_DIM==8,
        "persistent_state_exactly_32":VALUE_DIM*ADDRESS_DIM+ADDRESS_DIM==PERSISTENT_SCALARS,
        "parameter_count_exactly_120":params==PARAMETERS,
        "structural_masks_nonlearned":not ROLE_MASK.requires_grad and not SLOT_MASK.requires_grad,
        "one_sequence_has_all_eight_addresses":len(triples)==8,
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":params}

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    p=[r["persistent_ood_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    vd=[r["value_shuffle_degradation"] for r in rows]
    rd=[r["role_flip_degradation"] for r in rows]
    sd=[r["slot_flip_degradation"] for r in rows]
    q={
        "min_persistent_ge_090":min(p)>=0.90,
        "median_persistent_ge_095":statistics.median(p)>=0.95,
        "max_reset_le_035":max(reset)<=0.35,
        "min_gap_ge_050":min(gap)>=0.50,
        "min_value_shuffle_drop_ge_040":min(vd)>=0.40,
        "min_role_flip_drop_ge_040":min(rd)>=0.40,
        "min_slot_flip_drop_ge_040":min(sd)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_32":all(r["persistent_state_scalars"]==PERSISTENT_SCALARS for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count"]==PARAMETERS for r in rows),
        "no_holdout_quadruple_in_training":all(r["train_holdout_quadruples"]==0 for r in rows),
        "all_64_holdout_quadruples_scored":all(r["eval_distinct_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B18_FULL_LOAD_VALUE3D_BINDING"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B13_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B18",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":mech,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]:
        raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
