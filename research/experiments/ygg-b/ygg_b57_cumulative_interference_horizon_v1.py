#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b56_repeated_interference_repair_cycles_v1 as b56

PREREG="6d66eb80ec57e7b1f58d7ff2aca2c3978115bc60"
PARENT_RUN="36327037721"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90

b55=b56.b55
b54=b55.b54
b53=b54.b53
b52=b53.b52
b51=b52.b51
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
    depth_loss_counts={d:0 for d in range(1,7)}
    initial_anchor=True
    any_loss=False
    all_lost_recovered=True
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B57 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): cur=b46.refresh(model,base,xs,q)
            depth0,_=b56.score(model,base,cur,xs,q)
            initial_anchor=initial_anchor and depth0["target_capable"]
            order=[(q+d)%7 for d in range(1,7)]
            if sorted(order)!=[r for r in range(7) if r!=q]:
                raise AssertionError("B57 competitor order invalid")
            depths=[]
            first_loss=None
            for depth,r in enumerate(order,1):
                with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
                scored,_=b56.score(model,base,cur,xs,q)
                if not scored["target_capable"]:
                    depth_loss_counts[depth]+=1
                    any_loss=True
                    if first_loss is None: first_loss=depth
                depths.append({
                    "depth":depth,"competing_identity":r,
                    "target_accuracy":scored["target_accuracy"],
                    "target_capable":scored["target_capable"],
                    "collateral_baseline_correct_opportunities":scored["collateral_baseline_correct_opportunities"],
                    "collateral_new_errors":scored["collateral_new_errors"],
                    "collateral_repairs":scored["collateral_repairs"],
                })
            with torch.no_grad(): repaired=b46.refresh(model,cur,xs,q)
            post,_=b56.score(model,base,repaired,xs,q)
            if first_loss is not None and not post["target_capable"]:
                all_lost_recovered=False
            strata.append({
                "query_position":q,"count":count,
                "depth0":depth0,
                "competitor_order":order,
                "depths":depths,
                "first_loss_depth":first_loss,
                "post_depth6_repair":post,
            })
        rows.append({"seed":seed,"strata":strata})
    if not initial_anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif not any_loss: cat="NO_FAILURE_THROUGH_SIX_DISTINCT_WRITES"
    elif all_lost_recovered: cat="BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY"
    else: cat="INTERFERENCE_HORIZON_WITH_PARTIAL_RECOVERY"
    return {
        "rows":rows,
        "depth_loss_counts":depth_loss_counts,
        "initial_anchor":initial_anchor,
        "any_loss":any_loss,
        "all_lost_recovered":all_lost_recovered,
        "classification":cat,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "twenty_five_strata_exact":sum(len(r["strata"]) for r in a["rows"])==25,
        "six_distinct_competitors_each":all(
            len(s["competitor_order"])==6 and
            len(set(s["competitor_order"]))==6 and
            sorted(s["competitor_order"])==[r for r in range(7) if r!=s["query_position"]]
            for row in a["rows"] for s in row["strata"]),
        "cyclic_order_exact":all(
            s["competitor_order"]==[(s["query_position"]+d)%7 for d in range(1,7)]
            for row in a["rows"] for s in row["strata"]),
        "six_depths_scored_each":all([d["depth"] for d in s["depths"]]==list(range(1,7)) for row in a["rows"] for s in row["strata"]),
        "initial_anchor_exact":a["initial_anchor"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY","INTERFERENCE_HORIZON_WITH_PARTIAL_RECOVERY","NO_FAILURE_THROUGH_SIX_DISTINCT_WRITES","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B57","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B57_CUMULATIVE_INTERFERENCE_HORIZON":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
