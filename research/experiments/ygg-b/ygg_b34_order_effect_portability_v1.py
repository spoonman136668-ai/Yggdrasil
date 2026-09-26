#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b31_read1_age_vs_write_identity_v1 as b31
PREREG="77c7d032e36d9d1b068751e70452afc46f3a8447"; PARENT_RUN="36253384940"; SEEDS=[111,222,333,444,555]; POS=4; TH=.90
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def acc(m,x,y,q):
 m.eval()
 with torch.no_grad(): p=b31.b29.immediate_read1_logits(m,x).argmax(1)
 z=q==POS; return float((p[z]==y[z]).float().mean())
def ms(x,r): return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))
def one():
 rows=[]
 for seed in SEEDS:
  data=list(b31.b27.evaluation_data(seed,b31.b27.EVAL_N)); x,y,_,q,*_=data; m=b31.b29.train_model(seed,True); z=x.clone(); a=x[:,20:24].clone(); c=x[:,12:16].clone(); z[:,20:24]=c; z[:,12:16]=a
  rows.append({"seed":seed,"original":acc(m,x,y,q),"swap_5_3":acc(m,z,y,q),"improved":acc(m,z,y,q)>acc(m,x,y,q),"multiset_preserved":all(ms(x,r)==ms(z,r) for r in range(x.shape[0]))})
 n=sum(r["improved"] for r in rows); before=sum(r["original"]>=TH for r in rows); after=sum(r["swap_5_3"]>=TH for r in rows)
 if n==5 and after>=before: cat="PORTABLE_ORDER_EFFECT"
 elif 1<n<5: cat="PARTIAL_PORTABILITY"
 elif n==1 and next(r for r in rows if r["seed"]==222)["improved"]: cat="SEED222_SPECIFIC"
 else: cat="MIXED_ORDER_EFFECT"
 return {"rows":rows,"classification":cat,"capable_before":before,"capable_after":after}
def main():
 if len(sys.argv)!=2: raise SystemExit("usage: OUT")
 a=one(); b=one(); ba=canon(a); r222=next(r for r in a["rows"] if r["seed"]==222)
 v={"seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,"query_exact":POS==4,"threshold_exact":TH==.90,"state_exact":b31.b27.PERSISTENT_SCALARS==32,"params_exact":sum(p.numel() for p in b31.b27.ReadUpdateRead().parameters())==120,"seed222_original_reproduced":abs(r222["original"]-0.8322368264198303)<1e-12,"seed222_swap_reproduced":abs(r222["swap_5_3"]-0.9161184430122375)<1e-12,"multiset_preserved":all(r["multiset_preserved"] for r in a["rows"]),"duplicate_byte_identical":ba==canon(b)}
 out={"schema":1,"experiment":"YGG-B34","prereg":PREREG,"parent_run":PARENT_RUN,"duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":v,"valid":all(v.values()),"qualification":{"YGG_B34_ORDER_EFFECT_PORTABILITY":all(v.values()),"classification":a["classification"]},"analysis":a}; Path(sys.argv[1]).write_bytes(canon(out))
if __name__=="__main__": main()
