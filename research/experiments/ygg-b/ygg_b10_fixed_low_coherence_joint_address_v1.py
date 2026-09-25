#!/usr/bin/env python3
import hashlib,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))

import torch
from torch import nn
from torch.nn import functional as F
import ygg_b6_role_conditioned_holdout_v1 as b6

PREREG="c95906c9d26b58272a3a195e5cbbe2c6eaa3d611"
PARENT_CLOSURE="540d004b8a99b3b909f074e143fd699f3c9a367d"
PARAMETERS=24
ADDRESS_DIM=8
CODEBOOK=torch.tensor([
 [1,1,1,1,1,1,1,1],
 [1,1,1,1,1,1,-1,-1],
 [1,1,1,1,1,-1,1,-1],
 [1,1,1,1,1,-1,-1,1],
 [1,1,1,1,-1,1,1,-1],
 [1,1,1,1,-1,1,-1,1],
 [1,1,1,1,-1,-1,1,1],
 [1,1,1,1,-1,-1,-1,-1],
 [1,1,1,-1,1,1,1,-1],
 [1,1,1,-1,1,1,-1,1],
 [1,1,1,-1,1,-1,1,1],
 [1,1,1,-1,1,-1,-1,-1],
 [1,1,1,-1,-1,1,1,1],
 [1,1,1,-1,-1,1,-1,-1],
 [1,1,1,-1,-1,-1,1,-1],
 [1,1,1,-1,-1,-1,-1,1],
],dtype=torch.float32)/(8.0**0.5)

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

class RoleBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("codebook",CODEBOOK.clone())
        self.value_emb=nn.Embedding(b6.VALUES,b6.VALUE_DIM)
        self.readout=nn.Linear(b6.VALUE_DIM,b6.VALUES)

    def address(self,key_ids,role_ids):
        idx=2*key_ids+role_ids
        return self.codebook[idx]

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
                if torch.any((token<0)|(token>=b6.KEYS)):
                    raise AssertionError("key token range")
                pending=F.one_hot(token,num_classes=b6.KEYS).to(torch.float32)
            elif t in (1,4,7,10):
                role_id=token-b6.ROLE_BASE
                if torch.any((role_id<0)|(role_id>=b6.ROLES)):
                    raise AssertionError("role token range")
                key_id=pending.argmax(dim=1)
                pending=self.address(key_id,role_id)
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
                pending=F.one_hot(key_id,num_classes=b6.KEYS).to(torch.float32)
            elif t==13:
                role_id=token-b6.QUERY_ROLE_BASE
                if torch.any((role_id<0)|(role_id>=b6.ROLES)):
                    raise AssertionError("query role range")
                key_id=pending.argmax(dim=1)
                query=self.address(key_id,role_id)
                read=torch.bmm(M,query.unsqueeze(2)).squeeze(2)
                return self.readout(read)
            else:
                raise AssertionError("sequence position")
        raise AssertionError("missing query")

def mechanical():
    model=RoleBinding()
    cb=model.codebook.detach()
    gram=cb@cb.T
    off=gram-torch.eye(16,dtype=gram.dtype)
    max_off=float(off.abs().max().item())
    norms=torch.linalg.vector_norm(cb,dim=1)
    unique=len({tuple(float(v) for v in row.tolist()) for row in cb})==16
    antipodal=False
    for i in range(16):
        for j in range(i+1,16):
            if torch.allclose(cb[i],-cb[j],atol=1e-7,rtol=0.0):
                antipodal=True
    params=sum(p.numel() for p in model.parameters())
    checks={
        "sixteen_unique_addresses":unique,
        "unit_norm_le_1e_7":float((norms-1.0).abs().max().item())<=1e-7,
        "max_abs_offdiag_cosine_le_05000001":max_off<=0.5000001,
        "no_antipodal_pair":not antipodal,
        "persistent_state_exactly_16":ADDRESS_DIM+ADDRESS_DIM==16,
        "parameter_count_exactly_24":params==PARAMETERS,
        "codebook_requires_grad_false":not model.codebook.requires_grad,
    }
    return {
        "all_pass":all(checks.values()),
        "checks":checks,
        "max_abs_offdiag_address_cosine":max_off,
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
    q["parameter_count_exactly_24"]=all(r["parameter_count"]==PARAMETERS for r in out["rows"])
    q["YGG_B10_FIXED_LOW_COHERENCE_JOINT_ADDRESS"]=all(q.values())
    return out

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_B10_MECHANICAL_GATE_FAILED")
    p1=one_pass()
    p2=one_pass()
    b1=b6.canonical(p1)
    b2=b6.canonical(p2)
    out={
        "schema":1,
        "experiment":"YGG-B10",
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
