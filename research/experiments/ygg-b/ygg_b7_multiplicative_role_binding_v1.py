#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b6_role_conditioned_holdout_v1 as b6

PREREG="246cdc87bdced07e910b7072e1ac7a5a42c794a3"
PARENT_CLOSURE="ec43ed86a3adc889a0ebec36dccccf97f1827fe4"
MASK=torch.tensor([[1,1,1,1,1,1,1,1],[1,-1,1,-1,1,-1,1,-1]],dtype=torch.float32)

class RoleBinding(nn.Module):
    def __init__(self):
        super().__init__()
        self.key_emb=nn.Embedding(8,8)
        self.value_emb=nn.Embedding(8,1)
        self.readout=nn.Linear(1,8)
    def bind(self,v,r):
        return F.normalize(v*MASK[r],p=2,dim=1,eps=1e-12)
    def address(self,k,r):
        return self.bind(self.key_emb(k),r)
    def forward(self,x,reset_each=False):
        n=x.shape[0]
        M=torch.zeros((n,1,8),dtype=torch.float32)
        pending=torch.zeros((n,8),dtype=torch.float32)
        for t in range(14):
            if reset_each:
                M.zero_(); pending.zero_()
            token=x[:,t]
            if t in (0,3,6,9):
                pending=self.key_emb(token)
            elif t in (1,4,7,10):
                pending=self.bind(pending,token-b6.ROLE_BASE)
            elif t in (2,5,8,11):
                v=self.value_emb(token-b6.VALUE_BASE)
                M=M+v.unsqueeze(2)*pending.unsqueeze(1)
                pending=torch.zeros_like(pending)
            elif t==12:
                pending=self.key_emb(token-b6.QUERY_KEY_BASE)
            else:
                q=self.bind(pending,token-b6.QUERY_ROLE_BASE)
                return self.readout(torch.bmm(M,q.unsqueeze(2)).squeeze(2))
        raise AssertionError("missing query")

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
    q["parameter_count_exactly_88"]=all(r["parameter_count"]==88 for r in out["rows"])
    q["YGG_B7_MULTIPLICATIVE_ROLE_BINDING"]=all(q.values())
    return out

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    p1=one_pass(); p2=one_pass()
    b1=b6.canonical(p1); b2=b6.canonical(p2)
    out={"schema":1,"experiment":"YGG-B7","prereg":PREREG,"parent_closure":PARENT_CLOSURE,
         "role_masks":MASK.tolist(),"duplicate_byte_identical":b1==b2,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"primary":p1}
    if not out["duplicate_byte_identical"]: raise SystemExit("duplicate evidence mismatch")
    Path(sys.argv[1]).write_bytes(b6.canonical(out))

if __name__=="__main__": main()
