#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a41_replicate6_program_seed_factorial_v1 as a41

PREREG="1d497fc48959c83fa86be6ea6f62671c98cd04ab"
PARENT_RUN="36278456398"
TARGET=2
R6=6
MODES=("U_A0","U_A25")

lu=a41.lu
p=a41.p
g=a41.g
a8=a41.a8
a28=a41.a28

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def request_fields(seed,programs):
    arrivals=lu.make_arrivals(seed,programs)
    corrupt=[x["rid"] for x in arrivals if p.u01("LU2T-TASK4-CORRUPT",seed,x["rid"])<0.05]
    return arrivals,corrupt

def build(runtime_context,request_seed,programs,lesion):
    m=copy.deepcopy(runtime_context)
    m["programs"]=copy.deepcopy(programs)
    arrivals,corrupt=request_fields(request_seed,programs)
    m["arrivals"]=arrivals
    m["corrupt_ids"]=corrupt
    m["anchors0"]=p.anchors_for(m["seed"],0)
    m["anchors4"]=p.anchors_for(m["seed"],128)
    m["lesion"]=sorted(lesion)
    m["manifest_sha256"]=lu.manifest_identity(m)
    return m

_EXPECTED={}
def validator(candidate):
    sha=candidate.get("manifest_sha256")
    meta=_EXPECTED.get(sha)
    if meta is None: raise AssertionError("A42 unregistered manifest")
    if canonical(candidate)!=canonical(meta["manifest"]): raise AssertionError("A42 manifest drift")
    if candidate["manifest_sha256"]!=lu.manifest_identity(candidate): raise AssertionError("A42 hash")
    arrivals,corrupt=request_fields(meta["request_seed"],candidate["programs"])
    if candidate["arrivals"]!=arrivals: raise AssertionError("A42 request arrivals")
    if candidate["corrupt_ids"]!=corrupt: raise AssertionError("A42 request corrupt ids")
    if candidate["anchors0"]!=p.anchors_for(candidate["seed"],0) or candidate["anchors4"]!=p.anchors_for(candidate["seed"],128):
        raise AssertionError("A42 runtime anchors")
    return True

def score(runtime_context,request_seed,programs,mode,lesion):
    m=build(runtime_context,request_seed,programs,lesion)
    _EXPECTED[m["manifest_sha256"]]={"manifest":copy.deepcopy(m),"request_seed":request_seed}
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

def pair(runtime_context,request_seed,programs,mode):
    z,m0=score(runtime_context,request_seed,programs,mode,[])
    s,m1=score(runtime_context,request_seed,programs,mode,[TARGET])
    fs=a28.collapsed(z,s)
    return {
        "collapse":bool(fs),"failures":fs,
        "runtime_seed":runtime_context["seed"],"request_seed":request_seed,
        "zero_lesion":m0["lesion"],"singleton_lesion":m1["lesion"],
        "integrity":bool(integrity(z) and integrity(s)),
        "programs_exact":m0["programs"]==programs and m1["programs"]==programs,
        "anchors_runtime_exact":m0["anchors0"]==p.anchors_for(runtime_context["seed"],0) and m1["anchors4"]==p.anchors_for(runtime_context["seed"],128),
        "request_realization_exact":m0["arrivals"]==request_fields(request_seed,programs)[0] and m1["corrupt_ids"]==request_fields(request_seed,programs)[1],
        "runtime_constants_frozen":a41.context_frozen(m0)==a41.context_frozen(runtime_context) and a41.context_frozen(m1)==a41.context_frozen(runtime_context),
    }

def one_mode(mode):
    by=a41.bases()
    r6=by[R6]
    programs=r6["programs"]
    partners=[x for x in sorted(by) if x!=R6]

    native=[]
    for rep in sorted(by):
        native.append({"replicate":rep,**pair(by[rep],by[rep]["seed"],programs,mode)})

    fam_a=[]; fam_b=[]
    for rep in partners:
        fam_a.append({"partner":rep,"family":"R6_RUNTIME_PARTNER_REQUEST",**pair(r6,by[rep]["seed"],programs,mode)})
        fam_b.append({"partner":rep,"family":"PARTNER_RUNTIME_R6_REQUEST",**pair(by[rep],r6["seed"],programs,mode)})

    return {
        "mode":mode,"replicate_ids":sorted(by),"partners":partners,
        "native":native,"native_collapsing":[x["replicate"] for x in native if x["collapse"]],
        "r6_runtime_partner_request":fam_a,
        "r6_runtime_partner_request_collapsing":[x["partner"] for x in fam_a if x["collapse"]],
        "partner_runtime_r6_request":fam_b,
        "partner_runtime_r6_request_collapsing":[x["partner"] for x in fam_b if x["collapse"]],
    }

def classify(rows):
    if any(r["native_collapsing"]!=[6] for r in rows): return "ANCHOR_NOT_REPRODUCED"
    a=[r["r6_runtime_partner_request_collapsing"] for r in rows]
    b=[r["partner_runtime_r6_request_collapsing"] for r in rows]
    if a[0]!=a[1] or b[0]!=b[1]: return "CROSS_MODE_CONTEXT_DIFFERENCE"
    partners=rows[0]["partners"]
    if a[0]==partners and b[0]==[]: return "RUNTIME_SEED_DOMINANT"
    if b[0]==partners and a[0]==[]: return "REQUEST_REALIZATION_DOMINANT"
    if a[0]==partners and b[0]==partners: return "BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT"
    if a[0]==[] and b[0]==[]: return "RUNTIME_REQUEST_INTERACTION_REQUIRED"
    return "MIXED_RUNTIME_REQUEST_INTERACTION"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=p.lesion_set; old_alpha=float(g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allarms=[x for r in first["rows"] for key in ("native","r6_runtime_partner_request","partner_runtime_r6_request") for x in r[key]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "target_exact":TARGET==a28.TARGET_CELL==2,
        "primary_ids_exact":all(r["replicate_ids"]==list(range(1,11)) for r in first["rows"]),
        "partner_ids_exact":all(r["partners"]==[1,2,3,4,5,7,8,9,10] for r in first["rows"]),
        "native_anchors_reproduced":all(r["native_collapsing"]==[6] for r in first["rows"]),
        "programs_exact":all(x["programs_exact"] for x in allarms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allarms),
        "request_realization_exact":all(x["request_realization_exact"] for x in allarms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allarms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allarms),
        "scientific_integrity":all(x["integrity"] for x in allarms),
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"RUNTIME_SEED_DOMINANT","REQUEST_REALIZATION_DOMINANT","BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT","RUNTIME_REQUEST_INTERACTION_REQUIRED","MIXED_RUNTIME_REQUEST_INTERACTION","CROSS_MODE_CONTEXT_DIFFERENCE","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-A42","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A42_RUNTIME_SEED_VS_REQUEST_REALIZATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
