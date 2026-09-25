#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a19_l12_to_l13_single_cell_recovery_v1 as a19

PREREG="28f6f20ebea6e2f1f14d16132c15fb7290b76648"
PARENT_CLOSURE="a8d562506ce989acbb79c416b0163399016c1df0"
LEVELS=(13,14,15,16)
EXPECTED_L13_FAILURE=[
    {"replicate":6,"phase":4,"stream":"S","l8":5,"current":3,"ratio":0.6}
]

a13=a19.a13
g=a19.g
p=a19.p
a8=a19.a8
t=a19.t
TARGET_ALPHA=1.0

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def lesion_for(seed,count):
    if count not in LEVELS:
        raise AssertionError("A20 unregistered lesion count")
    base=a19.inherited_l8(seed)
    used=set(base)
    remaining=[c for c in range(p.N) if c not in used]
    ranked=sorted(remaining,key=lambda c:(p.h64("YGG-C3-RESOURCE-PRESSURE",seed,c),c))
    out=sorted(base+ranked[:count-8])
    if len(out)!=count:
        raise AssertionError("A20 lesion cardinality")
    return out

def one_pass(anchor_rows):
    old_lesion_for=a19.lesion_for
    a19.lesion_for=lesion_for
    try:
        groups=[a19.run_count(level,anchor_rows) for level in LEVELS]
    finally:
        a19.lesion_for=old_lesion_for
    return {"groups":groups}

def classify(groups):
    retained={g["lesion_cells"]:bool(g["aggregate"]["stream_noncollapse"]) for g in groups}
    first=next((level for level in LEVELS if retained[level]),None)
    if first is None:
        category="NO_RECOVERY_THROUGH_L16"
    elif all(retained[level] for level in LEVELS if level>=first):
        category=f"THRESHOLD_LIKE_RECOVERY_AT_L{first}"
    else:
        category="IRREGULAR_RECOVERY"
    return first,category,retained

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_alpha=float(g.ALPHA)
    original_validate=t.validate_manifest
    original_lesion=p.lesion_set
    original_schedule=a8.damage_schedule
    original_lfn=a19.lesion_for

    g.ALPHA=TARGET_ALPHA
    try:
        anchor=a13.one_pass()
    finally:
        g.ALPHA=original_alpha

    first=one_pass(anchor["rows"])
    second=one_pass(anchor["rows"])
    b1=canonical(first)
    b2=canonical(second)

    groups=first["groups"]
    by={g["lesion_cells"]:g for g in groups}
    first_recovery,category,retained=classify(groups)

    l13_fail=by[13]["aggregate"]["stream_failures"]
    nesting=True
    for idx in range(len(by[13]["rows"])):
        prev=None
        for level in LEVELS:
            cells=set(by[level]["rows"][idx]["manifest"]["lesion"])
            if prev is not None:
                nesting=nesting and prev.issubset(cells) and len(cells-prev)==1
            prev=cells

    all_frozen_gates=all(all(gp["qualification"].values()) for gp in groups)
    allowed={
        "NO_RECOVERY_THROUGH_L16",
        "IRREGULAR_RECOVERY",
        "THRESHOLD_LIKE_RECOVERY_AT_L13",
        "THRESHOLD_LIKE_RECOVERY_AT_L14",
        "THRESHOLD_LIKE_RECOVERY_AT_L15",
        "THRESHOLD_LIKE_RECOVERY_AT_L16",
    }

    validity={
        "a15_alpha100_anchor_exact":hashlib.sha256(canonical(anchor)).hexdigest()==a19.A15_ALPHA100_HASH,
        "l13_accepted_failure_exact":l13_fail==EXPECTED_L13_FAILURE,
        "strict_one_cell_nesting_13_to_16":bool(nesting),
        "all_frozen_integrity_capability_gates":bool(all_frozen_gates),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "lesion_set_restored":p.lesion_set is original_lesion,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
        "a19_lesion_function_restored":a19.lesion_for is original_lfn,
    }
    qualification={
        "YGG_A20_INTEGRATED_FINE_RECOVERY_MAP":bool(all(validity.values()) and category in allowed),
        "classification":category,
        "first_recovered_level":first_recovery,
        "stream_noncollapse_by_level":{str(k):retained[k] for k in LEVELS},
    }
    out={
        "schema":1,
        "experiment":"YGG-A20",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "levels":list(LEVELS),
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "groups":groups,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
