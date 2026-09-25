#!/usr/bin/env python3
import copy, hashlib, json, sys
from pathlib import Path

import lu2v_task4_independent_confirmation_v1 as lu2v

PREREG="3165d352485dfcc5614ed53fcc90fccfc4ed2110"
PARENT_CLOSURE="f1befdb1476b7ec9b7f3d36d471d996393370619"
SHARED_BASELINE="878464cf84833d06a1ac7e45988bfb79608547dc"
LU2VF1="e832853554e813db2e185d6b607543541f32d887"
EXPECTED_L8_EVIDENCE_SHA256="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"
PRESSURE=(8,12,16,24,32)
PRIMARY_COUNT=16
ORIG_LESION_SET=lu2v.p.lesion_set

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def inherited_lesion(seed):
    cells=sorted(ORIG_LESION_SET(seed))
    if len(cells)!=8:
        raise AssertionError("inherited lesion cardinality")
    return cells

def pressure_lesion(seed,count):
    if count not in PRESSURE:
        raise AssertionError("unregistered pressure")
    base=inherited_lesion(seed)
    if count==8:
        return base
    used=set(base)
    remaining=[c for c in range(lu2v.p.N) if c not in used]
    ranked=sorted(remaining,key=lambda c:(lu2v.p.h64("YGG-C3-RESOURCE-PRESSURE",seed,c),c))
    return sorted(base+ranked[:count-8])

def non_lesion_bytes(m):
    x=copy.deepcopy(m)
    x.pop("manifest_sha256",None)
    x.pop("lesion",None)
    return canonical(x)

def pressure_manifest(base,count):
    m=copy.deepcopy(base)
    m["lesion"]=pressure_lesion(m["seed"],count)
    m["manifest_sha256"]=lu2v.manifest_identity(m)
    if non_lesion_bytes(m)!=non_lesion_bytes(base):
        raise AssertionError("non-lesion manifest mutation")
    return m

def run_pressure_manifest(m,count):
    expected=pressure_lesion(m["seed"],count)
    if m["lesion"]!=expected:
        raise AssertionError("pressure manifest lesion mismatch")

    # Mechanical harness adapter only. The frozen LU-2V validator hard-codes
    # the inherited eight-cell lesion cardinality. Validate every other field
    # against an exact normalized copy, while the real scored execution keeps
    # the preregistered pressure lesion and dynamic lesion_set.
    original_validate=lu2v.validate_manifest
    original_set=lu2v.p.lesion_set

    def pressure_validate(candidate):
        normalized=copy.deepcopy(candidate)
        normalized["lesion"]=inherited_lesion(candidate["seed"])
        normalized["manifest_sha256"]=lu2v.manifest_identity(normalized)
        current_set=lu2v.p.lesion_set
        lu2v.p.lesion_set=ORIG_LESION_SET
        try:
            return original_validate(normalized)
        finally:
            lu2v.p.lesion_set=current_set

    lu2v.validate_manifest=pressure_validate
    lu2v.p.lesion_set=lambda seed:set(pressure_lesion(seed,count))
    try:
        return lu2v.run_pair(m)
    finally:
        lu2v.validate_manifest=original_validate
        lu2v.p.lesion_set=original_set

def build_manifests():
    base=lu2v.primary_manifests(LU2VF1)
    out={}
    for count in PRESSURE:
        out[count]=[pressure_manifest(m,count) for m in base]
    for i in range(len(base)):
        sets=[set(out[c][i]["lesion"]) for c in PRESSURE]
        if not all(len(sets[j])==PRESSURE[j] for j in range(len(PRESSURE))):
            raise AssertionError("pressure cardinality")
        if not all(sets[j].issubset(sets[j+1]) for j in range(len(sets)-1)):
            raise AssertionError("pressure nesting")
        if sorted(sets[0])!=inherited_lesion(base[i]["seed"]):
            raise AssertionError("L8 parent mismatch")
    return base,out

def run_once():
    base,manifests=build_manifests()
    parent_reference=[lu2v.run_pair(m) for m in base]
    levels=[]
    for count in PRESSURE:
        rows=[run_pressure_manifest(m,count) for m in manifests[count]]
        levels.append({"lesion_cells":count,"rows":rows})
    return {"base_manifests":base,"parent_reference":parent_reference,"levels":levels}

def by_count(run):
    return {x["lesion_cells"]:x["rows"] for x in run["levels"]}

def stream_noncollapse(base_rows,rows):
    b={r["manifest"]["replicate"]:r for r in base_rows}
    for row in rows:
        rep=row["manifest"]["replicate"]
        br=b[rep]
        for ph in range(5):
            for stream in ("C","S"):
                base_n=br["a25"]["stream_phase"][str(ph)][stream]
                cur_n=row["a25"]["stream_phase"][str(ph)][stream]
                if base_n>=4 and cur_n<0.75*base_n:
                    return False
    return True

def summarize_level(count,rows,base_rows):
    area_a0=sum(r["a0"]["events"]["correct_completion_area_phases0_4"] for r in rows)
    area_a25=sum(r["a25"]["events"]["correct_completion_area_phases0_4"] for r in rows)
    base_area=sum(r["a25"]["events"]["correct_completion_area_phases0_4"] for r in base_rows)
    ratio=area_a25/base_area if base_area else None
    incorrect=sum(r["a25"]["incorrect_done"] for r in rows)
    matching=all(
        r["integrity"]["a25_duplicate_cell"] and r["integrity"]["a25_duplicate_request"]
        for r in rows
    )
    maturity=all(r["maturity"]["a25"]["pass"] for r in rows)
    streams=stream_noncollapse(base_rows,rows)
    retained=bool(
        ratio is not None and ratio>=0.90 and incorrect==0 and matching and maturity and streams
    )
    return {
        "lesion_cells":count,
        "lesion_fraction":count/64.0,
        "a0_correct_completion_area":area_a0,
        "a25_correct_completion_area":area_a25,
        "a25_retention_ratio_vs_l8":ratio,
        "a25_correct_done_total":sum(r["a25"]["correct_done"] for r in rows),
        "a25_incorrect_done_total":incorrect,
        "a25_expired_total":sum(r["a25"]["expired"] for r in rows),
        "a25_final_backlog_total":sum(r["a25"]["backlog"] for r in rows),
        "a25_maturity_pass_count":sum(1 for r in rows if r["maturity"]["a25"]["pass"]),
        "a25_matching_integrity":matching,
        "stream_noncollapse":streams,
        "demand_recovery":[r["a25"]["events"]["demand_reversal_recovery_latency"] for r in rows],
        "lesion_recovery":[r["a25"]["events"]["lesion_recovery_latency"] for r in rows],
        "anchor_recovery":[r["a25"]["events"]["anchor_rotation_recovery_latency"] for r in rows],
        "retained":retained,
    }

def qualification(run):
    levels=by_count(run)
    base=levels[8]
    summaries=[summarize_level(c,levels[c],base) for c in PRESSURE]
    smap={s["lesion_cells"]:s for s in summaries}
    retained=[s["lesion_cells"] for s in summaries if s["retained"]]
    return {
        "YGG_C3_DOUBLED_RESOURCE_PRESSURE_RETENTION":bool(smap[PRIMARY_COUNT]["retained"]),
        "primary_lesion_cells":PRIMARY_COUNT,
        "max_tested_retained_lesion_cells":max(retained) if retained else None,
        "levels":summaries,
    }

def validity(run1,run2):
    b1=canonical(run1)
    b2=canonical(run2)
    levels=by_count(run1)
    l8_hash=hashlib.sha256(canonical(levels[8])).hexdigest()
    parent_hash=hashlib.sha256(canonical(run1["parent_reference"])).hexdigest()
    l8_parent_exact=canonical(levels[8])==canonical(run1["parent_reference"])
    nested=True
    exact_l8=True
    nonlesion=True
    for idx in range(10):
        pressure_sets=[]
        base=run1["base_manifests"][idx]
        for count in PRESSURE:
            m=levels[count][idx]["manifest"]
            pressure_sets.append(set(m["lesion"]))
            if non_lesion_bytes(m)!=non_lesion_bytes(base):
                nonlesion=False
        nested=nested and all(pressure_sets[j].issubset(pressure_sets[j+1]) for j in range(len(pressure_sets)-1))
        exact_l8=exact_l8 and sorted(pressure_sets[0])==inherited_lesion(base["seed"])
    lineage=(
        lu2v.ALPHA==0.25
        and lu2v.PARENT_LU2UF1=="ad60a966768e15cb3b9f5eb56b889d52b40c21ae"
        and lu2v.PARENT_LU2T_CLOSURE=="bca682d103d70db87b929c7cc09e246f141502ed"
    )
    all_matching=all(
        all(
            r["integrity"]["a0_duplicate_cell"] and r["integrity"]["a0_duplicate_request"]
            and r["integrity"]["a25_duplicate_cell"] and r["integrity"]["a25_duplicate_request"]
            for r in levels[count]
        )
        for count in PRESSURE
    )
    checks={
        "duplicate_complete_sweep_byte_identical":b1==b2,
        "l8_parent_execution_byte_exact":l8_parent_exact,
        "pressure_sets_nested":nested,
        "l8_exact_inherited_lesion":exact_l8,
        "nonlesion_manifest_fields_frozen":nonlesion,
        "frozen_lineage_intact":lineage,
        "all_matching_integrity":all_matching,
    }
    return checks,l8_hash,parent_hash,hashlib.sha256(b1).hexdigest()

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=run_once()
    second=run_once()
    checks,l8_hash,parent_hash,dup_hash=validity(first,second)
    out={
        "schema":1,
        "experiment":"YGG-C3",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "shared_baseline":SHARED_BASELINE,
        "lu2vf1":LU2VF1,
        "pressure_levels":list(PRESSURE),
        "validity":checks,
        "valid":all(checks.values()),
        "l8_pressure_evidence_sha256":l8_hash,
        "current_parent_reference_sha256":parent_hash,
        "historical_c2_evidence_sha256":EXPECTED_L8_EVIDENCE_SHA256,
        "duplicate_sha256":dup_hash,
        "qualification":qualification(first),
        "sweep":first["levels"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
