#!/usr/bin/env python3
import hashlib,json,statistics,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import torch
from torch import nn
from torch.nn import functional as F
import ygg_b15_two_entity_fixed_load_v1 as b15

PREREG="29d5f861ecde882a2fa9e69fc7a94e49b757c672"
PARENT_CLOSURE="61110520572d9e43b976ff900fd0fd187274a5cf"

VALUE_DIM=3
PERSISTENT_SCALARS=32
PARAMETERS=120

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

class Value3DBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(b15.KEYS,b15.ADDRESS_DIM)
        self.value_emb=nn.Embedding(b15.VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,b15.VALUES)

    def bind_role(self,v,r):
        return F.normalize(v*b15.ROLE_MASK[r],p=2,dim=1,eps=1e-12)

    def bind_slot(self,v,s):
        return F.normalize(v*b15.SLOT_MASK[s],p=2,dim=1,eps=1e-12)

    def address(self,k,r,s):
        return self.bind_slot(self.bind_role(self.key_emb(k),r),s)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,b15.ADDRESS_DIM),dtype=torch.float32)
        pending=torch.zeros((n,b15.ADDRESS_DIM),dtype=torch.float32)
        for t in range(b15.SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)
            token=x[:,t]
            if t<16:
                mod=t%4
                if mod==0:
                    if torch.any((token<0)|(token>=b15.KEYS)):
                        raise AssertionError("key token range")
                    pending=self.key_emb(token)
                elif mod==1:
                    role=token-b15.ROLE_BASE
                    if torch.any((role<0)|(role>=b15.ROLES)):
                        raise AssertionError("role token range")
                    pending=self.bind_role(pending,role)
                elif mod==2:
                    slot=token-b15.SLOT_BASE
                    if torch.any((slot<0)|(slot>=b15.SLOTS)):
                        raise AssertionError("slot token range")
                    pending=self.bind_slot(pending,slot)
                else:
                    value_id=token-b15.VALUE_BASE
                    if torch.any((value_id<0)|(value_id>=b15.VALUES)):
                        raise AssertionError("value token range")
                    value=self.value_emb(value_id)
                    M=M+value.unsqueeze(2)*pending.unsqueeze(1)
                    pending=torch.zeros_like(pending)
            elif t==16:
                key=token-b15.QUERY_KEY_BASE
                if torch.any((key<0)|(key>=b15.KEYS)):
                    raise AssertionError("query key range")
                pending=self.key_emb(key)
            elif t==17:
                role=token-b15.QUERY_ROLE_BASE
                if torch.any((role<0)|(role>=b15.ROLES)):
                    raise AssertionError("query role range")
                pending=self.bind_role(pending,role)
            elif t==18:
                slot=token-b15.QUERY_SLOT_BASE
                if torch.any((slot<0)|(slot>=b15.SLOTS)):
                    raise AssertionError("query slot range")
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
    model=Value3DBinding()
    opt=torch.optim.Adam(model.parameters(),lr=b15.LR)
    loss_fn=nn.CrossEntropyLoss()

    xtr,ytr,ktr,rtr,str_,vtr,_,_,_,_=b15.training_data(seed,b15.TRAIN_N)
    xev,yev,kev,rev,sev,vev,_,qkev,qrev,qsev=b15.evaluation_data(seed,b15.EVAL_N)

    train_holdout=b15.holdout_quadruples_present(ktr,rtr,str_,vtr)
    eval_count=b15.queried_holdout_quadruple_count(qkev,qrev,qsev,yev)
    if train_holdout!=0:
        raise AssertionError("held-out quadruple leaked into training")
    if torch.any(((qkev+2*qrev+3*qsev+yev)%4)!=0):
        raise AssertionError("evaluation target not held out")

    gen=torch.Generator(device="cpu")
    gen.manual_seed(seed*100000+33)
    for _ in range(b15.EPOCHS):
        model.train()
        order=torch.randperm(b15.TRAIN_N,generator=gen)
        for i in range(0,b15.TRAIN_N,b15.BATCH):
            idx=order[i:i+b15.BATCH]
            opt.zero_grad(set_to_none=True)
            loss=loss_fn(model(xtr[idx]),ytr[idx])
            loss.backward()
            opt.step()

    persistent=accuracy(model,xev,yev,False)
    reset=accuracy(model,xev,yev,True)
    value_shuffle=accuracy(model,b15.shuffled_values(xev,seed),yev,False)
    role_flip=accuracy(model,b15.flipped_roles(xev),yev,False)
    slot_flip=accuracy(model,b15.flipped_slots(xev),yev,False)

    with torch.no_grad():
        addr=[]
        for k in range(b15.KEYS):
            for r in range(b15.ROLES):
                for s in range(b15.SLOTS):
                    addr.append(model.address(torch.tensor([k]),torch.tensor([r]),torch.tensor([s])).squeeze(0))
        addresses=torch.stack(addr,dim=0)
        gram=addresses@addresses.T
        offdiag=gram-torch.eye(b15.KEYS*b15.ROLES*b15.SLOTS,dtype=gram.dtype)
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
    model=Value3DBinding()
    x,_,keys,roles,slots,_,_,_,_,_=b15.training_data(995,512)
    checks={
        "learned_entity_geometry":isinstance(model.key_emb,nn.Embedding) and tuple(model.key_emb.weight.shape)==(8,8),
        "role_masks_exact":torch.equal(b15.ROLE_MASK,b15.ROLE_MASK),
        "slot_masks_exact":torch.equal(b15.SLOT_MASK,b15.SLOT_MASK),
        "two_distinct_entities_per_sequence":all(len(set(row.tolist()))==2 for row in keys),
        "two_structural_addresses_per_entity":all(
            len(set(zip(roles[i,:2].tolist(),slots[i,:2].tolist())))==2
            and len(set(zip(roles[i,2:].tolist(),slots[i,2:].tolist())))==2
            for i in range(keys.shape[0])
        ),
        "bindings_exactly_4":keys.shape[1]==4,
        "sequence_length_exactly_19":x.shape[1]==19,
        "value_dimension_exactly_3":VALUE_DIM==3,
        "memory_shape_3x8":VALUE_DIM==3 and b15.ADDRESS_DIM==8,
        "persistent_state_exactly_32":PERSISTENT_SCALARS==32,
        "parameter_count_exactly_120":sum(p.numel() for p in model.parameters())==PARAMETERS,
    }
    return {"all_pass":all(checks.values()),"checks":checks,"parameter_count":sum(p.numel() for p in model.parameters())}

def one_pass():
    rows=[train_seed(s) for s in b15.SEEDS]
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
        "state_exactly_32":all(r["persistent_state_scalars"]==32 for r in rows),
        "parameter_count_exactly_120":all(r["parameter_count"]==120 for r in rows),
        "no_holdout_quadruple_in_training":all(r["train_holdout_quadruples"]==0 for r in rows),
        "all_64_holdout_quadruples_scored":all(r["eval_distinct_heldout_quadruples"]==64 for r in rows),
    }
    q["YGG_B17_VALUE3D_ENTITY_BINDING"]=all(q.values())
    return {"rows":rows,"qualification":q}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B17_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=canonical(p1)
    b2=canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B17",
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
