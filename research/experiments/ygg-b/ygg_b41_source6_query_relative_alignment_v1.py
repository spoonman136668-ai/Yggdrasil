#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b40_source6_adjacent_destination5_v1 as b40

PREREG="d613fcd084b1d18b0c104e3f0181a1f6c56bc933"
PARENT_RUN="36270587677"
SEEDS=[111,222,333,444,555]
SOURCE=6
QUERY_POSITIONS=[0,1,2,3,4,5]
TH=.90
EXPECTED_Q4={111:1.0,222:1.0,333:1.0,444:1.0,555:1.0}

torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def reciprocal(x,a,b):
    z=x.clone(); xa=x[:,4*a:4*a+4].clone(); xb=x[:,4*b:4*b+4].clone()
    z[:,4*a:4*a+4]=xb; z[:,4*b:4*b+4]=xa
    return z

def acc(m,x,y,q,pos):
    m.eval()
    with torch.no_grad(): p=b40.b39.b38.b37.b36.b35.b34.b31.b29.immediate_read1_logits(m,x).argmax(1)
    mask=q==pos
    if int(mask.sum())<=0: raise AssertionError("empty query stratum")
    return float((p[mask]==y[mask]).float().mean()),int(mask.sum())

def ms(x,r):
    return sorted(tuple(float(v) for v in x[r,4*p:4*p+4].tolist()) for p in range(7))

def one():
    rows=[]
    for seed in SEEDS:
        data=list(b40.b39.b38.b37.b36.b35.b34.b31.b27.evaluation_data(seed,b40.b39.b38.b37.b36.b35.b34.b31.b27.EVAL_N))
        x,y,_,q,*_=data
        m=b40.b39.b38.b37.b36.b35.b34.b31.b29.train_model(seed,True)
        strata=[]
        for pos in QUERY_POSITIONS:
            z=reciprocal(x,SOURCE,pos)
            original,count=acc(m,x,y,q,pos)
            swapped,_=acc(m,z,y,q,pos)
            strata.append({"query_position":pos,"count":count,"original":original,"swapped":swapped,
                           "capable":swapped>=TH,
                           "multiset_preserved":all(ms(x,r)==ms(z,r) for r in range(x.shape[0]))})
        rows.append({"seed":seed,"strata":strata})
    counts={str(pos):sum(next(s for s in r["strata"] if s["query_position"]==pos)["capable"] for r in rows) for pos in QUERY_POSITIONS}
    q4=counts["4"]==5
    others=[p for p in QUERY_POSITIONS if p!=4 and counts[str(p)]==5]
    if not q4: cat="ANCHOR_NOT_REPRODUCED"
    elif len(others)==5: cat="QUERY_RELATIVE_PORTABLE"
    elif not others: cat="ABSOLUTE4_SPECIFIC"
    elif others: cat="PARTIAL_QUERY_RELATIVE"
    else: cat="OTHER_VALID_PATTERN"
    return {"rows":rows,"capable_counts":counts,"classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canon(a)
    got4={r["seed"]:next(s for s in r["strata"] if s["query_position"]==4)["swapped"] for r in a["rows"]}
    v={
        "seeds_exact":[r["seed"] for r in a["rows"]]==SEEDS,
        "query_positions_exact":all([s["query_position"] for s in r["strata"]]==QUERY_POSITIONS for r in a["rows"]),
        "all_query_strata_nonempty":all(all(s["count"]>0 for s in r["strata"]) for r in a["rows"]),
        "threshold_exact":TH==.90,
        "state_exact":b40.b39.b38.b37.b36.b35.b34.b31.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b40.b39.b38.b37.b36.b35.b34.b31.b27.ReadUpdateRead().parameters())==120,
        "b40_q4_endpoints_reproduced":all(abs(got4[s]-EXPECTED_Q4[s])<1e-12 for s in SEEDS),
        "multiset_preserved":all(s["multiset_preserved"] for r in a["rows"] for s in r["strata"]),
        "duplicate_byte_identical":ba==canon(b),
    }
    allowed={"QUERY_RELATIVE_PORTABLE","ABSOLUTE4_SPECIFIC","PARTIAL_QUERY_RELATIVE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B41","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":v,"valid":all(v.values()),
         "qualification":{"YGG_B41_SOURCE6_QUERY_RELATIVE_ALIGNMENT":all(v.values()) and a["classification"] in allowed,"classification":a["classification"]},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canon(out))
if __name__=="__main__": main()
