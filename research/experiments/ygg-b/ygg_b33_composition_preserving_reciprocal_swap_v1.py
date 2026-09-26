#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b31_read1_age_vs_write_identity_v1 as b31
PREREG="df6eec2da9af07e190cf5c1a550c56380b48163c"; PARENT_RUN="36248716226"
SEED=222; POS=4; THRESHOLD=0.90; SWAPS=((0,6),(5,3),(6,5))
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def acc(model,x,y,q):
 model.eval()
 with torch.no_grad(): pred=b31.b29.immediate_read1_logits(model,x).argmax(dim=1)
 m=q==POS; return float((pred[m]==y[m]).float().mean()),int(m.sum())
def block_multiset(x,row):
 return sorted(tuple(float(v) for v in x[row,4*p:4*p+4].detach().cpu().tolist()) for p in range(7))
def one_pass():
 data=list(b31.b27.evaluation_data(SEED,b31.b27.EVAL_N)); x,y,_,q,*_=data; full=b31.permuted_data(SEED)[0]; model=b31.b29.train_model(SEED,True)
 oa,n=acc(model,x,y,q); fa,_=acc(model,full,y,q); arms=[]
 for a,b in SWAPS:
  z=x.clone(); za=x[:,4*a:4*a+4].clone(); zb=x[:,4*b:4*b+4].clone(); z[:,4*a:4*a+4]=zb; z[:,4*b:4*b+4]=za
  preserved=all(block_multiset(x,r)==block_multiset(z,r) for r in range(x.shape[0]))
  aa,_=acc(model,z,y,q); arms.append({"swap":[a,b],"accuracy":aa,"capable":aa>=THRESHOLD,"binding_multiset_preserved":preserved})
 capable=sum(1 for a in arms if a["capable"])
 if fa<THRESHOLD: cat="FULL_EFFECT_NOT_REPRODUCED"
 elif capable==3: cat="ORDER_SUFFICIENT_ALL"
 elif capable in (1,2): cat="ORDER_SUFFICIENT_PARTIAL"
 elif capable==0: cat="COMPOSITION_EFFECT_REQUIRED"
 else: cat="OTHER_VALID_PATTERN"
 return {"original_accuracy":oa,"full_permutation_accuracy":fa,"count":n,"arms":arms,"classification":cat}
def main():
 if len(sys.argv)!=2: raise SystemExit("usage: OUT")
 mech=b31.b27.mechanical(); first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
 validity={"mechanical_gate":bool(mech["all_pass"]),"seed_exact":SEED==222,"query_position_exact":POS==4,"threshold_exact":THRESHOLD==0.90,"state_exactly_32":b31.b27.PERSISTENT_SCALARS==32,"parameter_count_exactly_120":sum(p.numel() for p in b31.b27.ReadUpdateRead().parameters())==120,"original_endpoint_reproduced":abs(first["original_accuracy"]-0.8322368264198303)<1e-12,"full_endpoint_reproduced":abs(first["full_permutation_accuracy"]-0.90625)<1e-12,"three_fixed_reciprocal_arms":len(first["arms"])==3,"binding_multiset_preserved":all(a["binding_multiset_preserved"] for a in first["arms"]),"duplicate_complete_execution_byte_identical":b1==b2}
 cat=first["classification"]; allowed={"ORDER_SUFFICIENT_ALL","ORDER_SUFFICIENT_PARTIAL","COMPOSITION_EFFECT_REQUIRED","FULL_EFFECT_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
 out={"schema":1,"experiment":"YGG-B33","prereg":PREREG,"parent_run":PARENT_RUN,"duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),"qualification":{"YGG_B33_COMPOSITION_PRESERVING_RECIPROCAL_SWAP":all(validity.values()) and cat in allowed,"classification":cat},"analysis":first}
 Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
