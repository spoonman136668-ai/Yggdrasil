#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a65_matrix_guided_double_context_v1 as a65

PREREG="683cbac26c692920a5df117c2bf98bbb9b970df0"
PARENT_RUN="36346244037"
MODES=("U_A0","U_A25")
PAIRS=((103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123))
FAILED=(
((97,103),(105,111)),
((97,105),(103,111)),
((98,117),(105,111)),
((99,105),(103,111)),
((106,121),(105,117)),
)
CORRUPT=a65.CORRUPT
a44=a65.a44
a41=a65.a41
lu=a65.lu
flip_set=a65.flip_set
exact_change=a65.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

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
    cases=[]
    for contexts,selected in FAILED:
        k,l=contexts
        selected_arm=run(tuple(selected)+(k,l))
        eligible=[p for p in PAIRS if not (set(p)&set(contexts))]
        tested=[]
        for p in eligible:
            arm=run(tuple(p)+(k,l))
            tested.append({"pair":list(p),"arm":arm,"effective":not arm["collapse"]})
        effective=[x["pair"] for x in tested if x["effective"]]
        cases.append({
            "contexts":list(contexts),"selected_pair":list(selected),
            "selected_compound_failure":selected_arm,
            "eligible_pairs":[list(p) for p in eligible],
            "tested_pairs":tested,"effective_pairs":effective
        })
    return {"mode":mode,"cases":cases}

def classify(rows):
    if not all(all(x["selected_compound_failure"]["collapse"] for x in r["cases"]) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    maps=[[{"contexts":x["contexts"],"effective_pairs":x["effective_pairs"]} for x in r["cases"]] for r in rows]
    if maps[0]!=maps[1]: return "CROSS_MODE_FALLBACK_DIFFERENCE"
    have=[bool(x["effective_pairs"]) for x in rows[0]["cases"]]
    if all(have): return "ALTERNATE_ROUTE_EXISTS_ALL"
    if any(have): return "PARTIAL_ALTERNATE_ROUTE"
    return "NO_ALTERNATE_ROUTE"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allarms=[]
    for r in first["rows"]:
        for x in r["cases"]:
            allarms.append(x["selected_compound_failure"])
            allarms.extend(t["arm"] for t in x["tested_pairs"])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "exact_five_contexts":all(
            [(tuple(x["contexts"]),tuple(x["selected_pair"])) for x in r["cases"]]==list(FAILED)
            for r in first["rows"]),
        "frozen_pair_set_exact":list(PAIRS)==[(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)],
        "eligibility_mechanical_exact":all(
            [tuple(p) for p in x["eligible_pairs"]]==[p for p in PAIRS if not (set(p)&set(x["contexts"]))]
            for r in first["rows"] for x in r["cases"]),
        "selected_a65_failures_reproduced":all(x["selected_compound_failure"]["collapse"] for r in first["rows"] for x in r["cases"]),
        "every_tested_compound_four_distinct_flips":all(
            len(t["arm"]["subset"])==4 and len(set(t["arm"]["subset"]))==4
            for r in first["rows"] for x in r["cases"] for t in x["tested_pairs"]),
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
    allowed={"ALTERNATE_ROUTE_EXISTS_ALL","PARTIAL_ALTERNATE_ROUTE","NO_ALTERNATE_ROUTE","CROSS_MODE_FALLBACK_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A66","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A66_COMPOUND_CONTEXT_FALLBACK":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
