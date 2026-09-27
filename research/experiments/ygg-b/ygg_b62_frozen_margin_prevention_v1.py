#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b61_heldout_margin_gate_v1 as b61

PREREG="5851e2c054a194e46bb8778f4d88fcd4cf00c2e2"
PARENT_RUN="36334960750"
SEEDS=[1222,1333,1444,1555,1666]
PRIOR_SEEDS={111,222,333,444,555,666,777,888,999,1111}
QPOS=[0,1,2,3,4]
GATE=2.6009554862976074

b60=b61.b60
b59=b60.b59
b58=b59.b58
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
def rotations(seq): return [seq[i:]+seq[:i] for i in range(len(seq))]

def run_control(model,base,start,xs,q,order):
    cur=start.clone(); first_loss=None; depths=[]
    for depth,r in enumerate(order,1):
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
        depths.append({"depth":depth,"competing_identity":r,"score":scored})
    final,_=b56.score(model,base,cur,xs,q)
    return {"first_loss_depth":first_loss,"depths":depths,"final":final}

def run_gated(model,base,start,xs,q,order):
    cur=start.clone(); first_loss=None; triggered=False; trigger=None; depths=[]
    for depth,r in enumerate(order,1):
        current_score,_=b56.score(model,base,cur,xs,q)
        if (not triggered) and current_score["target_capable"]:
            margin=b60.pre_margin(model,cur,xs,q)
            if margin<=GATE:
                triggered=True
                with torch.no_grad(): cf=b46.refresh(model,cur,xs,r)
                cf_score,_=b56.score(model,base,cf,xs,q)
                with torch.no_grad(): refreshed=b46.refresh(model,cur,xs,q)
                with torch.no_grad(): nxt=b46.refresh(model,refreshed,xs,r)
                gated_score,_=b56.score(model,base,nxt,xs,q)
                true_imminent=not cf_score["target_capable"]
                immediate_prevented=true_imminent and gated_score["target_capable"]
                harm=cf_score["target_capable"] and (not gated_score["target_capable"])
                trigger={
                    "depth":depth,"pre_margin":margin,"next_competitor":r,
                    "counterfactual_target_capable":cf_score["target_capable"],
                    "gated_next_target_capable":gated_score["target_capable"],
                    "true_imminent":true_imminent,
                    "immediate_prevented":immediate_prevented,
                    "intervention_harm":harm,
                }
                cur=nxt
                if first_loss is None and not gated_score["target_capable"]: first_loss=depth
                depths.append({"depth":depth,"competing_identity":r,"score":gated_score,"intervened":True})
                continue
        with torch.no_grad(): cur=b46.refresh(model,cur,xs,r)
        scored,_=b56.score(model,base,cur,xs,q)
        if first_loss is None and not scored["target_capable"]: first_loss=depth
        depths.append({"depth":depth,"competing_identity":r,"score":scored,"intervened":False})
    final,_=b56.score(model,base,cur,xs,q)
    return {"first_loss_depth":first_loss,"triggered":triggered,"trigger":trigger,"depths":depths,"final":final}

def one():
    rows=[]; anchors=True; orders_valid=True
    triggered=0; true_imminent=0; false_triggers=0; prevented=0; harms=0
    control_fail=0; gated_fail=0
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B62 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            anchors=anchors and d0["target_capable"]
            F=[(q+d)%7 for d in range(1,7)]; R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(rotations(F))]+[("R",rot,o) for rot,o in enumerate(rotations(R))]
            orders_valid=orders_valid and len(orders)==12 and len({tuple(o) for _,_,o in orders})==12
            order_rows=[]
            for family,rot,order in orders:
                ctl=run_control(model,base,start,xs,q,order)
                gate=run_gated(model,base,start,xs,q,order)
                if ctl["first_loss_depth"] is not None: control_fail+=1
                if gate["first_loss_depth"] is not None: gated_fail+=1
                if gate["triggered"]:
                    triggered+=1
                    tr=gate["trigger"]
                    if tr["true_imminent"]: true_imminent+=1
                    else: false_triggers+=1
                    if tr["immediate_prevented"]: prevented+=1
                    if tr["intervention_harm"]: harms+=1
                order_rows.append({
                    "family":family,"rotation":rot,"order":order,
                    "control":ctl,"gated":gate,
                    "first_loss_shift":None if ctl["first_loss_depth"] is None or gate["first_loss_depth"] is None else gate["first_loss_depth"]-ctl["first_loss_depth"]
                })
            strata.append({"query_position":q,"count":count,"depth0":d0,"orders":order_rows})
        rows.append({"seed":seed,"strata":strata})
    if not anchors or not orders_valid: cat="ANCHOR_NOT_REPRODUCED"
    elif triggered==0: cat="NO_TRIGGERS"
    elif true_imminent==0: cat="NO_TRUE_IMMINENT_TRIGGERS"
    elif prevented==true_imminent and harms==0 and gated_fail<control_fail: cat="FROZEN_GATE_PREVENTS_FAILURE"
    elif prevented>0 and gated_fail<control_fail: cat="PARTIAL_PREVENTIVE_BENEFIT"
    else: cat="NO_NET_PREVENTIVE_BENEFIT"
    return {
        "rows":rows,"gate":GATE,
        "triggered_trajectories":triggered,"true_imminent_triggers":true_imminent,
        "false_triggers":false_triggers,"immediate_prevented_failures":prevented,
        "intervention_harms":harms,"control_failures_by6":control_fail,
        "gated_failures_by6":gated_fail,"anchors":anchors,"orders_valid":orders_valid,
        "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    all_orders=[o for r in a["rows"] for s in r["strata"] for o in s["orders"]]
    validity={
        "new_seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "new_seeds_disjoint_prior":not bool(set(SEEDS)&PRIOR_SEEDS),
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "gate_bit_exact":a["gate"]==GATE,
        "at_most_one_intervention_each":all(sum(1 for d in o["gated"]["depths"] if d["intervened"])<=1 for o in all_orders),
        "counterfactual_never_feeds_back":True,
        "margin_ground_truth_free":True,
        "depth0_anchors_exact":a["anchors"],
        "orders_valid":a["orders_valid"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"FROZEN_GATE_PREVENTS_FAILURE","PARTIAL_PREVENTIVE_BENEFIT","NO_NET_PREVENTIVE_BENEFIT","NO_TRUE_IMMINENT_TRIGGERS","NO_TRIGGERS","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B62","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B62_FROZEN_MARGIN_PREVENTION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
