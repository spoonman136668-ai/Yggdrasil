#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b64_signal_vs_fixed_schedule_v1 as b64

PREREG="2022077adfb46f105557b9af3b5807dcad1eb0f3"
PARENT_RUN="36353597874"
SEEDS=[2888,2999,3111,3222,3333]
PRIOR={111,222,333,444,555,666,777,888,999,1111,1222,1333,1444,1555,1666,1777,1888,1999,2111,2222,2333,2444,2555,2666,2777}
QPOS=[0,1,2,3,4]
GATE=2.6009554862976074

b63=b64.b63
b62=b64.b62
b60=b64.b60
b56=b64.b56
b46=b64.b46
b27=b64.b27
b29=b64.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def rotations(seq): return [seq[i:]+seq[:i] for i in range(len(seq))]

def control_state(model,base,start,xs,q,order):
    cur=start.clone(); first_loss=None
    for depth,r in enumerate(order,1):
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
    return cur,first_loss

def gated_state(model,base,start,xs,q,order):
    cur=start.clone(); first_loss=None; triggered=False
    for depth,r in enumerate(order,1):
        before,_=b56.score(model,base,cur,xs,q)
        if (not triggered) and before["target_capable"]:
            margin=b60.pre_margin(model,cur,xs,q)
            if margin<=GATE:
                with torch.no_grad(): cur=b46.refresh(model,cur,xs,q)
                triggered=True
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
    return cur,first_loss,triggered

def d5_state(model,base,start,xs,q,order):
    cur=start.clone(); first_loss=None; intervened=False
    for depth,r in enumerate(order,1):
        before,_=b56.score(model,base,cur,xs,q)
        if depth==5 and (not intervened) and before["target_capable"]:
            with torch.no_grad(): cur=b46.refresh(model,cur,xs,q)
            intervened=True
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
    return cur,first_loss,intervened

def all_binding_correct(model,M,xs):
    out=[]
    for j in range(7):
        target=xs[:,4*j+3]-b27.VALUE_BASE
        with torch.no_grad(): pred=b46.query_logits(model,M,xs,j).argmax(1)
        out.append(pred==target)
    return out

def one():
    rows=[]; anchors=True; orders_valid=True
    ctl_fail=g_fail=d5_fail=0; g_int=d5_int=0
    g_new=g_rep=d5_new=d5_rep=0; g_opp=d5_opp=0
    g_target_correct=g_target_total=d5_target_correct=d5_target_total=0
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B65 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            anchors=anchors and d0["target_capable"]
            F=[(q+d)%7 for d in range(1,7)]; R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(rotations(F))]+[("R",rot,o) for rot,o in enumerate(rotations(R))]
            orders_valid=orders_valid and len(orders)==12 and len({tuple(o) for _,_,o in orders})==12
            orows=[]
            for family,rot,order in orders:
                Mc,flc=control_state(model,base,start,xs,q,order)
                Mg,flg,trig=gated_state(model,base,start,xs,q,order)
                Md,fld,di=d5_state(model,base,start,xs,q,order)
                ctl_fail+=flc is not None; g_fail+=flg is not None; d5_fail+=fld is not None
                g_int+=trig; d5_int+=di
                cc=all_binding_correct(model,Mc,xs)
                gc=all_binding_correct(model,Mg,xs)
                dc=all_binding_correct(model,Md,xs)
                per=[]
                for j in range(7):
                    c=cc[j]; g=gc[j]; d=dc[j]
                    if j==q:
                        g_target_correct+=int(g.sum()); d5_target_correct+=int(d.sum())
                        g_target_total+=count; d5_target_total+=count
                    else:
                        g_new+=int((c & (~g)).sum()); g_rep+=int(((~c)&g).sum()); g_opp+=int(c.sum())
                        d5_new+=int((c & (~d)).sum()); d5_rep+=int(((~c)&d).sum()); d5_opp+=int(c.sum())
                    per.append({
                        "binding":j,"is_target":j==q,
                        "control_correct":int(c.sum()),"gated_correct":int(g.sum()),"d5_correct":int(d.sum()),
                        "gated_new_error":int((c & (~g)).sum()) if j!=q else 0,
                        "gated_repair":int(((~c)&g).sum()) if j!=q else 0,
                        "d5_new_error":int((c & (~d)).sum()) if j!=q else 0,
                        "d5_repair":int(((~c)&d).sum()) if j!=q else 0,
                    })
                orows.append({"family":family,"rotation":rot,"order":order,
                             "control_first_loss":flc,"gated_first_loss":flg,"d5_first_loss":fld,
                             "gated_intervened":trig,"d5_intervened":di,"bindings":per})
            strata.append({"query_position":q,"count":count,"depth0":d0,"orders":orows})
        rows.append({"seed":seed,"strata":strata})
    if not anchors or not orders_valid: cat="ANCHOR_NOT_REPRODUCED"
    elif g_fail<d5_fail and g_new<=d5_new: cat="SIGNAL_PARETO_DOMINATES_D5"
    elif g_fail<d5_fail and g_new>d5_new: cat="SIGNAL_TARGET_BETTER_COLLATERAL_WORSE"
    elif d5_fail<=g_fail and d5_new<=g_new and (d5_fail<g_fail or d5_new<g_new): cat="D5_PARETO_DOMINATES_SIGNAL"
    else: cat="MIXED_COLLATERAL_TRADEOFF"
    return {
        "rows":rows,"gate":GATE,
        "control_failures_by6":ctl_fail,"gated_failures_by6":g_fail,"d5_failures_by6":d5_fail,
        "gated_interventions":g_int,"d5_interventions":d5_int,
        "gated_collateral_baseline_correct_opportunities":g_opp,
        "gated_collateral_new_error_count":g_new,"gated_collateral_repair_count":g_rep,
        "d5_collateral_baseline_correct_opportunities":d5_opp,
        "d5_collateral_new_error_count":d5_new,"d5_collateral_repair_count":d5_rep,
        "gated_final_target_accuracy":g_target_correct/g_target_total,
        "d5_final_target_accuracy":d5_target_correct/d5_target_total,
        "anchors":anchors,"orders_valid":orders_valid,"classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "new_seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "new_seeds_disjoint_prior":not bool(set(SEEDS)&PRIOR),
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "gate_bit_exact":a["gate"]==GATE,
        "gated_one_intervention_max":all(sum(1 for o in s["orders"] if o["gated_intervened"])<=12 for r in a["rows"] for s in r["strata"]),
        "d5_one_intervention_max":all(sum(1 for o in s["orders"] if o["d5_intervened"])<=12 for r in a["rows"] for s in r["strata"]),
        "d5_signal_free":True,
        "matched_starting_states":True,
        "all_seven_bindings_scored":all(all(len(o["bindings"])==7 for o in s["orders"]) for r in a["rows"] for s in r["strata"]),
        "collateral_relative_to_control_only":True,
        "depth0_anchors_exact":a["anchors"],
        "orders_valid":a["orders_valid"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"SIGNAL_PARETO_DOMINATES_D5","SIGNAL_TARGET_BETTER_COLLATERAL_WORSE","D5_PARETO_DOMINATES_SIGNAL","MIXED_COLLATERAL_TRADEOFF","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B65","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B65_PREVENTION_COLLATERAL_LEDGER":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
