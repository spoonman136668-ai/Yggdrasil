#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a63_request99_global_suppressor_v1 as a63

PREREG="98d5f35f7b19f9f4ab4bdb82201024319d0653de"
PARENT_RUN="36333417454"
MODES=("U_A0","U_A25")
PAIRS=((103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123))
PHASE3=tuple(range(96,128))
S_A61=(96,97,99,103,111,112,113,116,121)
S_A62=(99,100,106,107,114)
A63_99_RESCUED=((105,111),(105,117),(106,117),(117,123),(121,123))
CORRUPT=a63.CORRUPT

a44=a63.a44
a41=a63.a41
lu=a63.lu
flip_set=a63.flip_set
exact_change=a63.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def jaccard(a,b):
    a=set(a); b=set(b)
    return 1.0 if not (a|b) else len(a&b)/len(a|b)

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    def run(subset):
        arr=flip_set(native,subset)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        return {
            "subset":list(subset),"collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,subset),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        }
    native_row=run(())
    pair_rows=[]
    for i,j in PAIRS:
        si=run((i,)); sj=run((j,)); p=run((i,j))
        contexts=[]
        for k in PHASE3:
            if k in (i,j): continue
            x=run((i,j,k))
            contexts.append({"context_rid":k,**x})
        suppressors=[x["context_rid"] for x in contexts if x["collapse"]]
        pair_rows.append({
            "pair":[i,j],"single_i":si,"single_j":sj,"pair_arm":p,
            "contexts":contexts,"suppressor_rids":suppressors
        })
    sets=[set(x["suppressor_rids"]) for x in pair_rows]
    intersection=sorted(set.intersection(*sets)) if sets else []
    union=sorted(set.union(*sets)) if sets else []
    freq={str(k):sum(k in s for s in sets) for k in PHASE3}
    overlaps=[]
    for ai in range(len(pair_rows)):
        for bi in range(ai+1,len(pair_rows)):
            overlaps.append({
                "pair_a":pair_rows[ai]["pair"],"pair_b":pair_rows[bi]["pair"],
                "jaccard":jaccard(pair_rows[ai]["suppressor_rids"],pair_rows[bi]["suppressor_rids"])
            })
    return {
        "mode":mode,"native":native_row,"pairs":pair_rows,
        "intersection":intersection,"union":union,"suppressor_frequency":freq,
        "pairwise_jaccard":overlaps
    }

def inherited_ok(row):
    by={tuple(x["pair"]):x["suppressor_rids"] for x in row["pairs"]}
    if by[(106,117)]!=list(S_A61): return False
    if by[(105,111)]!=list(S_A62): return False
    rescued=[list(pair) for pair in PAIRS if 99 in by[pair]]
    return rescued==[list(x) for x in A63_99_RESCUED]

def classify(rows):
    if not all(r["native"]["collapse"] and all(
        p["single_i"]["collapse"] and p["single_j"]["collapse"] and not p["pair_arm"]["collapse"]
        for p in r["pairs"]) and inherited_ok(r) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    maps=[[(tuple(p["pair"]),tuple(p["suppressor_rids"])) for p in r["pairs"]] for r in rows]
    if maps[0]!=maps[1]: return "CROSS_MODE_MATRIX_DIFFERENCE"
    if rows[0]["intersection"]: return "GLOBAL_SUPPRESSOR_CORE"
    if all(p["suppressor_rids"] for p in rows[0]["pairs"]): return "PAIR_SPECIFIC_SUPPRESSOR_MATRIX"
    return "MIXED_SUPPRESSOR_MATRIX"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allrows=[]
    for r in first["rows"]:
        allrows.append(r["native"])
        for p in r["pairs"]:
            allrows.extend([p["single_i"],p["single_j"],p["pair_arm"]]); allrows.extend(p["contexts"])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "seven_pairs_exact":all([tuple(p["pair"]) for p in r["pairs"]]==list(PAIRS) for r in first["rows"]),
        "thirty_contexts_each_pair":all(all(len(p["contexts"])==30 for p in r["pairs"]) for r in first["rows"]),
        "exact_210_contexts_per_mode":all(sum(len(p["contexts"]) for p in r["pairs"])==210 for r in first["rows"]),
        "anchors_exact":all(r["native"]["collapse"] and all(p["single_i"]["collapse"] and p["single_j"]["collapse"] and not p["pair_arm"]["collapse"] for p in r["pairs"]) for r in first["rows"]),
        "inherited_a61_a63_exact":all(inherited_ok(r) for r in first["rows"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in allrows),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allrows),
        "programs_exact":all(x["programs_exact"] for x in allrows),
        "arrivals_exact":all(x["arrivals_exact"] for x in allrows),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allrows),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allrows),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allrows),
        "scientific_integrity":all(x["integrity"] for x in allrows),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"GLOBAL_SUPPRESSOR_CORE","PAIR_SPECIFIC_SUPPRESSOR_MATRIX","MIXED_SUPPRESSOR_MATRIX","CROSS_MODE_MATRIX_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A64","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A64_FULL_PAIR_CONTEXT_MATRIX":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
