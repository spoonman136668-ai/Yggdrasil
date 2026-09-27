#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b51_pre_replay_identity_sweep_v1 as b51

PREREG="d2e947691047ec3f64d02abbce0bb30c77084608"
PARENT_RUN="36309193996"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
DOSES=[1,2,3]
TH=.90
b50=b51.b50
b49=b50.b49
b48=b49.b48
b47=b48.b47
b46=b47.b46
b27=b47.b27
b29=b47.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one():
    rows=[]
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B52 empty q")
            xs=x[mask]; Ms=M[mask]
            target=xs[:,4*q+3]-b27.VALUE_BASE
            dose_rows=[]
            current=Ms
            for dose in DOSES:
                with torch.no_grad(): current=b46.refresh(model,current,xs,q)
                with torch.no_grad(): qp=b46.query_logits(model,current,xs,q).argmax(1)
                qacc=float((qp==target).float().mean())
                opp=new=rep=0
                bindings=[]
                for j in range(7):
                    jt=xs[:,4*j+3]-b27.VALUE_BASE
                    with torch.no_grad():
                        bp=b46.query_logits(model,Ms,xs,j).argmax(1)
                        pp=b46.query_logits(model,current,xs,j).argmax(1)
                    bc=(bp==jt); pc=(pp==jt)
                    ne=int((bc & (~pc)).sum()); rp=int(((~bc)&pc).sum())
                    if j!=q:
                        opp+=int(bc.sum()); new+=ne; rep+=rp
                    bindings.append({
                        "binding":j,"is_target":j==q,
                        "baseline_correct_count":int(bc.sum()),"post_correct_count":int(pc.sum()),
                        "new_error_count":ne,"repair_count":rp
                    })
                dose_rows.append({
                    "dose":dose,"target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "collateral_baseline_correct_opportunities":opp,
                    "collateral_new_error_count":new,
                    "collateral_repair_count":rep,
                    "bindings":bindings
                })
            strata.append({"query_position":q,"count":count,"doses":dose_rows})
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    totals={d:sum(next(x for x in s["doses"] if x["dose"]==d)["collateral_new_error_count"] for s in flat) for d in DOSES}
    universal={d:all(next(x for x in s["doses"] if x["dose"]==d)["target_capable"] for s in flat) for d in DOSES}
    if not universal[1]: cat="ANCHOR_NOT_REPRODUCED"
    elif not (universal[2] and universal[3]): cat="TARGET_RESCUE_LOST_AT_HIGHER_DOSE"
    elif totals[1]<totals[2]<=totals[3]: cat="SINGLE_REFRESH_MINIMAL"
    elif any(totals[d]<totals[1] for d in (2,3)): cat="REPEATED_REFRESH_REDUCES_COLLATERAL"
    else: cat="DOSE_NONMONOTONIC"
    return {"rows":rows,"aggregate_collateral_new_errors":totals,"universal_target":universal,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "doses_exact":all([x["dose"] for x in s["doses"]]==DOSES for r in a["rows"] for s in r["strata"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "d1_anchor_exact":a["universal_target"][1],
        "six_collateral_bindings_scored":all(sum(not x["is_target"] for x in d["bindings"])==6 for r in a["rows"] for s in r["strata"] for d in s["doses"]),
        "exact_75_dose_arms":sum(len(s["doses"]) for r in a["rows"] for s in r["strata"])==75,
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"SINGLE_REFRESH_MINIMAL","REPEATED_REFRESH_REDUCES_COLLATERAL","DOSE_NONMONOTONIC","TARGET_RESCUE_LOST_AT_HIGHER_DOSE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B52","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B52_TARGET_REFRESH_DOSE":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
