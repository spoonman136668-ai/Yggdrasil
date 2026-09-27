#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a58_pairwise_robust_triples_v1 as a58

PREREG="5031542edf60dbf0a2b7e13cc28431071c19923c"
PARENT_RUN="36322926253"
MODES=("U_A0","U_A25")
CANDIDATES=(
    (103,105,106,123),
    (103,105,106,125),
    (103,105,123,125),
    (103,106,121,125),
    (103,117,121,125),
)
EXPECTED_PAIRS=[list(x) for x in sorted(a58.E)]
EXPECTED_TRIPLES=[
    [105,106,121],[105,121,125],[106,123,125],
    [111,117,121],[111,117,125],[111,121,125],
]
CORRUPT=a58.CORRUPT
a44=a58.a44
a41=a58.a41
lu=a58.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one_mode(mode):
    inherited=a58.one_mode(mode)
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    quads=[]
    for q in CANDIDATES:
        arr=a58.a57.flip_set(native,q)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        quads.append({
            "quadruple":list(q),"collapse":bool(row["collapse"]),
            "exact_registered_change":a58.a57.exact_change(native,arr,q),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    sensitive=[x["quadruple"] for x in quads if not x["collapse"]]
    return {
        "mode":mode,"native_collapse":inherited["native_collapse"],
        "single_anchors":inherited["single_anchors"],
        "sensitive_pairs":inherited["sensitive_pairs"],
        "sensitive_triples":inherited["sensitive_triples"],
        "quadruples":quads,"sensitive_quadruples":sensitive,
        "native_integrity":inherited["native_integrity"],
    }

def classify(rows):
    if not all(r["native_collapse"] for r in rows): return "NATIVE_ANCHOR_NOT_REPRODUCED"
    if not all(
        all(x["collapse"] for x in r["single_anchors"]) and
        r["sensitive_pairs"]==EXPECTED_PAIRS and
        r["sensitive_triples"]==EXPECTED_TRIPLES
        for r in rows
    ):
        return "LOWER_ORDER_ANCHOR_NOT_REPRODUCED"
    if rows[0]["sensitive_quadruples"]!=rows[1]["sensitive_quadruples"]:
        return "CROSS_MODE_QUADRUPLE_DIFFERENCE"
    if rows[0]["sensitive_quadruples"]: return "GENUINE_FOURTH_ORDER_CAUSALITY"
    return "LOWER_ORDER_MODEL_SUFFICIENT_THROUGH_FOUR"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"candidate_quadruples":[list(q) for q in CANDIDATES],"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    quads=[x for r in first["rows"] for x in r["quadruples"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "native_anchor_exact":all(r["native_collapse"] for r in first["rows"]),
        "candidate_count_exact":len(CANDIDATES)==5,
        "lower_order_anchors_reproduced":all(
            all(x["collapse"] for x in r["single_anchors"]) and
            r["sensitive_pairs"]==EXPECTED_PAIRS and r["sensitive_triples"]==EXPECTED_TRIPLES
            for r in first["rows"]),
        "exact_five_quadruples_per_mode":all([tuple(x["quadruple"]) for x in r["quadruples"]]==list(CANDIDATES) for r in first["rows"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in quads),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in quads),
        "programs_exact":all(x["programs_exact"] for x in quads),
        "arrivals_exact":all(x["arrivals_exact"] for x in quads),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in quads),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in quads),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in quads),
        "scientific_integrity":all(x["integrity"] for x in quads) and all(r["native_integrity"] for r in first["rows"]),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"GENUINE_FOURTH_ORDER_CAUSALITY","LOWER_ORDER_MODEL_SUFFICIENT_THROUGH_FOUR","CROSS_MODE_QUADRUPLE_DIFFERENCE","LOWER_ORDER_ANCHOR_NOT_REPRODUCED","NATIVE_ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A59","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A59_LOWER_ORDER_ROBUST_QUADRUPLES":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
