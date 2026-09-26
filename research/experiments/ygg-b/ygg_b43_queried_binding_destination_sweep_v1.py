#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b42_reciprocal_direction_decomposition_v1 as b42

PREREG="25f8fd2477bcd441e44364aacc743131a5b435e3"
PARENT_RUN="36273730650"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4,5]
DESTS=[0,1,2,3,4,5,6]
TH=.90

torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def parking(q,d):
    if d==6:
        return (q+1)%6
    for p in range(6):
        if p!=q and p!=d:
            return p
    raise AssertionError("no parking position")

def relocate(x,q,d,p):
    z=x.clone(); src=x.clone()
    z[:,4*d:4*d+4]=src[:,4*q:4*q+4]
    z[:,4*p:4*p+4]=src[:,4*d:4*d+4]
    z[:,4*q:4*q+4]=src[:,4*p:4*p+4]
    return z

def acc(m,x,y,qev,pos):
    m.eval()
    with torch.no_grad():
        pred=b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.immediate_read1_logits(m,x).argmax(1)
    mask=qev==pos
    if int(mask.sum())<=0: raise AssertionError("empty query stratum")
    return float((pred[mask]==y[mask]).float().mean()),int(mask.sum())

def ms(x,r):
    return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,qev,*_=data
        m=b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        strata=[]
        for q in QPOS:
            original,count=acc(m,x,y,qev,q)
            arms=[]
            for d in DESTS:
                if d==q: continue
                p=parking(q,d)
                z=relocate(x,q,d,p)
                a,_=acc(m,z,y,qev,q)
                arms.append({
                    "destination":d,"parking":p,"accuracy":a,"capable":a>=TH,
                    "multiset_preserved":all(ms(x,r)==ms(z,r) for r in range(x.shape[0])),
                })
            strata.append({"query_position":q,"count":count,"original":original,"arms":arms})
        rows.append({"seed":seed,"strata":strata})

    universal={}
    counts={}
    for d in DESTS:
        eligible=[a for r in rows for s in r["strata"] for a in s["arms"] if a["destination"]==d]
        counts[str(d)]={"capable":sum(a["capable"] for a in eligible),"total":len(eligible)}
        universal[d]=len(eligible)>0 and all(a["capable"] for a in eligible)

    if not universal[6]:
        cat="ANCHOR_NOT_REPRODUCED"
    elif all(universal[d] for d in DESTS):
        cat="POSITION_INVARIANT"
    elif any(universal[d] for d in DESTS if d!=6):
        cat="RECENCY_BAND"
    elif universal[6]:
        cat="LATEST_ONLY"
    else:
        cat="PARTIAL_POSITION_PATTERN"
    return {"rows":rows,"universal_by_destination":{str(k):v for k,v in universal.items()},"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    flat=[(s,a0) for r in a["rows"] for s in r["strata"] for a0 in s["arms"]]
    d6=[a0 for s,a0 in flat if a0["destination"]==6]
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "destination_set_exact":all(sorted(a0["destination"] for a0 in s["arms"])==[d for d in DESTS if d!=s["query_position"]] for r in a["rows"] for s in r["strata"]),
        "parking_rule_exact":all(
            a0["parking"]==parking(s["query_position"],a0["destination"]) and
            a0["parking"]!=s["query_position"] and a0["parking"]!=a0["destination"] and a0["parking"]!=6
            for s,a0 in flat
        ),
        "all_query_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "threshold_exact":TH==.90,
        "state_exact":b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b42_d6_endpoints_reproduced":len(d6)==30 and all(abs(a0["accuracy"]-1.0)<1e-12 for a0 in d6),
        "multiset_preserved":all(a0["multiset_preserved"] for _,a0 in flat),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"LATEST_ONLY","RECENCY_BAND","POSITION_INVARIANT","PARTIAL_POSITION_PATTERN","ANCHOR_NOT_REPRODUCED"}
    out={
        "schema":1,"experiment":"YGG-B43","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_B43_QUERIED_BINDING_DESTINATION_SWEEP":all(validity.values()) and a["classification"] in allowed,"classification":a["classification"]},
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))
if __name__=="__main__": main()
