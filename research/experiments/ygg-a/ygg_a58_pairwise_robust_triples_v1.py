#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a57_insensitive_pair_flip_v1 as a57

PREREG="927562ce4491fa19dcb6af96db12483383ec8989"
PARENT_RUN="36317382651"
MODES=("U_A0","U_A25")
I=tuple(a57.I)
E={tuple(x) for x in [(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)]}
CANDIDATES=tuple(
    t for t in itertools.combinations(I,3)
    if all(tuple(sorted(p)) not in E for p in itertools.combinations(t,2))
)
CORRUPT=a57.CORRUPT
a44=a57.a44
a41=a57.a41
lu=a57.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one_mode(mode):
    inherited=a57.one_mode(mode)
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    triples=[]
    for t in CANDIDATES:
        arr=a57.flip_set(native,t)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        triples.append({
            "triple":list(t),"collapse":bool(row["collapse"]),
            "exact_registered_change":a57.exact_change(native,arr,t),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    sensitive=[x["triple"] for x in triples if not x["collapse"]]
    return {
        "mode":mode,
        "native_collapse":inherited["native_collapse"],
        "single_anchors":inherited["single_anchors"],
        "pairs":inherited["pairs"],
        "sensitive_pairs":inherited["sensitive_pairs"],
        "triples":triples,
        "sensitive_triples":sensitive,
        "native_integrity":inherited["native_integrity"]
    }

def classify(rows):
    if not all(r["native_collapse"] for r in rows): return "NATIVE_ANCHOR_NOT_REPRODUCED"
    expected_pairs=[list(x) for x in sorted(E)]
    if not all(all(x["collapse"] for x in r["single_anchors"]) and r["sensitive_pairs"]==expected_pairs for r in rows):
        return "PAIR_ANCHOR_NOT_REPRODUCED"
    if rows[0]["sensitive_triples"]!=rows[1]["sensitive_triples"]:
        return "CROSS_MODE_TRIPLE_DIFFERENCE"
    if rows[0]["sensitive_triples"]: return "GENUINE_THIRD_ORDER_CAUSALITY"
    return "PAIRWISE_MODEL_SUFFICIENT_WITHIN_I"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"candidate_triples":[list(t) for t in CANDIDATES],"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    triples=[x for r in first["rows"] for x in r["triples"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "native_anchor_exact":all(r["native_collapse"] for r in first["rows"]),
        "candidate_count_exact":len(CANDIDATES)==23,
        "candidate_set_pairwise_robust":all(all(tuple(sorted(p)) not in E for p in itertools.combinations(t,2)) for t in CANDIDATES),
        "a57_single_anchors_reproduced":all(all(x["collapse"] for x in r["single_anchors"]) for r in first["rows"]),
        "a57_sensitive_pairs_reproduced":all(r["sensitive_pairs"]==[list(x) for x in sorted(E)] for r in first["rows"]),
        "exact_23_triples_per_mode":all([tuple(x["triple"]) for x in r["triples"]]==list(CANDIDATES) for r in first["rows"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in triples),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in triples),
        "programs_exact":all(x["programs_exact"] for x in triples),
        "arrivals_exact":all(x["arrivals_exact"] for x in triples),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in triples),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in triples),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in triples),
        "scientific_integrity":all(x["integrity"] for x in triples) and all(r["native_integrity"] for r in first["rows"]),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"GENUINE_THIRD_ORDER_CAUSALITY","PAIRWISE_MODEL_SUFFICIENT_WITHIN_I","CROSS_MODE_TRIPLE_DIFFERENCE","PAIR_ANCHOR_NOT_REPRODUCED","NATIVE_ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A58","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A58_PAIRWISE_ROBUST_TRIPLES":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
