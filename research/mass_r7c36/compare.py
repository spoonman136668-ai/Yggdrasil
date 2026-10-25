"""Independent C36 real original-source trajectories and exact second whole run."""
import argparse,hashlib,json
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c36.run import P,prereg,ARMS

def stable(x):
 a=dict(x);a.pop("resources",None);return a
def valid(v):
 prereg()
 if(v.get("schema")!=P["schema"] or
    v.get("result") not in (P["criteria"]["positive"],P["criteria"]["noGo"]) or
    v.get("science_accepted") is not False or
    v.get("first_use") is not False or
    v.get("native_R3_original_unchanged") is not True or
    v.get("fully_executed_true_actions") is not True or
    v.get("source_prereg_sha256")!=hashlib.sha256(
      (Path(__file__).parent/"PREREG.json").read_bytes()).hexdigest()):
  raise ValueError("C36_SCIENCE_OR_ORIGINAL_SOURCE_DRIFT")
 records=v["genuine_original_source_episode_trajectories"]
 keys=set()
 for r in records:
  tag=(r["arm"],r["family"],r["seed"])
  if (tag in keys or r["arm"] not in ARMS or
      r["family"] not in P["freshPublicEpisodeEvaluation"] or
      r["seed"] not in P["freshPublicEpisodeEvaluation"][r["family"]]):
   raise ValueError("C36_REPEATED_CONSUMED_OR_UNFROZEN_SOURCE")
  keys.add(tag)
  steps=r["real_true_source_actions"]
  if (not steps or len(steps)>P["maxSourceActions"] or
      r["actual_source_steps"]!=len(steps) or
      hashlib.sha256(canonical(steps)).hexdigest()!=r["trace_sha256"]):
   raise ValueError("C36_FAKE_PHYSICAL_ORIGINAL_ACTIONS")
  for i,e in enumerate(steps):
   before=e["before"];after=e["real_after"]
   if(set(before)!={"x","y","goal_x","goal_y","direction","front_blocked"} or
      set(after)!=set(before) or
      type(e["real_selected"]) is not int or
      e["real_selected"] not in (0,1,2) or
      (i and steps[i-1]["real_after"]!=before) or
      (e["real_selected"]!=e["R3_proposed"] and
       e["R3_proposed"] not in (0,1))):
    raise ValueError("C36_REAL_SOURCE_CHRONOLOGY_OR_ILLEGAL_OVERRIDE")
  if r["checkpoint_cold"]["fresh_os"] is not True:
   raise ValueError("C36_FROZEN_EPISODE_NOT_COLD_RESTORED")
 if len(keys)!=len(ARMS)*8:
  raise ValueError("C36_MISSING_ORIGINAL_SOURCE_ACTOR_WORLDS")
 return True

def compare(a,b):
 valid(a);valid(b)
 same=canonical(stable(a))==canonical(stable(b))
 qualified=same and a["result"]==b["result"]==P["criteria"]["positive"]
 return {"schema":"itd02.c36.independent-actual-source-causal-policy-v1",
  "result":("REPEATED_BOUNDED_C36_TRUE_TWO_STEP_SOURCE_POLICY_SIGNAL_NOT_TRANSFER"
    if qualified else "NO_REPEATABLE_C36_TRUE_SOURCE_TWO_STEP_POLICY_ADVANCEMENT"),
  "source_A":a["result"],"source_B":b["result"],
  "science_identical":same,"first_use":False,"science_accepted":False}

def main():
 p=argparse.ArgumentParser()
 for n in ("first","second","output"):
  p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args()
 if a.output.exists():raise ValueError("C36_NONFRESH_COMPARISON")
 r=compare(json.loads(a.first.read_text()),json.loads(a.second.read_text()))
 a.output.write_bytes(canonical(r)+b"\n")
 print("C36_INDEPENDENT_REAL_POLICY_RESULT="+r["result"])
 print("C36_ORIGINAL_SOURCE_EXACT_PROCESS_REPLAY="+str(r["science_identical"]))
 if not r["science_identical"]:raise SystemExit(1)
if __name__=="__main__":main()
