#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a66_compound_context_fallback_v1 as a66

PREREG="642741c873fb3b2b074bcd86b882b97f42d2c318"
PARENT_RUN="36348900193"
MODES=("U_A0","U_A25")
PAIRS=((103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123))
SUPPRESSORS={
    (103,111):{98,101,106},
    (105,111):{99,100,106,107,114},
    (105,117):{96,97,99,100,102,109,116},
    (106,111):{101,103,105,114,117,119},
    (106,117):{96,97,99,103,111,112,113,116,121},
    (117,123):{96,97,99,111,113,116,118,120,121,125},
    (121,123):{96,97,99,107,109,116,117,120,122},
}
PHASE3=tuple(range(96,128))
CORRUPT=a66.CORRUPT
a44=a66.a44
a41=a66.a41
lu=a66.lu
flip_set=a66.flip_set
exact_change=a66.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def derive_cases():
    out=[]
    for k,l in itertools.combinations(PHASE3,2):
        cand=[]
        for p in PAIRS:
            if k in p or l in p: continue
            if k in SUPPRESSORS[p] or l in SUPPRESSORS[p]: continue
            cand.append(p)
        if len(cand)==2:
            out.append(((k,l),tuple(cand)))
    return tuple(out)

CASES=derive_cases()

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
    rows=[]
    for contexts,candidates in CASES:
        k,l=contexts
        tested=[]
        for p in candidates:
            arm=run(tuple(p)+(k,l))
            tested.append({"pair":list(p),"arm":arm,"effective":not arm["collapse"]})
        eff=[x["pair"] for x in tested if x["effective"]]
        rows.append({
            "contexts":[k,l],
            "candidate_pairs":[list(p) for p in candidates],
            "tested_pairs":tested,
            "effective_pairs":eff,
            "effective_count":len(eff),
        })
    return {"mode":mode,"cases":rows,"zero_effective_contexts":[x["contexts"] for x in rows if x["effective_count"]==0]}

def classify(rows):
    summary=[[{"contexts":x["contexts"],"effective_pairs":x["effective_pairs"]} for x in r["cases"]] for r in rows]
    if summary[0]!=summary[1]: return "CROSS_MODE_REDUNDANCY_DIFFERENCE"
    if all(x["effective_count"]>=1 for x in rows[0]["cases"]):
        return "TWO_ROUTE_REDUNDANCY_COVERS_ALL"
    return "TWO_ROUTE_REDUNDANCY_HAS_GAPS"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {
        "derived_case_count":len(CASES),
        "cases":[{"contexts":list(c),"candidate_pairs":[list(p) for p in ps]} for c,ps in CASES],
        "rows":rows,
        "classification":classify(rows) if len(CASES)==93 and all(len(ps)==2 for _,ps in CASES) else "ANCHOR_NOT_REPRODUCED",
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allarms=[t["arm"] for r in first["rows"] for x in r["cases"] for t in x["tested_pairs"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "frozen_pair_set_exact":list(PAIRS)==[(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)],
        "frozen_suppressor_matrix_exact":SUPPRESSORS[(106,117)]=={96,97,99,103,111,112,113,116,121} and SUPPRESSORS[(105,111)]=={99,100,106,107,114},
        "exact_93_cases":len(CASES)==93,
        "exact_two_candidates_each":all(len(ps)==2 for _,ps in CASES),
        "all_tested_compound_four_distinct_flips":all(len(x["subset"])==4 and len(set(x["subset"]))==4 for x in allarms),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in allarms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allarms),
        "programs_exact":all(x["programs_exact"] for x in allarms),
        "arrivals_exact":all(x["arrivals_exact"] for x in allarms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allarms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allarms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allarms),
        "scientific_integrity":all(x["integrity"] for x in allarms),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"TWO_ROUTE_REDUNDANCY_COVERS_ALL","TWO_ROUTE_REDUNDANCY_HAS_GAPS","CROSS_MODE_REDUNDANCY_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A67","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A67_TWO_ROUTE_REDUNDANCY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
