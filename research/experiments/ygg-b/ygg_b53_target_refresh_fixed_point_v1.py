#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b52_target_refresh_dose_v1 as b52

PREREG="90d34004f0bbc89bc27f4783e3e56c02a62aca92"
PARENT_RUN="36310819187"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
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

def max_abs(a,b):
    if a.numel()==0: return 0.0
    return float((a-b).abs().max())

def changed_count(a,b):
    return int((a!=b).sum())

def one():
    rows=[]
    aggregate={1:0,2:0,3:0}
    universal={1:True,2:True,3:True}
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B53 empty q")
            xs=x[mask]; base=M0[mask]
            target=xs[:,4*q+3]-b27.VALUE_BASE
            states=[]
            cur=base
            dose_rows=[]
            for dose in (1,2,3):
                with torch.no_grad(): cur=b46.refresh(model,cur,xs,q)
                states.append(cur.clone())
                logits=[]
                opp=new=rep=0
                for j in range(7):
                    jt=xs[:,4*j+3]-b27.VALUE_BASE
                    with torch.no_grad():
                        bl=b46.query_logits(model,base,xs,j)
                        pl=b46.query_logits(model,cur,xs,j)
                    logits.append(pl.clone())
                    bp=bl.argmax(1); pp=pl.argmax(1); bc=(bp==jt); pc=(pp==jt)
                    if j!=q:
                        opp+=int(bc.sum()); new+=int((bc & (~pc)).sum()); rep+=int(((~bc)&pc).sum())
                with torch.no_grad(): qp=b46.query_logits(model,cur,xs,q).argmax(1)
                qacc=float((qp==target).float().mean())
                aggregate[dose]+=new
                universal[dose]=universal[dose] and (qacc>=TH)
                dose_rows.append({
                    "dose":dose,"target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "collateral_baseline_correct_opportunities":opp,
                    "collateral_new_error_count":new,"collateral_repair_count":rep,
                    "logits":logits
                })
            transitions=[]
            for ia,ib in ((0,1),(1,2)):
                sa,sb=states[ia],states[ib]
                la=dose_rows[ia]["logits"]; lb=dose_rows[ib]["logits"]
                transitions.append({
                    "from_dose":ia+1,"to_dose":ib+1,
                    "state_equal":bool(torch.equal(sa,sb)),
                    "state_max_abs_delta":max_abs(sa,sb),
                    "state_changed_elements":changed_count(sa,sb),
                    "logit_equal_by_binding":[bool(torch.equal(la[j],lb[j])) for j in range(7)],
                    "logit_max_abs_delta_by_binding":[max_abs(la[j],lb[j]) for j in range(7)],
                    "logit_changed_elements_by_binding":[changed_count(la[j],lb[j]) for j in range(7)],
                })
            for d in dose_rows: d.pop("logits")
            strata.append({"query_position":q,"count":count,"doses":dose_rows,"transitions":transitions})
        rows.append({"seed":seed,"strata":strata})
    behavioral_anchor=(aggregate=={1:3724,2:3724,3:3724} and all(universal.values()))
    all_trans=[t for r in rows for s in r["strata"] for t in s["transitions"]]
    all_state_equal=all(t["state_equal"] for t in all_trans)
    all_logits_equal=all(all(t["logit_equal_by_binding"]) for t in all_trans)
    if not behavioral_anchor: cat="BEHAVIORAL_ANCHOR_NOT_REPRODUCED"
    elif all_state_equal and all_logits_equal: cat="EXACT_STATE_FIXED_POINT_AFTER_ONE"
    elif (not all_state_equal) and all_logits_equal: cat="BEHAVIORAL_FIXED_POINT_ONLY"
    elif not all_logits_equal: cat="OUTPUT_CHANGES_WITHOUT_DECISION_CHANGE"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "rows":rows,"aggregate_collateral_new_errors":aggregate,"universal_target":universal,
        "behavioral_anchor":behavioral_anchor,
        "all_state_equal":all_state_equal,"all_logits_equal":all_logits_equal,
        "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "two_transitions_each":all(len(s["transitions"])==2 for r in a["rows"] for s in r["strata"]),
        "state_shape_exact":all(all(t["state_changed_elements"]>=0 for t in s["transitions"]) for r in a["rows"] for s in r["strata"]),
        "all_seven_logits_inspected":all(all(len(t["logit_equal_by_binding"])==7 and len(t["logit_max_abs_delta_by_binding"])==7 for t in s["transitions"]) for r in a["rows"] for s in r["strata"]),
        "b52_behavioral_anchor_exact":a["behavioral_anchor"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"EXACT_STATE_FIXED_POINT_AFTER_ONE","BEHAVIORAL_FIXED_POINT_ONLY","OUTPUT_CHANGES_WITHOUT_DECISION_CHANGE","BEHAVIORAL_ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B53","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B53_TARGET_REFRESH_FIXED_POINT":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
