#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a24_l12_marginal_cell_attribution_v1 as a24
import ygg_a25_cell59_portability_v1 as a25

PREREG="e24e04bf26dca2b0a7e849ac0b34a691b712699c"
A24_CLOSURE="64d1aed4e8a4a8aea41324ae3a6625c4beb4e6ee"
A25_RUN="33a0c812893f652e8b7c1bce9c0080dce6743536"
REPLICATE=6
RANK=12
MODES=("U_A0","U_A25")

a22=a24.a22
a8=a24.a8
g=a24.g
t=a24.t
p=a22.p

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def base_manifest():
    rows=t.primary_manifests(a8.A1_PREREG)
    found=[m for m in rows if int(m["replicate"])==REPLICATE]
    if len(found)!=1:
        raise AssertionError("A26 replicate-6 base manifest cardinality")
    return found[0]

def a24_manifest(base):
    old_lfn=a22.lesion_for
    a22.lesion_for=a24.candidate_lesion
    try:
        return a22.manifest_for(base,RANK)
    finally:
        a22.lesion_for=old_lfn

def a25_manifest(base):
    return a25.manifest_for(base,True)

def first_difference(left,right):
    keys=sorted(set(left)|set(right))
    for k in keys:
        if canonical(left.get(k))!=canonical(right.get(k)):
            return {"field":k,"a24":left.get(k),"a25":right.get(k)}
    return None

def select_rep6(group):
    rows=[r for r in group["rows"] if int(r["manifest"]["replicate"])==REPLICATE]
    if len(rows)!=1:
        raise AssertionError("A26 replicate-6 runtime row cardinality")
    return rows[0]

def run_a24_path(mode):
    old_levels=tuple(a22.LEVELS)
    old_lfn=a22.lesion_for
    old_alpha=float(g.ALPHA)
    a22.LEVELS=(a24.BASE_LEVEL,)+a24.CANDIDATES
    a22.lesion_for=a24.candidate_lesion
    g.ALPHA=a24.ALPHA
    try:
        _anchor=a22.run_mode_level(mode,a24.BASE_LEVEL)
        candidate=a22.run_mode_level(mode,RANK)
        return select_rep6(candidate)
    finally:
        a22.LEVELS=old_levels
        a22.lesion_for=old_lfn
        g.ALPHA=old_alpha

def run_a25_path(mode):
    old_alpha=float(g.ALPHA)
    g.ALPHA=a25.ALPHA
    try:
        _anchor=a25.run_group(mode,False)
        target=a25.run_group(mode,True)
        return select_rep6(target)
    finally:
        g.ALPHA=old_alpha

def row_fingerprint(row):
    result=row["result"]
    return {
        "result_sha256":digest(result),
        "stream_phase_sha256":digest(result["stream_phase"]),
        "state_sha256":result.get("state_sha256"),
        "trace_sha256":result.get("trace_sha256"),
        "correct_done":result.get("correct_done"),
        "stream_phase":result.get("stream_phase"),
    }

def one_pass():
    base=base_manifest()
    m24=a24_manifest(base)
    m25=a25_manifest(base)
    manifest_equal=canonical(m24)==canonical(m25)
    diff=first_difference(m24,m25)

    runtime24=sorted(a24.candidate_lesion(base["seed"],RANK))
    runtime25=sorted(a25.test_lesion(base["seed"]))
    runtime_equal=runtime24==runtime25
    validator_equal=a22.pressure_validate is a25.a22.pressure_validate

    mode_rows=[]
    for mode in MODES:
        r24=run_a24_path(mode)
        r25=run_a25_path(mode)
        f24=row_fingerprint(r24)
        f25=row_fingerprint(r25)
        mode_rows.append({
            "mode":mode,
            "a24":f24,
            "a25":f25,
            "result_equal":f24["result_sha256"]==f25["result_sha256"],
            "stream_phase_equal":f24["stream_phase_sha256"]==f25["stream_phase_sha256"],
            "state_equal":f24["state_sha256"]==f25["state_sha256"],
            "trace_equal":f24["trace_sha256"]==f25["trace_sha256"],
        })

    if not manifest_equal:
        category="INPUT_DIVERGENCE"
    elif not runtime_equal:
        category="RUNTIME_BINDING_DIVERGENCE"
    elif any(not (r["result_equal"] and r["stream_phase_equal"] and r["state_equal"]) for r in mode_rows):
        category="EXECUTION_PATH_DIVERGENCE"
    elif all(r["result_equal"] and r["stream_phase_equal"] and r["state_equal"] for r in mode_rows):
        category="EXACT_EQUIVALENCE_REPRODUCED"
    else:
        category="OTHER_VALID_DISCREPANCY"

    return {
        "replicate":REPLICATE,
        "seed":base["seed"],
        "a24_manifest_sha256":digest(m24),
        "a25_manifest_sha256":digest(m25),
        "manifest_byte_identical":manifest_equal,
        "first_manifest_difference":diff,
        "a24_lesion":m24["lesion"],
        "a25_lesion":m25["lesion"],
        "runtime_a24_lesion":runtime24,
        "runtime_a25_lesion":runtime25,
        "runtime_binding_equal":runtime_equal,
        "validator_path_equal":validator_equal,
        "mode_results":mode_rows,
        "classification":category,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    old_levels=tuple(a22.LEVELS)
    old_lfn=a22.lesion_for
    old_alpha=float(g.ALPHA)
    old_validate=t.validate_manifest
    old_lesion=p.lesion_set

    first=one_pass()
    second=one_pass()
    same=canonical(first)==canonical(second)
    allowed={
        "INPUT_DIVERGENCE","RUNTIME_BINDING_DIVERGENCE",
        "EXECUTION_PATH_DIVERGENCE","EXACT_EQUIVALENCE_REPRODUCED",
        "OTHER_VALID_DISCREPANCY",
    }
    validity={
        "replicate_exact":first["replicate"]==6,
        "target_cell_59_present":59 in first["a24_lesion"] and 59 in first["a25_lesion"],
        "duplicate_complete_reconciliation_byte_identical":same,
        "a22_levels_restored":tuple(a22.LEVELS)==old_levels,
        "a22_lesion_function_restored":a22.lesion_for is old_lfn,
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":t.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    category=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-A26",
        "prereg":PREREG,
        "parent_a24_closure":A24_CLOSURE,
        "parent_a25_run":A25_RUN,
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_A26_A24_A25_EQUIVALENCE_RECONCILIATION":bool(all(validity.values()) and category in allowed),
            "classification":category,
        },
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
