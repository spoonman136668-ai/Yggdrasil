#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a64_full_pair_context_matrix_v1 as a64

PREREG="5580aa8aa52415d664df8ca3065a3d3e104dced4"
PARENT_RUN="36334957482"
MODES=("U_A0","U_A25")
CASES=(
((96,101),(105,111)),((96,103),(105,111)),((96,105),(103,111)),((96,114),(103,111)),
((97,101),(105,111)),((97,103),(105,111)),((97,105),(103,111)),((97,114),(103,111)),
((98,99),(106,111)),((98,117),(105,111)),((99,105),(103,111)),((99,114),(103,111)),
((99,117),(103,111)),((99,119),(103,111)),((100,111),(121,123)),((100,117),(103,111)),
((101,116),(105,111)),((101,117),(105,111)),((102,111),(121,123)),((103,116),(105,111)),
((103,117),(105,111)),((105,111),(121,123)),((105,116),(103,111)),((105,117),(103,111)),
((105,121),(103,111)),((106,109),(117,123)),((106,120),(105,117)),((106,121),(105,117)),
((106,123),(105,117)),((107,111),(105,117)),((107,117),(103,111)),((111,120),(105,117)),
((111,121),(105,117)),((111,122),(105,117)),((111,123),(105,117)),((114,116),(103,111)),
((114,117),(103,111)),
)
CORRUPT=a64.CORRUPT
a44=a64.a44
a41=a64.a41
lu=a64.lu
flip_set=a64.flip_set
exact_change=a64.exact_change

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
    rows=[]
    for contexts,pair in CASES:
        k,l=contexts; i,j=pair
        p=run((i,j))
        pk=run((i,j,k))
        pl=run((i,j,l))
        both=run((i,j,k,l))
        rows.append({
            "contexts":[k,l],"selected_pair":[i,j],
            "pair_anchor":p,"single_context_k_anchor":pk,"single_context_l_anchor":pl,
            "compound":both,"compound_effective":not both["collapse"],
        })
    failed=[{"contexts":x["contexts"],"selected_pair":x["selected_pair"]} for x in rows if not x["compound_effective"]]
    return {"mode":mode,"cases":rows,"failed_compound_cases":failed}

def classify(rows):
    if not all(all(
        (not x["pair_anchor"]["collapse"]) and
        (not x["single_context_k_anchor"]["collapse"]) and
        (not x["single_context_l_anchor"]["collapse"])
        for x in r["cases"]) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["failed_compound_cases"]!=rows[1]["failed_compound_cases"]:
        return "CROSS_MODE_COMPOSITION_DIFFERENCE"
    if not rows[0]["failed_compound_cases"]:
        return "SINGLE_CONTEXT_MATRIX_COMPOSES"
    return "COMPOUND_CONTEXT_BREAKS_SELECTOR"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"cases":[{"contexts":list(c),"selected_pair":list(p)} for c,p in CASES],
            "rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allarms=[]
    for r in first["rows"]:
        for x in r["cases"]:
            allarms.extend([x["pair_anchor"],x["single_context_k_anchor"],x["single_context_l_anchor"],x["compound"]])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "exact_37_cases":len(CASES)==37 and all(len(r["cases"])==37 for r in first["rows"]),
        "cases_unique":len({(c,p) for c,p in CASES})==37,
        "anchors_reproduced":all(all(
            not x["pair_anchor"]["collapse"] and not x["single_context_k_anchor"]["collapse"] and not x["single_context_l_anchor"]["collapse"]
            for x in r["cases"]) for r in first["rows"]),
        "compound_has_exact_four_registered_flips":all(len(x["compound"]["subset"])==4 for r in first["rows"] for x in r["cases"]),
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
    allowed={"SINGLE_CONTEXT_MATRIX_COMPOSES","COMPOUND_CONTEXT_BREAKS_SELECTOR","CROSS_MODE_COMPOSITION_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A65","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A65_MATRIX_GUIDED_DOUBLE_CONTEXT":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
