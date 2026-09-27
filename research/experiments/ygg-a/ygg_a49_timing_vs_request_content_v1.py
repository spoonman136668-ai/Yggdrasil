#!/usr/bin/env python3
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a48_event118_background_factorial_v1 as a48

PREREG="b164f3a0efb8fba9512db22ecc37d0e8e204ffcb"
PARENT_RUN="36286531409"
MODES=("U_A0","U_A25")
SLOTS=(118,119)
ASSIGNMENTS=("NATIVE","SWAP_118_119")
BASE_CORRUPT=[16,38,146]
CONTENT_FIELDS=("stream","bits","program_a","program_b","program_c","program_d")

a44=a48.a47.a46.a45.a44
a41=a44.a41
lu=a44.lu

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def swapped_arrivals(native):
    out=copy.deepcopy(native)
    a=next(x for x in out if x["rid"]==118)
    b=next(x for x in out if x["rid"]==119)
    ac={k:copy.deepcopy(a[k]) for k in CONTENT_FIELDS}
    bc={k:copy.deepcopy(b[k]) for k in CONTENT_FIELDS}
    for k in CONTENT_FIELDS:
        a[k]=bc[k]; b[k]=ac[k]
    return out

def only_expected_swap(native,swapped):
    if len(native)!=len(swapped): return False
    for n,s in zip(native,swapped):
        if n["rid"]!=s["rid"] or n["t"]!=s["t"]: return False
        if n["rid"] not in (118,119):
            if n!=s: return False
        else:
            other=119 if n["rid"]==118 else 118
            src=next(x for x in native if x["rid"]==other)
            for k in CONTENT_FIELDS:
                if s[k]!=src[k]: return False
            for k in n:
                if k in CONTENT_FIELDS: continue
                if s[k]!=n[k]: return False
    return True

def phase3_stream_counts(arrivals):
    return {s:sum(1 for x in arrivals if 96<=x["t"]<128 and x["stream"]==s) for s in ("C","S")}

def one_mode(mode):
    by=a41.bases()
    r6=by[6]
    programs=r6["programs"]
    native=lu.make_arrivals(r6["seed"],programs)
    swapped=swapped_arrivals(native)
    assignments={"NATIVE":native,"SWAP_118_119":swapped}
    arms=[]
    for assignment in ASSIGNMENTS:
        arrivals=assignments[assignment]
        for slot in SLOTS:
            ids=sorted(BASE_CORRUPT+[slot])
            row=a44.pair(r6,programs,arrivals,ids,mode)
            arms.append({
                "assignment":assignment,"corruption_slot":slot,
                "collapse":bool(row["collapse"]),"failures":row["failures"],
                "corrupt_ids":ids,
                "rid_t_fixed":all(x["rid"]==x["t"] for x in arrivals),
                "swap_exact": assignment=="NATIVE" or only_expected_swap(native,arrivals),
                "other_158_exact":all(
                    next(y for y in arrivals if y["rid"]==rid)==next(y for y in native if y["rid"]==rid)
                    for rid in range(160) if rid not in (118,119)
                ),
                "phase3_stream_counts_preserved":phase3_stream_counts(arrivals)==phase3_stream_counts(native),
                "integrity":bool(row["integrity"]),
                "runtime_seed_exact":bool(row["runtime_seed_exact"]),
                "programs_exact":bool(row["programs_exact"]),
                "arrivals_exact":bool(row["arrivals_exact"]),
                "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
                "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
                "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
            })
    matrix={f'{x["assignment"]}:{x["corruption_slot"]}':x["collapse"] for x in arms}
    return {"mode":mode,"arms":arms,"matrix":matrix}

def classify(rows):
    for r in rows:
        m=r["matrix"]
        if not m["NATIVE:118"] or m["NATIVE:119"]:
            return "ANCHOR_NOT_REPRODUCED"
    if rows[0]["matrix"]!=rows[1]["matrix"]:
        return "CROSS_MODE_SLOT_CONTENT_DIFFERENCE"
    m=rows[0]["matrix"]
    if m=={"NATIVE:118":True,"NATIVE:119":False,"SWAP_118_119:118":True,"SWAP_118_119:119":False}:
        return "ABSOLUTE_SLOT_DOMINANT"
    if m=={"NATIVE:118":True,"NATIVE:119":False,"SWAP_118_119:118":False,"SWAP_118_119:119":True}:
        return "REQUEST_CONTENT_DOMINANT"
    return "SLOT_CONTENT_INTERACTION"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=lu.validate_manifest
    old_lesion=a44.p.lesion_set
    old_alpha=float(a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    validity={
        "duplicate_complete_execution_byte_identical":b1==b2,
        "four_arms_per_mode_exact":all([(x["assignment"],x["corruption_slot"]) for x in r["arms"]]==[(a,s) for a in ASSIGNMENTS for s in SLOTS] for r in first["rows"]),
        "native_anchors_reproduced":all(r["matrix"]["NATIVE:118"] and not r["matrix"]["NATIVE:119"] for r in first["rows"]),
        "rid_t_fixed":all(x["rid_t_fixed"] for x in arms),
        "swap_exact":all(x["swap_exact"] for x in arms),
        "other_158_arrivals_exact":all(x["other_158_exact"] for x in arms),
        "phase3_stream_counts_preserved":all(x["phase3_stream_counts_preserved"] for x in arms),
        "corruption_sets_exact":all(x["corrupt_ids"]==sorted(BASE_CORRUPT+[x["corruption_slot"]]) for x in arms),
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
    allowed={"ABSOLUTE_SLOT_DOMINANT","REQUEST_CONTENT_DOMINANT","SLOT_CONTENT_INTERACTION","CROSS_MODE_SLOT_CONTENT_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A49","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A49_TIMING_VS_REQUEST_CONTENT":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
