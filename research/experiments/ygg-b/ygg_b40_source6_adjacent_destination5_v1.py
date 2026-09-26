#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b39_source6_destination_specificity_v1 as b39

PREREG="c1b11ffe2bd4bca380d89686dbd8de727a277248"
PARENT_RUN="36269419517"
SEEDS=[111,222,333,444,555]
SOURCE=6
DESTS=[4,5]
POS=4
TH=.90
EXPECTED_D4={111:1.0,222:1.0,333:1.0,444:1.0,555:1.0}

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def reciprocal(x,a,b):
    z=x.clone()
    xa=x[:,4*a:4*a+4].clone()
    xb=x[:,4*b:4*b+4].clone()
    z[:,4*a:4*a+4]=xb
    z[:,4*b:4*b+4]=xa
    return z

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        original=b39.b38.b37.b36.b35.b34.acc(m,x,y,q)
        arms=[]
        for dest in DESTS:
            z=reciprocal(x,SOURCE,dest)
            a=b39.b38.b37.b36.b35.b34.acc(m,z,y,q)
            arms.append({
                "source":SOURCE,
                "destination":dest,
                "swap":f"{SOURCE}<->{dest}",
                "accuracy":a,
                "capable":a>=TH,
                "multiset_preserved":all(b39.b38.b37.b36.b35.b34.ms(x,r)==b39.b38.b37.b36.b35.b34.ms(z,r) for r in range(x.shape[0])),
            })
        rows.append({"seed":seed,"original":original,"arms":arms})
    counts={
        str(dest):sum(next(a for a in r["arms"] if a["destination"]==dest)["capable"] for r in rows)
        for dest in DESTS
    }
    if counts["4"]!=5:
        cat="ANCHOR_NOT_REPRODUCED"
    elif counts["5"]==5:
        cat="ADJACENT5_PORTABLE"
    elif counts["5"]<5:
        cat="DESTINATION4_ONLY"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    got4={r["seed"]:next(x for x in r["arms"] if x["destination"]==4)["accuracy"] for r in a["rows"]}
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "source_exact":all(all(x["source"]==SOURCE for x in r["arms"]) for r in a["rows"]),
        "destinations_exact":all([x["destination"] for x in r["arms"]]==DESTS for r in a["rows"]),
        "query_exact":POS==4,
        "threshold_exact":TH==.90,
        "state_exact":b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b39_destination4_endpoints_reproduced":all(abs(got4[s]-EXPECTED_D4[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(x["multiset_preserved"] for r in a["rows"] for x in r["arms"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"ADJACENT5_PORTABLE","DESTINATION4_ONLY","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B40",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_B40_SOURCE6_ADJACENT_DESTINATION5":all(v.values()) and a["classification"] in allowed,
            "classification":a["classification"],
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__":
    main()
