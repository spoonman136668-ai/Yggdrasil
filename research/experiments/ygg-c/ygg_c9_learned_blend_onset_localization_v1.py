#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c8_learned_blend_interaction_dose_v1 as c8
import lu2d_u_authority_dose_response_v1 as dose

c6=c8.c6
EXTENDED_DOSE_ALPHAS=(0.0,0.0625,0.125,0.1875,0.25,0.5,1.0)
PREREG="2e9d62453b77e62bcd02f482980be7e33962c5e5"
PARENT_CLOSURE="a104e7a23107c56262572b0a2dcf89c07da8a263"
ALPHAS=(0.0625,0.125,0.1875,0.25)
ACCEPTED_A25=dict(c8.ACCEPTED_A25)
EXPECTED_CONTEXT=("A","C")
EXPECTED_PARENT_025="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("unregistered alpha")

    parent=c6.c3.lu2v.parent
    old_parent=float(parent.ALPHA)
    old_runtime=float(parent.g.ALPHA)
    old_dose_alphas=tuple(dose.ALPHAS)
    if old_dose_alphas!=(0.0,0.25,0.5,1.0):
        raise AssertionError("unexpected frozen dose allowlist")
    dose.ALPHAS=EXTENDED_DOSE_ALPHAS
    parent.ALPHA=float(alpha)
    parent.g.ALPHA=float(alpha)
    try:
        first=c6.one_pass()
        second=c6.one_pass()
        checks,parent_hash=c6.validity(first,second)
        qual=c6.classify(first["groups"])
    finally:
        parent.ALPHA=old_parent
        parent.g.ALPHA=old_runtime
        dose.ALPHAS=old_dose_alphas

    summaries={
        g["condition"]:{
            "retained":bool(g["summary"]["retained"]),
            "a25_correct_completion_area":g["summary"]["a25_correct_completion_area"],
            "a25_retention_ratio_vs_l8":g["summary"]["a25_retention_ratio_vs_l8"],
            "stream_noncollapse":bool(g["summary"]["stream_noncollapse"]),
            "maturity_pass_count":g["summary"]["a25_maturity_pass_count"],
        }
        for g in first["groups"]
    }
    validity={
        "duplicate_complete_execution_byte_identical":bool(checks["duplicate_complete_execution_byte_identical"]),
        "factorial_lesion_sets_exact":bool(checks["factorial_lesion_sets_exact"]),
        "nonlesion_manifest_fields_frozen":bool(checks["nonlesion_manifest_fields_frozen"]),
        "all_matching_integrity":bool(checks["all_matching_integrity"]),
        "runtime_alpha_restored":float(parent.ALPHA)==old_parent and float(parent.g.ALPHA)==old_runtime,
        "dose_allowlist_restored":tuple(dose.ALPHAS)==old_dose_alphas,
    }
    return {
        "alpha":alpha,
        "validity":validity,
        "valid":all(validity.values()),
        "parent_output_sha256":parent_hash,
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "classification":qual["classification"],
        "interaction_driven":bool(qual["YGG_C6_TRANSITION_INTERACTION"]),
        "retained_by_condition":qual["retained_by_condition"],
        "context_dependent_slots":qual["context_dependent_slots"],
        "paired_effects":qual["paired_effects"],
        "summaries":summaries,
        "base_manifest_sha256":hashlib.sha256(canonical(first["base_manifests"])).hexdigest(),
    }

def onset_category(first_alpha):
    if first_alpha==0.0625:
        return "ONSET_AT_OR_BELOW_00625"
    if first_alpha==0.125:
        return "ONSET_BETWEEN_00625_AND_0125"
    if first_alpha==0.1875:
        return "ONSET_BETWEEN_0125_AND_01875"
    if first_alpha==0.25:
        return "ONSET_BETWEEN_01875_AND_025"
    return "OTHER_VALID_PATTERN"

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    parent=c6.c3.lu2v.parent
    runtime_before=float(parent.g.ALPHA)
    parent_before=float(parent.ALPHA)
    weight_hash=hashlib.sha256(parent.base._weights_bytes()).hexdigest()

    rows=[run_alpha(a) for a in ALPHAS]
    by={float(r["alpha"]):r for r in rows}
    first_alpha=None
    for a in ALPHAS:
        if by[a]["interaction_driven"]:
            first_alpha=a
            break
    category=onset_category(first_alpha)

    anchor=by[0.25]
    alpha_exact=[r["alpha"] for r in rows]==list(ALPHAS)
    manifests_same=len({r["base_manifest_sha256"] for r in rows})==1
    weights_exact=weight_hash==c6.c3.lu2v.WEIGHT_SHA
    runtime_final=float(parent.g.ALPHA)==runtime_before and float(parent.ALPHA)==parent_before
    dose_allowlist_final=tuple(dose.ALPHAS)==(0.0,0.25,0.5,1.0)
    all_valid=all(r["valid"] for r in rows)
    anchor_map=anchor["retained_by_condition"]==ACCEPTED_A25
    anchor_context=tuple(anchor["context_dependent_slots"])==EXPECTED_CONTEXT
    anchor_class=anchor["classification"]=="INTERACTION_DRIVEN"
    anchor_parent=anchor["parent_output_sha256"]==EXPECTED_PARENT_025

    validity={
        "alpha_levels_exact":alpha_exact,
        "base_manifests_identical_across_alpha":manifests_same,
        "learned_weight_identity_exact":weights_exact,
        "factorial_and_matching_valid_each_alpha":all_valid,
        "runtime_alpha_restored_final":runtime_final,
        "dose_allowlist_restored_final":dose_allowlist_final,
        "alpha025_accepted_c7_map_exact":anchor_map,
        "alpha025_context_slots_exact_A_C":anchor_context,
        "alpha025_interaction_classification_exact":anchor_class,
        "alpha025_parent_reference_hash_exact":anchor_parent,
    }
    allowed={
        "ONSET_AT_OR_BELOW_00625",
        "ONSET_BETWEEN_00625_AND_0125",
        "ONSET_BETWEEN_0125_AND_01875",
        "ONSET_BETWEEN_01875_AND_025",
        "OTHER_VALID_PATTERN",
    }
    qualification={
        "YGG_C9_LEARNED_BLEND_ONSET_LOCALIZATION":bool(all(validity.values()) and category in allowed),
        "first_tested_interaction_alpha":first_alpha,
        "onset_classification":category,
        "interaction_by_alpha":{str(a):bool(by[a]["interaction_driven"]) for a in ALPHAS},
    }

    out={
        "schema":1,
        "experiment":"YGG-C9",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "weight_sha256":weight_hash,
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "alpha_results":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
