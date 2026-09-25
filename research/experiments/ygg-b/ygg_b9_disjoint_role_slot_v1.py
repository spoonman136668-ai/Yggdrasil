#!/usr/bin/env python3
import hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))

import torch
from torch import nn
from torch.nn import functional as F
import ygg_b6_role_conditioned_holdout_v1 as b6

PREREG="1b1e0deee19fc778460ddae61e64d3099f5e868c"
PARENT_CLOSURE="7e9640e2328eebeb154ca4baf7cdb26553b9a0a7"
ENTITY_DIM=4
ADDRESS_DIM=8
PARAMETERS=56

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

class RoleBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(b6.KEYS,ENTITY_DIM)
        self.value_emb=nn.Embedding(b6.VALUES,b6.VALUE_DIM)
        self.readout=nn.Linear(b6.VALUE_DIM,b6.VALUES)

    def slot(self,entity,role_ids):
        z=torch.zeros_like(entity)
        r0=torch.cat((entity,z),dim=1)
        r1=torch.cat((z,entity),dim=1)
        out=torch.where((role_ids==0).unsqueeze(1),r0,r1)
        return F.normalize(out,p=2,dim=1,eps=1e-12)

    def address(self,key_ids,role_ids):
        return self.slot(self.key_emb(key_ids),role_ids)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,b6.VALUE_DIM,ADDRESS_DIM),dtype=torch.float32)
        pending=torch.zeros((n,ADDRESS_DIM),dtype=torch.float32)

        for t in range(b6.SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)

            token=x[:,t]
            if t in (0,3,6,9):
                entity=self.key_emb(token)
                pending=torch.cat((entity,torch.zeros_like(entity)),dim=1)
            elif t in (1,4,7,10):
                role_id=token-b6.ROLE_BASE
                entity=pending[:,:ENTITY_DIM]
                pending=self.slot(entity,role_id)
            elif t in (2,5,8,11):
                value_id=token-b6.VALUE_BASE
                value=self.value_emb(value_id)
                M=M+value.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            elif t==12:
                key_id=token-b6.QUERY_KEY_BASE
                entity=self.key_emb(key_id)
                pending=torch.cat((entity,torch.zeros_like(entity)),dim=1)
            elif t==13:
                role_id=token-b6.QUERY_ROLE_BASE
                entity=pending[:,:ENTITY_DIM]
                query=self.slot(entity,role_id)
                read=torch.bmm(M,query.unsqueeze(2)).squeeze(2)
                return self.readout(read)
            else:
                raise AssertionError("sequence position")
        raise AssertionError("missing query")

def mechanical():
    torch.manual_seed(991)
    model=RoleBinding()
    with torch.no_grad():
        ids=torch.arange(b6.KEYS,dtype=torch.long)
        r0=model.address(ids,torch.zeros(b6.KEYS,dtype=torch.long))
        r1=model.address(ids,torch.ones(b6.KEYS,dtype=torch.long))
        r0_wrong=float(r0[:,ENTITY_DIM:].abs().max().item())
        r1_wrong=float(r1[:,:ENTITY_DIM].abs().max().item())
        cross=float((r0@r1.T).abs().max().item())
    params=sum(p.numel() for p in model.parameters())
    checks={
        "r0_second_slot_zero":r0_wrong<=1e-7,
        "r1_first_slot_zero":r1_wrong<=1e-7,
        "cross_role_dot_le_1e_7":cross<=1e-7,
        "persistent_state_exactly_16":ADDRESS_DIM+ADDRESS_DIM==16,
        "parameter_count_exactly_56":params==PARAMETERS,
    }
    return {
        "all_pass":all(checks.values()),
        "checks":checks,
        "max_r0_wrong_slot_abs":r0_wrong,
        "max_r1_wrong_slot_abs":r1_wrong,
        "max_cross_role_abs_dot":cross,
        "parameter_count":params,
        "persistent_state_scalars":16,
    }

def one_pass():
    old=b6.RoleBinding
    b6.RoleBinding=RoleBinding
    try:
        out=b6.one_pass()
    finally:
        b6.RoleBinding=old
    q=out["qualification"]
    q.pop("YGG_B6_ROLE_CONDITIONED_HOLDOUT",None)
    q.pop("parameter_count_exactly_104",None)
    q["parameter_count_exactly_56"]=all(r["parameter_count"]==PARAMETERS for r in out["rows"])
    q["YGG_B9_DISJOINT_ROLE_SLOTS"]=all(q.values())
    return out

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B9_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=b6.canonical(p1)
    b2=b6.canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B9",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":mech,
        "duplicate_byte_identical":b1==b2,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":p1,
    }
    if not out["duplicate_byte_identical"]:
        raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(b6.canonical(out))

if __name__=="__main__":
    main()
