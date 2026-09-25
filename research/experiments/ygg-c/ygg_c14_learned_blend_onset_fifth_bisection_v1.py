#!/usr/bin/env python3
import json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c9_learned_blend_onset_localization_v1 as c9

PREREG="dfea1e1d28e3798d9c2de7c50088fd5c74edb1a6"
PARENT_CLOSURE="e9373550e946396aa8e6d0c3af529a77e1a75994"
ALPHAS=(0.1328125,0.134765625,0.13671875)
EXTENDED=(0.0,0.0625,0.125,0.1328125,0.134765625,0.13671875,0.140625,0.15625,0.1875,0.25,0.5,1.0)
ANCHOR_01328125="35a4341d528efdee8dd14320b132f1d01727987dcadb1c4cd3bd903a8d856a55"
ANCHOR_013671875="90f0869984ed21292635bdad3be26859645f3a837b325eb22e083b4a1a24414b"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    old_alphas=tuple(c9.ALPHAS)
    old_extended=tuple(c9.EXTENDED_DOSE_ALPHAS)
    if old_alphas!=(0.0625,0.125,0.1875,0.25):
        raise SystemExit("YGG_C14_UNEXPECTED_C9_ALPHA_SET")
    if old_extended!=(0.0,0.0625,0.125,0.1875,0.25,0.5,1.0):
        raise SystemExit("YGG_C14_UNEXPECTED_C9_EXTENDED_SET")

    c9.ALPHAS=ALPHAS
    c9.EXTENDED_DOSE_ALPHAS=EXTENDED
    try:
        rows=[c9.run_alpha(a) for a in ALPHAS]
    finally:
        c9.ALPHAS=old_alphas
        c9.EXTENDED_DOSE_ALPHAS=old_extended

    by={float(r["alpha"]):r for r in rows}
    lo=by[0.1328125]
    mid=by[0.134765625]
    hi=by[0.13671875]

    category=(
        "ONSET_BETWEEN_01328125_AND_0134765625"
        if mid["interaction_driven"]
        else "ONSET_BETWEEN_0134765625_AND_013671875"
    )

    validity={
        "alpha_levels_exact":[r["alpha"] for r in rows]==list(ALPHAS),
        "alpha01328125_duplicate_anchor_exact":lo["duplicate_sha256"]==ANCHOR_01328125,
        "alpha013671875_duplicate_anchor_exact":hi["duplicate_sha256"]==ANCHOR_013671875,
        "alpha01328125_interaction_false":not lo["interaction_driven"],
        "alpha013671875_interaction_true":bool(hi["interaction_driven"]),
        "alpha013671875_context_slots_exact_A_C":tuple(hi["context_dependent_slots"])==("A","C"),
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
        "YGG_C14_LEARNED_BLEND_ONSET_FIFTH_BISECTION":bool(
            all(validity.values()) and category in {
                "ONSET_BETWEEN_01328125_AND_0134765625",
                "ONSET_BETWEEN_0134765625_AND_013671875",
            }
        ),
        "onset_classification":category,
        "midpoint_alpha":0.134765625,
        "midpoint_interaction_driven":bool(mid["interaction_driven"]),
    }
    out={
        "schema":1,
        "experiment":"YGG-C14",
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
