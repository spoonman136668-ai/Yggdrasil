#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b57_cumulative_interference_horizon_v1 as b57

PREREG="adf82c5eaa458215702ea040fd32223c72e24d42"
PARENT_RUN="36329853182"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
B57_FIRST={
    111:{0:5,1:4,2:5,3:5,4:4},
    222:{0:4,1:4,2:5,3:4,4:4},
    333:{0:4,1:4,2:5,3:5,4:4},
    444:{0:4,1:4,2:5,3:5,4:4},
    555:{0:4,1:3,2:5,3:5,4:4},
}

b56=b57.b56
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
    rows=[]; initial_anchor=True; any_loss=False; all_lost_recovered=True; any_shift=False
    loss_counts={d:0 for d in range(1,7)}
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B58 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): cur=b46.refresh(model,base,xs,q)
            depth0,_=b56.score(model,base,cur,xs,q)
            initial_anchor=initial_anchor and depth0["target_capable"]
            order=[(q-d)%7 for d in range(1,7)]
            if sorted(order)!=[r for r in range(7) if r!=q]:
                raise AssertionError("B58 reverse order invalid")
            depths=[]; first_loss=None
            for depth,r in enumerate(order,1):
                with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
                scored,_=b56.score(model,base,cur,xs,q)
                if not scored["target_capable"]:
                    loss_counts[depth]+=1; any_loss=True
                    if first_loss is None: first_loss=depth
                depths.append({
                    "depth":depth,"competing_identity":r,
                    "target_accuracy":scored["target_accuracy"],"target_capable":scored["target_capable"],
                    "collateral_new_errors":scored["collateral_new_errors"],"collateral_repairs":scored["collateral_repairs"]
                })
            with torch.no_grad(): repaired=b46.refresh(model,cur,xs,q)
            post,_=b56.score(model,base,repaired,xs,q)
            if first_loss is not None and not post["target_capable"]: all_lost_recovered=False
            inherited=B57_FIRST[seed][q]
            any_shift=any_shift or first_loss!=inherited
            strata.append({
                "query_position":q,"count":count,"depth0":depth0,"competitor_order":order,
                "depths":depths,"first_loss_depth":first_loss,
                "b57_first_loss_depth":inherited,"first_loss_shifted":first_loss!=inherited,
                "post_depth6_repair":post
            })
        rows.append({"seed":seed,"strata":strata})
    if not initial_anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif not any_loss: cat="NO_FAILURE_REVERSE_ORDER"
    elif any_shift and not all_lost_recovered: cat="ORDER_SHIFTS_AND_RECOVERY_FAILS"
    elif any_shift and all_lost_recovered: cat="ORDER_SHIFTS_HORIZON_WITH_RECOVERY"
    elif all_lost_recovered: cat="ORDER_INVARIANT_HORIZON"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "rows":rows,"depth_loss_counts":loss_counts,"initial_anchor":initial_anchor,
        "any_loss":any_loss,"all_lost_recovered":all_lost_recovered,"any_first_loss_shift":any_shift,
        "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "twenty_five_strata_exact":sum(len(r["strata"]) for r in a["rows"])==25,
        "reverse_order_exact":all(
            s["competitor_order"]==[(s["query_position"]-d)%7 for d in range(1,7)]
            for row in a["rows"] for s in row["strata"]),
        "six_distinct_competitors_each":all(
            len(set(s["competitor_order"]))==6 and sorted(s["competitor_order"])==[r for r in range(7) if r!=s["query_position"]]
            for row in a["rows"] for s in row["strata"]),
        "six_depths_scored_each":all([d["depth"] for d in s["depths"]]==list(range(1,7)) for row in a["rows"] for s in row["strata"]),
        "b57_comparison_table_exact":all(s["b57_first_loss_depth"]==B57_FIRST[row["seed"]][s["query_position"]] for row in a["rows"] for s in row["strata"]),
        "initial_anchor_exact":a["initial_anchor"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"ORDER_INVARIANT_HORIZON","ORDER_SHIFTS_HORIZON_WITH_RECOVERY","ORDER_SHIFTS_AND_RECOVERY_FAILS","NO_FAILURE_REVERSE_ORDER","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B58","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B58_REVERSE_INTERFERENCE_ORDER":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
