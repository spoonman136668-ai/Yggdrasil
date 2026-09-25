#!/usr/bin/env python3
import hashlib,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))

import torch
from torch import nn
from torch.nn import functional as F
import ygg_b6_role_conditioned_holdout_v1 as b6
import ygg_b7_multiplicative_role_binding_v1 as b7

PREREG="f2eeaf2df9ea5cc7389002733b457b82242506a7"
PARENT_CLOSURE="fcdca2a0ea0604fb9758a795c3bd71d56791cf06"
VALUE_DIM=2
ADDRESS_DIM=8
PERSISTENT_SCALARS=24
PARAMETERS=104
MASK=b7.MASK.clone()

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

class RoleBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(b6.KEYS,ADDRESS_DIM)
        self.value_emb=nn.Embedding(b6.VALUES,VALUE_DIM)
        self.readout=nn.Linear(VALUE_DIM,b6.VALUES)

    def bind(self,v,r):
        return F.normalize(v*MASK[r],p=2,dim=1,eps=1e-12)

    def address(self,k,r):
        return self.bind(self.key_emb(k),r)

    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,VALUE_DIM,ADDRESS_DIM),dtype=torch.float32)
        pending=torch.zeros((n,ADDRESS_DIM),dtype=torch.float32)
        for t in range(b6.SEQ):
            if reset_each:
                M=torch.zeros_like(M)
                pending=torch.zeros_like(pending)
            token=x[:,t]
            if t in (0,3,6,9):
                if torch.any((token<0)|(token>=b6.KEYS)):
                    raise AssertionError("key token range")
                pending=self.key_emb(token)
            elif t in (1,4,7,10):
                role_id=token-b6.ROLE_BASE
                if torch.any((role_id<0)|(role_id>=b6.ROLES)):
                    raise AssertionError("role token range")
                pending=self.bind(pending,role_id)
            elif t in (2,5,8,11):
                value_id=token-b6.VALUE_BASE
                if torch.any((value_id<0)|(value_id>=b6.VALUES)):
                    raise AssertionError("value token range")
                value=self.value_emb(value_id)
                M=M+value.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            elif t==12:
                key_id=token-b6.QUERY_KEY_BASE
                if torch.any((key_id<0)|(key_id>=b6.KEYS)):
                    raise AssertionError("query key range")
                pending=self.key_emb(key_id)
            elif t==13:
                role_id=token-b6.QUERY_ROLE_BASE
                if torch.any((role_id<0)|(role_id>=b6.ROLES)):
                    raise AssertionError("query role range")
                query=self.bind(pending,role_id)
                read=torch.bmm(M,query.unsqueeze(2)).squeeze(2)
                return self.readout(read)
            else:
                raise AssertionError("sequence position")
        raise AssertionError("missing query")

def mechanical():
    torch.manual_seed(991)
    model=RoleBinding()
    params=sum(p.numel() for p in model.parameters())
    with torch.no_grad():
        ids=torch.arange(b6.KEYS,dtype=torch.long)
        addr=[]
        for k in range(b6.KEYS):
            for r in range(b6.ROLES):
                addr.append(model.address(torch.tensor([k]),torch.tensor([r])).squeeze(0))
        addresses=torch.stack(addr,dim=0)
        gram=addresses@addresses.T
        offdiag=gram-torch.eye(b6.KEYS*b6.ROLES,dtype=gram.dtype)
        max_abs_offdiag=float(offdiag.abs().max().item())
    expected_mask=torch.tensor(
        [[1,1,1,1,1,1,1,1],[1,-1,1,-1,1,-1,1,-1]],
        dtype=torch.float32,
    )
    checks={
        "role_masks_exact_b7":torch.equal(MASK,expected_mask),
        "value_dimension_exactly_2":model.value_emb.weight.shape==(b6.VALUES,VALUE_DIM),
        "memory_shape_2x8":VALUE_DIM==2 and ADDRESS_DIM==8,
        "persistent_state_exactly_24":VALUE_DIM*ADDRESS_DIM+ADDRESS_DIM==PERSISTENT_SCALARS,
        "parameter_count_exactly_104":params==PARAMETERS,
        "role_masks_nonlearned":not MASK.requires_grad,
    }
    return {
        "all_pass":all(checks.values()),
        "checks":checks,
        "max_abs_offdiag_address_cosine":max_abs_offdiag,
        "parameter_count":params,
        "persistent_state_scalars":PERSISTENT_SCALARS,
    }

def one_pass():
    old_model=b6.RoleBinding
    old_state=b6.PERSISTENT_SCALARS
    b6.RoleBinding=RoleBinding
    b6.PERSISTENT_SCALARS=PERSISTENT_SCALARS
    try:
        out=b6.one_pass()
    finally:
        b6.RoleBinding=old_model
        b6.PERSISTENT_SCALARS=old_state
    q=out["qualification"]
    q.pop("YGG_B6_ROLE_CONDITIONED_HOLDOUT",None)
    q.pop("state_exactly_16",None)
    q["state_exactly_24"]=all(r["persistent_state_scalars"]==PERSISTENT_SCALARS for r in out["rows"])
    q["parameter_count_exactly_104"]=all(r["parameter_count"]==PARAMETERS for r in out["rows"])
    q["YGG_B12_MULTIPLICATIVE_ROLE_VALUE2D"]=all(q.values())
    for row in out["rows"]:
        row["value_dimension"]=VALUE_DIM
    return out

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B12_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=b6.canonical(p1)
    b2=b6.canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B12",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "role_masks":MASK.tolist(),
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
