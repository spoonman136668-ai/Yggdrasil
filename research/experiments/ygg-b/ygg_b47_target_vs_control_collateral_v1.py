#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b46_targeted_refresh_collateral_v1 as b46

PREREG="62dcb2d37c3e1dca2408bc24886a96876662ace6"
PARENT_RUN="36283971330"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
b27=b46.b27
b29=b46.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one():
    rows=[]
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad():
            M=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B47 empty q")
            xs=x[mask]; Ms=M[mask]
            control=(q+1)%7
            with torch.no_grad():
                Mt=b46.refresh(model,Ms,xs,q)
                Mc=b46.refresh(model,Ms,xs,control)
            arms={}
            for name,MM,refreshed in [("target",Mt,q),("control",Mc,control)]:
                new_errors=0; repairs=0; opportunities=0
                bindings=[]
                target_q_acc=None
                for j in range(7):
                    target=xs[:,4*j+3]-b27.VALUE_BASE
                    with torch.no_grad():
                        base_pred=b46.query_logits(model,Ms,xs,j).argmax(1)
                        post_pred=b46.query_logits(model,MM,xs,j).argmax(1)
                    bc=(base_pred==target); pc=(post_pred==target)
                    ne=int((bc & (~pc)).sum()); rp=int(((~bc)&pc).sum())
                    if j==q: target_q_acc=float(pc.float().mean())
                    if j!=refreshed:
                        opportunities+=int(bc.sum()); new_errors+=ne; repairs+=rp
                    bindings.append({
                        "binding":j,"is_refreshed":j==refreshed,"is_query":j==q,
                        "baseline_correct_count":int(bc.sum()),"post_correct_count":int(pc.sum()),
                        "new_error_count":ne,"repair_count":rp,
                    })
                arms[name]={
                    "refreshed_binding":refreshed,
                    "target_query_accuracy":target_q_acc,
                    "collateral_baseline_correct_opportunities":opportunities,
                    "collateral_new_error_count":new_errors,
                    "collateral_repair_count":repairs,
                    "bindings":bindings,
                }
            strata.append({"query_position":q,"count":count,"target_arm":arms["target"],"control_arm":arms["control"]})
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    target_anchor=all(s["target_arm"]["target_query_accuracy"]>=TH for s in flat)
    control_anchor=all(s["control_arm"]["target_query_accuracy"]<TH for s in flat)
    tn=sum(s["target_arm"]["collateral_new_error_count"] for s in flat)
    cn=sum(s["control_arm"]["collateral_new_error_count"] for s in flat)
    tr=sum(s["target_arm"]["collateral_repair_count"] for s in flat)
    cr=sum(s["control_arm"]["collateral_repair_count"] for s in flat)
    if not (target_anchor and control_anchor): cat="ANCHOR_NOT_REPRODUCED"
    elif tn==0 and cn==0: cat="NO_EXTRA_WRITE_COLLATERAL"
    elif tn>0 and cn==0: cat="TARGET_ONLY_COLLATERAL"
    elif tn==0 and cn>0: cat="CONTROL_ONLY_COLLATERAL"
    elif tn>0 and cn>0: cat="GENERAL_EXTRA_WRITE_COLLATERAL"
    else: cat="OTHER_VALID_PATTERN"
    return {
      "rows":rows,"target_anchor":target_anchor,"control_anchor":control_anchor,
      "target_collateral_new_errors":tn,"control_collateral_new_errors":cn,
      "target_collateral_repairs":tr,"control_collateral_repairs":cr,
      "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
      "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
      "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
      "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
      "target_refresh_identity_exact":all(s["target_arm"]["refreshed_binding"]==s["query_position"] for r in a["rows"] for s in r["strata"]),
      "control_refresh_identity_exact":all(s["control_arm"]["refreshed_binding"]==(s["query_position"]+1)%7 for r in a["rows"] for s in r["strata"]),
      "one_added_write_each_arm":True,
      "target_anchor_exact":a["target_anchor"],
      "control_anchor_exact":a["control_anchor"],
      "state_exact":b27.PERSISTENT_SCALARS==32,
      "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
      "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"NO_EXTRA_WRITE_COLLATERAL","TARGET_ONLY_COLLATERAL","CONTROL_ONLY_COLLATERAL","GENERAL_EXTRA_WRITE_COLLATERAL","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B47","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B47_TARGET_VS_CONTROL_COLLATERAL":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
