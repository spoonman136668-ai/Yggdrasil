#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a54_rightward_context_extension_v1 as a54

PREREG="1b63565351af7e4cb352c6e86c2b008cddd46f14"
PARENT_RUN="36310814545"
MODES=("U_A0","U_A25")
ARMS=("NATIVE","FLIP_116_ONLY","FLIP_97_ONLY","FLIP_116_PLUS_97")
CORRUPT=[16,38,146,118]

a44=a54.a44
a41=a54.a41
lu=a54.lu
p=a44.p

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def phase3_counts(arr):
    return dict(Counter(x["stream"] for x in arr if p.phase_of(x["t"])==3))

def mutate(native,name):
    out=copy.deepcopy(native)
    by={rid:next(x for x in out if x["rid"]==rid) for rid in (97,116)}
    if (by[97]["stream"],by[116]["stream"])!=("S","C"):
        raise AssertionError("A55 native labels drift")
    if name=="NATIVE": pass
    elif name=="FLIP_116_ONLY": by[116]["stream"]="S"
    elif name=="FLIP_97_ONLY": by[97]["stream"]="C"
    elif name=="FLIP_116_PLUS_97": by[116]["stream"]="S"; by[97]["stream"]="C"
    else: raise AssertionError(name)
    return out

def exact_change(native,arr,name):
    expect={
        "NATIVE":("S","C"),
        "FLIP_116_ONLY":("S","S"),
        "FLIP_97_ONLY":("C","C"),
        "FLIP_116_PLUS_97":("C","S"),
    }[name]
    got=tuple(next(x for x in arr if x["rid"]==rid)["stream"] for rid in (97,116))
    if got!=expect: return False
    for rid in range(160):
        n=next(x for x in native if x["rid"]==rid)
        a=next(x for x in arr if x["rid"]==rid)
        if rid not in (97,116):
            if a!=n: return False
        else:
            for k in n:
                if k=="stream": continue
                if a[k]!=n[k]: return False
    return True

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    native_counts=phase3_counts(native)
    arms=[]
    for name in ARMS:
        arr=mutate(native,name)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        local={str(rid):next(x for x in arr if x["rid"]==rid)["stream"] for rid in (117,118,119,120,121)}
        arms.append({
            "arm":name,
            "stream97":next(x for x in arr if x["rid"]==97)["stream"],
            "stream116":next(x for x in arr if x["rid"]==116)["stream"],
            "local_117_121":local,
            "phase3_counts":phase3_counts(arr),
            "native_phase3_counts":native_counts,
            "collapse":bool(row["collapse"]),"failures":row["failures"],
            "exact_registered_change":exact_change(native,arr,name),
            "local_117_121_native":all(
                next(x for x in arr if x["rid"]==rid)==next(x for x in native if x["rid"]==rid)
                for rid in (117,118,119,120,121)
            ),
            "rid_t_fixed":all(x["rid"]==x["t"] for x in arr),
            "bits_programs_fixed":all(
                all(
                    next(x for x in arr if x["rid"]==rid)[k]==next(x for x in native if x["rid"]==rid)[k]
                    for k in ("bits","program_a","program_b","program_c","program_d")
                ) for rid in (97,116)
            ),
            "other_arrivals_exact":all(
                next(x for x in arr if x["rid"]==rid)==next(x for x in native if x["rid"]==rid)
                for rid in range(160) if rid not in (97,116)
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
        if not r["matrix"]["NATIVE"] or r["matrix"]["FLIP_116_ONLY"]:
            return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["matrix"]!=rows[1]["matrix"]:
        return "CROSS_MODE_COUNT_COMPENSATION_DIFFERENCE"
    m=rows[0]["matrix"]
    if not m["FLIP_97_ONLY"]: return "DISTANT_97_EFFECT"
    if not m["FLIP_116_PLUS_97"]: return "LOCAL_116_EFFECT"
    if m["FLIP_116_PLUS_97"]: return "PHASE_COUNT_COMPENSATION_RESTORES"
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
        "anchors_reproduced":all(r["matrix"]["NATIVE"] and not r["matrix"]["FLIP_116_ONLY"] for r in first["rows"]),
        "native_labels_97_116_exact":all(
            next(x for x in r["arms"] if x["arm"]=="NATIVE")["stream97"]=="S" and
            next(x for x in r["arms"] if x["arm"]=="NATIVE")["stream116"]=="C"
            for r in first["rows"]),
        "double_arm_restores_phase3_counts":all(
            next(x for x in r["arms"] if x["arm"]=="FLIP_116_PLUS_97")["phase3_counts"]==
            next(x for x in r["arms"] if x["arm"]=="NATIVE")["phase3_counts"]
            for r in first["rows"]),
        "local_117_121_native":all(x["local_117_121_native"] for x in arms),
        "exact_registered_changes":all(x["exact_registered_change"] for x in arms),
        "rid_t_fixed":all(x["rid_t_fixed"] for x in arms),
        "bits_programs_fixed":all(x["bits_programs_fixed"] for x in arms),
        "other_arrivals_exact":all(x["other_arrivals_exact"] for x in arms),
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
    allowed={"LOCAL_116_EFFECT","PHASE_COUNT_COMPENSATION_RESTORES","DISTANT_97_EFFECT","CROSS_MODE_COUNT_COMPENSATION_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A55","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A55_PHASE_COUNT_COMPENSATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
