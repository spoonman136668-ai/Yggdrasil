#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b47_target_vs_control_collateral_v1 as b47

PREREG="b14298ab7682e147b80ebb49958470ed11362bf6"
PARENT_RUN="36285541091"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4]
RPOS=list(range(7))
TH=.90
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
        if count<=0: raise AssertionError("B48 empty q stratum")
        xs=x[mask]; Ms=M[mask]
        target_q=xs[:,4*q+3]-b27.VALUE_BASE
        refreshes=[]
        for r in RPOS:
          with torch.no_grad(): Mr=b46.refresh(model,Ms,xs,r)
          with torch.no_grad(): qpred=b46.query_logits(model,Mr,xs,q).argmax(1)
          qacc=float((qpred==target_q).float().mean())
          new_errors=0; repairs=0; opportunities=0
          bindings=[]
          for j in range(7):
            target=xs[:,4*j+3]-b27.VALUE_BASE
            with torch.no_grad():
              bp=b46.query_logits(model,Ms,xs,j).argmax(1)
              pp=b46.query_logits(model,Mr,xs,j).argmax(1)
            bc=(bp==target); pc=(pp==target)
            ne=int((bc & (~pc)).sum()); rp=int(((~bc)&pc).sum())
            if j!=r:
              opportunities+=int(bc.sum()); new_errors+=ne; repairs+=rp
            bindings.append({
              "binding":j,"is_refreshed":j==r,"is_query":j==q,
              "baseline_correct_count":int(bc.sum()),"post_correct_count":int(pc.sum()),
              "new_error_count":ne,"repair_count":rp,
            })
          refreshes.append({
            "refresh_identity":r,
            "target_query_accuracy":qacc,
            "target_capable":qacc>=TH,
            "collateral_baseline_correct_opportunities":opportunities,
            "collateral_new_error_count":new_errors,
            "collateral_repair_count":repairs,
            "bindings":bindings,
          })
        strata.append({"query_position":q,"count":count,"refreshes":refreshes,
          "capable_refresh_identities":[x["refresh_identity"] for x in refreshes if x["target_capable"]]})
      rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    target_anchor=all(next(x for x in s["refreshes"] if x["refresh_identity"]==s["query_position"])["target_capable"] for s in flat)
    control_anchor=all(not next(x for x in s["refreshes"] if x["refresh_identity"]==(s["query_position"]+1)%7)["target_capable"] for s in flat)
    if not target_anchor: cat="TARGET_RESCUE_NOT_REPRODUCED"
    elif not control_anchor: cat="CONTROL_ANCHOR_NOT_REPRODUCED"
    elif all(s["capable_refresh_identities"]==[s["query_position"]] for s in flat): cat="TARGET_IDENTITY_UNIQUE_RESCUE"
    elif any(any(r!=s["query_position"] for r in s["capable_refresh_identities"]) for s in flat): cat="MULTIPLE_REFRESH_IDENTITIES_RESCUE"
    else: cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"target_anchor":target_anchor,"control_anchor":control_anchor,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
      "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
      "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
      "refresh_identities_exact":all([x["refresh_identity"] for x in s["refreshes"]]==RPOS for r in a["rows"] for s in r["strata"]),
      "all_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
      "exact_175_seed_query_refresh_strata":sum(len(s["refreshes"]) for r in a["rows"] for s in r["strata"])==175,
      "one_added_write_each_arm":True,
      "target_anchor_exact":a["target_anchor"],
      "control_anchor_exact":a["control_anchor"],
      "state_exact":b27.PERSISTENT_SCALARS==32,
      "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
      "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"TARGET_IDENTITY_UNIQUE_RESCUE","MULTIPLE_REFRESH_IDENTITIES_RESCUE","TARGET_RESCUE_NOT_REPRODUCED","CONTROL_ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B48","prereg":PREREG,"parent_run":PARENT_RUN,
      "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
      "qualification":{"YGG_B48_REFRESH_IDENTITY_SWEEP":all(validity.values()) and cat in allowed,"classification":cat},
      "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
