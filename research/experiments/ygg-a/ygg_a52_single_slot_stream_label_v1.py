#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a51_stream_vs_program_identity_v1 as a51

PREREG="dd0b85838bc1f0c4cd257b9f18d2bf126d77ea19"
PARENT_RUN="36309192379"
MODES=("U_A0","U_A25")
ARMS=("NATIVE","FLIP_118_ONLY","FLIP_119_ONLY","FLIP_BOTH")
CORRUPT=[16,38,146,118]

a49=a51.a49
a44=a51.a44
a41=a51.a41
lu=a51.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def mutate(native,name):
    out=copy.deepcopy(native)
    a=next(x for x in out if x["rid"]==118)
    b=next(x for x in out if x["rid"]==119)
    if (a["stream"],b["stream"])!=("C","S"):
        raise AssertionError("A52 native labels drift")
    if name=="NATIVE": pass
    elif name=="FLIP_118_ONLY": a["stream"]="S"
    elif name=="FLIP_119_ONLY": b["stream"]="C"
    elif name=="FLIP_BOTH": a["stream"]="S"; b["stream"]="C"
    else: raise AssertionError(name)
    return out

def exact_change(native,arrivals,name):
    expect={
        "NATIVE":("C","S"),
        "FLIP_118_ONLY":("S","S"),
        "FLIP_119_ONLY":("C","C"),
        "FLIP_BOTH":("S","C"),
    }[name]
    for rid in range(160):
        n=next(x for x in native if x["rid"]==rid)
        a=next(x for x in arrivals if x["rid"]==rid)
        if rid not in (118,119):
            if a!=n: return False
        else:
            for k in n:
                if k=="stream": continue
                if a[k]!=n[k]: return False
    a=next(x for x in arrivals if x["rid"]==118)
    b=next(x for x in arrivals if x["rid"]==119)
    return (a["stream"],b["stream"])==expect

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    arms=[]
    for name in ARMS:
        arr=mutate(native,name)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        arms.append({
            "arm":name,
            "stream118":next(x for x in arr if x["rid"]==118)["stream"],
            "stream119":next(x for x in arr if x["rid"]==119)["stream"],
            "collapse":bool(row["collapse"]),"failures":row["failures"],
            "exact_registered_change":exact_change(native,arr,name),
            "rid_t_fixed":all(x["rid"]==x["t"] for x in arr),
            "bits_programs_fixed":all(
                all(
                    next(x for x in arr if x["rid"]==rid)[k]==
                    next(x for x in native if x["rid"]==rid)[k]
                    for k in ("bits","program_a","program_b","program_c","program_d")
                ) for rid in (118,119)
            ),
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
    return {"mode":mode,"arms":arms,"matrix":{x["arm"]:x["collapse"] for x in arms}}

def classify(rows):
    for r in rows:
        if not r["matrix"]["NATIVE"] or r["matrix"]["FLIP_BOTH"]:
            return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["matrix"]!=rows[1]["matrix"]:
        return "CROSS_MODE_SINGLE_SLOT_LABEL_DIFFERENCE"
    m=rows[0]["matrix"]; a=m["FLIP_118_ONLY"]; b=m["FLIP_119_ONLY"]
    if (not a) and b: return "CORRUPTED_SLOT_LABEL_REQUIRED"
    if a and (not b): return "NEIGHBOR_LABEL_REQUIRED"
    if (not a) and (not b): return "BOTH_LABELS_INDEPENDENTLY_REQUIRED"
    if a and b and (not m["FLIP_BOTH"]): return "PAIRED_LABEL_CONTEXT_INTERACTION"
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
        "four_arms_exact":all([x["arm"] for x in r["arms"]]==list(ARMS) for r in first["rows"]),
        "anchors_reproduced":all(r["matrix"]["NATIVE"] and not r["matrix"]["FLIP_BOTH"] for r in first["rows"]),
        "exact_registered_changes":all(x["exact_registered_change"] for x in arms),
        "rid_t_fixed":all(x["rid_t_fixed"] for x in arms),
        "bits_programs_fixed":all(x["bits_programs_fixed"] for x in arms),
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
    allowed={"CORRUPTED_SLOT_LABEL_REQUIRED","NEIGHBOR_LABEL_REQUIRED","BOTH_LABELS_INDEPENDENTLY_REQUIRED","PAIRED_LABEL_CONTEXT_INTERACTION","CROSS_MODE_SINGLE_SLOT_LABEL_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A52","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A52_SINGLE_SLOT_STREAM_LABEL":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
