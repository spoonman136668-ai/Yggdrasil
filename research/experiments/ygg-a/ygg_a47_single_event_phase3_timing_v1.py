#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a46_phase3_within_phase_rotation_v1 as a46

PREREG="dda9042cf7eb1dcbb799b77c99b05670c81558b5"
PARENT_RUN="36284325097"
DONOR=3
BASE=[16,38,105,113,118,146]
EVENTS=[105,113,118]
MODES=("U_A0","U_A25")

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def schedule_for(event,new_offset):
    out=[]
    for rid in BASE:
        if rid==event: out.append(96+new_offset)
        else: out.append(rid)
    if len(set(out))!=len(out): return None
    return sorted(out)

def one_mode(mode):
    by=a46.a45.a44.a41.bases()
    r6=by[6]; programs=r6["programs"]
    arrivals=a46.a45.a44.lu.make_arrivals(r6["seed"],programs)
    donor_seed=by[DONOR]["seed"]
    base=a46.a45.a44.base_corrupt(donor_seed,arrivals)
    if base!=BASE: raise AssertionError("A47 base drift")
    families=[]
    for event in EVENTS:
        base_offset=event-96
        arms=[]; omitted=[]
        for s in range(32):
            ids=schedule_for(event,s)
            if ids is None:
                omitted.append(s); continue
            row=a46.a45.a44.pair(r6,programs,arrivals,ids,mode)
            arms.append({
                "offset":s,"is_base":s==base_offset,
                "collapse":bool(row["collapse"]),"failures":row["failures"],
                "corrupt_ids":ids,
                "only_one_event_changed":all(
                    (x in ids)==(x in BASE)
                    for x in BASE if x!=event
                ),
                "non_phase3_exact":[x for x in ids if not (96<=x<128)]==[16,38,146],
                "phase3_count_exact":len([x for x in ids if 96<=x<128])==3,
                "integrity":bool(row["integrity"]),
                "runtime_seed_exact":bool(row["runtime_seed_exact"]),
                "programs_exact":bool(row["programs_exact"]),
                "arrivals_exact":bool(row["arrivals_exact"]),
                "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
                "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
                "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
            })
        families.append({
            "event":event,"base_offset":base_offset,"omitted_offsets":omitted,
            "arms":arms,
            "collapsing_offsets":[x["offset"] for x in arms if x["collapse"]],
            "noncollapsing_offsets":[x["offset"] for x in arms if not x["collapse"]],
        })
    return {"mode":mode,"families":families}

def classify(rows):
    for r in rows:
        for f in r["families"]:
            base=next((x for x in f["arms"] if x["is_base"]),None)
            if base is None or not base["collapse"]:
                return "ANCHOR_NOT_REPRODUCED"
    m0={f["event"]:{x["offset"]:x["collapse"] for x in f["arms"]} for f in rows[0]["families"]}
    m1={f["event"]:{x["offset"]:x["collapse"] for x in f["arms"]} for f in rows[1]["families"]}
    if m0!=m1: return "CROSS_MODE_SINGLE_EVENT_DIFFERENCE"
    sensitive=[]
    for event,vals in m0.items():
        v=list(vals.values())
        sensitive.append(any(v) and any(not x for x in v))
    n=sum(sensitive)
    if n==0: return "NO_SINGLE_EVENT_TIMING_EFFECT"
    if n==1: return "SINGLE_EVENT_TIMING_SENSITIVE"
    if n==2: return "SUBSET_EVENT_TIMING_SENSITIVE"
    if n==3: return "ALL_THREE_EVENT_TIMING_SENSITIVE"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    old_validate=a46.a45.a44.lu.validate_manifest
    old_lesion=a46.a45.a44.p.lesion_set
    old_alpha=float(a46.a45.a44.g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for f in r["families"] for x in f["arms"]]
    validity={
      "duplicate_complete_execution_byte_identical":b1==b2,
      "base_schedule_exact":all([16,38,105,113,118,146]==BASE for _ in [0]),
      "event_families_exact":all([f["event"] for f in r["families"]]==EVENTS for r in first["rows"]),
      "base_anchors_reproduced":all(next(x for x in f["arms"] if x["is_base"])["collapse"] for r in first["rows"] for f in r["families"]),
      "only_one_event_changed":all(x["only_one_event_changed"] for x in arms),
      "non_phase3_exact":all(x["non_phase3_exact"] for x in arms),
      "phase3_count_exact":all(x["phase3_count_exact"] for x in arms),
      "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
      "programs_exact":all(x["programs_exact"] for x in arms),
      "arrivals_exact":all(x["arrivals_exact"] for x in arms),
      "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
      "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
      "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
      "scientific_integrity":all(x["integrity"] for x in arms),
      "runtime_alpha_restored":float(a46.a45.a44.g.ALPHA)==old_alpha,
      "validator_restored":a46.a45.a44.lu.validate_manifest is old_validate,
      "lesion_set_restored":a46.a45.a44.p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"NO_SINGLE_EVENT_TIMING_EFFECT","SINGLE_EVENT_TIMING_SENSITIVE","SUBSET_EVENT_TIMING_SENSITIVE","ALL_THREE_EVENT_TIMING_SENSITIVE","CROSS_MODE_SINGLE_EVENT_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A47","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_A47_SINGLE_EVENT_PHASE3_TIMING":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
