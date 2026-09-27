#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a42_runtime_seed_vs_request_realization_v1 as a42

PREREG="49e3f6be2e4652eb588c837cbf5b9046cacd7276"
PARENT_RUN="36282442182"
TARGET=2
R6=6
PARTNERS=[1,2,3,4,5,7,8,9,10]
EXPECTED_FULL=[3,8,10]
MODES=("U_A0","U_A25")

a41=a42.a41
lu=a42.lu
p=a42.p
g=a42.g
a8=a42.a8
a28=a42.a28

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def arrivals_for(seed,programs):
    return lu.make_arrivals(seed,programs)

def corrupt_for(seed,arrivals):
    return [x["rid"] for x in arrivals if p.u01("LU2T-TASK4-CORRUPT",seed,x["rid"])<0.05]

def build(runtime_context,arrival_seed,corrupt_seed,programs,lesion):
    m=copy.deepcopy(runtime_context)
    m["programs"]=copy.deepcopy(programs)
    arr=arrivals_for(arrival_seed,programs)
    m["arrivals"]=arr
    m["corrupt_ids"]=corrupt_for(corrupt_seed,arr)
    m["anchors0"]=p.anchors_for(m["seed"],0)
    m["anchors4"]=p.anchors_for(m["seed"],128)
    m["lesion"]=sorted(lesion)
    m["manifest_sha256"]=lu.manifest_identity(m)
    return m

_EXPECTED={}
def validator(candidate):
    sha=candidate.get("manifest_sha256")
    meta=_EXPECTED.get(sha)
    if meta is None: raise AssertionError("A43 unregistered manifest")
    if canonical(candidate)!=canonical(meta["manifest"]): raise AssertionError("A43 manifest drift")
    if candidate["manifest_sha256"]!=lu.manifest_identity(candidate): raise AssertionError("A43 hash")
    exp_arr=arrivals_for(meta["arrival_seed"],candidate["programs"])
    if candidate["arrivals"]!=exp_arr: raise AssertionError("A43 arrivals")
    exp_cor=corrupt_for(meta["corrupt_seed"],exp_arr)
    if candidate["corrupt_ids"]!=exp_cor: raise AssertionError("A43 corruption")
    if candidate["anchors0"]!=p.anchors_for(candidate["seed"],0) or candidate["anchors4"]!=p.anchors_for(candidate["seed"],128):
        raise AssertionError("A43 runtime anchors")
    return True

def score(runtime_context,arrival_seed,corrupt_seed,programs,mode,lesion):
    m=build(runtime_context,arrival_seed,corrupt_seed,programs,lesion)
    _EXPECTED[m["manifest_sha256"]]={
        "manifest":copy.deepcopy(m),
        "arrival_seed":arrival_seed,
        "corrupt_seed":corrupt_seed,
    }
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

def pair(runtime_context,arrival_seed,corrupt_seed,programs,mode):
    z,m0=score(runtime_context,arrival_seed,corrupt_seed,programs,mode,[])
    s,m1=score(runtime_context,arrival_seed,corrupt_seed,programs,mode,[TARGET])
    fs=a28.collapsed(z,s)
    arr=arrivals_for(arrival_seed,programs)
    return {
        "collapse":bool(fs),"failures":fs,
        "arrival_seed":arrival_seed,"corrupt_seed":corrupt_seed,
        "zero_lesion":m0["lesion"],"singleton_lesion":m1["lesion"],
        "integrity":bool(integrity(z) and integrity(s)),
        "programs_exact":m0["programs"]==programs and m1["programs"]==programs,
        "runtime_seed_exact":m0["seed"]==runtime_context["seed"] and m1["seed"]==runtime_context["seed"],
        "anchors_runtime_exact":m0["anchors0"]==p.anchors_for(runtime_context["seed"],0) and m1["anchors4"]==p.anchors_for(runtime_context["seed"],128),
        "arrival_realization_exact":m0["arrivals"]==arr and m1["arrivals"]==arr,
        "corruption_realization_exact":m0["corrupt_ids"]==corrupt_for(corrupt_seed,arr) and m1["corrupt_ids"]==corrupt_for(corrupt_seed,arr),
        "runtime_constants_frozen":a41.context_frozen(m0)==a41.context_frozen(runtime_context) and a41.context_frozen(m1)==a41.context_frozen(runtime_context),
    }

def one_mode(mode):
    by=a41.bases(); r6=by[R6]; programs=r6["programs"]; r6seed=r6["seed"]
    native=pair(r6,r6seed,r6seed,programs,mode)
    full=[]; fam_a=[]; fam_b=[]
    for rep in PARTNERS:
        seed=by[rep]["seed"]
        full.append({"partner":rep,**pair(r6,seed,seed,programs,mode)})
        fam_a.append({"partner":rep,"family":"PARTNER_ARRIVALS_R6_CORRUPTION",**pair(r6,seed,r6seed,programs,mode)})
        fam_b.append({"partner":rep,"family":"R6_ARRIVALS_PARTNER_CORRUPTION",**pair(r6,r6seed,seed,programs,mode)})
    return {
        "mode":mode,
        "native_replicate6_collapse":native["collapse"],
        "native":native,
        "full_partner":full,
        "full_partner_collapsing":[x["partner"] for x in full if x["collapse"]],
        "partner_arrivals_r6_corruption":fam_a,
        "partner_arrivals_r6_corruption_collapsing":[x["partner"] for x in fam_a if x["collapse"]],
        "r6_arrivals_partner_corruption":fam_b,
        "r6_arrivals_partner_corruption_collapsing":[x["partner"] for x in fam_b if x["collapse"]],
    }

def classify(rows):
    if any((not r["native_replicate6_collapse"]) or r["full_partner_collapsing"]!=EXPECTED_FULL for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    A=[r["partner_arrivals_r6_corruption_collapsing"] for r in rows]
    B=[r["r6_arrivals_partner_corruption_collapsing"] for r in rows]
    if A[0]!=A[1] or B[0]!=B[1]:
        return "CROSS_MODE_REQUEST_COMPONENT_DIFFERENCE"
    if A[0]==EXPECTED_FULL and B[0]==PARTNERS:
        return "ARRIVAL_STREAM_DOMINANT"
    if B[0]==EXPECTED_FULL and A[0]==PARTNERS:
        return "CORRUPTION_SCHEDULE_DOMINANT"
    if A[0]==PARTNERS and B[0]==PARTNERS:
        return "REQUEST_COMPONENT_INTERACTION_REQUIRED"
    if A[0]!=PARTNERS and B[0]!=PARTNERS and (len(A[0])<len(PARTNERS)) and (len(B[0])<len(PARTNERS)):
        return "BOTH_COMPONENTS_INDEPENDENTLY_MODULATE"
    return "MIXED_REQUEST_COMPONENT_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=p.lesion_set; old_alpha=float(g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allarms=[]
    for r in first["rows"]:
        allarms.append(r["native"])
        allarms.extend(r["full_partner"])
        allarms.extend(r["partner_arrivals_r6_corruption"])
        allarms.extend(r["r6_arrivals_partner_corruption"])
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "target_exact":TARGET==a28.TARGET_CELL==2,
        "partner_ids_exact":PARTNERS==[1,2,3,4,5,7,8,9,10],
        "native_anchor_reproduced":all(r["native_replicate6_collapse"] for r in first["rows"]),
        "a42_full_partner_anchors_reproduced":all(r["full_partner_collapsing"]==EXPECTED_FULL for r in first["rows"]),
        "programs_exact":all(x["programs_exact"] for x in allarms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allarms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allarms),
        "arrival_realization_exact":all(x["arrival_realization_exact"] for x in allarms),
        "corruption_realization_exact":all(x["corruption_realization_exact"] for x in allarms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allarms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allarms),
        "scientific_integrity":all(x["integrity"] for x in allarms),
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"ARRIVAL_STREAM_DOMINANT","CORRUPTION_SCHEDULE_DOMINANT","BOTH_COMPONENTS_INDEPENDENTLY_MODULATE","REQUEST_COMPONENT_INTERACTION_REQUIRED","MIXED_REQUEST_COMPONENT_PATTERN","CROSS_MODE_REQUEST_COMPONENT_DIFFERENCE","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-A43","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A43_ARRIVAL_VS_CORRUPTION_REQUEST_DECOMPOSITION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
