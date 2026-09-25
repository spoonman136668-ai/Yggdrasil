#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c7_paired_arm_interaction_origin_v1 as c7

c6=c7.c6
c3=c6.c3

PREREG="7f6a5711053af0c370158bf2411d6ed889b8a6b3"
PARENT_CLOSURE="c19a8f5bb5f0f446bf6b09dbd711b41b58ecbb4a"
ALPHAS=(0.0,0.125,0.25)
EXPECTED_PARENT_025="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"
ACCEPTED_A25=dict(c7.ACCEPTED_A25)
EXPECTED_CONTEXT_025=("A","C")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def normalized_result(x):
    y=dict(x)
    y.pop("arm",None)
    return y

def parent_teacher_parity(parent_rows):
    for row in parent_rows:
        if normalized_result(row["a0"])!=normalized_result(row["a25"]):
            return False
        if row["maturity"]["a0"]!=row["maturity"]["a25"]:
            return False
    return True

def structural_validity(run):
    exact=True
    lineage=True
    matching=True
    for group in run["groups"]:
        bits=group["condition"]
        expected_count=10+bits.count("1")
        matching=matching and bool(group["summary"]["a25_matching_integrity"])
        for base,m in zip(run["base_manifests"],group["manifests"]):
            l10,a,b,c=c6.transition_cells(base["seed"])
            expected=set(l10)
            for bit,cell in zip(bits,(a,b,c)):
                if bit=="1":
                    expected.add(cell)
            exact=exact and set(m["lesion"])==expected and len(m["lesion"])==expected_count
            lineage=lineage and c3.non_lesion_bytes(m)==c3.non_lesion_bytes(base)
    return {
        "factorial_lesion_sets_exact":bool(exact),
        "nonlesion_manifest_fields_frozen":bool(lineage),
        "all_matching_integrity":bool(matching),
    }

def classify(run):
    retained={g["condition"]:bool(g["summary"]["retained"]) for g in run["groups"]}
    path=bool(
        retained["000"]
        and not retained["100"]
        and not retained["110"]
        and retained["111"]
    )
    effects={}
    context=[]
    for slot in ("A","B","C"):
        rows=c6.paired_effects(retained,slot)
        effects[slot]=rows
        if len({r["effect"] for r in rows})>1:
            context.append(slot)
    if not path:
        classification="PATH_NOT_REPRODUCED"
    elif context:
        classification="INTERACTION_DRIVEN"
    else:
        classification="SINGLE_DIRECTION_OR_ADDITIVE"
    return {
        "retained_by_condition":retained,
        "paired_effects":effects,
        "context_dependent_slots":context,
        "classification":classification,
        "interaction_driven":bool(path and context),
    }

def parent_summary(parent_rows):
    return {
        "a0_correct_completion_area":sum(r["a0"]["events"]["correct_completion_area_phases0_4"] for r in parent_rows),
        "a25_correct_completion_area":sum(r["a25"]["events"]["correct_completion_area_phases0_4"] for r in parent_rows),
        "a0_correct_done":sum(r["a0"]["correct_done"] for r in parent_rows),
        "a25_correct_done":sum(r["a25"]["correct_done"] for r in parent_rows),
        "a0_maturity_pass_count":sum(1 for r in parent_rows if r["maturity"]["a0"]["pass"]),
        "a25_maturity_pass_count":sum(1 for r in parent_rows if r["maturity"]["a25"]["pass"]),
    }

def run_alpha(alpha):
    g=c3.lu2v.parent.g
    old=float(g.ALPHA)
    if abs(old-0.25)>1e-12:
        raise AssertionError("unexpected inherited alpha")
    g.ALPHA=float(alpha)
    try:
        run=c6.one_pass()
    finally:
        g.ALPHA=old

    parent_hash=hashlib.sha256(canonical(run["parent"])).hexdigest()
    cls=classify(run)
    checks=structural_validity(run)
    report_groups=[
        {
            "condition":g["condition"],
            "lesion_cells":g["lesion_cells"],
            "summary":g["summary"],
        }
        for g in run["groups"]
    ]
    return {
        "alpha":alpha,
        "run_sha256":hashlib.sha256(canonical(run)).hexdigest(),
        "parent_sha256":parent_hash,
        "parent_summary":parent_summary(run["parent"]),
        "teacher_parity":parent_teacher_parity(run["parent"]) if alpha==0.0 else None,
        "validity":checks,
        "interaction":cls,
        "groups":report_groups,
    }

def sweep():
    return [run_alpha(a) for a in ALPHAS]

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    first=sweep()
    second=sweep()
    duplicate=canonical(first)==canonical(second)
    by_alpha={float(r["alpha"]):r for r in first}

    zero=by_alpha[0.0]
    mid=by_alpha[0.125]
    full=by_alpha[0.25]

    i0=bool(zero["interaction"]["interaction_driven"])
    i125=bool(mid["interaction"]["interaction_driven"])
    i25=bool(full["interaction"]["interaction_driven"])

    if (not i0) and i125 and i25:
        onset="ONSET_BY_0125"
    elif (not i0) and (not i125) and i25:
        onset="ENDPOINT_ONLY_025"
    else:
        onset="OTHER_NONMONOTONIC_PATTERN"

    first_interaction=None
    for a in ALPHAS:
        if by_alpha[a]["interaction"]["interaction_driven"]:
            first_interaction=a
            break

    structural_all=all(all(r["validity"].values()) for r in first)
    alpha0_teacher=bool(zero["teacher_parity"])
    alpha25_map=full["interaction"]["retained_by_condition"]==ACCEPTED_A25
    alpha25_context=tuple(full["interaction"]["context_dependent_slots"])==EXPECTED_CONTEXT_025
    alpha25_class=full["interaction"]["classification"]=="INTERACTION_DRIVEN"
    alpha25_parent=full["parent_sha256"]==EXPECTED_PARENT_025

    validity={
        "duplicate_complete_execution_byte_identical":duplicate,
        "all_factorial_lesion_sets_exact":structural_all,
        "alpha0_teacher_parity_exact":alpha0_teacher,
        "alpha025_parent_reference_exact":alpha25_parent,
        "alpha025_accepted_c7_map_exact":alpha25_map,
        "alpha025_context_slots_exact_A_C":alpha25_context,
        "alpha025_interaction_classification_exact":alpha25_class,
    }
    valid=all(validity.values())
    qualification={
        "YGG_C8_LEARNED_BLEND_INTERACTION_ONSET":bool(valid and onset in {
            "ONSET_BY_0125","ENDPOINT_ONLY_025","OTHER_NONMONOTONIC_PATTERN"
        }),
        "onset_classification":onset,
        "first_tested_interaction_alpha":first_interaction,
        "interaction_by_alpha":{str(a):bool(by_alpha[a]["interaction"]["interaction_driven"]) for a in ALPHAS},
    }
    out={
        "schema":1,
        "experiment":"YGG-C8",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "validity":validity,
        "valid":valid,
        "qualification":qualification,
        "results":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
