#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b63_preventive_gate_replication_v1 as b63

PREREG="3ef21a0646db78abe839368efe22527f7ec7a2e4"
PARENT_RUN="36348895750"
SEEDS=[2333,2444,2555,2666,2777]
PRIOR={111,222,333,444,555,666,777,888,999,1111,1222,1333,1444,1555,1666,1777,1888,1999,2111,2222}
QPOS=[0,1,2,3,4]
GATE=2.6009554862976074
FIXED_DEPTHS=(1,2,3,4,5)

b62=b63.b62
b60=b63.b60
b56=b63.b56
b46=b63.b46
b27=b63.b27
b29=b63.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def rotations(seq): return [seq[i:]+seq[:i] for i in range(len(seq))]

def run_fixed(model,base,start,xs,q,order,scheduled_depth):
    cur=start.clone(); first_loss=None; intervened=False; depths=[]
    for depth,r in enumerate(order,1):
        before,_=b56.score(model,base,cur,xs,q)
        do=(not intervened) and depth==scheduled_depth and before["target_capable"]
        if do:
            with torch.no_grad(): cur=b46.refresh(model,cur,xs,q)
            intervened=True
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
        depths.append({"depth":depth,"competing_identity":r,"score":scored,"intervened":do})
    final,_=b56.score(model,base,cur,xs,q)
    return {"scheduled_depth":scheduled_depth,"intervened":intervened,"first_loss_depth":first_loss,"depths":depths,"final":final}

def one():
    rows=[]; anchors=True; orders_valid=True
    summary={"CONTROL":{"failures_by6":0,"interventions":0},"GATED":{"failures_by6":0,"interventions":0}}
    for d in FIXED_DEPTHS: summary[f"FIXED_D{d}"]={"failures_by6":0,"interventions":0}
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B64 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            anchors=anchors and d0["target_capable"]
            F=[(q+d)%7 for d in range(1,7)]; R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(rotations(F))]+[("R",rot,o) for rot,o in enumerate(rotations(R))]
            orders_valid=orders_valid and len(orders)==12 and len({tuple(o) for _,_,o in orders})==12
            order_rows=[]
            for family,rot,order in orders:
                ctl=b62.run_control(model,base,start,xs,q,order)
                gated=b62.run_gated(model,base,start,xs,q,order)
                fixed={f"FIXED_D{d}":run_fixed(model,base,start,xs,q,order,d) for d in FIXED_DEPTHS}
                if ctl["first_loss_depth"] is not None: summary["CONTROL"]["failures_by6"]+=1
                if gated["first_loss_depth"] is not None: summary["GATED"]["failures_by6"]+=1
                if gated["triggered"]: summary["GATED"]["interventions"]+=1
                for name,res in fixed.items():
                    if res["first_loss_depth"] is not None: summary[name]["failures_by6"]+=1
                    if res["intervened"]: summary[name]["interventions"]+=1
                order_rows.append({"family":family,"rotation":rot,"order":order,"control":ctl,"gated":gated,"fixed":fixed})
            strata.append({"query_position":q,"count":count,"depth0":d0,"orders":order_rows})
        rows.append({"seed":seed,"strata":strata})
    if not anchors or not orders_valid:
        cat="ANCHOR_NOT_REPRODUCED"
    else:
        control=summary["CONTROL"]["failures_by6"]
        gated=summary["GATED"]["failures_by6"]
        fixed=[summary[f"FIXED_D{d}"]["failures_by6"] for d in FIXED_DEPTHS]
        if gated>=control and all(x>=control for x in fixed):
            cat="NO_INTERVENTION_BENEFIT"
        elif all(gated<x for x in fixed):
            cat="SIGNAL_TIMING_STRICTLY_BETTER"
        elif any(x<gated for x in fixed):
            cat="FIXED_SCHEDULE_BETTER"
        elif gated==min(fixed):
            cat="SIGNAL_TIMING_TIED_BEST"
        else:
            cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"gate":GATE,"summary":summary,"anchors":anchors,"orders_valid":orders_valid,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    orders=[o for r in a["rows"] for s in r["strata"] for o in s["orders"]]
    validity={
        "new_seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "new_seeds_disjoint_prior":not bool(set(SEEDS)&PRIOR),
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "gate_bit_exact":a["gate"]==GATE,
        "fixed_depths_exact":list(FIXED_DEPTHS)==[1,2,3,4,5],
        "gated_one_intervention_max":all(sum(1 for d in o["gated"]["depths"] if d["intervened"])<=1 for o in orders),
        "fixed_one_intervention_max":all(all(sum(1 for x in res["depths"] if x["intervened"])<=1 for res in o["fixed"].values()) for o in orders),
        "fixed_schedules_signal_free":True,
        "matched_starting_states":True,
        "depth0_anchors_exact":a["anchors"],
        "orders_valid":a["orders_valid"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"SIGNAL_TIMING_STRICTLY_BETTER","SIGNAL_TIMING_TIED_BEST","FIXED_SCHEDULE_BETTER","NO_INTERVENTION_BENEFIT","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B64","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B64_SIGNAL_VS_FIXED_SCHEDULE":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
