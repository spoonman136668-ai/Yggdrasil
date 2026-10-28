"""V31F frozen development-only legal selected-action information experiment."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev

POLICIES=("scheduled","disagreement","greedy_fast")
def run(name,stages,offset,source,policy):
 m=DistinctReturnRingDev(source);sha=m.bank.source_sha
 records=[];return_idx=0;latency=None;false_source=0;regret=0.;return_error=0.
 for stage,(family,n) in enumerate(stages):
  for i in range(n):
   original=context(i,offset)
   cue,first=original[:2]
   m.start_observation(cue);m.accept_first(first)
   sp=[m.bank.source_score(a) for a in ACTIONS]
   fp=[m.bank.fast_score(a) for a in ACTIONS]
   if policy=="scheduled":choice=original[2]
   elif policy=="disagreement":
    choice=ACTIONS[max(range(len(ACTIONS)),key=lambda j:abs(sp[j]-fp[j]))]
   else:choice=ACTIONS[max(range(len(ACTIONS)),key=lambda j:fp[j])]
   selected=(cue,first,choice)
   y=reward(family,selected)
   all_rewards=[reward(family,(cue,first,a)) for a in ACTIONS]
   regret+=max(all_rewards)-y
   before=m.fast
   pred=fp[ACTIONS.index(choice)] if before else sp[ACTIONS.index(choice)]
   m.accept_second(choice,y)
   assert m.bank.slow.parameters_sha256()==sha
   is_return=stage>0 and family=="source" and stages[stage-1][0]!="source"
   if is_return:
    return_idx+=1
    if latency is None and not m.fast:latency=return_idx
    return_error+=abs(y-pred)
   if name.startswith("unchanged_t") and stage==1 and i>=4:
    false_source+=int(not m.fast)
   records.append({"public":selected,"observed_reward":round(y,12),
     "source_before":[round(v,12) for v in sp],
     "fast_before":[round(v,12) for v in fp],
     "selected_fast_after":m.fast})
 return {"stream":name,"policy":policy,"latency":latency,"false_source":false_source,
  "regret":round(regret,10),"return_preupdate_error":round(return_error,10),
  "source_sha_unchanged":True,"events":records}
def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
 for pin in ("96b95d9c2311c6bd73e3284a71b98ca392e66733","f064c9fb21ed5f8986dea490833728ed692da68a"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 source=train_source()["pretrained_shared"]
 chosen=[x for x in STREAMS if x[0] in ("basic_t1","basic_t2","unchanged_t1","unchanged_t2")]
 rows=[run(n,st,o,source,p) for n,st,o in chosen for p in POLICIES]
 positive=True
 for p in POLICIES:
  basic=[x for x in rows if x["policy"]==p and x["stream"].startswith("basic")]
  nochange=[x for x in rows if x["policy"]==p and x["stream"].startswith("unchanged")]
  scheduled={x["stream"]:x for x in rows if x["policy"]=="scheduled"}
  if any(x["latency"] is None or x["latency"]>4 for x in basic):positive=False
  if any(x["false_source"]!=0 for x in nochange):positive=False
  if any(x["regret"]>scheduled[x["stream"]]["regret"] for x in basic):positive=False
 result={"schema":"ygg.itd02.v31f.informative_action.dev_only.v1",
  "classification":"V31F_SOURCE_ONLY_INFORMATION_POSITIVE_NOT_SCIENCE" if positive else
      "V31F_INFORMATIVE_ACTION_POLICY_NO_GO__NO_SCIENCE",
  "holdout_evaluated":False,"scientific_first_use":False,"source_only":True,
  "policies":list(POLICIES),"development_streams":len(chosen),
  "summary":[{k:v for k,v in x.items() if k!="events"} for x in rows],
  "canonical_all_public_feedback_sha256":hashlib.sha256(canonical(rows)).hexdigest()}
 print(json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
