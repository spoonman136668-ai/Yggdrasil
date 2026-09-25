#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c5_fine_pressure_transition_v1 as c5
import lu2d_u_authority_dose_response_v1 as dose

EXTENDED_DOSE_ALPHAS=(0.0,0.1357421875,0.25,0.5,1.0)

PREREG="c32e13303c54cb2fac2f2342d4cdf5d052871d56"
PARENT_CLOSURE="1c19f852ff1472abf167246ac70eef2c11aa5106"
ALPHAS=(0.1357421875,0.25)
LEVELS=tuple(range(8,17))

c3=c5.c3
lu2v=c3.lu2v
parent=lu2v.parent

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("C16 unregistered alpha")
    old_parent=float(parent.ALPHA)
    old_runtime=float(parent.g.ALPHA)
    old_fine=c3.pressure_lesion
    old_dose_alphas=tuple(dose.ALPHAS)
    if old_dose_alphas!=(0.0,0.25,0.5,1.0):
        raise AssertionError("unexpected frozen dose allowlist")
    weight_before=hashlib.sha256(parent.base._weights_bytes()).hexdigest()

    dose.ALPHAS=EXTENDED_DOSE_ALPHAS
    parent.ALPHA=float(alpha)
    parent.g.ALPHA=float(alpha)
    c3.pressure_lesion=c5.fine_pressure
    try:
        first=c5.one_pass()
        second=c5.one_pass()
    finally:
        c3.pressure_lesion=old_fine
        parent.ALPHA=old_parent
        parent.g.ALPHA=old_runtime
        dose.ALPHAS=old_dose_alphas

    groups={g["lesion_cells"]:g for g in first["groups"]}
    duplicate=canonical(first)==canonical(second)

    exact_cardinality=True
    nested=True
    l8_exact=True
    nonlesion=True
    matching=True
    for idx,base in enumerate(first["base_manifests"]):
        prev=None
        for count in LEVELS:
            m=groups[count]["manifests"][idx]
            cells=set(m["lesion"])
            exact_cardinality=exact_cardinality and len(cells)==count
            if prev is not None:
                nested=nested and prev.issubset(cells) and len(cells-prev)==1
            prev=cells
            nonlesion=nonlesion and c3.non_lesion_bytes(m)==c3.non_lesion_bytes(base)
        l8_exact=l8_exact and groups[8]["manifests"][idx]["lesion"]==c3.inherited_lesion(base["seed"])
    for count in LEVELS:
        matching=matching and bool(groups[count]["summary"]["a25_matching_integrity"])

    weight_after=hashlib.sha256(parent.base._weights_bytes()).hexdigest()
    validity={
        "duplicate_complete_sweep_byte_identical":duplicate,
        "all_levels_exact_cardinality":bool(exact_cardinality),
        "strictly_nested_one_cell_increments":bool(nested),
        "l8_exact_inherited_lesion":bool(l8_exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion),
        "all_matching_integrity":bool(matching),
        "learned_weight_identity_exact":(
            weight_before==lu2v.WEIGHT_SHA and weight_after==lu2v.WEIGHT_SHA
        ),
        "runtime_alpha_restored":float(parent.ALPHA)==old_parent and float(parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(dose.ALPHAS)==old_dose_alphas,
        "pressure_lesion_function_restored":c3.pressure_lesion is old_fine,
    }
    summaries={}
    retained={}
    for count in LEVELS:
        s=groups[count]["summary"]
        retained[count]=bool(s["retained"])
        summaries[str(count)]={
            "retained":bool(s["retained"]),
            "a25_correct_completion_area":s["a25_correct_completion_area"],
            "a25_retention_ratio_vs_l8":s["a25_retention_ratio_vs_l8"],
            "a25_correct_done_total":s["a25_correct_done_total"],
            "a25_maturity_pass_count":s["a25_maturity_pass_count"],
            "a25_matching_integrity":bool(s["a25_matching_integrity"]),
            "stream_noncollapse":bool(s["stream_noncollapse"]),
        }

    failures=[k for k in LEVELS if not retained[k]]
    first_failure=min(failures) if failures else None
    first_recovery=None
    if first_failure is not None:
        first_recovery=next((k for k in LEVELS if k>first_failure and retained[k]),None)
    max_retained=max((k for k in LEVELS if retained[k]),default=None)

    return {
        "alpha":alpha,
        "valid":all(validity.values()),
        "validity":validity,
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "weight_sha256":weight_before,
        "retained_by_level":{str(k):retained[k] for k in LEVELS},
        "first_failure_level":first_failure,
        "first_recovery_level":first_recovery,
        "max_retained_level":max_retained,
        "summaries":summaries,
    }

def classify(near,ref):
    n={int(k):bool(v) for k,v in near["retained_by_level"].items()}
    r={int(k):bool(v) for k,v in ref["retained_by_level"].items()}
    if n==r:
        return "NEAR_ONSET_MATCHES_REFERENCE"
    nset={k for k,v in n.items() if v}
    rset={k for k,v in r.items() if v}
    if nset.issubset(rset) and nset!=rset:
        return "NEAR_ONSET_WEAKER"
    if rset.issubset(nset) and nset!=rset:
        return "NEAR_ONSET_STRONGER"
    return "CROSSING_PATTERNS"

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    before_parent=float(parent.ALPHA)
    before_runtime=float(parent.g.ALPHA)
    before_dose=tuple(dose.ALPHAS)
    rows=[run_alpha(a) for a in ALPHAS]
    by={float(r["alpha"]):r for r in rows}
    category=classify(by[0.1357421875],by[0.25])
    allowed={
        "NEAR_ONSET_MATCHES_REFERENCE",
        "NEAR_ONSET_WEAKER",
        "NEAR_ONSET_STRONGER",
        "CROSSING_PATTERNS",
    }
    validity={
        "alpha_levels_exact":[r["alpha"] for r in rows]==list(ALPHAS),
        "all_alpha_sweeps_valid":all(r["valid"] for r in rows),
        "runtime_alpha_restored_final":float(parent.ALPHA)==before_parent and float(parent.g.ALPHA)==before_runtime,
        "dose_allowlist_restored_final":tuple(dose.ALPHAS)==before_dose,
        "learned_weight_identity_same_across_alpha":len({r["weight_sha256"] for r in rows})==1,
    }
    qualification={
        "YGG_C16_NEAR_ONSET_PRESSURE_SWEEP":bool(all(validity.values()) and category in allowed),
        "comparison_classification":category,
        "near_onset_retained_by_level":by[0.1357421875]["retained_by_level"],
        "reference_retained_by_level":by[0.25]["retained_by_level"],
    }
    out={
        "schema":1,
        "experiment":"YGG-C16",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "levels":list(LEVELS),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "alpha_results":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
