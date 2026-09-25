#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import torch
import ygg_b14_reduced_load_two_factor_binding_v1 as b14

PREREG="18efc0ea2734d23e20e9306264300c864bf02921"
PARENT_CLOSURE="dd5254209f72785ac27389171589b0f0bb74b6db"

KEYS=b14.KEYS
ROLES=b14.ROLES
SLOTS=b14.SLOTS
VALUES=b14.VALUES
BINDINGS=4
SEQ=19
ADDRESS_DIM=b14.ADDRESS_DIM
VALUE_DIM=b14.VALUE_DIM
PERSISTENT_SCALARS=b14.PERSISTENT_SCALARS
PARAMETERS=b14.PARAMETERS
TRAIN_N=b14.TRAIN_N
EVAL_N=b14.EVAL_N
BATCH=b14.BATCH
EPOCHS=b14.EPOCHS
LR=b14.LR
SEEDS=b14.SEEDS

ROLE_BASE=b14.ROLE_BASE
SLOT_BASE=b14.SLOT_BASE
VALUE_BASE=b14.VALUE_BASE
QUERY_KEY_BASE=b14.QUERY_KEY_BASE
QUERY_ROLE_BASE=b14.QUERY_ROLE_BASE
QUERY_SLOT_BASE=b14.QUERY_SLOT_BASE
ROLE_MASK=b14.ROLE_MASK
SLOT_MASK=b14.SLOT_MASK
ALLOWED=b14.ALLOWED
HELDOUT=b14.HELDOUT
StructuralBinding=b14.StructuralBinding

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def distinct_two_keys(g,n):
    scores=torch.rand((n,KEYS),generator=g)
    return torch.argsort(scores,dim=1)[:,:2]

def structural_addresses(g,n):
    pair=distinct_two_keys(g,n)
    combo_roles=torch.tensor((0,0,1,1),dtype=torch.long)
    combo_slots=torch.tensor((0,1,0,1),dtype=torch.long)
    scores=torch.rand((n,2,4),generator=g)
    sel=torch.argsort(scores,dim=2)[:,:,:2]
    keys=torch.cat((
        pair[:,0].unsqueeze(1).expand(-1,2),
        pair[:,1].unsqueeze(1).expand(-1,2),
    ),dim=1).clone()
    roles=torch.cat((combo_roles[sel[:,0]],combo_roles[sel[:,1]]),dim=1).clone()
    slots=torch.cat((combo_slots[sel[:,0]],combo_slots[sel[:,1]]),dim=1).clone()
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
    x[:,16]=QUERY_KEY_BASE+qk
    x[:,17]=QUERY_ROLE_BASE+qr
    x[:,18]=QUERY_SLOT_BASE+qs
    return x,target,qk,qr,qs

def training_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+31)
    keys,roles,slots=structural_addresses(g,n)
    choice=torch.randint(0,ALLOWED.shape[3],(n,BINDINGS),generator=g,dtype=torch.long)
    vals=ALLOWED[keys,roles,slots,choice]
    qi=torch.randint(0,BINDINGS,(n,),generator=g,dtype=torch.long)
    x,target,qk,qr,qs=pack(keys,roles,slots,vals,qi)
    return x,target,keys,roles,slots,vals,qi,qk,qr,qs

def evaluation_data(seed,n):
    g=torch.Generator(device="cpu")
    g.manual_seed(seed*100000+32)
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
    return len(set((int(k),int(r),int(s),int(v)) for k,r,s,v in zip(qk.tolist(),qr.tolist(),qs.tolist(),target.tolist())))

VALUE_COLS=torch.tensor((3,7,11,15),dtype=torch.long)
ROLE_COLS=torch.tensor((1,5,9,13),dtype=torch.long)
SLOT_COLS=torch.tensor((2,6,10,14),dtype=torch.long)

def shuffled_values(x,seed):
    g=torch.Generator(device="cpu")
    g.manual_seed(9400000+seed)
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

def accuracy(model,x,y,reset=False):
    return b14.accuracy(model,x,y,reset)

def train_seed(seed):
    torch.manual_seed(seed)
    model=StructuralBinding()
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    loss_fn=torch.nn.CrossEntropyLoss()

    xtr,ytr,ktr,rtr,str_,vtr,_,_,_,_=training_data(seed,TRAIN_N)
    xev,yev,kev,rev,sev,vev,_,qkev,qrev,qsev=evaluation_data(seed,EVAL_N)

    train_holdout=holdout_quadruples_present(ktr,rtr,str_,vtr)
    eval_count=queried_holdout_quadruple_count(qkev,qrev,qsev,yev)
    if train_holdout!=0:
        raise AssertionError("held-out quadruple leaked into training")
    if torch.any(((qkev+2*qrev+3*qsev+yev)%4)!=0):
        raise AssertionError("evaluation target not held out")

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+33)
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
                    addr.append(model.address(torch.tensor([k]),torch.tensor([r]),torch.tensor([s])).squeeze(0))
        addresses=torch.stack(addr,dim=0)
        gram=addresses@addresses.T
        offdiag=gram-torch.eye(KEYS*ROLES*SLOTS,dtype=gram.dtype)
        max_abs_offdiag=float(offdiag.abs().max().item())

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
        "train_holdout_quadruples":train_holdout,
        "eval_distinct_heldout_quadruples":eval_count,
        "max_abs_offdiag_address_cosine":max_abs_offdiag,
    }

def mechanical():
    torch.manual_seed(995)
    model=StructuralBinding()
    x,_,keys,roles,slots,_,_,_,_,_=training_data(995,512)
    all_combos=set(zip(roles.flatten().tolist(),slots.flatten().tolist()))
    two_each=True
    for i in range(keys.shape[0]):
        if len(set(keys[i].tolist()))!=2:
            two_each=False
            break
        if len(set(zip(roles[i,:2].tolist(),slots[i,:2].tolist())))!=2:
            two_each=False
            break
        if len(set(zip(roles[i,2:].tolist(),slots[i,2:].tolist())))!=2:
            two_each=False
            break
    checks={
        "role_masks_exact":torch.equal(ROLE_MASK,b14.ROLE_MASK),
        "slot_masks_exact":torch.equal(SLOT_MASK,b14.SLOT_MASK),
        "two_distinct_entities_per_sequence":all(len(set(row.tolist()))==2 for row in keys),
        "two_distinct_structural_addresses_per_entity":two_each,
        "all_four_structural_types_covered":all_combos=={(0,0),(0,1),(1,0),(1,1)},
        "bindings_exactly_4":keys.shape[1]==4,
        "sequence_length_exactly_19":x.shape[1]==19,
        "value_dimension_exactly_2":VALUE_DIM==2,
        "memory_shape_2x8":VALUE_DIM==2 and ADDRESS_DIM==8,
        "persistent_state_exactly_24":PERSISTENT_SCALARS==24,
        "parameter_count_exactly_104":sum(p.numel() for p in model.parameters())==PARAMETERS,
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":sum(p.numel() for p in model.parameters())}

def one_pass():
    rows=[train_seed(s) for s in SEEDS]
    persistent=[r["persistent_ood_accuracy"] for r in rows]
    reset=[r["reset_accuracy"] for r in rows]
    gap=[r["persistent_reset_gap"] for r in rows]
    value_drop=[r["value_shuffle_degradation"] for r in rows]
    role_drop=[r["role_flip_degradation"] for r in rows]
    slot_drop=[r["slot_flip_degradation"] for r in rows]
    q={
        "min_persistent_ge_090":min(persistent)>=0.90,
        "median_persistent_ge_095":statistics.median(persistent)>=0.95,
        "max_reset_le_035":max(reset)<=0.35,
        "min_gap_ge_050":min(gap)>=0.50,
        "min_value_shuffle_drop_ge_040":min(value_drop)>=0.40,
        "min_role_flip_drop_ge_040":min(role_drop)>=0.40,
        "min_slot_flip_drop_ge_040":min(slot_drop)>=0.40,
        "all_causal_direction":all(r["causal_direction"] for r in rows),
        "state_exactly_24":all(r["persistent_state_scalars"]==24 for r in rows),
        "parameter_count_exactly_104":all(r["parameter_count"]==104 for r in rows),
        "no_holdout_quadruple_in_training":all(r["train_holdout_quadruples"]==0 for r in rows),
        "all_64_holdout_quadruples_scored":all(r["eval_distinct_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B15_TWO_ENTITY_FIXED_LOAD_BINDING"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B15_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1)
    b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B15",
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
