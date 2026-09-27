#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a47_single_event_phase3_timing_v1 as a47

PREREG="ed4ff3c441898407a05f0a875f59688ccb24c2dd"
PARENT_RUN="36285542450"
MODES=("U_A0","U_A25")
BASE_NONPHASE3=[16,38,146]
THIRD_IDS={22:118,23:119}

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def schedule(p105,p113,third_offset):
    ids=list(BASE_NONPHASE3)
    if p105: ids.append(105)
    if p113: ids.append(113)
    ids.append(96+third_offset)
    ids=sorted(ids)
    if len(ids)!=len(set(ids)): raise AssertionError("A48 duplicate corruption id")
    return ids

def one_mode(mode):
    by=a47.a46.a45.a44.a41.bases()
    r6=by[6]; programs=r6["programs"]
    arrivals=a47.a46.a45.a44.lu.make_arrivals(r6["seed"],programs)
    arms=[]
    for p105 in (False,True):
      for p113 in (False,True):
        for third_offset in (22,23):
          ids=schedule(p105,p113,third_offset)
          row=a47.a46.a45.a44.pair(r6,programs,arrivals,ids,mode)
          arms.append({
            "event105_present":p105,"event113_present":p113,"third_offset":third_offset,
            "collapse":bool(row["collapse"]),"failures":row["failures"],
            "corrupt_ids":ids,"corruption_count":len(ids),
            "non_phase3_exact":[x for x in ids if not (96<=x<128)]==BASE_NONPHASE3,
            "only_registered_factors_vary":all(x in set(BASE_NONPHASE3+[105,113,118,119]) for x in ids),
            "integrity":bool(row["integrity"]),
            "runtime_seed_exact":bool(row["runtime_seed_exact"]),
            "programs_exact":bool(row["programs_exact"]),
            "arrivals_exact":bool(row["arrivals_exact"]),
            "anchors_runtime_exact":bool(row["anchors_runtime_exact"]),
            "runtime_constants_frozen":bool(row["runtime_constants_frozen"]),
            "zero_lesion":row["zero_lesion"],"singleton_lesion":row["singleton_lesion"],
          })
    return {"mode":mode,"arms":arms}

def classify(rows):
    for r in rows:
      a22=next(x for x in r["arms"] if x["event105_present"] and x["event113_present"] and x["third_offset"]==22)
      a23=next(x for x in r["arms"] if x["event105_present"] and x["event113_present"] and x["third_offset"]==23)
      if not a22["collapse"] or a23["collapse"]: return "ANCHOR_NOT_REPRODUCED"
    def matrix(r):
      return {(x["event105_present"],x["event113_present"],x["third_offset"]):x["collapse"] for x in r["arms"]}
    if matrix(rows[0])!=matrix(rows[1]): return "CROSS_MODE_FACTORIAL_DIFFERENCE"
    effects=[]
    m=matrix(rows[0])
    for p105 in (False,True):
      for p113 in (False,True):
        effects.append((m[(p105,p113,22)],m[(p105,p113,23)]))
    if all(a and not b for a,b in effects): return "THIRD_EVENT_TIMING_SUFFICIENT"
    if any(a!=b for a,b in effects): return "BACKGROUND_DEPENDENT_THIRD_EVENT"
    if all(a==b for a,b in effects): return "THIRD_EVENT_TIMING_LOST"
    return "OTHER_VALID_PATTERN"

def one_pass():
    rows=[one_mode(m) for m in MODES]
    return {"rows":rows,"classification":classify(rows)}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    lu=a47.a46.a45.a44.lu; p=a47.a46.a45.a44.p; g=a47.a46.a45.a44.g
    old_validate=lu.validate_manifest; old_lesion=p.lesion_set; old_alpha=float(g.ALPHA)
    first=one_pass(); second=one_pass(); b1=canonical(first); b2=canonical(second)
    arms=[x for r in first["rows"] for x in r["arms"]]
    expected=[(a,b,c) for a in (False,True) for b in (False,True) for c in (22,23)]
    validity={
      "duplicate_complete_execution_byte_identical":b1==b2,
      "eight_factorial_arms_exact":all([(x["event105_present"],x["event113_present"],x["third_offset"]) for x in r["arms"]]==expected for r in first["rows"]),
      "anchors_reproduced":all(
        next(x for x in r["arms"] if x["event105_present"] and x["event113_present"] and x["third_offset"]==22)["collapse"] and
        not next(x for x in r["arms"] if x["event105_present"] and x["event113_present"] and x["third_offset"]==23)["collapse"]
        for r in first["rows"]),
      "non_phase3_exact":all(x["non_phase3_exact"] for x in arms),
      "only_registered_factors_vary":all(x["only_registered_factors_vary"] for x in arms),
      "runtime_seed_exact":all(x["runtime_seed_exact"] for x in arms),
      "programs_exact":all(x["programs_exact"] for x in arms),
      "arrivals_exact":all(x["arrivals_exact"] for x in arms),
      "anchors_runtime_exact":all(x["anchors_runtime_exact"] for x in arms),
      "runtime_constants_frozen":all(x["runtime_constants_frozen"] for x in arms),
      "lesions_exact":all(x["zero_lesion"]==[] and x["singleton_lesion"]==[2] for x in arms),
      "scientific_integrity":all(x["integrity"] for x in arms),
      "runtime_alpha_restored":float(g.ALPHA)==old_alpha,
      "validator_restored":lu.validate_manifest is old_validate,
      "lesion_set_restored":p.lesion_set is old_lesion,
    }
    cat=first["classification"]
    allowed={"THIRD_EVENT_TIMING_SUFFICIENT","BACKGROUND_DEPENDENT_THIRD_EVENT","THIRD_EVENT_TIMING_LOST","CROSS_MODE_FACTORIAL_DIFFERENCE","ANCHOR_NOT_REPRODUCED","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-A48","prereg":PREREG,"parent_run":PARENT_RUN,
      "duplicate_sha256":hashlib.sha256(b1).hexdigest(),"validity":validity,"valid":all(validity.values()),
      "qualification":{"YGG_A48_EVENT118_BACKGROUND_FACTORIAL":all(validity.values()) and cat in allowed,"classification":cat},
      "analysis":first}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
