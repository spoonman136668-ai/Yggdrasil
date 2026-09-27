#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b59_order_family_horizon_v1 as b59

PREREG="935b79cd84569ba06a3535da920453a72208bdcc"
PARENT_RUN="36332262366"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
B59_FIRST={
111:{0:[5,4,4,5,5,5,4,4,5,5,5,5],1:[4,4,5,5,5,4,5,5,4,5,5,5],2:[5,5,4,4,4,4,4,5,6,5,5,4],3:[5,4,3,3,5,5,3,3,5,5,5,4],4:[4,3,3,4,5,5,4,3,3,5,5,4]},
222:{0:[4,4,4,5,5,4,4,4,5,4,5,5],1:[4,4,5,5,5,4,5,5,5,5,5,5],2:[5,5,4,4,4,5,4,5,5,5,4,4],3:[4,4,3,3,4,5,3,3,4,5,5,4],4:[4,4,3,4,5,5,4,3,4,5,5,4]},
333:{0:[4,4,4,5,5,4,4,4,5,4,5,5],1:[4,4,5,5,4,4,5,5,4,5,4,4],2:[5,4,4,4,4,4,3,4,5,5,4,4],3:[5,4,3,3,4,5,3,3,5,5,4,4],4:[4,3,3,4,5,5,3,3,3,5,5,4]},
444:{0:[4,4,4,5,5,5,4,4,5,5,5,5],1:[4,4,5,5,5,4,5,5,5,5,5,5],2:[5,5,4,4,4,5,4,5,6,5,4,4],3:[5,4,3,3,4,5,3,3,5,5,5,4],4:[4,3,3,3,5,5,3,3,3,5,5,4]},
555:{0:[4,3,3,5,5,4,4,4,4,4,5,5],1:[3,4,5,5,5,4,5,4,4,4,4,4],2:[5,5,4,5,5,5,4,5,6,5,5,4],3:[5,4,3,2,4,5,3,2,5,5,4,4],4:[4,4,3,4,5,5,4,3,3,5,5,4]}}

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

def pre_margin(model,state,xs,q):
    with torch.no_grad(): logits=b46.query_logits(model,state,xs,q)
    top2=torch.topk(logits,k=2,dim=1).values
    return float((top2[:,0]-top2[:,1]).mean())

def pairwise_auc(failure,survival):
    if not failure or not survival: return None
    wins=0.0
    for f in failure:
        for s in survival:
            if s>f: wins+=1.0
            elif s==f: wins+=0.5
    return wins/(len(failure)*len(survival))

def one():
    rows=[]; obs=[]; anchors=True
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B60 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            if not d0["target_capable"]: anchors=False
            F=[(q+d)%7 for d in range(1,7)]
            R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(rotations(F))]+[("R",rot,o) for rot,o in enumerate(rotations(R))]
            order_rows=[]
            for oi,(family,rot,order) in enumerate(orders):
                cur=start.clone(); first_loss=None; transitions=[]
                for depth,r in enumerate(order,1):
                    if first_loss is None:
                        margin=pre_margin(model,cur,xs,q)
                    else:
                        margin=None
                    with torch.no_grad(): nxt=b46.refresh(model,cur,xs,r)
                    scored,_=b56.score(model,base,nxt,xs,q)
                    if first_loss is None:
                        next_failure=not scored["target_capable"]
                        rec={"seed":seed,"query_position":q,"family":family,"rotation":rot,
                             "depth":depth,"next_competitor":r,"pre_margin":margin,
                             "next_failure":next_failure}
                        obs.append(rec); transitions.append(rec)
                        if next_failure: first_loss=depth
                    cur=nxt
                expected=B59_FIRST[seed][q][oi]
                if first_loss!=expected: anchors=False
                order_rows.append({"family":family,"rotation":rot,"first_loss_depth":first_loss,
                                   "expected_first_loss_depth":expected,"eligible_transitions":transitions})
            strata.append({"query_position":q,"count":count,"orders":order_rows})
        rows.append({"seed":seed,"strata":strata})
    failures=[o["pre_margin"] for o in obs if o["next_failure"]]
    survival=[o["pre_margin"] for o in obs if not o["next_failure"]]
    if not anchors: cat="ANCHOR_NOT_REPRODUCED"
    elif not failures: cat="NO_FAILURE_TRANSITIONS"
    elif max(failures)<min(survival): cat="STRICT_MARGIN_SEPARATION"
    else: cat="MARGIN_OVERLAP"
    return {
        "rows":rows,"observations":obs,
        "failure_count":len(failures),"survival_count":len(survival),
        "failure_margin_min":min(failures) if failures else None,
        "failure_margin_max":max(failures) if failures else None,
        "survival_margin_min":min(survival) if survival else None,
        "survival_margin_max":max(survival) if survival else None,
        "survival_rank_auc":pairwise_auc(failures,survival),
        "anchors":anchors,"classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "exact_12_orders_each":all(len(s["orders"])==12 for r in a["rows"] for s in r["strata"]),
        "b59_first_loss_anchors_exact":a["anchors"],
        "only_pre_first_loss_transitions_included":all(
            len(o["eligible_transitions"])==o["first_loss_depth"]
            for r in a["rows"] for s in r["strata"] for o in s["orders"]),
        "failure_and_survival_groups_nonempty":a["failure_count"]>0 and a["survival_count"]>0,
        "margin_ground_truth_free":True,
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"STRICT_MARGIN_SEPARATION","MARGIN_OVERLAP","NO_FAILURE_TRANSITIONS","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B60","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B60_PREFAILURE_CONFIDENCE_MARGIN":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
