#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a28_replicate6_cell2_interaction_decomposition_v1 as a28

PREREG="7f667e5360ab502312bc29d13b5fe9c378fcb879"
PARENT_RUN="36276039607"
TARGET=2
MODES=("U_A0","U_A25")
R6=6

lu=a28.a27.t
p=a28.a27.p
g=a28.a27.g
a8=a28.a27.a8

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def bases():
    rows=lu.primary_manifests(a8.A1_PREREG)
    by={int(m["replicate"]):m for m in rows}
    if sorted(by)!=list(range(1,11)):
        raise AssertionError("A41 primary replicate set")
    return by

def context_frozen(m):
    x=copy.deepcopy(m)
    for k in ("programs","arrivals","corrupt_ids","lesion","manifest_sha256"):
        x.pop(k,None)
    return x

def build(context,programs,lesion):
    m=copy.deepcopy(context)
    m["programs"]=copy.deepcopy(programs)
    m["arrivals"]=lu.t.make_arrivals(m["seed"],m["programs"])
    m["corrupt_ids"]=[x["rid"] for x in m["arrivals"] if p.u01("LU2U-TASK4-CORRUPT",m["seed"],x["rid"])<0.05]
    m["anchors0"]=p.anchors_for(m["seed"],0)
    m["anchors4"]=p.anchors_for(m["seed"],128)
    m["lesion"]=sorted(lesion)
    m["manifest_sha256"]=lu.manifest_identity(m)
    return m

_EXPECTED={}
def exact_validator(candidate):
    sha=candidate.get("manifest_sha256")
    if sha not in _EXPECTED:
        raise AssertionError("A41 unregistered manifest")
    if canonical(candidate)!=canonical(_EXPECTED[sha]):
        raise AssertionError("A41 manifest drift")
    if candidate["manifest_sha256"]!=lu.manifest_identity(candidate):
        raise AssertionError("A41 manifest hash")
    if candidate["arrivals"]!=lu.t.make_arrivals(candidate["seed"],candidate["programs"]):
        raise AssertionError("A41 arrivals")
    exp=[x["rid"] for x in candidate["arrivals"] if p.u01("LU2U-TASK4-CORRUPT",candidate["seed"],x["rid"])<0.05]
    if candidate["corrupt_ids"]!=exp:
        raise AssertionError("A41 corrupt ids")
    if candidate["anchors0"]!=p.anchors_for(candidate["seed"],0) or candidate["anchors4"]!=p.anchors_for(candidate["seed"],128):
        raise AssertionError("A41 anchors")
    return True

def score(context,programs,mode,lesion):
    m=build(context,programs,lesion)
    _EXPECTED[m["manifest_sha256"]]=copy.deepcopy(m)
    old_validate=lu.validate_manifest
    old_lesion=p.lesion_set
    old_alpha=float(g.ALPHA)
    lu.validate_manifest=exact_validator
    p.lesion_set=lambda seed:set(lesion)
    g.ALPHA=a28.a27.ALPHA
    try:
        row=a8.scored(m,mode,False)
    finally:
        lu.validate_manifest=old_validate
        p.lesion_set=old_lesion
        g.ALPHA=old_alpha
    return row,m

def integrity(row):
    return (
        row["result"]["incorrect_done"]==0 and
        row["result"]["matching_duplicate_cell"]==0 and
        row["result"]["matching_duplicate_request"]==0 and
        bool(row["maturity"]["pass"]) and
        bool(row["horizon_aware_repair_integrity"]) and
        row["branch"]["scheduled"]==0 and
        row["branch"]["applied"]==0 and
        row["branch"]["repaired"]==0
    )

def pair(context,programs,mode):
    z,mz=score(context,programs,mode,[])
    s,ms=score(context,programs,mode,[TARGET])
    fs=a28.collapsed(z,s)
    return {
        "collapse":bool(fs),"failures":fs,
        "zero_integrity":bool(integrity(z)),"singleton_integrity":bool(integrity(s)),
        "zero_lesion":list(mz["lesion"]),"singleton_lesion":list(ms["lesion"]),
        "deterministic_relationships_exact":(
            mz["arrivals"]==lu.t.make_arrivals(mz["seed"],mz["programs"]) and
            ms["arrivals"]==lu.t.make_arrivals(ms["seed"],ms["programs"]) and
            mz["anchors0"]==p.anchors_for(mz["seed"],0) and
            ms["anchors4"]==p.anchors_for(ms["seed"],128)
        ),
    }

def one_mode(mode):
    by=bases()
    native=[]
    for rep in sorted(by):
        r=pair(by[rep],by[rep]["programs"],mode)
        native.append({"replicate":rep,**r})

    partners=[r for r in sorted(by) if r!=R6]
    fam_a=[]; fam_b=[]
    r6=by[R6]
    for partner in partners:
        pr=by[partner]
        a=pair(pr,r6["programs"],mode)
        b=pair(r6,pr["programs"],mode)
        fam_a.append({
            "partner":partner,
            "context_replicate":partner,
            "program_donor":R6,
            "context_constants_frozen":context_frozen(build(pr,r6["programs"],[]))==context_frozen(pr),
            "programs_exact":build(pr,r6["programs"],[])["programs"]==r6["programs"],
            **a
        })
        fam_b.append({
            "partner":partner,
            "context_replicate":R6,
            "program_donor":partner,
            "context_constants_frozen":context_frozen(build(r6,pr["programs"],[]))==context_frozen(r6),
            "programs_exact":build(r6,pr["programs"],[])["programs"]==pr["programs"],
            **b
        })

    return {
        "mode":mode,
        "replicate_ids":sorted(by),
        "partners":partners,
        "native":native,
        "native_collapsing":[r["replicate"] for r in native if r["collapse"]],
        "r6_program_in_partner_context":fam_a,
        "r6_program_in_partner_context_collapsing":[r["partner"] for r in fam_a if r["collapse"]],
        "partner_program_in_r6_context":fam_b,
        "partner_program_in_r6_context_collapsing":[r["partner"] for r in fam_b if r["collapse"]],
    }

def classify(rows):
    if any(r["native_collapsing"]!=[6] for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    a=[r["r6_program_in_partner_context_collapsing"] for r in rows]
    b=[r["partner_program_in_r6_context_collapsing"] for r in rows]
    if a[0]!=a[1] or b[0]!=b[1]:
        return "CROSS_MODE_FACTORIAL_DIFFERENCE"
    partners=rows[0]["partners"]
    aset=a[0]; bset=b[0]
    if aset==[] and bset==partners:
        return "SEED_CONTEXT_DOMINANT"
    if aset==partners and bset==[]:
        return "PROGRAM_DOMINANT"
    if aset==partners and bset==partners:
        return "BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT"
    if aset==[] and bset==[]:
        return "INTERACTION_REQUIRED"
    return "MIXED_PROGRAM_SEED_INTERACTION"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest
    old_lesion=p.lesion_set
    old_alpha=float(g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    allhy=[x for r in first["rows"] for fam in ("r6_program_in_partner_context","partner_program_in_r6_context") for x in r[fam]]
    allnative=[x for r in first["rows"] for x in r["native"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "alpha_exact":a28.a27.ALPHA==0.25,
        "modes_exact":[r["mode"] for r in first["rows"]]==list(MODES),
        "target_cell_exact":TARGET==a28.TARGET_CELL==2,
        "primary_ids_exact":all(r["replicate_ids"]==list(range(1,11)) for r in first["rows"]),
        "partner_set_exact":all(r["partners"]==[1,2,3,4,5,7,8,9,10] for r in first["rows"]),
        "native_a40_anchors_reproduced":all(r["native_collapsing"]==[6] for r in first["rows"]),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allhy+allnative),
        "hybrid_deterministic_relationships_exact":all(x["deterministic_relationships_exact"] for x in allhy),
        "hybrid_context_constants_frozen":all(x["context_constants_frozen"] for x in allhy),
        "hybrid_programs_exact":all(x["programs_exact"] for x in allhy),
        "scientific_arm_integrity":all(x["zero_integrity"] and x["singleton_integrity"] for x in allhy+allnative),
        "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"SEED_CONTEXT_DOMINANT","PROGRAM_DOMINANT","BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT","INTERACTION_REQUIRED","MIXED_PROGRAM_SEED_INTERACTION","CROSS_MODE_FACTORIAL_DIFFERENCE","ANCHOR_NOT_REPRODUCED"}
    out={
        "schema":1,"experiment":"YGG-A41","prereg":PREREG,"parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "validity":validity,"valid":all(validity.values()),
        "qualification":{"YGG_A41_REPLICATE6_PROGRAM_SEED_FACTORIAL":all(validity.values()) and cat in allowed,"classification":cat},
        "analysis":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__": main()
