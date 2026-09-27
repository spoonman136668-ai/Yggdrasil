#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a67_two_route_redundancy_v1 as a67

PREREG="c5f11d43efeb1568599dbab91d4a1ba8e329f9ac"
PARENT_RUN="36353588258"
MODES=("U_A0","U_A25")
PAIRS=((103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123))
CTX=(99,107)
SUPPRESSORS={
    (103,111):{98,101,106},
    (105,111):{99,100,106,107,114},
    (105,117):{96,97,99,100,102,109,116},
    (106,111):{101,103,105,114,117,119},
    (106,117):{96,97,99,103,111,112,113,116,121},
    (117,123):{96,97,99,111,113,116,118,120,121,125},
    (121,123):{96,97,99,107,109,116,117,120,122},
}
CORRUPT=a67.CORRUPT
a44=a67.a44
a41=a67.a41
lu=a67.lu
flip_set=a67.flip_set
exact_change=a67.exact_change

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
    for p in PAIRS:
        i,j=p
        pair=run((i,j))
        p99=run((i,j,99))
        p107=run((i,j,107))
        both=run((i,j,99,107))
        expect99=99 in SUPPRESSORS[p]
        expect107=107 in SUPPRESSORS[p]
        rows.append({
            "pair":[i,j],"pair_arm":pair,"plus99":p99,"plus107":p107,"compound":both,
            "expected_99_suppresses":expect99,"expected_107_suppresses":expect107,
            "compound_effective":not both["collapse"],
            "reactivated":(not both["collapse"]) and (expect99 or expect107),
        })
    effective=[x["pair"] for x in rows if x["compound_effective"]]
    reactivated=[x["pair"] for x in rows if x["reactivated"]]
    return {"mode":mode,"rows":rows,"compound_effective_pairs":effective,"reactivated_pairs":reactivated}

def classify(rows):
    if not all(all(
        (not x["pair_arm"]["collapse"]) and
        (x["plus99"]["collapse"]==(x["expected_99_suppresses"])) and
        (x["plus107"]["collapse"]==(x["expected_107_suppresses"]))
        for x in r["rows"]) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if not all(all(
        x["compound"]["collapse"] for x in r["rows"] if tuple(x["pair"]) in ((103,111),(106,111))
    ) for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["compound_effective_pairs"]!=rows[1]["compound_effective_pairs"]:
        return "CROSS_MODE_GAP_DIFFERENCE"
    if rows[0]["reactivated_pairs"]:
        return "HIGHER_ORDER_ROUTE_REACTIVATION"
    if rows[0]["compound_effective_pairs"]:
        return "ALTERNATE_ROUTE_WITHOUT_REACTIVATION"
    return "KNOWN_ROUTE_CAPACITY_EXHAUSTED"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[]
    for r in first["rows"]:
        for x in r["rows"]: arms.extend([x["pair_arm"],x["plus99"],x["plus107"],x["compound"]])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "seven_pairs_exact":all([tuple(x["pair"]) for x in r["rows"]]==list(PAIRS) for r in first["rows"]),
        "context_exact":CTX==(99,107),
        "contexts_not_in_pairs":all(not(set(CTX)&set(p)) for p in PAIRS),
        "a64_single_context_anchors_exact":all(all(
            (not x["pair_arm"]["collapse"]) and
            (x["plus99"]["collapse"]==x["expected_99_suppresses"]) and
            (x["plus107"]["collapse"]==x["expected_107_suppresses"])
            for x in r["rows"]) for r in first["rows"]),
        "a67_gap_anchors_exact":all(all(
            x["compound"]["collapse"] for x in r["rows"] if tuple(x["pair"]) in ((103,111),(106,111))
        ) for r in first["rows"]),
        "compound_four_distinct_flips":all(len(x["compound"]["subset"])==4 and len(set(x["compound"]["subset"]))==4 for r in first["rows"] for x in r["rows"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"HIGHER_ORDER_ROUTE_REACTIVATION","ALTERNATE_ROUTE_WITHOUT_REACTIVATION","KNOWN_ROUTE_CAPACITY_EXHAUSTED","CROSS_MODE_GAP_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A68","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A68_GAP_ROUTE_EXHAUSTION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
