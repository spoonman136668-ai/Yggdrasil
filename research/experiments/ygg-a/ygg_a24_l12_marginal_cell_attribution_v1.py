#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a23_a_context_fine_pressure_map_v1 as a23

PREREG="8b712901de835b21e9fa4e549d9eb2ed12654122"
PARENT_CLOSURE="bdd206305eeacd120e8d151184a9a1ad7c371859"
ALPHA=0.25
MODES=("U_A0","U_A25")
BASE_LEVEL=11
CANDIDATES=(12,13,14,15,16)

a22=a23.a22
a19=a23.a19
a8=a23.a8
g=a23.g
t=a23.t

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def marginal_cell(seed,rank):
    if rank not in CANDIDATES:
        raise AssertionError("A24 unregistered rank")
    prev=set(a23.fine_lesion(seed,rank-1))
    curr=set(a23.fine_lesion(seed,rank))
    added=sorted(curr-prev)
    if len(added)!=1:
        raise AssertionError("A24 marginal cell cardinality")
    return added[0]

def candidate_lesion(seed,level):
    if level==BASE_LEVEL:
        return a23.fine_lesion(seed,BASE_LEVEL)
    if level not in CANDIDATES:
        raise AssertionError("A24 unregistered level")
    base=list(a23.fine_lesion(seed,BASE_LEVEL))
    cell=marginal_cell(seed,level)
    if cell in base:
        raise AssertionError("A24 marginal cell already in anchor")
    out=sorted(base+[cell])
    if len(out)!=12:
        raise AssertionError("A24 candidate lesion cardinality")
    return out

def validate_group(group,level,anchor_total):
    rows=group["rows"]
    expected_count=BASE_LEVEL if level==BASE_LEVEL else 12
    exact=all(
        row["manifest"]["lesion"]==candidate_lesion(row["manifest"]["seed"],level)
        and len(row["manifest"]["lesion"])==expected_count
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
        "expected_lesion_cardinality":expected_count,
        "exact_lesion":bool(exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion),
        "repair_off_zero_branch_damage":bool(zero_branch),
        "matching_maturity_terminal_integrity_exact":bool(integrity),
        "correct_done_total":total,
        "correct_done_ratio_vs_l11":ratio,
        "aggregate_ratio_ge_090":ratio is not None and ratio>=0.90,
    }

def run_mode(mode):
    old_levels=tuple(a22.LEVELS)
    old_lfn=a22.lesion_for
    old_alpha=float(g.ALPHA)
    a22.LEVELS=(BASE_LEVEL,)+CANDIDATES
    a22.lesion_for=candidate_lesion
    g.ALPHA=ALPHA
    try:
        groups={level:a22.run_mode_level(mode,level) for level in (BASE_LEVEL,)+CANDIDATES}
    finally:
        a22.LEVELS=old_levels
        a22.lesion_for=old_lfn
        g.ALPHA=old_alpha

    anchor=groups[BASE_LEVEL]
    anchor_total=sum(row["result"]["correct_done"] for row in anchor["rows"])
    candidate_rows={}
    pass_map={}
    for rank in CANDIDATES:
        failures=a22.stream_failures(anchor,groups[rank])
        checks=validate_group(groups[rank],rank,anchor_total)
        cells=[
            {"replicate":i,"seed":row["manifest"]["seed"],"cell":marginal_cell(row["manifest"]["seed"],rank)}
            for i,row in enumerate(groups[rank]["rows"])
        ]
        candidate_rows[str(rank)]={
            "stream_noncollapse":len(failures)==0,
            "failures":failures,
            "marginal_cells":cells,
            "checks":checks,
        }
        pass_map[str(rank)]=len(failures)==0

    anchor_checks=validate_group(anchor,BASE_LEVEL,anchor_total)
    valid=bool(
        anchor_checks["exact_lesion"]
        and anchor_checks["nonlesion_manifest_fields_frozen"]
        and anchor_checks["repair_off_zero_branch_damage"]
        and anchor_checks["matching_maturity_terminal_integrity_exact"]
        and anchor_checks["aggregate_ratio_ge_090"]
        and all(
            row["checks"]["exact_lesion"]
            and row["checks"]["nonlesion_manifest_fields_frozen"]
            and row["checks"]["repair_off_zero_branch_damage"]
            and row["checks"]["matching_maturity_terminal_integrity_exact"]
            and row["checks"]["aggregate_ratio_ge_090"]
            for row in candidate_rows.values()
        )
    )
    return {
        "mode":mode,
        "valid":valid,
        "anchor_checks":anchor_checks,
        "candidate_pass_map":pass_map,
        "candidates":candidate_rows,
    }

def classify(rows):
    by={r["mode"]:r for r in rows}
    a0=by["U_A0"]["candidate_pass_map"]
    a25=by["U_A25"]["candidate_pass_map"]
    if a0!=a25:
        return "CROSS_MODE_DIFFERENCE"
    failing=[rank for rank,passed in a0.items() if not passed]
    if len(failing)==0:
        return "CUMULATIVE_ONLY"
    if len(failing)==1:
        return "SINGLE_CELL_SPECIFIC"
    return "MULTI_CELL_SENSITIVE"

def one_pass():
    rows=[run_mode(mode) for mode in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    original_levels=tuple(a22.LEVELS)
    original_lfn=a22.lesion_for
    original_alpha=float(g.ALPHA)
    original_validate=t.validate_manifest
    original_schedule=a8.damage_schedule

    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)

    allowed={"SINGLE_CELL_SPECIFIC","MULTI_CELL_SENSITIVE","CUMULATIVE_ONLY","CROSS_MODE_DIFFERENCE"}
    validity={
        "alpha_exact":ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "base_level_exact":BASE_LEVEL==11,
        "candidate_ranks_exact":list(CANDIDATES)==[12,13,14,15,16],
        "all_mode_results_valid":all(r["valid"] for r in first["rows"]),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "a22_levels_restored":tuple(a22.LEVELS)==original_levels,
        "a22_lesion_function_restored":a22.lesion_for is original_lfn,
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
    }
    classification=first["classification"]
    qualification={
        "YGG_A24_L12_MARGINAL_CELL_ATTRIBUTION":bool(all(validity.values()) and classification in allowed),
        "classification":classification,
        "candidate_pass_maps":{r["mode"]:r["candidate_pass_map"] for r in first["rows"]},
    }
    out={
        "schema":1,
        "experiment":"YGG-A24",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alpha":ALPHA,
        "base_level":BASE_LEVEL,
        "candidate_ranks":list(CANDIDATES),
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "mode_results":first["rows"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
