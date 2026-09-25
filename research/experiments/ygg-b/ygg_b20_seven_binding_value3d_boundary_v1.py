#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import torch
from torch import nn
from torch.nn import functional as F
import ygg_b18_full_load_value3d_binding_v1 as b18

PREREG="df446af1d2c8ecd4dae294380ebc32c426aef9e2"
PARENT_CLOSURE="b08a0189a04e5391161d8296373e28205fb8ea45"

KEYS=b18.KEYS
ROLES=b18.ROLES
SLOTS=b18.SLOTS
VALUES=b18.VALUES
BINDINGS=7
SEQ=31
ADDRESS_DIM=b18.ADDRESS_DIM
VALUE_DIM=3
PERSISTENT_SCALARS=32
PARAMETERS=120
TRAIN_N=b18.TRAIN_N
EVAL_N=b18.EVAL_N
BATCH=b18.BATCH
EPOCHS=b18.EPOCHS
LR=b18.LR
SEEDS=b18.SEEDS

ROLE_BASE=b18.ROLE_BASE
SLOT_BASE=b18.SLOT_BASE
VALUE_BASE=b18.VALUE_BASE
QUERY_KEY_BASE=b18.QUERY_KEY_BASE
QUERY_ROLE_BASE=b18.QUERY_ROLE_BASE
QUERY_SLOT_BASE=b18.QUERY_SLOT_BASE
ROLE_MASK=b18.ROLE_MASK
SLOT_MASK=b18.SLOT_MASK
ALLOWED=b18.ALLOWED
HELDOUT=b18.HELDOUT

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def structural_addresses(g,n):
    pair=b18.distinct_two_keys(g,n)
    full_entity=torch.randint(0,2,(n,),generator=g,dtype=torch.long)
    omit=torch.randint(0,4,(n,),generator=g,dtype=torch.long)
    combo=[(0,0),(0,1),(1,0),(1,1)]

    keys=torch.empty((n,BINDINGS),dtype=torch.long)
    roles=torch.empty((n,BINDINGS),dtype=torch.long)
    slots=torch.empty((n,BINDINGS),dtype=torch.long)

    for i in range(n):
        fe=int(full_entity[i].item())
        pe=1-fe
        full_key=int(pair[i,fe].item())
        partial_key=int(pair[i,pe].item())
        out=[]
        for r,s in combo:
            out.append((full_key,r,s))
        oi=int(omit[i].item())
        for j,(r,s) in enumerate(combo):
            if j!=oi:
                out.append((partial_key,r,s))
        for j,(k,r,s) in enumerate(out):
            keys[i,j]=k
            roles[i,j]=r
            slots[i,j]=s
    return keys,roles,slots,full_entity,omit

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
    x[:,28]=QUERY_KEY_BASE+qk
    x[:,29]=QUERY_ROLE_BASE+qr
    x[:,30]=QUERY_SLOT_BASE+qs
    return x,target,qk,qr,qs

def training_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+11)
    keys,roles,slots,full,omit=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[3],(n,BINDINGS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,slots,choice]
    qi=torch.randint(0,BINDINGS,(n,),generator=g,dtype=torch.long)
    x,target,qk,qr,qs=pack(keys,roles,slots,vals,qi)
    return x,target,keys,roles,slots,vals,qi,qk,qr,qs,full,omit

def evaluation_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+12)
    keys,roles,slots,full,omit=structural_addresses(g,n)
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
    return x,target,keys,roles,slots,vals,qi,qk,qr,qs,full,omit

def holdout_quadruples_present(keys,roles,slots,vals):
    return int((((keys+2*roles+3*slots+vals)%4)==0).sum().item())

def queried_holdout_quadruple_count(qk,qr,qs,target):
    return len(set((int(k),int(r),int(s),int(v)) for k,r,s,v in zip(qk.tolist(),qr.tolist(),qs.tolist(),target.tolist())))

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
            if t<28:
                mod=t%4
                if mod==0:
                    if torch.any((token<0)|(token>=KEYS)): raise AssertionError("key token range")
                    pending=self.key_emb(token)
                elif mod==1:
                    role=token-ROLE_BASE
                    if torch.any((role<0)|(role>=ROLES)): raise AssertionError("role token range")
                    pending=self.bind_role(pending,role)
                elif mod==2:
                    slot=token-SLOT_BASE
                    if torch.any((slot<0)|(slot>=SLOTS)): raise AssertionError("slot token range")
                    pending=self.bind_slot(pending,slot)
                else:
                    value=token-VALUE_BASE
                    if torch.any((value<0)|(value>=VALUES)): raise AssertionError("value token range")
                    vv=self.value_emb(value)
                    M=M+vv.unsqueeze(2)*pending.unsqueeze(1)
                    pending=torch.zeros_like(pending)
            elif t==28:
                key=token-QUERY_KEY_BASE
                if torch.any((key<0)|(key>=KEYS)): raise AssertionError("query key range")
                pending=self.key_emb(key)
            elif t==29:
                role=token-QUERY_ROLE_BASE
                if torch.any((role<0)|(role>=ROLES)): raise AssertionError("query role range")
                pending=self.bind_role(pending,role)
            elif t==30:
                slot=token-QUERY_SLOT_BASE
                if torch.any((slot<0)|(slot>=SLOTS)): raise AssertionError("query slot range")
                q=self.bind_slot(pending,slot)
                read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
                return self.readout(read)
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

    xtr,ytr,ktr,rtr,str_,vtr,_,_,_,_,_,_=training_data(seed,TRAIN_N)
    xev,yev,kev,rev,sev,vev,_,qkev,qrev,qsev,_,_=evaluation_data(seed,EVAL_N)
    leaked=holdout_quadruples_present(ktr,rtr,str_,vtr)
    eval_count=queried_holdout_quadruple_count(qkev,qrev,qsev,yev)
    if leaked!=0: raise AssertionError("held-out quadruple leaked into training")
    if torch.any(((qkev+2*qrev+3*qsev+yev)%4)!=0): raise AssertionError("evaluation target not held out")

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
        "causal_direction":bool(persistent>reset and persistent>value_shuffle and persistent>role_flip and persistent>slot_flip),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_holdout_quadruples":leaked,
        "eval_distinct_heldout_quadruples":eval_count,
    }

def mechanical():
    torch.manual_seed(991)
    model=StructuralBinding()
    g=torch.Generator(device="cpu"); g.manual_seed(1)
    keys,roles,slots,full,omit=structural_addresses(g,512)
    both_full_choices=set(full.tolist())=={0,1}
    all_omissions=set(omit.tolist())=={0,1,2,3}
    row_ok=True
    for i in range(keys.shape[0]):
        pair=list(dict.fromkeys(keys[i].tolist()))
        if len(pair)!=2:
            row_ok=False; break
        counts=[int((keys[i]==k).sum().item()) for k in pair]
        if sorted(counts)!=[3,4]:
            row_ok=False; break
        for k,count in zip(pair,counts):
            addr=set((int(r),int(s)) for r,s in zip(roles[i][keys[i]==k].tolist(),slots[i][keys[i]==k].tolist()))
            if len(addr)!=count:
                row_ok=False; break
    checks={
        "role_masks_exact":torch.equal(ROLE_MASK,b18.ROLE_MASK),
        "slot_masks_exact":torch.equal(SLOT_MASK,b18.SLOT_MASK),
        "two_distinct_entities_per_sequence":all(len(set(row.tolist()))==2 for row in keys),
        "one_entity_four_other_three_exact":row_ok,
        "both_full_entity_choices_exercised":both_full_choices,
        "all_four_omission_types_exercised":all_omissions,
        "bindings_exactly_7":keys.shape[1]==7,
        "sequence_length_exactly_31":SEQ==31,
        "value_dimension_exactly_3":VALUE_DIM==3,
        "memory_shape_3x8":VALUE_DIM==3 and ADDRESS_DIM==8,
        "persistent_state_exactly_32":PERSISTENT_SCALARS==32,
        "parameter_count_exactly_120":sum(p.numel() for p in model.parameters())==PARAMETERS,
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":sum(p.numel() for p in model.parameters())}

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
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count"]==120 for r in rows),
        "no_holdout_quadruple_in_training":all(r["train_holdout_quadruples"]==0 for r in rows),
        "all_64_holdout_quadruples_scored":all(r["eval_distinct_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B20_SEVEN_BINDING_VALUE3D_BOUNDARY"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]: raise SystemExit("YGG_B20_MECHANICAL_GATE_FAILED")
    p1=one_pass(); p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B20",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":mech,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]: raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
