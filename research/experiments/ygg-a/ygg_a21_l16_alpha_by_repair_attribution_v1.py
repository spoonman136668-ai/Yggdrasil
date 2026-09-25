#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a20_integrated_fine_recovery_map_v1 as a20

PREREG="f64a3cfc1fe24c930113a6a1fa96a8e643e71573"
PARENT_CLOSURE="8856415561fcae6bf43db7bc58152021fe5ff872"
ALPHAS=(0.25,0.50,1.00)
LEVEL=16

a19=a20.a19
a13=a20.a13
a8=a20.a8
g=a20.g
p=a20.p
t=a20.t

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def stream_failures(anchor_rows,current_rows,field):
    base={int(r["replicate"]):r[field] for r in anchor_rows}
    failures=[]
    for row in current_rows:
        rep=int(row["replicate"])
        br=base[rep]["result"]["stream_phase"]
        cr=row[field]["result"]["stream_phase"]
        for ph in range(5):
            ps=str(ph)
            for stream in ("C","S"):
                base_n=br[ps][stream]
                cur_n=cr[ps][stream]
                if base_n>=4 and cur_n<0.75*base_n:
                    failures.append({
                        "replicate":rep,
                        "phase":ph,
                        "stream":stream,
                        "l8":base_n,
                        "l16":cur_n,
                        "ratio":cur_n/base_n if base_n else None,
                    })
    return failures

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("A21 unregistered alpha")

    old_g=float(g.ALPHA)
    old_target=float(a19.TARGET_ALPHA)
    old_lfn=a19.lesion_for

    g.ALPHA=float(alpha)
    try:
        anchor=a13.one_pass()
    finally:
        g.ALPHA=old_g

    a19.TARGET_ALPHA=float(alpha)
    a19.lesion_for=a20.lesion_for
    try:
        current=a19.run_count(LEVEL,anchor["rows"])
    finally:
        a19.TARGET_ALPHA=old_target
        a19.lesion_for=old_lfn

    off_fail=stream_failures(anchor["rows"],current["rows"],"a25_off")
    on_fail=stream_failures(anchor["rows"],current["rows"],"a25_on")

    off_zero=all(
        r["a25_off"]["branch"]["scheduled"]==0
        and r["a25_off"]["branch"]["applied"]==0
        and r["a25_off"]["branch"]["repaired"]==0
        for r in current["rows"]
    )
    on_exact=all(
        r["a25_on"]["branch"]["scheduled"]==58
        and r["a25_on"]["branch"]["scheduled_b"]==29
        and r["a25_on"]["branch"]["scheduled_c"]==29
        and r["a25_on"]["branch"]["applied"]==58
        and r["a25_on"]["branch"]["repaired"]==58
        and r["a25_on"]["branch"]["all_repaired_before_d"]
        and r["a25_on"]["branch"]["unrepaired_terminal"]==0
        and r["a25_on"]["branch_stats"]["d_while_branch_incorrect"]==0
        for r in current["rows"]
    )
    integrity=all(
        r[field]["result"]["incorrect_done"]==0
        and r[field]["result"]["matching_duplicate_cell"]==0
        and r[field]["result"]["matching_duplicate_request"]==0
        and r[field]["maturity"]["pass"]
        and r[field]["horizon_aware_repair_integrity"]
        for r in current["rows"]
        for field in ("a25_off","a25_on")
    )
    ratios=[
        r["a25_on"]["result"]["correct_done"]/r["a25_off"]["result"]["correct_done"]
        if r["a25_off"]["result"]["correct_done"] else None
        for r in current["rows"]
    ]
    off_total=sum(r["a25_off"]["result"]["correct_done"] for r in current["rows"])
    on_total=sum(r["a25_on"]["result"]["correct_done"] for r in current["rows"])
    aggregate_ratio=on_total/off_total if off_total else None

    checks={
        "exact_l16_nested_lesion":bool(current["qualification"]["exact_nested_lesion_construction"]),
        "nonlesion_manifest_fields_frozen":bool(current["qualification"]["nonlesion_manifest_fields_frozen"]),
        "repair_off_zero_branch_damage":bool(off_zero),
        "repair_on_exact_58":bool(on_exact),
        "matching_maturity_terminal_integrity_exact":bool(integrity),
        "aggregate_on_off_ratio_ge_095":aggregate_ratio is not None and aggregate_ratio>=0.95,
        "all_world_on_off_ratio_ge_090":all(x is not None and x>=0.90 for x in ratios),
        "learned_arm_materially_exercised":bool(current["qualification"]["learned_arm_materially_exercised"]),
        "runtime_alpha_restored_after_cell":float(g.ALPHA)==old_g,
        "a19_target_alpha_restored_after_cell":float(a19.TARGET_ALPHA)==old_target,
        "a19_lesion_function_restored_after_cell":a19.lesion_for is old_lfn,
    }
    return {
        "alpha":alpha,
        "valid":all(checks.values()),
        "checks":checks,
        "anchor_sha256":hashlib.sha256(canonical(anchor)).hexdigest(),
        "repair_off":{
            "stream_noncollapse":len(off_fail)==0,
            "stream_failures":off_fail,
            "correct_done_total":off_total,
        },
        "repair_on":{
            "stream_noncollapse":len(on_fail)==0,
            "stream_failures":on_fail,
            "correct_done_total":on_total,
            "on_off_correct_done_ratio":aggregate_ratio,
        },
    }

def classify(rows):
    off=[r["repair_off"]["stream_noncollapse"] for r in rows]
    on=[r["repair_on"]["stream_noncollapse"] for r in rows]
    all_cells=off+on
    if all(all_cells):
        return "NO_STREAM_FAILURE_AT_L16"
    if not any(all_cells):
        return "PERSISTENT_STREAM_FAILURE"

    same_pattern=off==on
    off_transition=len(set(off))>1
    on_transition=len(set(on))>1
    alpha_transition=off_transition or on_transition
    repair_diff=any(a!=b for a,b in zip(off,on))

    if same_pattern and alpha_transition:
        return "ALPHA_DOMINANT"
    if repair_diff and not alpha_transition:
        return "REPAIR_DOMINANT"
    if repair_diff and alpha_transition:
        return "MIXED_ALPHA_REPAIR"
    return "OTHER_VALID_PATTERN"

def one_pass():
    return {"rows":[run_alpha(a) for a in ALPHAS]}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_g=float(g.ALPHA)
    original_target=float(a19.TARGET_ALPHA)
    original_lfn=a19.lesion_for
    original_validate=t.validate_manifest
    original_lesion=p.lesion_set
    original_schedule=a8.damage_schedule

    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    category=classify(first["rows"])

    allowed={
        "ALPHA_DOMINANT",
        "REPAIR_DOMINANT",
        "MIXED_ALPHA_REPAIR",
        "NO_STREAM_FAILURE_AT_L16",
        "PERSISTENT_STREAM_FAILURE",
        "OTHER_VALID_PATTERN",
    }
    matrix={}
    for row in first["rows"]:
        matrix[str(row["alpha"])]={
            "repair_off":row["repair_off"]["stream_noncollapse"],
            "repair_on":row["repair_on"]["stream_noncollapse"],
        }

    validity={
        "alpha_levels_exact":[r["alpha"] for r in first["rows"]]==list(ALPHAS),
        "all_factorial_cells_valid":all(r["valid"] for r in first["rows"]),
        "duplicate_complete_factorial_byte_identical":b1==b2,
        "runtime_alpha_restored_final":float(g.ALPHA)==original_g,
        "a19_target_alpha_restored_final":float(a19.TARGET_ALPHA)==original_target,
        "a19_lesion_function_restored_final":a19.lesion_for is original_lfn,
        "validator_restored_final":t.validate_manifest is original_validate,
        "lesion_set_restored_final":p.lesion_set is original_lesion,
        "damage_schedule_restored_final":a8.damage_schedule is original_schedule,
    }
    qualification={
        "YGG_A21_L16_ALPHA_BY_REPAIR_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
        "attribution_classification":category,
        "stream_noncollapse_matrix":matrix,
    }
    out={
        "schema":1,
        "experiment":"YGG-A21",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "lesion_cells":LEVEL,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "alpha_results":first["rows"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
