#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b27_read_update_read_v1 as b27
import ygg_b29_read1_interference_attribution_v1 as b29
import ygg_b30_read1_write_position_attribution_v1 as b30
PREREG="74abd1a756b03585081dec66cb70209c11b35986"
PARENT_RUN="36229736902"
THRESHOLD=0.90
POSITIONS=tuple(range(7))
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def permuted_data(seed):
    data=list(b27.evaluation_data(seed,b27.EVAL_N))
    x=data[0].clone(); q1=data[3]
    for row in range(x.shape[0]):
        pos=int(q1[row]); others=[i for i in POSITIONS if i!=pos]
        shift=1+((seed+pos)%len(others))
        rotated=others[shift:]+others[:shift]
        src=x[row].clone()
        for dst,src_i in zip(others,rotated):
            x[row,4*dst:4*dst+4]=src[4*src_i:4*src_i+4]
    data[0]=x
    return tuple(data)
def rows_for(seed,permuted):
    model=b29.train_model(seed,True)
    data=permuted_data(seed) if permuted else b27.evaluation_data(seed,b27.EVAL_N)
    x,y1,_,q1,*_=data
    model.eval()
    with torch.no_grad(): pred=b29.immediate_read1_logits(model,x).argmax(dim=1)
    rows=[]
    for pos in POSITIONS:
        mask=q1==pos; count=int(mask.sum())
        rows.append({"position":pos,"count":count,"accuracy":float((pred[mask]==y1[mask]).float().mean())})
    return rows
def one_pass():
    out=[]
    for seed in b27.SEEDS:
        orig=rows_for(seed,False); perm=rows_for(seed,True)
        out.append({"seed":seed,"original":orig,"permuted":perm})
    changed=[]; large=[]
    for r in out:
        for pos in POSITIONS:
            a=next(x["accuracy"] for x in r["original"] if x["position"]==pos)
            b=next(x["accuracy"] for x in r["permuted"] if x["position"]==pos)
            if (a>=THRESHOLD)!=(b>=THRESHOLD): changed.append([r["seed"],pos])
            if abs(a-b)>=0.10: large.append([r["seed"],pos,abs(a-b)])
    if changed: cat="IDENTITY_SENSITIVE"
    elif large: cat="SUBTHRESHOLD_IDENTITY_EFFECT"
    else: cat="AGE_DOMINANT"
    return {"rows":out,"capability_changes":changed,"large_accuracy_changes":large,"classification":cat}
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    mech=b27.mechanical()
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    validity={"mechanical_gate":bool(mech["all_pass"]),"threshold_inherited_exact":THRESHOLD==0.90,
      "duplicate_complete_execution_byte_identical":b1==b2,"positions_exact":list(POSITIONS)==list(range(7)),
      "state_exactly_32":b27.PERSISTENT_SCALARS==32,
      "parameter_count_exactly_120":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120}
    cat=first["classification"]; allowed={"AGE_DOMINANT","IDENTITY_SENSITIVE","SUBTHRESHOLD_IDENTITY_EFFECT","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B31","prereg":PREREG,"parent_run":PARENT_RUN,"inherited_threshold":THRESHOLD,
      "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
      "qualification":{"YGG_B31_READ1_AGE_VS_WRITE_IDENTITY":bool(all(validity.values()) and cat in allowed),"classification":cat},"analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
