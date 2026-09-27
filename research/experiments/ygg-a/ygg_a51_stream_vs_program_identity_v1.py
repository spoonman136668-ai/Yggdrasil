#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a50_bits_vs_stream_program_content_v1 as a50

PREREG="a752d8a055f66343a00b75018b43b884f86ae401"
PARENT_RUN="36307037815"
MODES=("U_A0","U_A25")
ASSIGNMENTS=("NATIVE","STREAM_SWAP_ONLY","PROGRAM_SWAP_ONLY","STREAM_PROGRAM_SWAP")
CORRUPT=[16,38,146,118]
STREAM=("stream",)
PROGRAM=("program_a","program_b","program_c","program_d")
BOTH=("stream","program_a","program_b","program_c","program_d")

a49=a50.a49
a44=a49.a44
a41=a49.a41
lu=a49.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def exchange(native,fields):
    out=copy.deepcopy(native)
    a=next(x for x in out if x["rid"]==118)
    b=next(x for x in out if x["rid"]==119)
    av={k:copy.deepcopy(a[k]) for k in fields}
    bv={k:copy.deepcopy(b[k]) for k in fields}
    for k in fields:
        a[k]=bv[k]; b[k]=av[k]
    return out

def assignment(native,name):
    if name=="NATIVE": return copy.deepcopy(native)
    if name=="STREAM_SWAP_ONLY": return exchange(native,STREAM)
    if name=="PROGRAM_SWAP_ONLY": return exchange(native,PROGRAM)
    if name=="STREAM_PROGRAM_SWAP": return exchange(native,BOTH)
    raise AssertionError(name)

def exact_change(native,arrivals,name):
    changed={rid for rid in range(160)
             if next(x for x in native if x["rid"]==rid)!=next(x for x in arrivals if x["rid"]==rid)}
    if name=="NATIVE": return changed==set()
    if changed!={118,119}: return False
    fields={"STREAM_SWAP_ONLY":set(STREAM),"PROGRAM_SWAP_ONLY":set(PROGRAM),"STREAM_PROGRAM_SWAP":set(BOTH)}[name]
    for rid in (118,119):
        n=next(x for x in native if x["rid"]==rid)
        a=next(x for x in arrivals if x["rid"]==rid)
        other=next(x for x in native if x["rid"]==(119 if rid==118 else 118))
        for k in n:
            if k in fields:
                if a[k]!=other[k]: return False
            else:
                if a[k]!=n[k]: return False
    return True

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    arms=[]
    for name in ASSIGNMENTS:
        arr=assignment(native,name)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        arms.append({
            "assignment":name,"collapse":bool(row["collapse"]),"failures":row["failures"],
            "bits_fixed":all(
                next(x for x in arr if x["rid"]==rid)["bits"]==
                next(x for x in native if x["rid"]==rid)["bits"] for rid in (118,119)
            ),
            "rid_t_fixed":all(x["rid"]==x["t"] for x in arr),
            "exact_registered_change":exact_change(native,arr,name),
            "other_158_exact":all(
                next(x for x in arr if x["rid"]==rid)==next(x for x in native if x["rid"]==rid)
                for rid in range(160) if rid not in (118,119)
            ),
            "corrupt_ids":CORRUPT,
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    return {"mode":mode,"arms":arms,"matrix":{x["assignment"]:x["collapse"] for x in arms}}

def classify(rows):
    for r in rows:
        if not r["matrix"]["NATIVE"] or r["matrix"]["STREAM_PROGRAM_SWAP"]:
            return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["matrix"]!=rows[1]["matrix"]:
        return "CROSS_MODE_STREAM_PROGRAM_DIFFERENCE"
    m=rows[0]["matrix"]; s=m["STREAM_SWAP_ONLY"]; p=m["PROGRAM_SWAP_ONLY"]
    if (not s) and p: return "STREAM_LABEL_REQUIRED"
    if s and (not p): return "PROGRAM_IDENTITY_REQUIRED"
    if (not s) and (not p): return "BOTH_INDEPENDENTLY_REQUIRED"
    if s and p and (not m["STREAM_PROGRAM_SWAP"]): return "COMBINED_STREAM_PROGRAM_INTERACTION"
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
        "four_assignments_exact":all([x["assignment"] for x in r["arms"]]==list(ASSIGNMENTS) for r in first["rows"]),
        "anchors_reproduced":all(r["matrix"]["NATIVE"] and not r["matrix"]["STREAM_PROGRAM_SWAP"] for r in first["rows"]),
        "bits_fixed":all(x["bits_fixed"] for x in arms),
        "rid_t_fixed":all(x["rid_t_fixed"] for x in arms),
        "exact_registered_changes":all(x["exact_registered_change"] for x in arms),
        "other_158_arrivals_exact":all(x["other_158_exact"] for x in arms),
        "corruption_set_fixed":all(x["corrupt_ids"]==CORRUPT for x in arms),
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
        "programs_exact":all(x["programs_exact"] for x in arms),
        "arrivals_exact":all(x["arrivals_exact"] for x in arms),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
        "scientific_integrity":all(x["integrity"] for x in arms),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"STREAM_LABEL_REQUIRED","PROGRAM_IDENTITY_REQUIRED","BOTH_INDEPENDENTLY_REQUIRED","COMBINED_STREAM_PROGRAM_INTERACTION","CROSS_MODE_STREAM_PROGRAM_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A51","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A51_STREAM_VS_PROGRAM_IDENTITY":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
