#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_c3_resource_pressure_retention_v1 as c3

PREREG="ba5aa2e2334012ca4cafd321ea238e5fa3cbae39"
PARENT_CLOSURE="ef52ad725460b9ba6f9f77b84910bbe7068ad7a1"
EXPECTED_PARENT_HASH="7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1"
LEVELS=tuple(range(8,17))

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def fine_pressure(seed,count):
    if count not in LEVELS:
        raise AssertionError("unregistered fine pressure")
    base=c3.inherited_lesion(seed)
    if count==8:
        return base
    used=set(base)
    remaining=[cell for cell in range(c3.lu2v.p.N) if cell not in used]
    ranked=sorted(
        remaining,
        key=lambda cell:(c3.lu2v.p.h64("YGG-C3-RESOURCE-PRESSURE",seed,cell),cell),
    )
    return sorted(base+ranked[:count-8])

def run_level(base,count):
    manifests=[c3.pressure_manifest(m,count) for m in base]
    rows=[c3.run_pressure_manifest(m,count) for m in manifests]
    return manifests,rows

def one_pass():
    base=c3.lu2v.primary_manifests(c3.LU2VF1)
    parent=[c3.lu2v.run_pair(m) for m in base]
    old=c3.pressure_lesion
    c3.pressure_lesion=fine_pressure
    try:
        groups=[]
        for count in LEVELS:
            manifests,rows=run_level(base,count)
            summary=c3.summarize_level(count,rows,parent)
            detail=[]
            for m,row in zip(manifests,rows):
                detail.append({
                    "replicate":m["replicate"],
                    "lesion":m["lesion"],
                    "a25_stream_phase":row["a25"]["stream_phase"],
                    "a25_correct_done":row["a25"]["correct_done"],
                    "a25_backlog":row["a25"]["backlog"],
                    "a25_maturity_pass":row["maturity"]["a25"]["pass"],
                })
            groups.append({
                "lesion_cells":count,
                "summary":summary,
                "manifests":manifests,
                "detail":detail,
            })
    finally:
        c3.pressure_lesion=old
    return {"parent":parent,"base_manifests":base,"groups":groups}

def threshold_classification(groups):
    retained={g["lesion_cells"]:bool(g["summary"]["retained"]) for g in groups}
    candidates=[]
    for k in (13,14,15,16):
        prior_failure=any(not retained[n] for n in range(9,13))
        lower_band=all(not retained[n] for n in range(12,k))
        plateau=all(retained[n] for n in range(k,17))
        if prior_failure and lower_band and plateau:
            candidates.append(k)
    return {
        "retained_by_level":{str(k):retained[k] for k in LEVELS},
        "threshold_like_recovery":bool(candidates),
        "threshold_k":min(candidates) if candidates else None,
        "classification":"THRESHOLD_LIKE" if candidates else "IRREGULAR_NON_THRESHOLD",
    }

def validity(run1,run2):
    parent_hash=hashlib.sha256(canonical(run1["parent"])).hexdigest()
    groups={g["lesion_cells"]:g for g in run1["groups"]}
    exact_cardinality=True
    nested=True
    l8_exact=True
    nonlesion=True
    all_matching=True
    for idx,base in enumerate(run1["base_manifests"]):
        prev=None
        for count in LEVELS:
            m=groups[count]["manifests"][idx]
            cells=set(m["lesion"])
            exact_cardinality=exact_cardinality and len(cells)==count
            if prev is not None:
                nested=nested and prev.issubset(cells) and len(cells-prev)==1
            prev=cells
            nonlesion=nonlesion and c3.non_lesion_bytes(m)==c3.non_lesion_bytes(base)
        l8_exact=l8_exact and groups[8]["manifests"][idx]["lesion"]==c3.inherited_lesion(base["seed"])
    for count in LEVELS:
        all_matching=all_matching and bool(groups[count]["summary"]["a25_matching_integrity"])
    checks={
        "duplicate_complete_execution_byte_identical":canonical(run1)==canonical(run2),
        "parent_reference_hash_exact":parent_hash==EXPECTED_PARENT_HASH,
        "all_levels_exact_cardinality":exact_cardinality,
        "strictly_nested_one_cell_increments":nested,
        "l8_exact_inherited_lesion":l8_exact,
        "nonlesion_manifest_fields_frozen":nonlesion,
        "all_matching_integrity":all_matching,
    }
    return checks,parent_hash

def compact_groups(run):
    out=[]
    for g in run["groups"]:
        out.append({
            "lesion_cells":g["lesion_cells"],
            "summary":g["summary"],
            "detail":g["detail"],
        })
    return out

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    checks,parent_hash=validity(first,second)
    qual=threshold_classification(first["groups"])
    out={
        "schema":1,
        "experiment":"YGG-C5",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "levels":list(LEVELS),
        "parent_reference_sha256":parent_hash,
        "validity":checks,
        "valid":all(checks.values()),
        "duplicate_sha256":hashlib.sha256(canonical(first)).hexdigest(),
        "qualification":qual,
        "groups":compact_groups(first),
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
