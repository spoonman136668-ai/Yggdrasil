#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a45_donor3_phase_pair_swap_v1 as a45

PREREG="863ce0325d260fba67a6fedcc22c7e0068f38d9f"
PARENT_RUN="36283969522"
DONOR=3
SHIFTS=list(range(32))
MODES=("U_A0","U_A25")
BASE_EXPECTED=[16,38,105,113,118,146]
PH3_EXPECTED=[105,113,118]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def ph3_spacing(ids):
    off=sorted([x-96 for x in ids if 96<=x<128])
    if not off: return []
    return sorted(((off[(i+1)%len(off)]-off[i])%32) for i in range(len(off)))

def shifted(base,s):
    out=[]
    for rid in base:
        if 96<=rid<128:
            out.append(96+(((rid-96)+s)%32))
        else:
            out.append(rid)
    if len(set(out))!=len(out): raise AssertionError("A46 duplicate corruption id")
    return sorted(out)

def one_mode(mode):
    by=a45.a44.a41.bases()
    r6=by[6]; programs=r6["programs"]
    arrivals=a45.a44.lu.make_arrivals(r6["seed"],programs)
    donor_seed=by[DONOR]["seed"]
    base=a45.a44.base_corrupt(donor_seed,arrivals)
    if base!=BASE_EXPECTED: raise AssertionError("A46 donor3 base drift")
    base_sp=ph3_spacing(base)
    arms=[]
    for s in SHIFTS:
        ids=shifted(base,s)
        row=a45.a44.pair(r6,programs,arrivals,ids,mode)
        arms.append({
            "shift":s,"collapse":bool(row["collapse"]),"failures":row["failures"],
            "corrupt_ids":ids,
            "non_phase3_exact":[x for x in ids if not (96<=x<128)]==[16,38,146],
            "total_count_preserved":len(ids)==len(base),
            "phase3_count_preserved":len([x for x in ids if 96<=x<128])==3,
            "phase3_spacing_preserved":ph3_spacing(ids)==base_sp,
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    return {
        "mode":mode,"donor":DONOR,"base_corrupt_ids":base,
        "phase3_ids":PH3_EXPECTED,
        "arms":arms,
        "collapsing_shifts":[x["shift"] for x in arms if x["collapse"]],
        "noncollapsing_shifts":[x["shift"] for x in arms if not x["collapse"]],
    }

def classify(rows):
    if any(0 not in r["collapsing_shifts"] for r in rows):
        return "ANCHOR_NOT_REPRODUCED"
    s0=rows[0]["collapsing_shifts"]; s1=rows[1]["collapsing_shifts"]
    if s0!=s1: return "CROSS_MODE_WITHIN_PHASE_DIFFERENCE"
    if len(s0)==32: return "PHASE3_MEMBERSHIP_SUFFICIENT"
    if s0==[0]: return "PHASE3_BASE_ONLY"
    if 0<len(s0)<32: return "WITHIN_PHASE_TIMING_SENSITIVE"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=a45.a44.lu.validate_manifest; old_lesion=a45.a44.p.lesion_set; old_alpha=float(a45.a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "donor3_exact":all(r["donor"]==3 for r in first["rows"]),
        "base_schedule_exact":all(r["base_corrupt_ids"]==BASE_EXPECTED for r in first["rows"]),
        "phase3_ids_exact":all(r["phase3_ids"]==PH3_EXPECTED for r in first["rows"]),
        "shifts_exact":all([x["shift"] for x in r["arms"]]==SHIFTS for r in first["rows"]),
        "s0_anchor_reproduced":all(0 in r["collapsing_shifts"] for r in first["rows"]),
        "non_phase3_exact":all(x["non_phase3_exact"] for x in arms),
        "total_count_preserved":all(x["total_count_preserved"] for x in arms),
        "phase3_count_preserved":all(x["phase3_count_preserved"] for x in arms),
        "phase3_spacing_preserved":all(x["phase3_spacing_preserved"] for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms),
        "runtime_alpha_restored":float(a45.a44.g.ALPHA)==old_alpha,
        "validator_restored":a45.a44.lu.validate_manifest is old_validate,
        "lesion_set_restored":a45.a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"PHASE3_MEMBERSHIP_SUFFICIENT","WITHIN_PHASE_TIMING_SENSITIVE","PHASE3_BASE_ONLY","CROSS_MODE_WITHIN_PHASE_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A46","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A46_PHASE3_WITHIN_PHASE_ROTATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
