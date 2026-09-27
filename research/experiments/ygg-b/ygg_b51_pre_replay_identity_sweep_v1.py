#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b50_second_replay_identity_sweep_v1 as b50

PREREG="f022ae36221a5e9aead6cf4658e62e29febbe4b7"
PARENT_RUN="36307035998"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
TH=.90
b49=b50.b49
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
            if count<=0: raise AssertionError("B51 empty q")
            xs=x[mask]; Ms=M[mask]
            with torch.no_grad(): Mt=b46.refresh(model,Ms,xs,q)
            target=xs[:,4*q+3]-b27.VALUE_BASE
            with torch.no_grad(): tp=b46.query_logits(model,Mt,xs,q).argmax(1)
            target_only_acc=float((tp==target).float().mean())
            pres=[]
            for r in range(7):
                if r==q: continue
                with torch.no_grad():
                    Mr=b46.refresh(model,Ms,xs,r)
                    M2=b46.refresh(model,Mr,xs,q)
                    qp=b46.query_logits(model,M2,xs,q).argmax(1)
                qacc=float((qp==target).float().mean())
                opp1,new1,rep1=common_counts(model,Ms,Mt,xs,q,r)
                opp2,new2,rep2=common_counts(model,Ms,M2,xs,q,r)
                if opp1!=opp2: raise AssertionError("common opportunities drift")
                pres.append({
                    "pre_replay_identity":r,
                    "target_query_accuracy":qacc,"target_capable":qacc>=TH,
                    "target_only_common_new_errors":new1,
                    "pre_plus_target_common_new_errors":new2,
                    "common_baseline_correct_opportunities":opp1,
                    "target_only_common_repairs":rep1,
                    "pre_plus_target_common_repairs":rep2,
                    "new_error_delta_pre_plus_target_minus_target_only":new2-new1,
                })
            strata.append({
                "query_position":q,"count":count,"target_only_accuracy":target_only_acc,
                "target_only_capable":target_only_acc>=TH,"pre_replays":pres
            })
        rows.append({"seed":seed,"strata":strata})
    flat=[s for row in rows for s in row["strata"]]
    anchor=all(s["target_only_capable"] for s in flat)
    rules=[]
    for r in range(7):
        eligible=[s for s in flat if s["query_position"]!=r]
        arms=[next(x for x in s["pre_replays"] if x["pre_replay_identity"]==r) for s in eligible]
        universal=all(x["target_capable"] for x in arms)
        one_total=sum(x["target_only_common_new_errors"] for x in arms)
        two_total=sum(x["pre_plus_target_common_new_errors"] for x in arms)
        no_worse=all(x["pre_plus_target_common_new_errors"]<=x["target_only_common_new_errors"] for x in arms)
        rules.append({
            "pre_replay_identity":r,"eligible_strata":len(arms),"universal_target":universal,
            "target_only_common_new_errors":one_total,"pre_plus_target_common_new_errors":two_total,
            "aggregate_reduction":two_total<one_total,"no_stratum_worse":no_worse
        })
    strict=[x["pre_replay_identity"] for x in rules if x["universal_target"] and x["aggregate_reduction"] and x["no_stratum_worse"]]
    aggregate=[x["pre_replay_identity"] for x in rules if x["universal_target"] and x["aggregate_reduction"]]
    all_lost=all(not x["universal_target"] for x in rules)
    if not anchor: cat="ANCHOR_NOT_REPRODUCED"
    elif strict: cat="STRICT_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS"
    elif aggregate: cat="AGGREGATE_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS"
    elif all_lost: cat="TARGET_RESCUE_LOST_FOR_ALL_PRE_REPLAY_IDENTITIES"
    else: cat="NO_RESTORATIVE_PRE_REPLAY_IDENTITY"
    return {"rows":rows,"rule_summary":rules,"strict_rules":strict,"aggregate_rules":aggregate,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "six_pre_identities_each":all(len(s["pre_replays"])==6 for r in a["rows"] for s in r["strata"]),
        "pre_identities_exact":all(sorted(x["pre_replay_identity"] for x in s["pre_replays"])==[r for r in range(7) if r!=s["query_position"]] for row in a["rows"] for s in row["strata"]),
        "target_only_anchor_exact":all(s["target_only_capable"] for row in a["rows"] for s in row["strata"]),
        "exact_150_pre_replay_arms":sum(len(s["pre_replays"]) for row in a["rows"] for s in row["strata"])==150,
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"STRICT_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS","AGGREGATE_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS","NO_RESTORATIVE_PRE_REPLAY_IDENTITY","TARGET_RESCUE_LOST_FOR_ALL_PRE_REPLAY_IDENTITIES","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B51","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B51_PRE_REPLAY_IDENTITY_SWEEP":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
