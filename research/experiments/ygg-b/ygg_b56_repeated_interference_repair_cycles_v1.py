#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b55_target_refresh_dose64_v1 as b55

PREREG="e55672c6f238c5f03d2d57076c76c993a0057f93"
PARENT_RUN="36322933593"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
CYCLES=[1,2,3,4]
TH=.90

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

def score(model,baseline,current,xs,q,initial_preds=None):
    target=xs[:,4*q+3]-b27.VALUE_BASE
    preds=[]; opp=new=rep=0
    for j in range(7):
        jt=xs[:,4*j+3]-b27.VALUE_BASE
        with torch.no_grad():
            bl=b46.query_logits(model,baseline,xs,j)
            pl=b46.query_logits(model,current,xs,j)
        bp=bl.argmax(1); pp=pl.argmax(1); preds.append(pp.clone())
        bc=(bp==jt); pc=(pp==jt)
        if j!=q:
            opp+=int(bc.sum()); new+=int((bc & (~pc)).sum()); rep+=int(((~bc)&pc).sum())
    qacc=float((preds[q]==target).float().mean())
    changes=None if initial_preds is None else [int((preds[j]!=initial_preds[j]).sum()) for j in range(7)]
    return {
        "target_accuracy":qacc,"target_capable":qacc>=TH,
        "collateral_baseline_correct_opportunities":opp,
        "collateral_new_errors":new,"collateral_repairs":rep,
        "decision_changes_vs_initial_repair":changes,
    },preds

def one():
    rows=[]
    all_initial_ok=True; all_post_interference_capable=True; all_post_repair_capable=True
    all_post_repair_equal=True
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B56 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): initial_state=b46.refresh(model,base,xs,q)
            initial,initial_preds=score(model,base,initial_state,xs,q)
            all_initial_ok=all_initial_ok and initial["target_capable"]
            competitors=[]
            for r in range(7):
                if r==q: continue
                cur=initial_state.clone()
                cycles=[]
                for cycle in CYCLES:
                    with torch.no_grad(): after_r=b46.refresh(model,cur,xs,r)
                    inter,_=score(model,base,after_r,xs,q,initial_preds)
                    all_post_interference_capable=all_post_interference_capable and inter["target_capable"]
                    with torch.no_grad(): after_q=b46.refresh(model,after_r,xs,q)
                    repaired,_=score(model,base,after_q,xs,q,initial_preds)
                    all_post_repair_capable=all_post_repair_capable and repaired["target_capable"]
                    equal=(repaired["collateral_new_errors"]==initial["collateral_new_errors"] and
                           repaired["collateral_repairs"]==initial["collateral_repairs"] and
                           repaired["decision_changes_vs_initial_repair"]==[0]*7)
                    all_post_repair_equal=all_post_repair_equal and equal
                    cycles.append({
                        "cycle":cycle,"post_interference":inter,"post_repair":repaired,
                        "post_repair_equal_initial":equal
                    })
                    cur=after_q
                competitors.append({"competing_identity":r,"cycles":cycles})
            strata.append({"query_position":q,"count":count,"initial_repair":initial,"competitors":competitors})
        rows.append({"seed":seed,"strata":strata})
    if not all_initial_ok: cat="ANCHOR_NOT_REPRODUCED"
    elif all_post_interference_capable: cat="NO_INTERFERENCE_TO_REPAIR"
    elif not all_post_repair_capable: cat="REPAIR_EVENTUALLY_FAILS"
    elif all_post_repair_equal: cat="REPEATABLE_TARGET_REPAIR_STABLE"
    else: cat="REPEATABLE_TARGET_REPAIR_WITH_COLLATERAL_DRIFT"
    return {
        "rows":rows,
        "all_initial_anchor":all_initial_ok,
        "all_post_interference_target_capable":all_post_interference_capable,
        "all_post_repair_target_capable":all_post_repair_capable,
        "all_post_repair_equal_initial":all_post_repair_equal,
        "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "six_competitors_each":all(len(s["competitors"])==6 for r in a["rows"] for s in r["strata"]),
        "competitor_identities_exact":all(
            sorted(c["competing_identity"] for c in s["competitors"])==[r for r in range(7) if r!=s["query_position"]]
            for row in a["rows"] for s in row["strata"]),
        "four_cycles_each":all([x["cycle"] for x in c["cycles"]]==CYCLES for r in a["rows"] for s in r["strata"] for c in s["competitors"]),
        "initial_anchor_exact":a["all_initial_anchor"],
        "exact_600_cycles":sum(len(c["cycles"]) for r in a["rows"] for s in r["strata"] for c in s["competitors"])==600,
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"REPEATABLE_TARGET_REPAIR_STABLE","REPEATABLE_TARGET_REPAIR_WITH_COLLATERAL_DRIFT","REPAIR_EVENTUALLY_FAILS","NO_INTERFERENCE_TO_REPAIR","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B56","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B56_REPEATED_INTERFERENCE_REPAIR_CYCLES":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
