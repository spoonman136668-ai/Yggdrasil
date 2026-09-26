#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b37_destination3_source_specificity_v1 as b37

PREREG="a54daccb740268a3bcbac3638761794839493a9d"
PARENT_RUN="36266367735"
SEEDS=[111,222,333,444,555]
SOURCES=[0,1,2,5,6]
DEST=4
POS=4
TH=.90
EXPECTED_SOURCE5={
    111:0.9653978943824768,
    222:0.9638158082962036,
    333:0.9537190198898315,
    444:0.9536082744598389,
    555:0.9551495313644409,
}

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
        data=list(b37.b36.b35.b34.b31.b27.evaluation_data(seed,b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b37.b36.b35.b34.b31.b29.train_model(seed,True)
        original=b37.b36.b35.b34.acc(m,x,y,q)
        arms=[]
        for source in SOURCES:
            z=reciprocal(x,source,DEST)
            a=b37.b36.b35.b34.acc(m,z,y,q)
            arms.append({
                "source":source,
                "destination":DEST,
                "swap":f"{source}<->{DEST}",
                "accuracy":a,
                "capable":a>=TH,
                "multiset_preserved":all(b37.b36.b35.b34.ms(x,r)==b37.b36.b35.b34.ms(z,r) for r in range(x.shape[0])),
            })
        rows.append({"seed":seed,"original":original,"arms":arms})
    counts={
        str(source):sum(next(a for a in r["arms"] if a["source"]==source)["capable"] for r in rows)
        for source in SOURCES
    }
    source5_ok=counts["5"]==5
    others=[source for source in SOURCES if source!=5 and counts[str(source)]==5]
    if not source5_ok:
        cat="SOURCE5_NOT_REPRODUCED"
    elif not others:
        cat="SOURCE5_WINDOW_SPECIFIC"
    elif others:
        cat="MULTISOURCE_DESTINATION4"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    a=one()
    b=one()
    ba=canon(a)
    got5={r["seed"]:next(x for x in r["arms"] if x["source"]==5)["accuracy"] for r in a["rows"]}
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "sources_exact":all([x["source"] for x in r["arms"]]==SOURCES for r in a["rows"]),
        "destination_exact":all(all(x["destination"]==DEST for x in r["arms"]) for r in a["rows"]),
        "query_exact":POS==4,
        "threshold_exact":TH==.90,
        "state_exact":b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b35_source5_destination4_endpoints_reproduced":all(abs(got5[s]-EXPECTED_SOURCE5[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(x["multiset_preserved"] for r in a["rows"] for x in r["arms"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"SOURCE5_WINDOW_SPECIFIC","MULTISOURCE_DESTINATION4","SOURCE5_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B38",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_B38_DESTINATION4_SOURCE_SPECIFICITY":all(v.values()) and a["classification"] in allowed,
            "classification":a["classification"],
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__":
    main()
