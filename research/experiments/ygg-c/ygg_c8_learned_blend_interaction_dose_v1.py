#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c6_transition_cell_factorial_v1 as c6

PREREG="dfafdb34cd73f4a31bb6068f41bb92b871d0440e"
PARENT_CLOSURE="c19a8f5bb5f0f446bf6b09dbd711b41b58ecbb4a"
ALPHAS=(0.0,0.25,0.5)
ACCEPTED_A25={
    "000":True,"100":False,"010":True,"001":True,
    "110":False,"101":True,"011":True,"111":True,
}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("unregistered alpha")
    parent=c6.c3.lu2v.parent
    old_parent=float(parent.ALPHA)
    old_runtime=float(parent.g.ALPHA)
    parent.ALPHA=float(alpha)
    parent.g.ALPHA=float(alpha)
    try:
        first=c6.one_pass()
        second=c6.one_pass()
        c6_checks,parent_hash=c6.validity(first,second)
        qual=c6.classify(first["groups"])
    finally:
        parent.ALPHA=old_parent
        parent.g.ALPHA=old_runtime

    checks={
        "duplicate_complete_execution_byte_identical":bool(c6_checks["duplicate_complete_execution_byte_identical"]),
        "factorial_lesion_sets_exact":bool(c6_checks["factorial_lesion_sets_exact"]),
        "nonlesion_manifest_fields_frozen":bool(c6_checks["nonlesion_manifest_fields_frozen"]),
        "all_matching_integrity":bool(c6_checks["all_matching_integrity"]),
        "runtime_alpha_restored":float(parent.ALPHA)==old_parent and float(parent.g.ALPHA)==old_runtime,
    }
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
    return {
        "alpha":alpha,
        "checks":checks,
        "valid":all(checks.values()),
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

def category(by_alpha):
    z=by_alpha["0.0"]
    q=by_alpha["0.25"]
    h=by_alpha["0.5"]
    if z["interaction_driven"]:
        return "INTERACTION_AT_ZERO_BLEND"
    if q["interaction_driven"] and not h["interaction_driven"]:
        return "INTERACTION_LOST_AT_050"
    if (not q["interaction_driven"]) and h["interaction_driven"]:
        return "THRESHOLD_ABOVE_025"
    if q["interaction_driven"] and h["interaction_driven"]:
        same=(
            q["retained_by_condition"]==h["retained_by_condition"]
            and q["context_dependent_slots"]==h["context_dependent_slots"]
        )
        return "BLEND_REQUIRED_STABLE" if same else "BLEND_REQUIRED_DOSE_MODULATED"
    return "OTHER_VALID_PATTERN"

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    parent=c6.c3.lu2v.parent
    runtime_before=float(parent.g.ALPHA)
    parent_before=float(parent.ALPHA)
    weight_hash=hashlib.sha256(parent.base._weights_bytes()).hexdigest()

    rows=[run_alpha(a) for a in ALPHAS]
    by={str(r["alpha"]):r for r in rows}
    anchor_exact=by["0.25"]["retained_by_condition"]==ACCEPTED_A25
    manifests_same=len({r["base_manifest_sha256"] for r in rows})==1
    alpha_exact=[r["alpha"] for r in rows]==list(ALPHAS)
    weights_exact=weight_hash==c6.c3.lu2v.WEIGHT_SHA
    runtime_final=(
        float(parent.g.ALPHA)==runtime_before
        and float(parent.ALPHA)==parent_before
    )
    cat=category(by)
    allowed={
        "BLEND_REQUIRED_STABLE",
        "BLEND_REQUIRED_DOSE_MODULATED",
        "THRESHOLD_ABOVE_025",
        "INTERACTION_AT_ZERO_BLEND",
        "INTERACTION_LOST_AT_050",
        "OTHER_VALID_PATTERN",
    }
    checks={
        "alpha_levels_exact":alpha_exact,
        "alpha025_accepted_c7_map_exact":anchor_exact,
        "factorial_and_matching_valid_each_alpha":all(r["valid"] for r in rows),
        "base_manifests_identical_across_alpha":manifests_same,
        "learned_weight_identity_exact":weights_exact,
        "runtime_alpha_restored_final":runtime_final,
        "mechanism_category_produced":cat in allowed,
    }
    q={
        "YGG_C8_LEARNED_BLEND_INTERACTION_DOSE":all(checks.values()),
        "mechanism_category":cat,
        "alpha0_vs_alpha025_map_different":by["0.0"]["retained_by_condition"]!=by["0.25"]["retained_by_condition"],
        "alpha025_vs_alpha050_map_identical":by["0.25"]["retained_by_condition"]==by["0.5"]["retained_by_condition"],
    }
    out={
        "schema":1,
        "experiment":"YGG-C8",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "weight_sha256":weight_hash,
        "validity":checks,
        "valid":all(checks.values()),
        "qualification":q,
        "alpha_results":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
