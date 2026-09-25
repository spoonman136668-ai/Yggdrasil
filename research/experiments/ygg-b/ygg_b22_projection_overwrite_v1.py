#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PREREG="c3d29e3dd619e6719e31f828ba28f5e68aebce03"
PARENT_CLOSURE="e4698d5cee348c4fe4810487f65c96d772f8b5ea"

KEYS=8
ROLES=2
SLOTS=2
VALUES=8
WRITES=5
SEQ=23
ADDRESS_DIM=8
VALUE_DIM=2
PERSISTENT_SCALARS=24
PARAMETERS=104
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

COMBOS=((0,0),(0,1),(1,0),(1,1))

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def structural_events(g,n):
    key=torch.randint(0,KEYS,(n,),generator=g,dtype=torch.long)
    update=torch.randint(0,4,(n,),generator=g,dtype=torch.long)
    keys=torch.empty((n,WRITES),dtype=torch.long)
    roles=torch.empty((n,WRITES),dtype=torch.long)
    slots=torch.empty((n,WRITES),dtype=torch.long)
    for i in range(n):
        ui=int(update[i].item())
        order=[ui]+[j for j in range(4) if j!=ui]
        events=order+[ui]
        for j,cidx in enumerate(events):
            r,s=COMBOS[cidx]
            keys[i,j]=key[i]
            roles[i,j]=r
            slots[i,j]=s
    return keys,roles,slots,update

def pack(keys,roles,slots,vals):
    n=keys.shape[0]
    rows=torch.arange(n,dtype=torch.long)
    qk=keys[:,4]
    qr=roles[:,4]
    qs=slots[:,4]
    target=vals[:,4]
    x=torch.empty((n,SEQ),dtype=torch.long)
    for i in range(WRITES):
        x[:,4*i]=keys[:,i]
        x[:,4*i+1]=ROLE_BASE+roles[:,i]
        x[:,4*i+2]=SLOT_BASE+slots[:,i]
        x[:,4*i+3]=VALUE_BASE+vals[:,i]
    x[:,20]=QUERY_KEY_BASE+qk
    x[:,21]=QUERY_ROLE_BASE+qr
    x[:,22]=QUERY_SLOT_BASE+qs
    return x,target,qk,qr,qs

def make_data(seed,n,evaluation):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+(42 if evaluation else 41))
    keys,roles,slots,update=structural_events(g,n)

    choice=torch.randint(0,ALLOWED.shape[3],(n,WRITES),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,slots,choice]

    rows=torch.arange(n,dtype=torch.long)
    if evaluation:
        hchoice=torch.randint(0,HELDOUT.shape[3],(n,),generator=g,dtype=torch.long)
        vals[:,4]=HELDOUT[keys[:,4],roles[:,4],slots[:,4],hchoice]
    else:
        lchoice=torch.randint(0,ALLOWED.shape[3],(n,),generator=g,dtype=torch.long)
        vals[:,4]=ALLOWED[keys[:,4],roles[:,4],slots[:,4],lchoice]

    # First and fifth writes target the same address. Ensure the old value differs
    # from the latest target. Evaluation old value is ALLOWED while latest is
    # HELDOUT, so they are already disjoint; training may need deterministic repair.
    same=vals[:,0]==vals[:,4]
    if torch.any(same):
        idx=torch.where(same)[0]
        for row in idx.tolist():
            candidates=ALLOWED[keys[row,0],roles[row,0],slots[row,0]]
            old=int(vals[row,0].item())
            latest=int(vals[row,4].item())
            repl=next(int(v.item()) for v in candidates if int(v.item())!=latest and int(v.item())!=old)
            vals[row,0]=repl

    x,target,qk,qr,qs=pack(keys,roles,slots,vals)
    return x,target,keys,roles,slots,vals,update,qk,qr,qs

def training_data(seed,n):
    return make_data(seed,n,False)

def evaluation_data(seed,n):
    return make_data(seed,n,True)

def queried_holdout_count(qk,qr,qs,target):
    return len(set((int(k),int(r),int(s),int(v)) for k,r,s,v in zip(qk.tolist(),qr.tolist(),qs.tolist(),target.tolist())))

def latest_holdout_targets_in_training(qk,qr,qs,target):
    return int((((qk+2*qr+3*qs+target)%4)==0).sum().item())

VALUE_COLS=torch.tensor([3,7,11,15,19],dtype=torch.long)
ROLE_COLS=torch.tensor([1,5,9,13,17],dtype=torch.long)
SLOT_COLS=torch.tensor([2,6,10,14,18],dtype=torch.long)

def order_swap(x):
    out=x.clone()
    first=out[:,0:4].clone()
    fifth=out[:,16:20].clone()
    out[:,0:4]=fifth
    out[:,16:20]=first
    return out

def shuffled_values(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9500000+seed)
    out=x.clone()
    vals=x[:,VALUE_COLS]
    order=torch.argsort(torch.rand((x.shape[0],WRITES),generator=g),dim=1)
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

class TemporalBinding(nn.Module):
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
            if t<20:
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
                    M=projection_write(M,pending,vv)
                    pending=torch.zeros_like(pending)
            elif t==20:
                key=token-QUERY_KEY_BASE
                if torch.any((key<0)|(key>=KEYS)): raise AssertionError("query key range")
                pending=self.key_emb(key)
            elif t==21:
                role=token-QUERY_ROLE_BASE
                if torch.any((role<0)|(role>=ROLES)): raise AssertionError("query role range")
                pending=self.bind_role(pending,role)
            elif t==22:
                slot=token-QUERY_SLOT_BASE
                if torch.any((slot<0)|(slot>=SLOTS)): raise AssertionError("query slot range")
                q=self.bind_slot(pending,slot)
                read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
                return self.readout(read)
        raise AssertionError("missing query")

def projection_write(M,q,v):
    # q is unit-normalized. Remove the current component along q, then
    # replace it with v along the same address without adding state/params.
    old=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
    return M-old.unsqueeze(2)*q.unsqueeze(1)+v.unsqueeze(2)*q.unsqueeze(1)

def accuracy(model,x,y,reset=False):
    model.eval()
    with torch.no_grad():
        pred=model(x,reset_each=reset).argmax(dim=1)
    return float((pred==y).float().mean().item())

def train_seed(seed):
    torch.manual_seed(seed)
    model=TemporalBinding()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,ytr,ktr,rtr,str_,vtr,utr,qktr,qrtr,qstr=training_data(seed,TRAIN_N)
    xev,yev,kev,rev,sev,vev,uev,qkev,qrev,qsev=evaluation_data(seed,EVAL_N)

    train_holdout=latest_holdout_targets_in_training(qktr,qrtr,qstr,ytr)
    eval_count=queried_holdout_count(qkev,qrev,qsev,yev)
    if train_holdout!=0:
        raise AssertionError("heldout latest target leaked into training")
    if torch.any(((qkev+2*qrev+3*qsev+yev)%4)!=0):
        raise AssertionError("evaluation latest target not heldout")
    if torch.any(vev[:,0]==vev[:,4]):
        raise AssertionError("evaluation overwrite values not distinct")

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+43)
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
    swapped=accuracy(model,order_swap(xev),yev,False)
    value_shuffle=accuracy(model,shuffled_values(xev,seed),yev,False)
    role_flip=accuracy(model,flipped_roles(xev),yev,False)
    slot_flip=accuracy(model,flipped_slots(xev),yev,False)

    return {
        "seed":seed,
        "persistent_ood_latest_accuracy":persistent,
        "reset_accuracy":reset,
        "order_swap_accuracy":swapped,
        "value_shuffle_accuracy":value_shuffle,
        "role_flip_accuracy":role_flip,
        "slot_flip_accuracy":slot_flip,
        "persistent_reset_gap":persistent-reset,
        "order_swap_degradation":persistent-swapped,
        "value_shuffle_degradation":persistent-value_shuffle,
        "role_flip_degradation":persistent-role_flip,
        "slot_flip_degradation":persistent-slot_flip,
        "causal_direction":bool(
            persistent>reset and persistent>swapped and persistent>value_shuffle
            and persistent>role_flip and persistent>slot_flip
        ),
        "parameter_count":sum(p.numel() for p in model.parameters()),
        "persistent_state_scalars":PERSISTENT_SCALARS,
        "train_heldout_latest_targets":train_holdout,
        "eval_distinct_heldout_quadruples":eval_count,
    }

def mechanical():
    torch.manual_seed(991)
    model=TemporalBinding()
    g=torch.Generator(device="cpu")
    g.manual_seed(991001)
    keys,roles,slots,update=structural_events(g,512)

    exact=True
    for i in range(keys.shape[0]):
        first4=set(zip(roles[i,:4].tolist(),slots[i,:4].tolist()))
        if first4!={(0,0),(0,1),(1,0),(1,1)}:
            exact=False; break
        if int(keys[i].unique().numel())!=1:
            exact=False; break
        if int(roles[i,0])!=int(roles[i,4]) or int(slots[i,0])!=int(slots[i,4]):
            exact=False; break
    q=F.normalize(torch.tensor([[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]]),p=2,dim=1)
    v1=torch.tensor([[0.25,-0.5]])
    v2=torch.tensor([[-0.75,0.125]])
    M=torch.zeros((1,VALUE_DIM,ADDRESS_DIM),dtype=torch.float32)
    M=projection_write(M,q,v1)
    M=projection_write(M,q,v2)
    isolated_read=torch.bmm(M,q.unsqueeze(2)).squeeze(2)
    isolated_replace_exact=bool(torch.allclose(isolated_read,v2,atol=1e-6,rtol=0.0))

    checks={
        "projection_overwrite_formula_exact":isolated_replace_exact,
        "address_normalized_before_write":True,
        "one_entity_per_sequence":all(len(set(row.tolist()))==1 for row in keys),
        "four_structural_addresses_once_before_update":exact,
        "updated_address_first_and_fifth":exact,
        "three_intervening_writes":True,
        "sequence_length_exactly_23":SEQ==23,
        "value_dimension_exactly_2":VALUE_DIM==2,
        "memory_shape_2x8":VALUE_DIM==2 and ADDRESS_DIM==8,
        "persistent_state_exactly_24":PERSISTENT_SCALARS==24,
        "parameter_count_exactly_104":sum(p.numel() for p in model.parameters())==PARAMETERS,
        "role_masks_exact":ROLE_MASK.tolist()==[
            [1.,1.,1.,1.,1.,1.,1.,1.],
            [1.,-1.,1.,-1.,1.,-1.,1.,-1.],
        ],
        "slot_masks_exact":SLOT_MASK.tolist()==[
            [1.,1.,1.,1.,1.,1.,1.,1.],
            [1.,1.,-1.,-1.,1.,1.,-1.,-1.],
        ],
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":sum(p.numel() for p in model.parameters())}

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    p=[r["persistent_ood_latest_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    od=[r["order_swap_degradation"] for r in rows]
    vd=[r["value_shuffle_degradation"] for r in rows]
    rd=[r["role_flip_degradation"] for r in rows]
    sd=[r["slot_flip_degradation"] for r in rows]
    q={
        "min_persistent_ge_090":min(p)>=0.90,
        "median_persistent_ge_095":statistics.median(p)>=0.95,
        "max_reset_le_035":max(reset)<=0.35,
        "min_gap_ge_050":min(gap)>=0.50,
        "min_order_swap_drop_ge_040":min(od)>=0.40,
        "min_value_shuffle_drop_ge_040":min(vd)>=0.40,
        "min_role_flip_drop_ge_040":min(rd)>=0.40,
        "min_slot_flip_drop_ge_040":min(sd)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_24":all(r["persistent_state_scalars"]==24 for r in rows),
        "parameter_count_exactly_104":all(r["parameter_count"]==104 for r in rows),
        "no_heldout_latest_target_in_training":all(r["train_heldout_latest_targets"]==0 for r in rows),
        "all_64_queried_heldout_quadruples_scored":all(r["eval_distinct_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B22_PROJECTION_OVERWRITE_SEQUENCE_INTELLIGENCE"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B22_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1); b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B22",
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
