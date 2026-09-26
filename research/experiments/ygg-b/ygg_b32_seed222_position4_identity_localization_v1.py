#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b31_read1_age_vs_write_identity_v1 as b31
PREREG="40e43269fee178eee72a23857bc6e47ea2d6aa37"; PARENT_RUN="36236451117"; SEED=222; POS=4; THRESHOLD=0.90
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def accuracy(x,y,q,model):
 model.eval()
 with torch.no_grad(): pred=b31.b29.immediate_read1_logits(model,x).argmax(dim=1)
 m=q==POS; return float((pred[m]==y[m]).float().mean()),int(m.sum())
def one_pass():
 data=list(b31.b27.evaluation_data(SEED,b31.b27.EVAL_N)); x,y,_,q,*_=data; full=b31.permuted_data(SEED)[0]; model=b31.b29.train_model(SEED,True)
 oa,n=accuracy(x,y,q,model); fa,_=accuracy(full,y,q,model); arms=[]
 for dst in [0,1,2,3,5,6]:
  z=x.clone(); z[:,4*dst:4*dst+4]=full[:,4*dst:4*dst+4]; a,_=accuracy(z,y,q,model); arms.append({"destination_position":dst,"accuracy":a,"capable":a>=THRESHOLD})
 crossings=[a["destination_position"] for a in arms if a["capable"]]
 if fa<THRESHOLD: cat="FULL_EFFECT_NOT_REPRODUCED"
 elif len(crossings)==1: cat="SINGLE_POSITION_SUFFICIENT"
 elif len(crossings)>1: cat="MULTIPLE_POSITIONS_SUFFICIENT"
 elif not crossings: cat="COMBINED_CONTEXT_REQUIRED"
 else: cat="OTHER_VALID_PATTERN"
 return {"original_accuracy":oa,"full_permutation_accuracy":fa,"count":n,"arms":arms,"crossing_positions":crossings,"classification":cat}
def main():
 if len(sys.argv)!=2: raise SystemExit("usage: OUT")
 mech=b31.b27.mechanical(); first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
 validity={"mechanical_gate":bool(mech["all_pass"]),"seed_exact":SEED==222,"query_position_exact":POS==4,"threshold_exact":THRESHOLD==0.90,"state_exactly_32":b31.b27.PERSISTENT_SCALARS==32,"parameter_count_exactly_120":sum(p.numel() for p in b31.b27.ReadUpdateRead().parameters())==120,"original_endpoint_reproduced":abs(first["original_accuracy"]-0.8322368264198303)<1e-12,"full_endpoint_reproduced":abs(first["full_permutation_accuracy"]-0.90625)<1e-12,"six_fixed_arms":len(first["arms"])==6,"duplicate_complete_execution_byte_identical":b1==b2}
 cat=first["classification"]; allowed={"SINGLE_POSITION_SUFFICIENT","MULTIPLE_POSITIONS_SUFFICIENT","COMBINED_CONTEXT_REQUIRED","FULL_EFFECT_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
 out={"schema":1,"experiment":"YGG-B32","prereg":PREREG,"parent_run":PARENT_RUN,"duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),"qualification":{"YGG_B32_SEED222_POSITION4_IDENTITY_LOCALIZATION":all(validity.values()) and cat in allowed,"classification":cat},"analysis":first}
 Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
