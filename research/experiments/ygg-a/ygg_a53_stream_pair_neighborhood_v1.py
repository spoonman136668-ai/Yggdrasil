#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a52_single_slot_stream_label_v1 as a52

PREREG="b4a29e03294071b283eebb59088c550b81c9ba19"
PARENT_RUN="36309892412"
MODES=("U_A0","U_A25")
ARMS=("NATIVE","FLIP_117_ONLY","FLIP_120_ONLY","FLIP_117_120")
CORRUPT=[16,38,146,118]

a44=a52.a44
a41=a52.a41
lu=a52.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def mutate(native,name):
    out=copy.deepcopy(native)
    by={rid:next(x for x in out if x["rid"]==rid) for rid in (117,118,119,120)}
    native_tuple=tuple(by[r]["stream"] for r in (117,118,119,120))
    if native_tuple!=("S","C","S","C"):
        raise AssertionError(f"A53 native labels drift {native_tuple}")
    if name=="NATIVE": pass
    elif name=="FLIP_117_ONLY": by[117]["stream"]="C"
    elif name=="FLIP_120_ONLY": by[120]["stream"]="S"
    elif name=="FLIP_117_120": by[117]["stream"]="C"; by[120]["stream"]="S"
    else: raise AssertionError(name)
    return out

def exact_change(native,arrivals,name):
    expected={
        "NATIVE":("S","C","S","C"),
        "FLIP_117_ONLY":("C","C","S","C"),
        "FLIP_120_ONLY":("S","C","S","S"),
        "FLIP_117_120":("C","C","S","S"),
    }[name]
    got=tuple(next(x for x in arrivals if x["rid"]==rid)["stream"] for rid in (117,118,119,120))
    if got!=expected: return False
    for rid in range(160):
        n=next(x for x in native if x["rid"]==rid)
        a=next(x for x in arrivals if x["rid"]==rid)
        if rid not in (117,120):
            if a!=n: return False
        else:
            for k in n:
                if k=="stream": continue
                if a[k]!=n[k]: return False
    return True

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    arms=[]
    for name in ARMS:
        arr=mutate(native,name)
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        labels={str(rid):next(x for x in arr if x["rid"]==rid)["stream"] for rid in (117,118,119,120)}
        arms.append({
            "arm":name,"labels_117_120":labels,
            "collapse":bool(row["collapse"]),"failures":row["failures"],
            "exact_registered_change":exact_change(native,arr,name),
            "pair_118_119_fixed":labels["118"]=="C" and labels["119"]=="S",
            "rid_t_fixed":all(x["rid"]==x["t"] for x in arr),
            "bits_programs_fixed":all(
                all(
                    next(x for x in arr if x["rid"]==rid)[k]==
                    next(x for x in native if x["rid"]==rid)[k]
                    for k in ("bits","program_a","program_b","program_c","program_d")
                ) for rid in (117,120)
            ),
            "other_arrivals_exact":all(
                next(x for x in arr if x["rid"]==rid)==next(x for x in native if x["rid"]==rid)
                for rid in range(160) if rid not in (117,120)
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
        if not r["matrix"]["NATIVE"]: return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["matrix"]!=rows[1]["matrix"]: return "CROSS_MODE_NEIGHBOR_DIFFERENCE"
    m=rows[0]["matrix"]
    if all(m.values()): return "PAIR_LOCALLY_SUFFICIENT"
    if (not m["FLIP_117_ONLY"]) and m["FLIP_120_ONLY"] and (not m["FLIP_117_120"]): return "LEFT_NEIGHBOR_REQUIRED"
    if m["FLIP_117_ONLY"] and (not m["FLIP_120_ONLY"]) and (not m["FLIP_117_120"]): return "RIGHT_NEIGHBOR_REQUIRED"
    if (not m["FLIP_117_ONLY"]) and (not m["FLIP_120_ONLY"]): return "BOTH_NEIGHBORS_INDEPENDENTLY_REQUIRED"
    if m["FLIP_117_ONLY"] and m["FLIP_120_ONLY"] and (not m["FLIP_117_120"]): return "BROADER_NEIGHBOR_INTERACTION"
    return "MIXED_NEIGHBOR_CONTEXT"

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
        "native_anchor_reproduced":all(r["matrix"]["NATIVE"] for r in first["rows"]),
        "pair_118_119_fixed":all(x["pair_118_119_fixed"] for x in arms),
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
    allowed={"PAIR_LOCALLY_SUFFICIENT","LEFT_NEIGHBOR_REQUIRED","RIGHT_NEIGHBOR_REQUIRED","BOTH_NEIGHBORS_INDEPENDENTLY_REQUIRED","BROADER_NEIGHBOR_INTERACTION","MIXED_NEIGHBOR_CONTEXT","CROSS_MODE_NEIGHBOR_DIFFERENCE","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-A53","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A53_STREAM_PAIR_NEIGHBORHOOD":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
