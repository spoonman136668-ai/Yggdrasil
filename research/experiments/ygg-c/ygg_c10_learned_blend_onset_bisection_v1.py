#!/usr/bin/env python3
import json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c9_learned_blend_onset_localization_v1 as c9

PREREG="43883b0149b42ea21deac7dea70b7c831c7a01ac"
PARENT_CLOSURE="193f06d96b9807e43071a228dcc93a4de706da4c"
ALPHAS=(0.125,0.15625,0.1875)
EXTENDED=(0.0,0.0625,0.125,0.15625,0.1875,0.25,0.5,1.0)
ANCHOR_0125="9f6a7bf9f64ee726a1f705a17cce22c99a9996d2dfa883c0740c3d2fc8bbfc26"
ANCHOR_01875="75e0993a93235bb08e00461c855f42a5ca220abe778a803492283282469ad7b4"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    old_alphas=tuple(c9.ALPHAS)
    old_extended=tuple(c9.EXTENDED_DOSE_ALPHAS)
    if old_alphas!=(0.0625,0.125,0.1875,0.25):
        raise SystemExit("YGG_C10_UNEXPECTED_C9_ALPHA_SET")
    if old_extended!=(0.0,0.0625,0.125,0.1875,0.25,0.5,1.0):
        raise SystemExit("YGG_C10_UNEXPECTED_C9_EXTENDED_SET")

    c9.ALPHAS=ALPHAS
    c9.EXTENDED_DOSE_ALPHAS=EXTENDED
    try:
        rows=[c9.run_alpha(a) for a in ALPHAS]
    finally:
        c9.ALPHAS=old_alphas
        c9.EXTENDED_DOSE_ALPHAS=old_extended

    by={float(r["alpha"]):r for r in rows}
    lo=by[0.125]
    mid=by[0.15625]
    hi=by[0.1875]

    category=(
        "ONSET_BETWEEN_0125_AND_015625"
        if mid["interaction_driven"]
        else "ONSET_BETWEEN_015625_AND_01875"
    )

    validity={
        "alpha_levels_exact":[r["alpha"] for r in rows]==list(ALPHAS),
        "alpha0125_duplicate_anchor_exact":lo["duplicate_sha256"]==ANCHOR_0125,
        "alpha01875_duplicate_anchor_exact":hi["duplicate_sha256"]==ANCHOR_01875,
        "alpha0125_interaction_false":not lo["interaction_driven"],
        "alpha01875_interaction_true":bool(hi["interaction_driven"]),
        "alpha01875_context_slots_exact_A_C":tuple(hi["context_dependent_slots"])==("A","C"),
        "all_rows_valid":all(r["valid"] for r in rows),
        "all_duplicate_exact":all(r["validity"]["duplicate_complete_execution_byte_identical"] for r in rows),
        "all_matching_integrity":all(r["validity"]["all_matching_integrity"] for r in rows),
        "all_factorial_lesions_exact":all(r["validity"]["factorial_lesion_sets_exact"] for r in rows),
        "all_nonlesion_lineage_frozen":all(r["validity"]["nonlesion_manifest_fields_frozen"] for r in rows),
        "all_runtime_alpha_restored":all(r["validity"]["runtime_alpha_restored"] for r in rows),
        "all_dose_allowlists_restored":all(r["validity"]["dose_allowlist_restored"] for r in rows),
        "c9_alpha_globals_restored":tuple(c9.ALPHAS)==old_alphas,
        "c9_extended_globals_restored":tuple(c9.EXTENDED_DOSE_ALPHAS)==old_extended,
    }
    qualification={
        "YGG_C10_LEARNED_BLEND_ONSET_BISECTION":bool(
            all(validity.values()) and category in {
                "ONSET_BETWEEN_0125_AND_015625",
                "ONSET_BETWEEN_015625_AND_01875",
            }
        ),
        "onset_classification":category,
        "midpoint_alpha":0.15625,
        "midpoint_interaction_driven":bool(mid["interaction_driven"]),
    }
    out={
        "schema":1,
        "experiment":"YGG-C10",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "alpha_results":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
