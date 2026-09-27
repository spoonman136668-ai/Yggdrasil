#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b49_two_write_restorative_replay_v1 as b49

PREREG="8d041aee46c6242d0b5513ddcc7d43c02e719358"
PARENT_RUN="36304394733"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
b48=b49.b48
b47=b48.b47
b46=b47.b46
b27=b47.b27
b29=b47.b29
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def common_counts(model,baseline,post,x,q,r):
    new=rep=opp=0
    for j in range(7):
        if j in (q,r): continue
        target=x[:,4*j+3]-b27.VALUE_BASE
        with torch.no_grad():
            bp=b46.query_logits(model,baseline,x,j).argmax(1)
            pp=b46.query_logits(model,post,x,j).argmax(1)
        bc=(bp==target); pc=(pp==target)
        opp+=int(bc.sum())
        new+=int((bc & (~pc)).sum())
        rep+=int(((~bc)&pc).sum())
    return opp,new,rep

def one():
    rows=[]
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M=b46.build_memory(model,x)
        strata=[]
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B50 empty q")
            xs=x[mask]; Ms=M[mask]
            with torch.no_grad(): Mt=b46.refresh(model,Ms,xs,q)
            target=xs[:,4*q+3]-b27.VALUE_BASE
            with torch.no_grad(): tp=b46.query_logits(model,Mt,xs,q).argmax(1)
            target_only_acc=float((tp==target).float().mean())
            seconds=[]
            for r in range(7):
                if r==q: continue
                with torch.no_grad(): M2=b46.refresh(model,Mt,xs,r)
                with torch.no_grad(): qp=b46.query_logits(model,M2,xs,q).argmax(1)
                qacc=float((qp==target).float().mean())
                opp1,new1,rep1=common_counts(model,Ms,Mt,xs,q,r)
                opp2,new2,rep2=common_counts(model,Ms,M2,xs,q,r)
                if opp1!=opp2: raise AssertionError("common baseline opportunities drift")
                seconds.append({
                    "second_replay_identity":r,
                    "target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "target_only_common_new_errors":new1,
                    "two_write_common_new_errors":new2,
                    "common_baseline_correct_opportunities":opp1,
                    "target_only_common_repairs":rep1,
                    "two_write_common_repairs":rep2,
                    "new_error_delta_two_minus_one":new2-new1,
                })
            strata.append({
                "query_position":q,"count":count,
                "target_only_accuracy":target_only_acc,
                "target_only_capable":target_only_acc>=TH,
                "seconds":seconds
            })
        rows.append({"seed":seed,"strata":strata})

    flat=[s for row in rows for s in row["strata"]]
    anchor=all(s["target_only_capable"] for s in flat)
    rule_summary=[]
    for r in range(7):
        eligible=[s for s in flat if s["query_position"]!=r]
        arms=[next(x for x in s["seconds"] if x["second_replay_identity"]==r) for s in eligible]
        universal_target=all(x["target_capable"] for x in arms)
        one_total=sum(x["target_only_common_new_errors"] for x in arms)
        two_total=sum(x["two_write_common_new_errors"] for x in arms)
        no_worse=all(x["two_write_common_new_errors"]<=x["target_only_common_new_errors"] for x in arms)
        rule_summary.append({
            "second_replay_identity":r,
            "eligible_strata":len(arms),
            "universal_target":universal_target,
            "target_only_common_new_errors":one_total,
            "two_write_common_new_errors":two_total,
            "aggregate_reduction":two_total<one_total,
            "no_stratum_worse":no_worse
        })
    strict=[x["second_replay_identity"] for x in rule_summary if x["universal_target"] and x["aggregate_reduction"] and x["no_stratum_worse"]]
    aggregate=[x["second_replay_identity"] for x in rule_summary if x["universal_target"] and x["aggregate_reduction"]]
    all_target_lost=all(not x["universal_target"] for x in rule_summary)
    if not anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif strict: cat="STRICT_RESTORATIVE_IDENTITY_EXISTS"
    elif aggregate: cat="AGGREGATE_RESTORATIVE_IDENTITY_EXISTS"
    elif all_target_lost: cat="TARGET_RESCUE_LOST_FOR_ALL_SECOND_IDENTITIES"
    else: cat="NO_RESTORATIVE_SECOND_IDENTITY"
    return {"rows":rows,"rule_summary":rule_summary,"strict_rules":strict,"aggregate_rules":aggregate,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "six_second_identities_each":all(len(s["seconds"])==6 for r in a["rows"] for s in r["strata"]),
        "second_identities_exact":all(sorted(x["second_replay_identity"] for x in s["seconds"])==[r for r in range(7) if r!=s["query_position"]] for row in a["rows"] for s in row["strata"]),
        "target_only_anchor_exact":all(s["target_only_capable"] for row in a["rows"] for s in row["strata"]),
        "common_panels_exact":all(x["common_baseline_correct_opportunities"]>=0 for row in a["rows"] for s in row["strata"] for x in s["seconds"]),
        "exact_150_second_replay_arms":sum(len(s["seconds"]) for row in a["rows"] for s in row["strata"])==150,
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"STRICT_RESTORATIVE_IDENTITY_EXISTS","AGGREGATE_RESTORATIVE_IDENTITY_EXISTS","NO_RESTORATIVE_SECOND_IDENTITY","TARGET_RESCUE_LOST_FOR_ALL_SECOND_IDENTITIES","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B50","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B50_SECOND_REPLAY_IDENTITY_SWEEP":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
