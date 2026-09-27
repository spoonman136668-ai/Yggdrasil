#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b58_reverse_interference_order_v1 as b58

PREREG="9069aaed22f67d7968321b8303ee089a2c91fe6e"
PARENT_RUN="36331204340"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
B57_FIRST={
111:{0:5,1:4,2:5,3:5,4:4},
222:{0:4,1:4,2:5,3:4,4:4},
333:{0:4,1:4,2:5,3:5,4:4},
444:{0:4,1:4,2:5,3:5,4:4},
555:{0:4,1:3,2:5,3:5,4:4}}
B58_FIRST={
111:{0:4,1:5,2:4,3:3,4:4},
222:{0:4,1:5,2:4,3:3,4:4},
333:{0:4,1:5,2:3,3:3,4:3},
444:{0:4,1:5,2:4,3:3,4:3},
555:{0:4,1:5,2:4,3:3,4:4}}

b57=b58.b57
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
def rotations(seq):
    return [tuple(seq[i:]+seq[:i]) for i in range(len(seq))]

def one():
    rows=[]; anchors=True; all_recovered=True; any_resist=False; any_range=False
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B59 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            if not d0["target_capable"]: anchors=False
            F=[(q+d)%7 for d in range(1,7)]
            R=list(reversed(F))
            orders=[]
            for family,seq in (("F",F),("R",R)):
                for rot,order in enumerate(rotations(seq)):
                    orders.append((family,rot,order))
            if len(set(o for _,_,o in orders))!=12: raise AssertionError("B59 order family not unique")
            order_rows=[]
            for family,rot,order in orders:
                cur=start.clone(); first_loss=None
                depths=[]
                for depth,r in enumerate(order,1):
                    with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
                    scored,_=b56.score(model,base,cur,xs,q)
                    if not scored["target_capable"] and first_loss is None: first_loss=depth
                    depths.append({"depth":depth,"competing_identity":r,"target_accuracy":scored["target_accuracy"],"target_capable":scored["target_capable"]})
                with torch.no_grad(): repaired=b46.refresh(model,cur,xs,q)
                post,_=b56.score(model,base,repaired,xs,q)
                if first_loss is None: any_resist=True
                if first_loss is not None and not post["target_capable"]: all_recovered=False
                order_rows.append({
                    "family":family,"rotation":rot,"order":list(order),
                    "first_loss_depth":first_loss,"post_repair_target_capable":post["target_capable"],
                    "post_repair_target_accuracy":post["target_accuracy"],"depths":depths
                })
            f0=next(o for o in order_rows if o["family"]=="F" and o["rotation"]==0)
            r0=next(o for o in order_rows if o["family"]=="R" and o["rotation"]==0)
            if f0["first_loss_depth"]!=B57_FIRST[seed][q] or r0["first_loss_depth"]!=B58_FIRST[seed][q]:
                anchors=False
            vals=[o["first_loss_depth"] for o in order_rows if o["first_loss_depth"] is not None]
            min_loss=min(vals) if vals else None
            max_loss=max(vals) if vals else None
            if min_loss!=max_loss: any_range=True
            strata.append({
                "query_position":q,"count":count,"depth0":d0,"orders":order_rows,
                "min_first_loss_depth":min_loss,"max_first_loss_depth":max_loss,
                "orders_resisting_through_six":sum(o["first_loss_depth"] is None for o in order_rows),
                "b57_anchor":B57_FIRST[seed][q],"b58_anchor":B58_FIRST[seed][q]
            })
        rows.append({"seed":seed,"strata":strata})
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif not all_recovered: cat="RECOVERY_ORDER_DEPENDENT"
    elif any_resist: cat="SOME_ORDERS_RESIST_SIX_WRITES"
    elif any_range: cat="ORDER_FAMILY_BOUNDED_WITH_UNIVERSAL_RECOVERY"
    else: cat="ORDER_FAMILY_HORIZON_INVARIANT"
    return {"rows":rows,"anchors":anchors,"all_lost_sequences_recovered":all_recovered,
            "any_order_resists_six":any_resist,"any_within_stratum_range":any_range,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "orders_unique_each":all(len({tuple(o["order"]) for o in s["orders"]})==12 for r in a["rows"] for s in r["strata"]),
        "six_depths_each_order":all(len(o["depths"])==6 for r in a["rows"] for s in r["strata"] for o in s["orders"]),
        "forward_reverse_anchors_exact":a["anchors"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"ORDER_FAMILY_BOUNDED_WITH_UNIVERSAL_RECOVERY","ORDER_FAMILY_HORIZON_INVARIANT","SOME_ORDERS_RESIST_SIX_WRITES","RECOVERY_ORDER_DEPENDENT","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B59","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B59_ORDER_FAMILY_HORIZON":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
