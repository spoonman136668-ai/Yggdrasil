#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b34_order_effect_portability_v1 as b34

PREREG="f4beb22c6430b4d5dff25d62bc5fad43df80d234"
PARENT_RUN="36255030345"
SEEDS=[111,222,333,444,555]
DESTS=[2,3,4]
POS=4
TH=.90
EXPECTED_ANCHOR={
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
        data=list(b34.b31.b27.evaluation_data(seed,b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b34.b31.b29.train_model(seed,True)
        original=b34.acc(m,x,y,q)
        arms=[]
        for dest in DESTS:
            z=reciprocal(x,5,dest)
            a=b34.acc(m,z,y,q)
            arms.append({
                "destination":dest,
                "swap":f"5<->{dest}",
                "accuracy":a,
                "capable":a>=TH,
                "multiset_preserved":all(b34.ms(x,r)==b34.ms(z,r) for r in range(x.shape[0])),
            })
        rows.append({"seed":seed,"original":original,"arms":arms})
    capable_counts={
        str(dest):sum(next(a for a in r["arms"] if a["destination"]==dest)["capable"] for r in rows)
        for dest in DESTS
    }
    anchor_all=capable_counts["3"]==5
    flank_all=[capable_counts["2"]==5,capable_counts["4"]==5]
    if anchor_all and all(flank_all):
        cat="BROAD_LOCAL_PORTABILITY"
    elif anchor_all and any(flank_all):
        cat="ALTERNATE_DESTINATION_PORTABLE"
    elif anchor_all and not any(flank_all):
        cat="POSITION3_ONLY_PORTABLE"
    elif not anchor_all:
        cat="ANCHOR_NOT_REPRODUCED"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"capable_counts":capable_counts,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    a=one()
    b=one()
    ba=canon(a)
    anchor={r["seed"]:next(x for x in r["arms"] if x["destination"]==3)["accuracy"] for r in a["rows"]}
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "destinations_exact":all([x["destination"] for x in r["arms"]]==DESTS for r in a["rows"]),
        "query_exact":POS==4,
        "threshold_exact":TH==.90,
        "state_exact":b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b34_anchor_endpoints_reproduced":all(abs(anchor[s]-EXPECTED_ANCHOR[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(x["multiset_preserved"] for r in a["rows"] for x in r["arms"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"POSITION3_ONLY_PORTABLE","ALTERNATE_DESTINATION_PORTABLE","BROAD_LOCAL_PORTABILITY","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B35",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_B35_POSITION5_DESTINATION_SPECIFICITY":all(v.values()) and a["classification"] in allowed,
            "classification":a["classification"],
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__":
    main()
