"""C35 independent true multi-step source-action provenance and replay comparison."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c35.run import P,PAIRS,validate,FIELDS

def stable(x):
 z=dict(x);z.pop("resources",None);return z
def compare(a,b):
 validate()
 for label,x in (("A",a),("B",b)):
  if(x.get("schema")!=P["schema"] or
     x.get("result") not in (P["acceptance"]["positive"],P["acceptance"]["noGo"]) or
     x.get("original_environment_source")!=P["source"]["external"] or
     x.get("science_accepted") is not False or
     x.get("original_R3_modified") is not False or
     x.get("new_protected_or_unknown_source_episodes")!=0 or
     x.get("two_independent_real_original_source_actions_per_fork") is not True or
     x.get("source_protocol_sha256")!=hashlib.sha256(
       (Path(__file__).parent/"PREREG.json").read_bytes()).hexdigest()):
   raise ValueError("C35_SOURCE_AUTHENTICITY_INVALID_"+label)
  for phase,cohort in (("FIT","source_original_fit_real_two_action_forks"),
                       ("FIT_CHECK","source_independent_internal_fit_check_real_forks")):
   seen=set()
   for row in x[cohort]:
    fam=row["family"];seed=row["seed"];tick=row["tick"]
    if(fam not in P["worlds"] or seed not in P["worlds"][fam][phase] or
       tick not in P["protocol"]["sourcePrefixTicks"] or
       (fam,seed,tick) in seen or
       set(row["public_initial"])!=FIELDS or
       set(row["all_nine_original_physical_pairs"])!={str(a)+str(b) for a,b in PAIRS} or
       len(row["anchor_source_sha256"])!=64 or
       len(row["initial_source_sha256"])!=64 or
       len(row["original_source_prefix"])!=tick):
     raise ValueError("C35_SOURCE_PREFIX_OR_ROLE_MISMATCH_"+label)
    seen.add((fam,seed,tick))
    for z in row["original_source_prefix"]:
     if(z["action"] not in (0,1,2) or set(z["before"])!=FIELDS or set(z["after"])!=FIELDS):
      raise ValueError("C35_SOURCE_PREFIX_ACTION_PRIVILEGED_"+label)
    for pair in PAIRS:
     actual=row["all_nine_original_physical_pairs"][str(pair[0])+str(pair[1])]
     two=actual["actual_selected_source_actions"]
     if(actual["pair"]!=list(pair) or len(two)!=2 or
        not actual["completed_two_original_actions"] or
        [t["action"] for t in two]!=list(pair) or
        two[0]["before"]!=row["public_initial"] or
        two[0]["after"]!=two[1]["before"] or
        int(two[-1]["after"]["front_blocked"])!=int(actual["actually_observed_next_front_blocked"]) or
        any(set(t["before"])!=FIELDS or set(t["after"])!=FIELDS for t in two) or
        hashlib.sha256(canonical(two)).hexdigest()!=actual["physical_trace_sha256"]):
      raise ValueError("C35_FAKE_ORIGINAL_TWO_ACTION_INTERVENTION_"+label)
  FIT=x["source_original_fit_real_two_action_forks"]
  CHECK=x["source_independent_internal_fit_check_real_forks"]
  if not FIT or not CHECK or x["FIT_source_original_fitted_intervention_pairs"]!=9*len(FIT) or {
       (z["family"],z["seed"]) for z in FIT}&{
       (z["family"],z["seed"]) for z in CHECK}:
   raise ValueError("C35_SOURCE_MODEL_EXPOSURE_OR_ROLE_LEAK_"+label)
 same=canonical(stable(a))==canonical(stable(b))
 ok=same and a["result"]==P["acceptance"]["positive"] and b["result"]==P["acceptance"]["positive"]
 return {"schema":"itd02.c35.independent-original-two-selected-action-science-v1",
   "science_identical":same,
   "result":("REPEATED_BOUNDED_C35_TWO_ACTION_FIT_MODEL_SIGNAL_NOT_POLICY"
     if ok else "NO_REPEATABLE_C35_TWO_ACTION_CAUSAL_EFFECT_PREDICTIVE_ADVANCEMENT"),
   "source_A":a["result"],"source_B":b["result"],
   "first_use":False,"science_accepted":False}
def main():
 ap=argparse.ArgumentParser()
 for name in ("first","second","output"):
  ap.add_argument("--"+name,type=Path,required=True)
 args=ap.parse_args()
 if args.output.exists() or not args.output.parent.is_dir():
  raise ValueError("C35_NONFRESH_COMPARISON")
 r=compare(json.loads(args.first.read_text()),json.loads(args.second.read_text()))
 args.output.write_bytes(canonical(r)+b"\n")
 print("C35_INDEPENDENT_SOURCE_RESULT="+r["result"])
 print("C35_EXACT_TWO_WHOLE_OS_SOURCE_RUNS="+str(r["science_identical"]))
 if not r["science_identical"]:raise SystemExit(1)
if __name__=="__main__":main()
