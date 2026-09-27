#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a43_arrival_vs_corruption_request_decomposition_v1 as a43

PREREG="b7b5b14abba689a2f7641c67044d52391810f1a2"
PARENT_RUN="36282823011"
TARGET=2
R6=6
DONORS=[1,2,3,4,5,6,7,8,9,10]
ROTATIONS=[0,1,2,3,4]
EXPECTED_K0=[3,6,8,10]
MODES=("U_A0","U_A25")

a42=a43.a42
a41=a43.a41
lu=a43.lu
p=a43.p
g=a43.g
a8=a43.a8
a28=a43.a28

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def circular_spacings(ids):
    s=sorted(ids)
    if not s: return []
    return sorted(((s[(i+1)%len(s)]-s[i])%160) for i in range(len(s)))

def base_corrupt(seed,arrivals):
    return [x["rid"] for x in arrivals if p.u01("LU2T-TASK4-CORRUPT",seed,x["rid"])<0.05]

def rotate(ids,k):
    return sorted(((rid+32*k)%160) for rid in ids)

def build(runtime_context,programs,arrivals,corrupt_ids,lesion):
    m=copy.deepcopy(runtime_context)
    m["programs"]=copy.deepcopy(programs)
    m["arrivals"]=copy.deepcopy(arrivals)
    m["corrupt_ids"]=sorted(corrupt_ids)
    m["anchors0"]=p.anchors_for(m["seed"],0)
    m["anchors4"]=p.anchors_for(m["seed"],128)
    m["lesion"]=sorted(lesion)
    m["manifest_sha256"]=lu.manifest_identity(m)
    return m

_EXPECTED={}
def validator(candidate):
    sha=candidate.get("manifest_sha256")
    exp=_EXPECTED.get(sha)
    if exp is None: raise AssertionError("A44 unregistered manifest")
    if canonical(candidate)!=canonical(exp): raise AssertionError("A44 manifest drift")
    if candidate["manifest_sha256"]!=lu.manifest_identity(candidate): raise AssertionError("A44 hash")
    if candidate["anchors0"]!=p.anchors_for(candidate["seed"],0) or candidate["anchors4"]!=p.anchors_for(candidate["seed"],128):
        raise AssertionError("A44 anchors")
    return True

def score(runtime_context,programs,arrivals,corrupt_ids,mode,lesion):
    m=build(runtime_context,programs,arrivals,corrupt_ids,lesion)
    _EXPECTED[m["manifest_sha256"]]=copy.deepcopy(m)
    old_validate=lu.validate_manifest; old_lesion=p.lesion_set; old_alpha=float(g.ALPHA)
    lu.validate_manifest=validator; p.lesion_set=lambda seed:set(lesion); g.ALPHA=a28.a27.ALPHA
    try:
        row=a8.scored(m,mode,False)
    finally:
        lu.validate_manifest=old_validate; p.lesion_set=old_lesion; g.ALPHA=old_alpha
    return row,m

def integrity(row):
    return (
        row["result"]["incorrect_done"]==0 and
        row["result"]["matching_duplicate_cell"]==0 and
        row["result"]["matching_duplicate_request"]==0 and
        bool(row["maturity"]["pass"]) and bool(row["horizon_aware_repair_integrity"]) and
        row["branch"]["scheduled"]==0 and row["branch"]["applied"]==0 and row["branch"]["repaired"]==0
    )

def pair(runtime_context,programs,arrivals,corrupt_ids,mode):
    z,m0=score(runtime_context,programs,arrivals,corrupt_ids,mode,[])
    s,m1=score(runtime_context,programs,arrivals,corrupt_ids,mode,[TARGET])
    fs=a28.collapsed(z,s)
    return {
        "collapse":bool(fs),"failures":fs,
        "corrupt_ids":sorted(corrupt_ids),
        "count":len(corrupt_ids),
        "zero_lesion":m0["lesion"],"singleton_lesion":m1["lesion"],
        "integrity":bool(integrity(z) and integrity(s)),
        "runtime_seed_exact":m0["seed"]==runtime_context["seed"] and m1["seed"]==runtime_context["seed"],
        "programs_exact":m0["programs"]==programs and m1["programs"]==programs,
        "arrivals_exact":m0["arrivals"]==arrivals and m1["arrivals"]==arrivals,
        "anchors_runtime_exact":m0["anchors0"]==p.anchors_for(runtime_context["seed"],0) and m1["anchors4"]==p.anchors_for(runtime_context["seed"],128),
        "runtime_constants_frozen":a41.context_frozen(m0)==a41.context_frozen(runtime_context) and a41.context_frozen(m1)==a41.context_frozen(runtime_context),
    }

def one_mode(mode):
    by=a41.bases(); r6=by[R6]; programs=r6["programs"]
    arrivals=lu.make_arrivals(r6["seed"],programs)
    donors=[]
    for donor in DONORS:
        seed=by[donor]["seed"]
        base=base_corrupt(seed,arrivals)
        base_spacing=circular_spacings(base)
        rots=[]
        for k in ROTATIONS:
            ids=rotate(base,k)
            row=pair(r6,programs,arrivals,ids,mode)
            rots.append({
                "rotation":k,
                "count_preserved":len(ids)==len(base),
                "circular_spacings_preserved":circular_spacings(ids)==base_spacing,
                **row,
            })
        donors.append({
            "donor":donor,
            "request_seed":seed,
            "base_corrupt_ids":base,
            "base_count":len(base),
            "rotations":rots,
            "collapsing_rotations":[x["rotation"] for x in rots if x["collapse"]],
        })
    k0=[d["donor"] for d in donors if next(x for x in d["rotations"] if x["rotation"]==0)["collapse"]]
    matrix={str(d["donor"]):[bool(x["collapse"]) for x in d["rotations"]] for d in donors}
    return {"mode":mode,"donors":donors,"k0_collapsing_donors":k0,"collapse_matrix":matrix}

def classify(rows):
    if any(r["k0_collapsing_donors"]!=EXPECTED_K0 for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["collapse_matrix"]!=rows[1]["collapse_matrix"]:
        return "CROSS_MODE_PHASE_DIFFERENCE"
    vals=list(rows[0]["collapse_matrix"].values())
    if all(all(v==arr[0] for v in arr) for arr in vals):
        return "PHASE_PLACEMENT_INVARIANT"
    if any(any(v!=arr[0] for v in arr) for arr in vals):
        return "PHASE_SENSITIVE"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=p.lesion_set; old_alpha=float(g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allrots=[x for r in first["rows"] for d in r["donors"] for x in d["rotations"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "target_exact":TARGET==a28.TARGET_CELL==2,
        "donor_ids_exact":DONORS==list(range(1,11)),
        "rotations_exact":all([x["rotation"] for x in d["rotations"]]==ROTATIONS for r in first["rows"] for d in r["donors"]),
        "k0_anchors_reproduced":all(r["k0_collapsing_donors"]==EXPECTED_K0 for r in first["rows"]),
        "corruption_count_preserved":all(x["count_preserved"] for x in allrots),
        "circular_spacings_preserved":all(x["circular_spacings_preserved"] for x in allrots),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allrots),
        "programs_exact":all(x["programs_exact"] for x in allrots),
        "arrivals_exact":all(x["arrivals_exact"] for x in allrots),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allrots),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allrots),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allrots),
        "scientific_integrity":all(x["integrity"] for x in allrots),
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"PHASE_PLACEMENT_INVARIANT","PHASE_SENSITIVE","CROSS_MODE_PHASE_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A44","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A44_CORRUPTION_PHASE_ROTATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
