#!/usr/bin/env python3
import copy,hashlib,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a56_phase3_single_stream_flip_sweep_v1 as a56

PREREG="f880305bacafbaab4610be9ded6ff38e68a6d929"
PARENT_RUN="36316830109"
MODES=("U_A0","U_A25")
I=(103,105,106,111,117,121,123,125)
PAIRS=tuple(itertools.combinations(I,2))
CORRUPT=[16,38,146,118]

a44=a56.a44
a41=a56.a41
lu=a56.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def flip_set(native,rids):
    out=copy.deepcopy(native)
    for rid in rids:
        a=next(x for x in out if x["rid"]==rid)
        if a["stream"] not in ("C","S"): raise AssertionError("A57 bad stream")
        a["stream"]="S" if a["stream"]=="C" else "C"
    return out

def exact_change(native,arr,rids):
    rset=set(rids)
    for rid in range(160):
        n=next(x for x in native if x["rid"]==rid)
        a=next(x for x in arr if x["rid"]==rid)
        if rid not in rset:
            if a!=n: return False
        else:
            if a["stream"]==n["stream"] or {a["stream"],n["stream"]}!={"C","S"}:
                return False
            for k in n:
                if k=="stream": continue
                if a[k]!=n[k]: return False
    return True

def one_mode(mode):
    by=a41.bases(); r6=by[6]; programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    nrow=a44.pair(r6,programs,native,CORRUPT,mode)
    singles=[]
    for rid in I:
        arr=flip_set(native,(rid,))
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        singles.append({
            "rid":rid,"collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,(rid,)),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    pairs=[]
    for i,j in PAIRS:
        arr=flip_set(native,(i,j))
        row=a44.pair(r6,programs,arr,CORRUPT,mode)
        pairs.append({
            "pair":[i,j],"collapse":bool(row["collapse"]),
            "exact_registered_change":exact_change(native,arr,(i,j)),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
        })
    sensitive_pairs=[x["pair"] for x in pairs if not x["collapse"]]
    return {
        "mode":mode,"native_collapse":bool(nrow["collapse"]),
        "single_anchors":singles,"pairs":pairs,"sensitive_pairs":sensitive_pairs,
        "native_integrity":bool(nrow["integrity"])
    }

def classify(rows):
    if not all(r["native_collapse"] for r in rows): return "NATIVE_ANCHOR_NOT_REPRODUCED"
    if not all(all(x["collapse"] for x in r["single_anchors"]) for r in rows):
        return "SINGLE_ANCHOR_NOT_REPRODUCED"
    if rows[0]["sensitive_pairs"]!=rows[1]["sensitive_pairs"]:
        return "CROSS_MODE_PAIR_DIFFERENCE"
    if rows[0]["sensitive_pairs"]: return "PAIRWISE_REDUNDANT_CAUSALITY"
    return "ALL_INSENSITIVE_PAIRS_ROBUST"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest; old_lesion=a44.p.lesion_set; old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    singles=[x for r in first["rows"] for x in r["single_anchors"]]
    pairs=[x for r in first["rows"] for x in r["pairs"]]
    allrows=singles+pairs
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "native_anchor_exact":all(r["native_collapse"] for r in first["rows"]),
        "a56_insensitive_set_exact":all([x["rid"] for x in r["single_anchors"]]==list(I) for r in first["rows"]),
        "single_anchors_reproduced":all(x["collapse"] for x in singles),
        "exact_28_pairs_per_mode":all([tuple(x["pair"]) for x in r["pairs"]]==list(PAIRS) for r in first["rows"]),
        "only_registered_stream_changes":all(x["exact_registered_change"] for x in allrows),
        "corruption_set_fixed":CORRUPT==[16,38,146,118],
        "runtime_seed_exact":all(x["runtime_seed_exact"] for x in allrows),
        "programs_exact":all(x["programs_exact"] for x in allrows),
        "arrivals_exact":all(x["arrivals_exact"] for x in allrows),
        "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in allrows),
        "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in allrows),
        "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in allrows),
        "scientific_integrity":all(x["integrity"] for x in allrows) and all(r["native_integrity"] for r in first["rows"]),
        "runtime_alpha_restored":float(a44.g.ALPHA)==old_alpha,
        "validator_restored":lu.validate_manifest is old_validate,
        "lesion_set_restored":a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"PAIRWISE_REDUNDANT_CAUSALITY","ALL_INSENSITIVE_PAIRS_ROBUST","CROSS_MODE_PAIR_DIFFERENCE","SINGLE_ANCHOR_NOT_REPRODUCED","NATIVE_ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A57","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A57_INSENSITIVE_PAIR_FLIPS":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
