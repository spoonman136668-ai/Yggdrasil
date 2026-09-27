#!/usr/bin/env python3
import hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a59_lower_order_robust_quadruples_v1 as a59

PREREG="beb9429c59e026b9d33d20bb8543ebdf3a31f95e"
PARENT_RUN="36327040147"
MODES=("U_A0","U_A25")
I=(103,105,106,111,117,121,123,125)
E2={frozenset(x) for x in [(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)]}
E3={frozenset(x) for x in [(105,106,121),(105,121,125),(106,123,125),(111,117,121),(111,117,125),(111,121,125)]}
E4={frozenset((103,105,123,125))}
EDGES=tuple(sorted([tuple(sorted(x)) for x in (E2|E3|E4)]))
CORRUPT=a59.CORRUPT

a44=a59.a44
a41=a59.a41
lu=a59.lu
flip_set=a59.a58.a57.flip_set
exact_change=a59.a58.a57.exact_change

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def all_subsets():
    out=[]
    for k in range(len(I)+1):
        out.extend(tuple(x) for x in itertools.combinations(I,k))
    return out

SUBSETS=all_subsets()

def predicts_noncollapse(subset):
    s=frozenset(subset)
    return any(edge.issubset(s) for edge in (E2|E3|E4))

def known_anchor_expectation(subset):
    s=frozenset(subset); n=len(s)
    if n==0: return True
    if n==1: return True
    if n==2: return s not in E2
    if n==3 and not any(e.issubset(s) for e in E2):
        return s not in E3
    robust3=(n==4 and not any(e.issubset(s) for e in E2) and not any(e.issubset(s) for e in E3))
    if robust3:
        return s not in E4
    return None

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    arms=[]
    for subset in SUBSETS:
        arr=flip_set(native,subset)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        pred_non=predicts_noncollapse(subset)
        obs_collapse=bool(row["collapse"])
        known=known_anchor_expectation(subset)
        arms.append({
            "subset":list(subset),"size":len(subset),
            "predicted_collapse":not pred_non,
            "observed_collapse":obs_collapse,
            "known_anchor_expected_collapse":known,
            "known_anchor_match":True if known is None else obs_collapse==known,
            "prediction_match":obs_collapse==(not pred_non),
            "exact_registered_change":exact_change(native,arr,subset),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    fp=[x["subset"] for x in arms if x["predicted_collapse"] and not x["observed_collapse"]]
    fn=[x["subset"] for x in arms if (not x["predicted_collapse"]) and x["observed_collapse"]]
    return {
        "mode":mode,
        "arms":arms,
        "false_positive_subsets":fp,
        "false_negative_subsets":fn,
        "mismatch_subsets":[x["subset"] for x in arms if not x["prediction_match"]],
        "known_anchor_mismatches":[x["subset"] for x in arms if not x["known_anchor_match"]],
    }

def classify(rows):
    if any(r["known_anchor_mismatches"] for r in rows): return "ANCHOR_NOT_REPRODUCED"
    maps=[[(tuple(a["subset"]),a["observed_collapse"]) for a in r["arms"]] for r in rows]
    if maps[0]!=maps[1]: return "CROSS_MODE_SUBSPACE_DIFFERENCE"
    fp=rows[0]["false_positive_subsets"]; fn=rows[0]["false_negative_subsets"]
    if not fp and not fn: return "HYPERGRAPH_MODEL_EXACT"
    if fp: return "MISSING_HIGHER_ORDER_EDGE"
    if fn: return "NONMONOTONE_EDGE_FAILURE"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"vertex_set":list(I),"frozen_edges":[list(x) for x in EDGES],"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "exact_256_subsets_per_mode":all(len(r["arms"])==256 and [tuple(a["subset"]) for a in r["arms"]]==SUBSETS for r in first["rows"]),
        "all_subsets_unique":len(SUBSETS)==len(set(SUBSETS))==256,
        "frozen_edges_exact":first["frozen_edges"]==[list(x) for x in EDGES],
        "known_lower_order_anchors_reproduced":all(not r["known_anchor_mismatches"] for r in first["rows"]),
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
    allowed={"HYPERGRAPH_MODEL_EXACT","MISSING_HIGHER_ORDER_EDGE","NONMONOTONE_EDGE_FAILURE","CROSS_MODE_SUBSPACE_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A60","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A60_INSENSITIVE_SUBSPACE_HYPERGRAPH":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
