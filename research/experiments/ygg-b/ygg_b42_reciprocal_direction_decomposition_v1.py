#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b41_source6_query_relative_alignment_v1 as b41

PREREG="4421363966615f85a7b7b2cdda3c5ae010d0acb2"
PARENT_RUN="36272095308"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4,5]
SOURCE=6
TH=.90

torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def set_blocks(x, assignments):
    z=x.clone()
    src=x.clone()
    for dest,source in assignments.items():
        z[:,4*dest:4*dest+4]=src[:,4*source:4*source+4]
    return z

def reciprocal(x,q):
    return set_blocks(x,{q:6,6:q})

def target_to_latest_only(x,q,p):
    return set_blocks(x,{6:q,p:6,q:p})

def source6_to_query_only(x,q,p):
    return set_blocks(x,{q:6,p:q,6:p})

def acc(m,x,y,qev,pos):
    m.eval()
    with torch.no_grad():
        p=b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.immediate_read1_logits(m,x).argmax(1)
    mask=qev==pos
    if int(mask.sum())<=0: raise AssertionError("empty query stratum")
    return float((p[mask]==y[mask]).float().mean()),int(mask.sum())

def ms(x,r):
    return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,qev,*_=data
        m=b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        strata=[]
        for q in QPOS:
            p=(q+1)%6
            zr=reciprocal(x,q)
            za=target_to_latest_only(x,q,p)
            zb=source6_to_query_only(x,q,p)
            original,count=acc(m,x,y,qev,q)
            ar,_=acc(m,zr,y,qev,q)
            aa,_=acc(m,za,y,qev,q)
            ab,_=acc(m,zb,y,qev,q)
            strata.append({
                "query_position":q,"parking_position":p,"count":count,
                "original":original,
                "reciprocal":ar,
                "target_to_latest_only":aa,
                "source6_to_query_only":ab,
                "reciprocal_capable":ar>=TH,
                "target_to_latest_only_capable":aa>=TH,
                "source6_to_query_only_capable":ab>=TH,
                "reciprocal_multiset_preserved":all(ms(x,r)==ms(zr,r) for r in range(x.shape[0])),
                "target_to_latest_multiset_preserved":all(ms(x,r)==ms(za,r) for r in range(x.shape[0])),
                "source6_to_query_multiset_preserved":all(ms(x,r)==ms(zb,r) for r in range(x.shape[0])),
            })
        rows.append({"seed":seed,"strata":strata})
    flat=[s for r in rows for s in r["strata"]]
    recip=all(s["reciprocal_capable"] for s in flat)
    a=all(s["target_to_latest_only_capable"] for s in flat)
    b=all(s["source6_to_query_only_capable"] for s in flat)
    if not recip: cat="ANCHOR_NOT_REPRODUCED"
    elif a and not b: cat="TARGET_TO_LATEST_SUFFICIENT"
    elif b and not a: cat="SOURCE6_TO_QUERY_SUFFICIENT"
    elif a and b: cat="BOTH_DIRECTIONS_SUFFICIENT"
    elif not a and not b: cat="JOINT_RECIPROCAL_REQUIRED"
    else: cat="PARTIAL_DIRECTIONAL_PATTERN"
    counts={
        "reciprocal":sum(s["reciprocal_capable"] for s in flat),
        "target_to_latest_only":sum(s["target_to_latest_only_capable"] for s in flat),
        "source6_to_query_only":sum(s["source6_to_query_only_capable"] for s in flat),
        "total_strata":len(flat),
    }
    return {"rows":rows,"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    flat=[s for r in a["rows"] for s in r["strata"]]
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "parking_rule_exact":all(s["parking_position"]==(s["query_position"]+1)%6 and s["parking_position"]!=s["query_position"] and s["parking_position"]!=6 for s in flat),
        "all_query_strata_nonempty":all(s["count"]>0 for s in flat),
        "threshold_exact":TH==.90,
        "state_exact":b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b41_reciprocal_endpoints_reproduced":all(abs(s["reciprocal"]-1.0)<1e-12 for s in flat),
        "multiset_preserved":all(s["reciprocal_multiset_preserved"] and s["target_to_latest_multiset_preserved"] and s["source6_to_query_multiset_preserved"] for s in flat),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"TARGET_TO_LATEST_SUFFICIENT","SOURCE6_TO_QUERY_SUFFICIENT","BOTH_DIRECTIONS_SUFFICIENT","JOINT_RECIPROCAL_REQUIRED","PARTIAL_DIRECTIONAL_PATTERN","ANCHOR_NOT_REPRODUCED"}
    out={
        "schema":1,"experiment":"YGG-B42","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,"valid":all(v.values()),
        "qualification":{"YGG_B42_RECIPROCAL_DIRECTION_DECOMPOSITION":all(v.values()) and a["classification"] in allowed,"classification":a["classification"]},
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))
if __name__=="__main__": main()
