#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b44_recency_band_parking_robustness_v1 as b44

PREREG="7a781c7a48cd944da39916f3e9f3f58bfb058b22"
PARENT_RUN="36277246562"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4,5]
DESTS=[5,6]
TH=.90

torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def rotations(xs):
    out=[]
    xs=list(xs)
    out.append(tuple(xs))
    for k in range(1,6):
        out.append(tuple(xs[k:]+xs[:k]))
    rev=list(reversed(xs))
    out.append(tuple(rev))
    for k in range(1,6):
        out.append(tuple(rev[k:]+rev[:k]))
    if len(out)!=12 or len(set(out))!=12:
        raise AssertionError("B45 order family")
    return out

def reorder(x,q,d,source_order):
    z=x.clone(); src=x.clone()
    z[:,4*d:4*d+4]=src[:,4*q:4*q+4]
    dests=[i for i in range(7) if i!=d]
    if len(source_order)!=6: raise AssertionError("source order len")
    for dest,source in zip(dests,source_order):
        z[:,4*dest:4*dest+4]=src[:,4*source:4*source+4]
    return z

def acc(m,x,y):
    m.eval()
    with torch.no_grad():
        pred=b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.immediate_read1_logits(m,x).argmax(1)
    return float((pred==y).float().mean())

def ms(x,r):
    return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))

def one():
    parent=b44.one()
    rows=[]
    anchor_checks=[]
    for seed in SEEDS:
        data=list(b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,qev,*_=data
        m=b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        prow=next(r for r in parent["rows"] if r["seed"]==seed)
        strata=[]
        for q in QPOS:
            mask=qev==q
            if int(mask.sum())<=0: raise AssertionError("empty query stratum")
            xs=x[mask].clone(); ys=y[mask].clone()
            ps=next(s for s in prow["strata"] if s["query_position"]==q)
            arms=[]
            for d in DESTS:
                if d==q: continue
                sources=[i for i in range(7) if i!=q]
                fam=rotations(sources)
                for oi,order in enumerate(fam):
                    z=reorder(xs,q,d,order)
                    a=acc(m,z,ys)
                    arms.append({
                        "destination":d,"order_index":oi,"source_order":list(order),
                        "accuracy":a,"capable":a>=TH,
                        "queried_at_destination":True,
                        "multiset_preserved":all(ms(xs,r)==ms(z,r) for r in range(xs.shape[0])),
                    })

                # reproduce exact B44 designated-parking anchor
                if d==6:
                    p=(q+1)%6
                else:
                    p=next(p0 for p0 in range(6) if p0!=q and p0!=d)
                za=b44.relocate(xs,q,d,p)
                aa=acc(m,za,ys)
                pa=next(a0 for a0 in ps["arms"] if a0["destination"]==d and a0["parking"]==p)
                exact=abs(aa-pa["accuracy"])<1e-12
                anchor_checks.append({
                    "seed":seed,"query_position":q,"destination":d,"parking":p,
                    "expected":pa["accuracy"],"actual":aa,"exact":exact
                })
            strata.append({"query_position":q,"count":int(mask.sum()),"arms":arms})
        rows.append({"seed":seed,"strata":strata})

    bydest={}
    for d in DESTS:
        arr=[a for r in rows for s in r["strata"] for a in s["arms"] if a["destination"]==d]
        bydest[str(d)]={
            "capable":sum(a["capable"] for a in arr),
            "total":len(arr),
            "universal":bool(arr) and all(a["capable"] for a in arr),
            "mixed":any(a["capable"] for a in arr) and any(not a["capable"] for a in arr),
            "min_accuracy":min(a["accuracy"] for a in arr),
            "max_accuracy":max(a["accuracy"] for a in arr),
        }

    anchors_ok=parent["classification"]=="ROBUST_TWO_POSITION_RECENCY_BAND" and all(x["exact"] for x in anchor_checks)
    u5=bydest["5"]["universal"]; u6=bydest["6"]["universal"]
    if not anchors_ok:
        cat="ANCHOR_NOT_REPRODUCED"
    elif u5 and u6:
        cat="FULL_BACKGROUND_ORDER_ROBUST_RECENCY"
    elif (not u5) and u6:
        cat="LATEST_ONLY_BACKGROUND_ORDER_ROBUST"
    elif bydest["5"]["mixed"] or bydest["6"]["mixed"]:
        cat="BACKGROUND_ORDER_SENSITIVE_RECENCY"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"parent_classification":parent["classification"],"rows":rows,"by_destination":bydest,"anchor_checks":anchor_checks,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    flat=[(s,x) for r in a["rows"] for s in r["strata"] for x in s["arms"]]
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "destination_set_exact":all(set(x["destination"] for x in s["arms"])==set(d for d in DESTS if d!=s["query_position"]) for r in a["rows"] for s in r["strata"]),
        "order_family_exact":all(
            sorted(x["order_index"] for x in s["arms"] if x["destination"]==d)==list(range(12))
            for r in a["rows"] for s in r["strata"] for d in DESTS if d!=s["query_position"]
        ),
        "all_query_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "threshold_exact":TH==.90,
        "state_exact":b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b44.b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b44_designated_parking_anchors_exact":a["parent_classification"]=="ROBUST_TWO_POSITION_RECENCY_BAND" and all(x["exact"] for x in a["anchor_checks"]),
        "queried_binding_destination_exact":all(x["queried_at_destination"] for _,x in flat),
        "multiset_preserved":all(x["multiset_preserved"] for _,x in flat),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"FULL_BACKGROUND_ORDER_ROBUST_RECENCY","LATEST_ONLY_BACKGROUND_ORDER_ROBUST","BACKGROUND_ORDER_SENSITIVE_RECENCY","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,"experiment":"YGG-B45","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_B45_RECENCY_BAND_BACKGROUND_ORDER":all(validity.values()) and a["classification"] in allowed,"classification":a["classification"]},
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__": main()
