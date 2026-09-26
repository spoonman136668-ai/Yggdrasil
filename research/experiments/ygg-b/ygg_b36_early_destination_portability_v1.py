#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b35_position5_destination_specificity_v1 as b35

PREREG="55b882c6232268e98d15e39042da92474fba8e75"
PARENT_RUN="36257434829"
SEEDS=[111,222,333,444,555]
DESTS=[0,1,2,3]
POS=4
TH=.90
EXPECTED_D2={
    111:0.899653971195221,
    222:0.8832237124443054,
    333:0.8545454740524292,
    444:0.8711340427398682,
    555:0.8837209343910217,
}
EXPECTED_D3={
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

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b35.b34.b31.b27.evaluation_data(seed,b35.b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b35.b34.b31.b29.train_model(seed,True)
        original=b35.b34.acc(m,x,y,q)
        arms=[]
        for dest in DESTS:
            z=b35.reciprocal(x,5,dest)
            a=b35.b34.acc(m,z,y,q)
            arms.append({
                "destination":dest,
                "swap":f"5<->{dest}",
                "accuracy":a,
                "capable":a>=TH,
                "multiset_preserved":all(b35.b34.ms(x,r)==b35.b34.ms(z,r) for r in range(x.shape[0])),
            })
        rows.append({"seed":seed,"original":original,"arms":arms})
    counts={
        str(dest):sum(next(a for a in r["arms"] if a["destination"]==dest)["capable"] for r in rows)
        for dest in DESTS
    }
    d2_ok=counts["2"]==0
    d3_ok=counts["3"]==5
    early=(counts["0"]==5 or counts["1"]==5)
    if not (d2_ok and d3_ok):
        cat="ANCHOR_NOT_REPRODUCED"
    elif early:
        cat="EARLY_REENTRY"
    elif counts["0"]<5 and counts["1"]<5:
        cat="LOCAL_WINDOW_CONFIRMED"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    a=one()
    b=one()
    ba=canon(a)
    got2={r["seed"]:next(x for x in r["arms"] if x["destination"]==2)["accuracy"] for r in a["rows"]}
    got3={r["seed"]:next(x for x in r["arms"] if x["destination"]==3)["accuracy"] for r in a["rows"]}
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "destinations_exact":all([x["destination"] for x in r["arms"]]==DESTS for r in a["rows"]),
        "query_exact":POS==4,
        "threshold_exact":TH==.90,
        "state_exact":b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b35_destination2_endpoints_reproduced":all(abs(got2[s]-EXPECTED_D2[s])<1e-12 for s in SEEDS),
        "b35_destination3_endpoints_reproduced":all(abs(got3[s]-EXPECTED_D3[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(x["multiset_preserved"] for r in a["rows"] for x in r["arms"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"LOCAL_WINDOW_CONFIRMED","EARLY_REENTRY","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B36",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":v,
        "valid":all(v.values()),
        "qualification":{
            "YGG_B36_EARLY_DESTINATION_PORTABILITY":all(v.values()) and a["classification"] in allowed,
            "classification":a["classification"],
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__":
    main()
