#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b54_target_refresh_convergence_v1 as b54

PREREG="a1d6e1dc58e0701bc16097ced0cdf40123901db4"
PARENT_RUN="36316835093"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
DOSES=list(range(1,65))
TH=.90
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
def max_abs(a,b): return 0.0 if a.numel()==0 else float((a-b).abs().max())
def changed(a,b): return int((a!=b).sum())

def one():
    rows=[]
    aggregate={d:0 for d in DOSES}
    universal={d:True for d in DOSES}
    any_decision_change=False
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B55 empty q")
            xs=x[mask]; base=M0[mask]
            target=xs[:,4*q+3]-b27.VALUE_BASE
            cur=base; prev_state=None; prev_logits=None; d1_preds=None
            dose_rows=[]; transitions=[]
            for dose in DOSES:
                with torch.no_grad(): cur=b46.refresh(model,cur,xs,q)
                logits=[]; preds=[]; opp=new=rep=0
                for j in range(7):
                    jt=xs[:,4*j+3]-b27.VALUE_BASE
                    with torch.no_grad():
                        bl=b46.query_logits(model,base,xs,j)
                        pl=b46.query_logits(model,cur,xs,j)
                    bp=bl.argmax(1); pp=pl.argmax(1)
                    logits.append(pl.clone()); preds.append(pp.clone())
                    bc=(bp==jt); pc=(pp==jt)
                    if j!=q:
                        opp+=int(bc.sum()); new+=int((bc & (~pc)).sum()); rep+=int(((~bc)&pc).sum())
                qacc=float((preds[q]==target).float().mean())
                aggregate[dose]+=new; universal[dose]=universal[dose] and (qacc>=TH)
                if dose==1:
                    d1_preds=[p.clone() for p in preds]; changes=[0]*7
                else:
                    changes=[int((preds[j]!=d1_preds[j]).sum()) for j in range(7)]
                    any_decision_change=any_decision_change or any(v>0 for v in changes)
                    transitions.append({
                        "from_dose":dose-1,"to_dose":dose,
                        "state_equal":bool(torch.equal(prev_state,cur)),
                        "state_max_abs_delta":max_abs(prev_state,cur),
                        "state_changed_elements":changed(prev_state,cur),
                        "logit_equal_by_binding":[bool(torch.equal(prev_logits[j],logits[j])) for j in range(7)],
                        "logit_max_abs_delta_by_binding":[max_abs(prev_logits[j],logits[j]) for j in range(7)],
                    })
                dose_rows.append({
                    "dose":dose,"target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "collateral_baseline_correct_opportunities":opp,
                    "collateral_new_error_count":new,"collateral_repair_count":rep,
                    "decision_changes_vs_dose1_by_binding":changes
                })
                prev_state=cur.clone(); prev_logits=[z.clone() for z in logits]
            stable_from=None
            for k in range(1,64):
                if all(t["state_equal"] for t in transitions if t["from_dose"]>=k):
                    stable_from=k; break
            strata.append({"query_position":q,"count":count,"doses":dose_rows,"transitions":transitions,"exact_state_stable_from_dose":stable_from})
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    anchor=all(universal[d] and aggregate[d]==3724 for d in range(1,17)) and not any(
        any(v>0 for v in d["decision_changes_vs_dose1_by_binding"])
        for s in flat for d in s["doses"][:16]
    )
    fixed_candidates=[k for k in range(1,64) if all(s["exact_state_stable_from_dose"] is not None and s["exact_state_stable_from_dose"]<=k for s in flat)]
    fixed_from=fixed_candidates[0] if fixed_candidates else None
    behavior_same=all(universal[d] and aggregate[d]==aggregate[1] for d in DOSES) and not any_decision_change
    if not anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif fixed_from is not None: cat="EXACT_FIXED_POINT_REACHED_BY_64"
    elif behavior_same: cat="NUMERIC_TAIL_DECISION_INVARIANT_THROUGH_64"
    else: cat="BEHAVIOR_CHANGES_BY_64"
    return {"rows":rows,"aggregate_collateral_new_errors":aggregate,"universal_target":universal,
            "inherited_anchor":anchor,"any_decision_change":any_decision_change,
            "universal_exact_fixed_from_dose":fixed_from,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "doses_1_to_64_exact":all([d["dose"] for d in s["doses"]]==DOSES for r in a["rows"] for s in r["strata"]),
        "sixty_three_transitions_each":all(len(s["transitions"])==63 for r in a["rows"] for s in r["strata"]),
        "all_seven_decisions_inspected":all(all(len(d["decision_changes_vs_dose1_by_binding"])==7 for d in s["doses"]) for r in a["rows"] for s in r["strata"]),
        "all_seven_logits_inspected":all(all(len(t["logit_equal_by_binding"])==7 and len(t["logit_max_abs_delta_by_binding"])==7 for t in s["transitions"]) for r in a["rows"] for s in r["strata"]),
        "b54_inherited_anchor_exact":a["inherited_anchor"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"EXACT_FIXED_POINT_REACHED_BY_64","NUMERIC_TAIL_DECISION_INVARIANT_THROUGH_64","BEHAVIOR_CHANGES_BY_64","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B55","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B55_TARGET_REFRESH_DOSE64":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
