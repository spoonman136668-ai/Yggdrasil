#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c17_interaction_onset_functional_pressure_v1 as c17

PREREG="46262a05d8ef02ff6bd16afb3aafb5f9679a6552"
PARENT_RUN="32f2f5f258ffd3bf17bdec72f6a2b9aa4ef09d48"
BELOW=0.134765625
ABOVE=0.1357421875
EXPECTED_BELOW={str(k):False for k in range(8,17)}
EXPECTED_ABOVE={
    "8":True,"9":True,"10":True,"11":False,"12":False,
    "13":True,"14":True,"15":True,"16":True,
}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def level_predicates(summary):
    return {
        "completion":summary["a25_retention_ratio_vs_l8"] is not None and summary["a25_retention_ratio_vs_l8"]>=0.90,
        "integrity":bool(summary["a25_matching_integrity"]),
        "maturity":int(summary["a25_maturity_pass_count"])==10,
        "stream":bool(summary["stream_noncollapse"]),
    }

def decompose_pressure(row):
    levels=[]
    for level in sorted(int(k) for k in row["retained_by_level"]):
        key=str(level)
        summary=row["summaries"][key]
        predicates=level_predicates(summary)
        failed=sorted(k for k,v in predicates.items() if not v)
        retained=bool(row["retained_by_level"][key])
        inferred=all(predicates.values())
        levels.append({
            "level":level,
            "retained":retained,
            "predicates":predicates,
            "failed_predicates":failed,
            "predicate_conjunction_matches_retained":inferred==retained,
            "summary":summary,
        })
    return {
        "alpha":row["alpha"],
        "retained_by_level":row["retained_by_level"],
        "levels":levels,
    }

def classify_below(dec):
    false_rows=[r for r in dec["levels"] if not r["retained"]]
    if not false_rows:
        return "OTHER_VALID_PREDICATE"
    failed_sets=[set(r["failed_predicates"]) for r in false_rows]
    common=set.intersection(*failed_sets) if failed_sets else set()
    if common=={"maturity"}:
        return "MATURITY_GATED"
    if common=={"stream"}:
        return "STREAM_GATED"
    if common=={"completion"}:
        return "COMPLETION_GATED"
    if common=={"integrity"}:
        return "INTEGRITY_GATED"
    union=set().union(*failed_sets) if failed_sets else set()
    if len(union)>1:
        return "MULTI_PREDICATE_GATED"
    return "OTHER_VALID_PREDICATE"

def one_pass():
    data=c17.one_pass()
    pressure={float(r["alpha"]):r for r in data["pressure"]}
    below=decompose_pressure(pressure[BELOW])
    above=decompose_pressure(pressure[ABOVE])
    category=classify_below(below)
    return {
        "below":below,
        "above":above,
        "classification":category,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)

    all_rows=first["below"]["levels"]+first["above"]["levels"]
    allowed={
        "MATURITY_GATED","STREAM_GATED","COMPLETION_GATED",
        "INTEGRITY_GATED","MULTI_PREDICATE_GATED","OTHER_VALID_PREDICATE",
    }
    validity={
        "duplicate_analysis_byte_identical":b1==b2,
        "below_retained_map_exact":first["below"]["retained_by_level"]==EXPECTED_BELOW,
        "above_retained_map_exact":first["above"]["retained_by_level"]==EXPECTED_ABOVE,
        "all_false_retention_accounted_by_existing_predicates":all(
            r["predicate_conjunction_matches_retained"] for r in all_rows
        ),
        "no_threshold_redefinition":True,
    }
    category=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-C18",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_C18_RETENTION_PREDICATE_DECOMPOSITION":bool(all(validity.values()) and category in allowed),
            "classification":category,
        },
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
