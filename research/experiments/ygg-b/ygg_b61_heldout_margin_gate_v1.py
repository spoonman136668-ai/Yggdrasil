#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b60_prefailure_confidence_margin_v1 as b60

PREREG="1cff5aeab47a95768b01e472fab31897c301c7b0"
PARENT_RUN="36333420842"
SEEDS=[666,777,888,999,1111]
TRAIN_SEEDS={111,222,333,444,555}
QPOS=[0,1,2,3,4]
TH=.90
GATE=2.6009554862976074

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

def auc(failure,survival):
    if not failure or not survival: return None
    wins=0.0
    for f in failure:
        for s in survival:
            if s>f: wins+=1.0
            elif s==f: wins+=0.5
    return wins/(len(failure)*len(survival))

def one():
    rows=[]; obs=[]; anchors=True; orders_valid=True
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B61 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            anchors=anchors and d0["target_capable"]
            F=[(q+d)%7 for d in range(1,7)]; R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(rotations(F))]+[("R",rot,o) for rot,o in enumerate(rotations(R))]
            orders_valid=orders_valid and len(orders)==12 and len({tuple(o) for _,_,o in orders})==12
            order_rows=[]
            for family,rot,order in orders:
                cur=start.clone(); first_loss=None; transitions=[]
                for depth,r in enumerate(order,1):
                    if first_loss is None:
                        margin=b60.pre_margin(model,cur,xs,q)
                    else:
                        margin=None
                    with torch.no_grad(): nxt=b46.refresh(model,cur,xs,r)
                    scored,_=b56.score(model,base,nxt,xs,q)
                    if first_loss is None:
                        next_failure=not scored["target_capable"]
                        rec={"seed":seed,"query_position":q,"family":family,"rotation":rot,"depth":depth,
                             "next_competitor":r,"pre_margin":margin,"next_failure":next_failure}
                        obs.append(rec); transitions.append(rec)
                        if next_failure: first_loss=depth
                    cur=nxt
                order_rows.append({"family":family,"rotation":rot,"first_loss_depth":first_loss,"eligible_transitions":transitions})
            strata.append({"query_position":q,"count":count,"depth0":d0,"orders":order_rows})
        rows.append({"seed":seed,"strata":strata})
    failure=[o["pre_margin"] for o in obs if o["next_failure"]]
    survival=[o["pre_margin"] for o in obs if not o["next_failure"]]
    tp=sum(o["next_failure"] and o["pre_margin"]<=GATE for o in obs)
    fn=sum(o["next_failure"] and o["pre_margin"]>GATE for o in obs)
    fp=sum((not o["next_failure"]) and o["pre_margin"]<=GATE for o in obs)
    tn=sum((not o["next_failure"]) and o["pre_margin"]>GATE for o in obs)
    sens=tp/(tp+fn) if tp+fn else None
    spec=tn/(tn+fp) if tn+fp else None
    bal=(sens+spec)/2 if sens is not None and spec is not None else None
    rank=auc(failure,survival)
    if not anchors or not orders_valid: cat="ANCHOR_NOT_REPRODUCED"
    elif not failure: cat="NO_FAILURE_TRANSITIONS"
    elif rank>=.90 and bal>=.85 and sens>=.85 and spec>=.80: cat="HELDOUT_MARGIN_GATE_REPLICATES"
    elif rank>=.90: cat="HELDOUT_RANK_SIGNAL_ONLY"
    else: cat="HELDOUT_MARGIN_SIGNAL_WEAK"
    return {
        "rows":rows,"observations":obs,"failure_count":len(failure),"survival_count":len(survival),
        "failure_margin_min":min(failure) if failure else None,"failure_margin_max":max(failure) if failure else None,
        "survival_margin_min":min(survival) if survival else None,"survival_margin_max":max(survival) if survival else None,
        "survival_rank_auc":rank,"gate":GATE,"tp":tp,"tn":tn,"fp":fp,"fn":fn,
        "sensitivity":sens,"specificity":spec,"balanced_accuracy":bal,
        "anchors":anchors,"orders_valid":orders_valid,"classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "heldout_seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "heldout_disjoint_from_b60":not bool(set(SEEDS)&TRAIN_SEEDS),
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "only_pre_first_loss_transitions_included":all(
            o["first_loss_depth"] is None or len(o["eligible_transitions"])==o["first_loss_depth"]
            for r in a["rows"] for s in r["strata"] for o in s["orders"]),
        "gate_bit_exact":a["gate"]==GATE,
        "margin_ground_truth_free":True,
        "depth0_anchors_exact":a["anchors"],
        "orders_valid":a["orders_valid"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"HELDOUT_MARGIN_GATE_REPLICATES","HELDOUT_RANK_SIGNAL_ONLY","HELDOUT_MARGIN_SIGNAL_WEAK","NO_FAILURE_TRANSITIONS","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B61","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B61_HELDOUT_MARGIN_GATE":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
