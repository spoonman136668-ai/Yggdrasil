#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a55_phase_count_compensation_v1 as a55

PREREG="88e00ce0a4f5bf3a640a36f52000b85d2831b712"
PARENT_RUN="36312696296"
MODES=("U_A0","U_A25")
PHASE3=list(range(96,128))
CORRUPT=[16,38,146,118]
KNOWN={97,116,118,119,120}

a44=a55.a44
a41=a55.a41
lu=a55.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def flip(native,rid):
    out=copy.deepcopy(native)
    a=next(x for x in out if x["rid"]==rid)
    if a["stream"] not in ("C","S"): raise AssertionError("A56 bad stream")
    a["stream"]="S" if a["stream"]=="C" else "C"
    return out

def exact_one(native,arr,rid):
    for k in range(160):
        n=next(x for x in native if x["rid"]==k)
        a=next(x for x in arr if x["rid"]==k)
        if k!=rid:
            if a!=n: return False
        else:
            if a["stream"]==n["stream"]: return False
            if {a["stream"],n["stream"]}!={"C","S"}: return False
            for f in n:
                if f=="stream": continue
                if a[f]!=n[f]: return False
    return True

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    nrow=a44.pair(r6,programs,native,CORRUPT,mode)
    arms=[]
    for rid in PHASE3:
        arr=flip(native,rid)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        arms.append({
            "rid":rid,"native_stream":next(x for x in native if x["rid"]==rid)["stream"],
            "flipped_stream":next(x for x in arr if x["rid"]==rid)["stream"],
            "collapse":bool(row["collapse"]),"failures":row["failures"],
            "exact_one_stream_flip":exact_one(native,arr,rid),
            "rid_t_fixed":all(x["rid"]==x["t"] for x in arr),
            "corrupt_ids":CORRUPT,
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    sensitive=[x["rid"] for x in arms if not x["collapse"]]
    insensitive=[x["rid"] for x in arms if x["collapse"]]
    return {
        "mode":mode,"native_collapse":bool(nrow["collapse"]),
        "sensitive_rids":sensitive,"insensitive_rids":insensitive,"arms":arms,
        "native_integrity":bool(nrow["integrity"])
    }

def classify(rows):
    if not all(r["native_collapse"] for r in rows): return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["sensitive_rids"]!=rows[1]["sensitive_rids"]: return "CROSS_MODE_PHASE3_FLIP_DIFFERENCE"
    n=len(rows[0]["sensitive_rids"])
    if n==32: return "PHASE3_STREAM_SCHEDULE_GLOBALLY_FRAGILE"
    if 2<=n<=31: return "DISTRIBUTED_STREAM_SENSITIVITY"
    if n==1: return "SINGLE_POSITION_STREAM_SENSITIVITY"
    if n==0: return "NO_SINGLE_STREAM_FLIP_EFFECT"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "native_anchor_exact":all(r["native_collapse"] for r in first["rows"]),
        "exact_32_flip_arms_per_mode":all([x["rid"] for x in r["arms"]]==PHASE3 for r in first["rows"]),
        "only_one_registered_stream_flip":all(x["exact_one_stream_flip"] for x in arms),
        "rid_t_fixed":all(x["rid_t_fixed"] for x in arms),
        "corruption_set_fixed":all(x["corrupt_ids"]==CORRUPT for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms) and all(r["native_integrity"] for r in first["rows"]),
        "known_sensitive_positions_reproduced":all(KNOWN.issubset(set(r["sensitive_rids"])) for r in first["rows"]),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"PHASE3_STREAM_SCHEDULE_GLOBALLY_FRAGILE","DISTRIBUTED_STREAM_SENSITIVITY","SINGLE_POSITION_STREAM_SENSITIVITY","NO_SINGLE_STREAM_FLIP_EFFECT","CROSS_MODE_PHASE3_FLIP_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A56","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A56_PHASE3_SINGLE_STREAM_FLIP_SWEEP":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
