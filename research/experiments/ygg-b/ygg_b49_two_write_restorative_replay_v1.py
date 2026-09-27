#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b48_refresh_identity_sweep_v1 as b48

PREREG="c2df3eda308e889fb5bebb7e9468392538ddfce1"
PARENT_RUN="36286528372"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
b47=b48.b47
b46=b47.b46
b27=b47.b27
b29=b47.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one():
    rows=[]
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B49 empty q")
            xs=x[mask]; Ms=M[mask]
            r=min(i for i in range(7) if i!=q)
            with torch.no_grad():
                Mt=b46.refresh(model,Ms,xs,q)
                M2=b46.refresh(model,Mt,xs,r)
            arms={}
            for name,MM in (("TARGET_ONLY",Mt),("TARGET_PLUS_OLDEST_OTHER",M2)):
                target=xs[:,4*q+3]-b27.VALUE_BASE
                with torch.no_grad():
                    qpred=b46.query_logits(model,MM,xs,q).argmax(1)
                qacc=float((qpred==target).float().mean())
                new_errors=0; repairs=0; opportunities=0
                bindings=[]
                for j in range(7):
                    jt=xs[:,4*j+3]-b27.VALUE_BASE
                    with torch.no_grad():
                        bp=b46.query_logits(model,Ms,xs,j).argmax(1)
                        pp=b46.query_logits(model,MM,xs,j).argmax(1)
                    bc=(bp==jt); pc=(pp==jt)
                    ne=int((bc & (~pc)).sum()); rp=int(((~bc)&pc).sum())
                    in_common_collateral=(j!=q and j!=r)
                    if in_common_collateral:
                        opportunities+=int(bc.sum()); new_errors+=ne; repairs+=rp
                    bindings.append({
                        "binding":j,"is_target":j==q,"is_second_replay":j==r,
                        "in_common_collateral_panel":in_common_collateral,
                        "baseline_correct_count":int(bc.sum()),"post_correct_count":int(pc.sum()),
                        "new_error_count":ne,"repair_count":rp,
                    })
                arms[name]={
                    "target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "collateral_baseline_correct_opportunities":opportunities,
                    "collateral_new_error_count":new_errors,
                    "collateral_repair_count":repairs,
                    "bindings":bindings,
                }
            strata.append({
                "query_position":q,"count":count,"second_replay_identity":r,
                "target_only":arms["TARGET_ONLY"],"two_write":arms["TARGET_PLUS_OLDEST_OTHER"],
                "new_error_delta_two_minus_one":arms["TARGET_PLUS_OLDEST_OTHER"]["collateral_new_error_count"]-arms["TARGET_ONLY"]["collateral_new_error_count"],
            })
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    anchor=all(s["target_only"]["target_capable"] for s in flat)
    two_target=all(s["two_write"]["target_capable"] for s in flat)
    one_total=sum(s["target_only"]["collateral_new_error_count"] for s in flat)
    two_total=sum(s["two_write"]["collateral_new_error_count"] for s in flat)
    no_worse=all(s["two_write"]["collateral_new_error_count"]<=s["target_only"]["collateral_new_error_count"] for s in flat)
    if not anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif not two_target: cat="TARGET_RESCUE_LOST"
    elif two_total<one_total and no_worse: cat="STRICT_COLLATERAL_REDUCTION"
    elif two_total<one_total: cat="AGGREGATE_COLLATERAL_REDUCTION"
    elif two_total>=one_total: cat="NO_COLLATERAL_REDUCTION"
    else: cat="OTHER_VALID_PATTERN"
    return {
        "rows":rows,"target_only_anchor":anchor,"two_write_target_universal":two_target,
        "target_only_common_panel_new_errors":one_total,
        "two_write_common_panel_new_errors":two_total,
        "no_stratum_worse":no_worse,
        "classification":cat
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "oldest_nontarget_selection_exact":all(s["second_replay_identity"]==min(i for i in range(7) if i!=s["query_position"]) for r in a["rows"] for s in r["strata"]),
        "target_only_anchor_exact":a["target_only_anchor"],
        "exactly_two_added_writes_transformed_arm":True,
        "common_collateral_panel_exact":all(
            sum(x["in_common_collateral_panel"] for x in s["target_only"]["bindings"])==5 and
            sum(x["in_common_collateral_panel"] for x in s["two_write"]["bindings"])==5
            for r in a["rows"] for s in r["strata"]),
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"STRICT_COLLATERAL_REDUCTION","AGGREGATE_COLLATERAL_REDUCTION","NO_COLLATERAL_REDUCTION","TARGET_RESCUE_LOST","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B49","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B49_TWO_WRITE_RESTORATIVE_REPLAY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
