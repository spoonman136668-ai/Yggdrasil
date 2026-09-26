#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b43_queried_binding_destination_sweep_v1 as b43

PREREG="9fd7dec8a3f34a3f996afe537552de00a1413dc7"
PARENT_RUN="36275111281"
SEEDS=[111,222,333,444,555]
QPOS=[0,1,2,3,4,5]
DESTS=[4,5,6]
TH=.90

EXPECTED=json.loads(r'''{"111":{"0":{"4":[1,0.8070175647735596],"5":[1,0.9314194321632385],"6":[1,1.0]},"1":{"4":[0,0.7811447978019714],"5":[0,0.9292929172515869],"6":[2,1.0]},"2":{"4":[0,0.7802768349647522],"5":[0,0.9134948253631592],"6":[3,1.0]},"3":{"4":[0,0.792553186416626],"5":[0,0.923758864402771],"6":[4,1.0]},"4":{"5":[0,0.9723183512687683],"6":[5,1.0]},"5":{"4":[0,0.9359190464019775],"6":[0,1.0]}},"222":{"0":{"4":[1,0.8159608840942383],"5":[1,0.9348534345626831],"6":[1,1.0]},"1":{"4":[0,0.8301886916160583],"5":[0,0.9554030895233154],"6":[2,1.0]},"2":{"4":[0,0.7905405163764954],"5":[0,0.9408783912658691],"6":[3,1.0]},"3":{"4":[0,0.7954545617103577],"5":[0,0.9545454382896423],"6":[4,1.0]},"4":{"5":[0,0.9539473652839661],"6":[5,1.0]},"5":{"4":[0,0.8966131806373596],"6":[0,1.0]}},"333":{"0":{"4":[1,0.7924528121948242],"5":[1,0.9313893914222717],"6":[1,1.0]},"1":{"4":[0,0.7857142686843872],"5":[0,0.9285714030265808],"6":[2,1.0]},"2":{"4":[0,0.8101472854614258],"5":[0,0.9443535208702087],"6":[3,1.0]},"3":{"4":[0,0.80756014585495],"5":[0,0.9329897165298462],"6":[4,1.0]},"4":{"5":[0,0.9520661234855652],"6":[5,1.0]},"5":{"4":[0,0.9172794222831726],"6":[0,1.0]}},"444":{"0":{"4":[1,0.7672131061553955],"5":[1,0.9327868819236755],"6":[1,1.0]},"1":{"4":[0,0.7987321615219116],"5":[0,0.9477020502090454],"6":[2,1.0]},"2":{"4":[0,0.8192371726036072],"5":[0,0.9386401176452637],"6":[3,1.0]},"3":{"4":[0,0.7766323089599609],"5":[0,0.9432989954948425],"6":[4,1.0]},"4":{"5":[0,0.9604811072349548],"6":[5,1.0]},"5":{"4":[0,0.9384886026382446],"6":[0,1.0]}},"555":{"0":{"4":[1,0.7954144477844238],"5":[1,0.9329805970191956],"6":[1,1.0]},"1":{"4":[0,0.7815884351730347],"5":[0,0.9277978539466858],"6":[2,1.0]},"2":{"4":[0,0.769881546497345],"5":[0,0.9255499243736267],"6":[3,1.0]},"3":{"4":[0,0.7611940503120422],"5":[0,0.9121061563491821],"6":[4,1.0]},"4":{"5":[0,0.9568106532096863],"6":[5,1.0]},"5":{"4":[0,0.8957983255386353],"6":[0,1.0]}}}''')

torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def parking_positions(q,d):
    if d==6:
        return [p for p in range(6) if p!=q]
    return [p for p in range(6) if p!=q and p!=d]

def relocate(x,q,d,p):
    z=x.clone(); src=x.clone()
    z[:,4*d:4*d+4]=src[:,4*q:4*q+4]
    z[:,4*p:4*p+4]=src[:,4*d:4*d+4]
    z[:,4*q:4*q+4]=src[:,4*p:4*p+4]
    return z

def acc(m,x,y):
    m.eval()
    with torch.no_grad():
        pred=b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.immediate_read1_logits(m,x).argmax(1)
    return float((pred==y).float().mean())

def ms(x,r):
    return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,qev,*_=data
        m=b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        strata=[]
        for q in QPOS:
            mask=qev==q
            if int(mask.sum())<=0: raise AssertionError("empty query stratum")
            xs=x[mask].clone(); ys=y[mask].clone()
            arms=[]
            for d in DESTS:
                if d==q: continue
                for p in parking_positions(q,d):
                    z=relocate(xs,q,d,p)
                    a=acc(m,z,ys)
                    arms.append({
                        "destination":d,"parking":p,"accuracy":a,"capable":a>=TH,
                        "multiset_preserved":all(ms(xs,r)==ms(z,r) for r in range(xs.shape[0])),
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
        }

    anchors_ok=True
    anchor_checks=[]
    for r in rows:
        seed=str(r["seed"])
        for s in r["strata"]:
            q=str(s["query_position"])
            for d in DESTS:
                ds=str(d)
                if ds not in EXPECTED[seed][q]: continue
                ep,ea=EXPECTED[seed][q][ds]
                got=next(a for a in s["arms"] if a["destination"]==d and a["parking"]==ep)
                ok=abs(got["accuracy"]-ea)<1e-12
                anchors_ok=anchors_ok and ok
                anchor_checks.append({"seed":r["seed"],"query_position":s["query_position"],"destination":d,"parking":ep,"expected":ea,"actual":got["accuracy"],"exact":ok})

    u4=bydest["4"]["universal"]; u5=bydest["5"]["universal"]; u6=bydest["6"]["universal"]
    if not anchors_ok:
        cat="ANCHOR_NOT_REPRODUCED"
    elif u4 and u5 and u6:
        cat="ROBUST_THREE_POSITION_BAND"
    elif (not u4) and u5 and u6:
        cat="ROBUST_TWO_POSITION_RECENCY_BAND"
    elif u6 and (not u5) and (not u4):
        cat="LATEST_ONLY_AFTER_PARKING"
    elif bydest["5"]["mixed"] or bydest["6"]["mixed"]:
        cat="PARKING_SENSITIVE_RECENCY"
    else:
        cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"by_destination":bydest,"anchor_checks":anchor_checks,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    flat=[(s,x) for r in a["rows"] for s in r["strata"] for x in s["arms"]]
    counts={d:sum(1 for _,x in flat if x["destination"]==d) for d in DESTS}
    validity={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QPOS for r in a["rows"]),
        "destination_set_exact":all(set(x["destination"] for x in s["arms"])==set(d for d in DESTS if d!=s["query_position"]) for r in a["rows"] for s in r["strata"]),
        "parking_enumeration_exact":all(sorted(x["parking"] for x in s["arms"] if x["destination"]==d)==parking_positions(s["query_position"],d) for r in a["rows"] for s in r["strata"] for d in DESTS if d!=s["query_position"]),
        "arm_counts_exact":counts=={4:100,5:100,6:150},
        "all_query_strata_nonempty":all(s["count"]>0 for r in a["rows"] for s in r["strata"]),
        "threshold_exact":TH==.90,
        "state_exact":b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b43.b42.b41.b40.b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b43_designated_parking_endpoints_exact":all(x["exact"] for x in a["anchor_checks"]),
        "multiset_preserved":all(x["multiset_preserved"] for _,x in flat),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"ROBUST_TWO_POSITION_RECENCY_BAND","ROBUST_THREE_POSITION_BAND","LATEST_ONLY_AFTER_PARKING","PARKING_SENSITIVE_RECENCY","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={
        "schema":1,"experiment":"YGG-B44","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_B44_RECENCY_BAND_PARKING_ROBUSTNESS":all(validity.values()) and a["classification"] in allowed,"classification":a["classification"]},
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canon(out))

if __name__=="__main__": main()
