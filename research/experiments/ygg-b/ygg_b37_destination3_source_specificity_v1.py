#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b36_early_destination_portability_v1 as b36

PREREG="93c0caec73dda2eb684ff2d0b25806fc3e96a4d7"
PARENT_RUN="36264388367"
SEEDS=[111,222,333,444,555]
SOURCES=[0,1,2,5,6]
DEST=3
POS=4
TH=.90
EXPECTED_SOURCE5={
    111:0.9429065585136414,
    222:0.9161184430122375,
    333:0.902479350566864,
    444:0.9209622144699097,
    555:0.9119601249694824,
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
        data=list(b36.b35.b34.b31.b27.evaluation_data(seed,b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b36.b35.b34.b31.b29.train_model(seed,True)
        original=b36.b35.b34.acc(m,x,y,q)
        arms=[]
        for source in SOURCES:
            z=reciprocal(x,source,DEST)
            a=b36.b35.b34.acc(m,z,y,q)
            arms.append({
                "source":source,
                "destination":DEST,
                "swap":f"{source}<->{DEST}",
                "accuracy":a,
                "capable":a>=TH,
                "multiset_preserved":all(b36.b35.b34.ms(x,r)==b36.b35.b34.ms(z,r) for r in range(x.shape[0])),
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
        cat="SOURCE5_SPECIFIC"
    elif others:
        cat="MULTISOURCE_DESTINATION3"
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
        "state_exact":b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b36_source5_endpoints_reproduced":all(abs(got5[s]-EXPECTED_SOURCE5[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(x["multiset_preserved"] for r in a["rows"] for x in r["arms"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"SOURCE5_SPECIFIC","MULTISOURCE_DESTINATION3","SOURCE5_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B37",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_B37_DESTINATION3_SOURCE_SPECIFICITY":all(v.values()) and a["classification"] in allowed,
            "classification":a["classification"],
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__":
    main()
