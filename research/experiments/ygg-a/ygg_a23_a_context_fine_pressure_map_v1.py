#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a22_l16_controller_family_attribution_v1 as a22

PREREG="46e278339e4d201bc35c8ffca22d8f836eb3c9b1"
PARENT_CLOSURE="3613dd94d6e9242245d63374d5d0be6ed4340180"
ALPHA=0.25
MODES=("U_A0","U_A25")
LEVELS=tuple(range(8,17))
C_REFERENCE={8:True,9:True,10:True,11:False,12:False,13:True,14:True,15:True,16:True}

a19=a22.a19
a20=a22.a20
a8=a22.a8
g=a22.g
p=a22.p
t=a22.t

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def fine_lesion(seed,count):
    if count not in LEVELS:
        raise AssertionError("A23 unregistered lesion count")
    base=a19.inherited_l8(seed)
    if count==8:
        return base
    used=set(base)
    remaining=[c for c in range(p.N) if c not in used]
    ranked=sorted(remaining,key=lambda c:(p.h64("YGG-C3-RESOURCE-PRESSURE",seed,c),c))
    out=sorted(base+ranked[:count-8])
    if len(out)!=count or not set(base).issubset(out):
        raise AssertionError("A23 fine lesion construction")
    return out

def validate_group(group,count,anchor_total):
    rows=group["rows"]
    exact=all(
        row["manifest"]["lesion"]==fine_lesion(row["manifest"]["seed"],count)
        for row in rows
    )
    zero_branch=all(
        row["branch"]["scheduled"]==0
        and row["branch"]["applied"]==0
        and row["branch"]["repaired"]==0
        for row in rows
    )
    integrity=all(
        row["result"]["incorrect_done"]==0
        and row["result"]["matching_duplicate_cell"]==0
        and row["result"]["matching_duplicate_request"]==0
        and row["maturity"]["pass"]
        and row["horizon_aware_repair_integrity"]
        for row in rows
    )
    base=t.primary_manifests(a8.A1_PREREG)
    nonlesion=all(
        a19.nonlesion_bytes(group["manifests"][i])==a19.nonlesion_bytes(base[i])
        for i in range(len(base))
    )
    total=sum(row["result"]["correct_done"] for row in rows)
    ratio=total/anchor_total if anchor_total else None
    return {
        "exact_lesion":bool(exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion),
        "repair_off_zero_branch_damage":bool(zero_branch),
        "matching_maturity_terminal_integrity_exact":bool(integrity),
        "correct_done_total":total,
        "correct_done_ratio_vs_l8":ratio,
        "aggregate_ratio_ge_090":ratio is not None and ratio>=0.90,
    }

def run_mode_map(mode):
    old_levels=tuple(a22.LEVELS)
    old_lfn=a22.lesion_for
    old_alpha=float(g.ALPHA)

    a22.LEVELS=LEVELS
    a22.lesion_for=fine_lesion
    g.ALPHA=ALPHA
    try:
        groups={level:a22.run_mode_level(mode,level) for level in LEVELS}
    finally:
        a22.LEVELS=old_levels
        a22.lesion_for=old_lfn
        g.ALPHA=old_alpha

    l8=groups[8]
    l8_total=sum(row["result"]["correct_done"] for row in l8["rows"])
    retained={}
    failures={}
    checks={}
    for level in LEVELS:
        retained[level]=len(a22.stream_failures(l8,groups[level]))==0
        failures[str(level)]=a22.stream_failures(l8,groups[level])
        checks[str(level)]=validate_group(groups[level],level,l8_total)

    first_failure=next((level for level in LEVELS if not retained[level]),None)
    first_recovery=None
    if first_failure is not None:
        first_recovery=next((level for level in LEVELS if level>first_failure and retained[level]),None)
    max_passing=max((level for level in LEVELS if retained[level]),default=None)

    nested=True
    for i in range(len(groups[8]["manifests"])):
        prev=None
        for level in LEVELS:
            cells=set(groups[level]["manifests"][i]["lesion"])
            if prev is not None:
                nested=nested and prev.issubset(cells) and len(cells-prev)==1
            prev=cells

    valid=bool(
        nested
        and all(
            v["exact_lesion"]
            and v["nonlesion_manifest_fields_frozen"]
            and v["repair_off_zero_branch_damage"]
            and v["matching_maturity_terminal_integrity_exact"]
            and v["aggregate_ratio_ge_090"]
            for v in checks.values()
        )
    )
    return {
        "mode":mode,
        "valid":valid,
        "strict_one_cell_nesting":bool(nested),
        "stream_noncollapse_by_level":{str(k):retained[k] for k in LEVELS},
        "stream_failures_by_level":failures,
        "first_failure_level":first_failure,
        "first_recovery_level":first_recovery,
        "max_passing_level":max_passing,
        "level_checks":checks,
        "matches_c_reference_stream_map":all(retained[k]==C_REFERENCE[k] for k in LEVELS),
    }

def classify(rows):
    by={r["mode"]:r for r in rows}
    a0={int(k) for k,v in by["U_A0"]["stream_noncollapse_by_level"].items() if v}
    a25={int(k) for k,v in by["U_A25"]["stream_noncollapse_by_level"].items() if v}
    if a0==a25:
        return "IDENTICAL_MAPS"
    if a25.issubset(a0):
        return "A25_WEAKER"
    if a0.issubset(a25):
        return "A25_STRONGER"
    return "CROSSING_MAPS"

def one_pass():
    return {"rows":[run_mode_map(mode) for mode in MODES]}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_levels=tuple(a22.LEVELS)
    original_lfn=a22.lesion_for
    original_alpha=float(g.ALPHA)
    original_validate=t.validate_manifest
    original_lesion=p.lesion_set
    original_schedule=a8.damage_schedule

    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    category=classify(first["rows"])

    validity={
        "alpha_exact":ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "levels_exact":list(LEVELS)==list(range(8,17)),
        "all_mode_maps_valid":all(r["valid"] for r in first["rows"]),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "a22_levels_restored":tuple(a22.LEVELS)==original_levels,
        "a22_lesion_function_restored":a22.lesion_for is original_lfn,
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "lesion_set_restored":p.lesion_set is original_lesion,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
    }
    allowed={"IDENTICAL_MAPS","A25_WEAKER","A25_STRONGER","CROSSING_MAPS"}
    qualification={
        "YGG_A23_A_CONTEXT_FINE_PRESSURE_MAP":bool(all(validity.values()) and category in allowed),
        "cross_mode_classification":category,
        "stream_maps":{r["mode"]:r["stream_noncollapse_by_level"] for r in first["rows"]},
    }
    out={
        "schema":1,
        "experiment":"YGG-A23",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alpha":ALPHA,
        "levels":list(LEVELS),
        "c_reference_stream_map":{str(k):C_REFERENCE[k] for k in LEVELS},
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "mode_results":first["rows"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
