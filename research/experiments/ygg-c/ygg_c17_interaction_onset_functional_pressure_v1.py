#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c16_near_onset_pressure_sweep_v1 as c16
import ygg_c15_learned_blend_onset_terminal_bisection_v1 as c15

PREREG="bc58dfcf69a7f7b107ff7d9f99651c642ccb619f"
PARENT_CLOSURE="df34abeeda7b4fe185f57676bf6c146a118c423b"
ALPHAS=(0.134765625,0.1357421875)
EXTENDED=(0.0,0.134765625,0.1357421875,0.25,0.5,1.0)
BELOW_SHA="4a649d00ea49a990248a0f258c49d360808085577cb3927c88bba951c936e947"
ABOVE_SHA="2f862a9878318ffde0e0401ecfb4372b386032d31f5d0a4a353d1ce558c6df59"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def classify(below,above):
    b={int(k):bool(v) for k,v in below["retained_by_level"].items()}
    a={int(k):bool(v) for k,v in above["retained_by_level"].items()}
    if b==a:
        return "BELOW_MATCHES_ABOVE"
    bs={k for k,v in b.items() if v}
    aset={k for k,v in a.items() if v}
    if bs.issubset(aset) and bs!=aset:
        return "BELOW_WEAKER"
    if aset.issubset(bs) and bs!=aset:
        return "BELOW_STRONGER"
    return "CROSSING_PATTERNS"

def one_pass():
    old_alphas=tuple(c16.ALPHAS)
    old_extended=tuple(c16.EXTENDED_DOSE_ALPHAS)
    c16.ALPHAS=ALPHAS
    c16.EXTENDED_DOSE_ALPHAS=EXTENDED
    try:
        pressure=[c16.run_alpha(a) for a in ALPHAS]
    finally:
        c16.ALPHAS=old_alphas
        c16.EXTENDED_DOSE_ALPHAS=old_extended

    anchors=[c15.run_alpha(a) for a in ALPHAS]
    return {"pressure":pressure,"anchors":anchors}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    old_alphas=tuple(c16.ALPHAS)
    old_extended=tuple(c16.EXTENDED_DOSE_ALPHAS)

    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)

    pressure={float(r["alpha"]):r for r in first["pressure"]}
    anchors={float(r["alpha"]):r for r in first["anchors"]}
    below=pressure[0.134765625]
    above=pressure[0.1357421875]
    below_anchor=anchors[0.134765625]
    above_anchor=anchors[0.1357421875]
    category=classify(below,above)

    validity={
        "alpha_levels_exact":[r["alpha"] for r in first["pressure"]]==list(ALPHAS),
        "all_pressure_sweeps_valid":all(r["valid"] for r in first["pressure"]),
        "duplicate_complete_experiment_byte_identical":b1==b2,
        "below_onset_anchor_sha_exact":below_anchor["duplicate_sha256"]==BELOW_SHA,
        "below_onset_anchor_noninteraction":not bool(below_anchor["interaction_driven"]),
        "above_onset_anchor_sha_exact":above_anchor["duplicate_sha256"]==ABOVE_SHA,
        "above_onset_anchor_interaction":bool(above_anchor["interaction_driven"]),
        "above_onset_context_slots_exact_A_C":tuple(above_anchor["context_dependent_slots"])==("A","C"),
        "learned_weight_identity_exact":below["weight_sha256"]==above["weight_sha256"]==c16.lu2v.WEIGHT_SHA,
        "c16_alpha_globals_restored":tuple(c16.ALPHAS)==old_alphas,
        "c16_extended_globals_restored":tuple(c16.EXTENDED_DOSE_ALPHAS)==old_extended,
    }

    allowed={"BELOW_MATCHES_ABOVE","BELOW_WEAKER","BELOW_STRONGER","CROSSING_PATTERNS"}
    qualification={
        "YGG_C17_INTERACTION_ONSET_FUNCTIONAL_PRESSURE_TEST":bool(all(validity.values()) and category in allowed),
        "comparison_classification":category,
        "below_retained_by_level":below["retained_by_level"],
        "above_retained_by_level":above["retained_by_level"],
    }

    out={
        "schema":1,
        "experiment":"YGG-C17",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "pressure_results":first["pressure"],
        "anchor_results":[{
            "alpha":r["alpha"],
            "duplicate_sha256":r["duplicate_sha256"],
            "interaction_driven":r["interaction_driven"],
            "context_dependent_slots":r["context_dependent_slots"],
        } for r in first["anchors"]],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
