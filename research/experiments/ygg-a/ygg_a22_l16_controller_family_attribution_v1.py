#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a20_integrated_fine_recovery_map_v1 as a20

PREREG="4682ff0798c64a27609ecc30b054909a77299c32"
PARENT_CLOSURE="cb882666823b2384c7a83e032f74b4b4c9b31b21"
ALPHA=0.25
MODES=("U_A0","U_A25")
LEVELS=(8,16)

a19=a20.a19
a13=a20.a13
a8=a20.a8
g=a20.g
p=a20.p
t=a20.t

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def lesion_for(seed,count):
    if count==8:
        return a19.inherited_l8(seed)
    if count==16:
        return a20.lesion_for(seed,16)
    raise AssertionError("A22 unregistered lesion count")

def manifest_for(base,count):
    m=copy.deepcopy(base)
    m["lesion"]=lesion_for(m["seed"],count)
    m["manifest_sha256"]=t.manifest_identity(m)
    if a19.nonlesion_bytes(m)!=a19.nonlesion_bytes(base):
        raise AssertionError("A22 nonlesion mutation")
    return m

def pressure_validate(candidate):
    normalized=copy.deepcopy(candidate)
    normalized["lesion"]=a19.inherited_l8(candidate["seed"])
    normalized["manifest_sha256"]=t.manifest_identity(normalized)
    current=p.lesion_set
    p.lesion_set=a19.ORIG_LESION_SET
    try:
        return a19.ORIG_VALIDATE(normalized)
    finally:
        p.lesion_set=current

def run_mode_level(mode,count):
    if mode not in MODES:
        raise AssertionError("A22 unregistered mode")
    if count not in LEVELS:
        raise AssertionError("A22 unregistered level")

    base=t.primary_manifests(a8.A1_PREREG)
    manifests=[manifest_for(m,count) for m in base]

    old_validate=t.validate_manifest
    old_lesion=p.lesion_set
    t.validate_manifest=pressure_validate
    p.lesion_set=lambda seed:set(lesion_for(seed,count))
    try:
        rows=[a8.scored(m,mode,False) for m in manifests]
    finally:
        t.validate_manifest=old_validate
        p.lesion_set=old_lesion

    return {
        "mode":mode,
        "lesion_cells":count,
        "rows":rows,
        "manifests":manifests,
    }

def stream_failures(anchor,current):
    base={int(r["manifest"]["replicate"]):r for r in anchor["rows"]}
    failures=[]
    for row in current["rows"]:
        rep=int(row["manifest"]["replicate"])
        br=base[rep]["result"]["stream_phase"]
        cr=row["result"]["stream_phase"]
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

def summarize(mode,l8,l16):
    failures=stream_failures(l8,l16)
    zero_branch=all(
        r["branch"]["scheduled"]==0
        and r["branch"]["applied"]==0
        and r["branch"]["repaired"]==0
        for group in (l8,l16)
        for r in group["rows"]
    )
    integrity=all(
        r["result"]["incorrect_done"]==0
        and r["result"]["matching_duplicate_cell"]==0
        and r["result"]["matching_duplicate_request"]==0
        and r["maturity"]["pass"]
        and r["horizon_aware_repair_integrity"]
        for group in (l8,l16)
        for r in group["rows"]
    )
    lesion_exact=all(
        row["manifest"]["lesion"]==lesion_for(row["manifest"]["seed"],count)
        for group,count in ((l8,8),(l16,16))
        for row in group["rows"]
    )
    bases=t.primary_manifests(a8.A1_PREREG)
    nonlesion=all(
        a19.nonlesion_bytes(group["manifests"][i])==a19.nonlesion_bytes(bases[i])
        for group in (l8,l16)
        for i in range(len(bases))
    )
    l8_total=sum(r["result"]["correct_done"] for r in l8["rows"])
    l16_total=sum(r["result"]["correct_done"] for r in l16["rows"])
    ratio=l16_total/l8_total if l8_total else None
    checks={
        "exact_l8_l16_lesions":bool(lesion_exact),
        "nonlesion_manifest_fields_frozen":bool(nonlesion),
        "repair_off_zero_branch_damage":bool(zero_branch),
        "matching_maturity_terminal_integrity_exact":bool(integrity),
        "l16_l8_correct_done_ratio_ge_090":ratio is not None and ratio>=0.90,
    }
    return {
        "mode":mode,
        "valid":all(checks.values()),
        "checks":checks,
        "stream_noncollapse":len(failures)==0,
        "stream_failures":failures,
        "l8_correct_done_total":l8_total,
        "l16_correct_done_total":l16_total,
        "l16_l8_correct_done_ratio":ratio,
    }

def classify(by_mode):
    a0=by_mode["U_A0"]["stream_noncollapse"]
    a25=by_mode["U_A25"]["stream_noncollapse"]
    if not a0 and not a25:
        return "BOTH_FAIL"
    if a0 and not a25:
        return "LEARNED_CONTROLLER_ONLY"
    if not a0 and a25:
        return "FIXED_CONTROLLER_ONLY"
    return "BOTH_PASS"

def one_pass():
    old_alpha=float(g.ALPHA)
    g.ALPHA=ALPHA
    try:
        summaries=[]
        for mode in MODES:
            l8=run_mode_level(mode,8)
            l16=run_mode_level(mode,16)
            summaries.append(summarize(mode,l8,l16))
    finally:
        g.ALPHA=old_alpha
    return {"summaries":summaries}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")

    original_alpha=float(g.ALPHA)
    original_validate=t.validate_manifest
    original_lesion=p.lesion_set
    original_schedule=a8.damage_schedule

    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)

    by={r["mode"]:r for r in first["summaries"]}
    category=classify(by)
    allowed={"BOTH_FAIL","LEARNED_CONTROLLER_ONLY","FIXED_CONTROLLER_ONLY","BOTH_PASS"}

    validity={
        "alpha_exact":ALPHA==0.25,
        "modes_exact":tuple(by)==MODES,
        "all_mode_evidence_valid":all(r["valid"] for r in first["summaries"]),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "runtime_alpha_restored":float(g.ALPHA)==original_alpha,
        "validator_restored":t.validate_manifest is original_validate,
        "lesion_set_restored":p.lesion_set is original_lesion,
        "damage_schedule_restored":a8.damage_schedule is original_schedule,
    }
    qualification={
        "YGG_A22_L16_CONTROLLER_FAMILY_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
        "attribution_classification":category,
        "stream_noncollapse_by_mode":{
            mode:by[mode]["stream_noncollapse"] for mode in MODES
        },
    }
    out={
        "schema":1,
        "experiment":"YGG-A22",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alpha":ALPHA,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "mode_results":first["summaries"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
