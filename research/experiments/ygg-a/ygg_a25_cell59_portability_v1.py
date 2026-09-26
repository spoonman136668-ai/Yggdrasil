#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a24_l12_marginal_cell_attribution_v1 as a24

PREREG="a253602bbec3bc6f7625f693817ceb6c5f0fe65e"
PARENT_CLOSURE="64d1aed4e8a4a8aea41324ae3a6625c4beb4e6ee"
ALPHA=0.25
TARGET_CELL=59
MODES=("U_A0","U_A25")

a23=a24.a23
a22=a24.a22
a19=a24.a19
a8=a24.a8
g=a24.g
t=a24.t
p=a22.p

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def anchor_lesion(seed):
    return list(a23.fine_lesion(seed,11))

def eligible(seed):
    return TARGET_CELL not in set(anchor_lesion(seed))

def test_lesion(seed):
    base=anchor_lesion(seed)
    if TARGET_CELL in base:
        raise AssertionError("A25 ineligible seed")
    out=sorted(base+[TARGET_CELL])
    if len(out)!=12:
        raise AssertionError("A25 test cardinality")
    return out

def manifest_for(base,use_target):
    m=copy.deepcopy(base)
    m["lesion"]=test_lesion(m["seed"]) if use_target else anchor_lesion(m["seed"])
    m["manifest_sha256"]=t.manifest_identity(m)
    if a19.nonlesion_bytes(m)!=a19.nonlesion_bytes(base):
        raise AssertionError("A25 nonlesion mutation")
    return m

def run_group(mode,use_target):
    bases=[m for m in t.primary_manifests(a8.A1_PREREG) if eligible(m["seed"])]
    manifests=[manifest_for(m,use_target) for m in bases]
    old_validate=t.validate_manifest
    old_lesion=p.lesion_set
    t.validate_manifest=a22.pressure_validate
    try:
        rows=[]
        for m in manifests:
            p.lesion_set=lambda seed,ut=use_target:set(test_lesion(seed) if ut else anchor_lesion(seed))
            rows.append(a8.scored(m,mode,False))
    finally:
        t.validate_manifest=old_validate
        p.lesion_set=old_lesion
    return {"mode":mode,"use_target":use_target,"rows":rows,"manifests":manifests}

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
                b=br[ps][stream]
                c=cr[ps][stream]
                if b>=4 and c<0.75*b:
                    failures.append({"replicate":rep,"phase":ph,"stream":stream,"anchor":b,"current":c,"ratio":c/b if b else None})
    return failures

def run_mode(mode):
    old_alpha=float(g.ALPHA)
    g.ALPHA=ALPHA
    try:
        anchor=run_group(mode,False)
        target=run_group(mode,True)
    finally:
        g.ALPHA=old_alpha

    failures=stream_failures(anchor,target)
    fail_reps=sorted({int(x["replicate"]) for x in failures})
    eligible_reps=sorted(int(r["manifest"]["replicate"]) for r in anchor["rows"])
    bases=t.primary_manifests(a8.A1_PREREG)
    exact=all(
        len(r["manifest"]["lesion"])==(12 if group is target else 11)
        and (TARGET_CELL in r["manifest"]["lesion"])== (group is target)
        for group in (anchor,target) for r in group["rows"]
    )
    nonlesion=all(
        a19.nonlesion_bytes(group["manifests"][i])==a19.nonlesion_bytes(
            next(m for m in bases if int(m["replicate"])==int(group["manifests"][i]["replicate"]))
        )
        for group in (anchor,target) for i in range(len(group["manifests"]))
    )
    integrity=all(
        r["result"]["incorrect_done"]==0
        and r["result"]["matching_duplicate_cell"]==0
        and r["result"]["matching_duplicate_request"]==0
        and r["maturity"]["pass"]
        and r["horizon_aware_repair_integrity"]
        and r["branch"]["scheduled"]==0
        and r["branch"]["applied"]==0
        and r["branch"]["repaired"]==0
        for group in (anchor,target) for r in group["rows"]
    )
    anchor_total=sum(r["result"]["correct_done"] for r in anchor["rows"])
    target_total=sum(r["result"]["correct_done"] for r in target["rows"])
    ratio=target_total/anchor_total if anchor_total else None
    return {
        "mode":mode,
        "valid":bool(exact and nonlesion and integrity and ratio is not None and ratio>=0.90),
        "eligible_replicates":eligible_reps,
        "failing_replicates":fail_reps,
        "failures":failures,
        "anchor_correct_done":anchor_total,
        "target_correct_done":target_total,
        "target_anchor_ratio":ratio,
    }

def classify(rows):
    by={r["mode"]:r for r in rows}
    a0=by["U_A0"]["failing_replicates"]
    a25=by["U_A25"]["failing_replicates"]
    if a0!=a25:
        return "CROSS_MODE_DIFFERENCE"
    if not a0:
        return "NO_REPRODUCED_CELL59_EFFECT"
    if a0==[6]:
        return "REPLICATE6_CONTEXT_SPECIFIC"
    if len(a0)>=2:
        return "GLOBAL_CELL59_SENSITIVITY"
    return "OTHER_CONTEXT_PATTERN"

def one_pass():
    rows=[run_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    old_alpha=float(g.ALPHA)
    old_validate=t.validate_manifest
    old_lesion=p.lesion_set
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)
    allowed={"GLOBAL_CELL59_SENSITIVITY","REPLICATE6_CONTEXT_SPECIFIC","CROSS_MODE_DIFFERENCE","NO_REPRODUCED_CELL59_EFFECT","OTHER_CONTEXT_PATTERN"}
    validity={
        "alpha_exact":ALPHA==0.25,
        "target_cell_exact":TARGET_CELL==59,
        "all_mode_results_valid":all(r["valid"] for r in first["rows"]),
        "replicate6_eligible":all(6 in r["eligible_replicates"] for r in first["rows"]),
        "duplicate_complete_execution_byte_identical":b1==b2,
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":t.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    category=first["classification"]
    out={
        "schema":1,
        "experiment":"YGG-A25",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "target_cell":TARGET_CELL,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_A25_CELL59_PORTABILITY_ATTRIBUTION":bool(all(validity.values()) and category in allowed),
            "classification":category,
            "failing_replicates_by_mode":{r["mode"]:r["failing_replicates"] for r in first["rows"]},
        },
        "mode_results":first["rows"],
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
