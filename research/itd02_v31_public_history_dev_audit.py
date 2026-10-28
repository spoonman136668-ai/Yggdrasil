"""V31 development-only behavioral audit. Q1–Q3 holdout never imported."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward,RidgeCUSUM
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
from yggdrasil.itd02_v31_public_history_dev import PublicHistoryGate

def run(name,stages,offset,source):
 m=PublicHistoryGate(source)
 fast=SharedContextRingDev()
 conv=RidgeCUSUM(source)
 sha=m.bank.source_sha
 events=[];latency=None;return_event=0;false_source=0
 err={"active":0.0,"fast":0.0,"conventional":0.0}
 for stage,(family,n) in enumerate(stages):
  for i in range(n):
   case=context(i,offset);y=reward(family,case)
   m.start_observation(case[0]);m.accept_first(case[1])
   active=m.score(case[2])
   fast.start_observation(case[0]);fast.accept_first(case[1])
   fp=fast.score(case[2])
   slow,ridge,cp,_=conv.predictions(case)
   before=m.fast
   fast.accept_second(case[2],y)
   m.accept_second(case[2],y)
   conv.observe(case,y,slow,ridge)
   assert m.bank.slow.parameters_sha256()==sha
   assert m.bank.fast.parameters_sha256()==fast.parameters_sha256()
   returning=stage>0 and family=="source" and stages[stage-1][0]!="source"
   if returning:
    return_event+=1
    if latency is None and not m.fast:latency=return_event
    for k,v in (("active",active),("fast",fp),("conventional",cp)):
     err[k]+=abs(y-v)
   if name.startswith("unchanged_t") and stage==1 and i>=4:
    false_source+=int(not m.fast)
   events.append({"public":case,"reward":round(y,12),"fast_before":before,
                  "fast_after":m.fast,"active_pre_error":round(abs(y-active),12),
                  "history_count":len(m.history)})
 return {"name":name,"return_latency":latency,"false_source":false_source,
         "return_preupdate_error":{k:round(v,10) for k,v in err.items()},
         "source_sha_unchanged":True,"extra_public_history_events":len(m.history),
         "events":events}

def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
 assert git("merge-base","--is-ancestor","94c9245b02f7164c7ac28ce6b82c7a36606bf92a","HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 source=train_source()["pretrained_shared"]
 result=[run(n,seg,o,source) for n,seg,o in STREAMS]
 latency=[x["return_latency"] for x in result[:2]]
 false=[x["false_source"] for x in result[-2:]]
 classification=("V31_DEV_ONLY_RETURN_DETECTION_NO_GO__NO_SCIENCE"
    if any(x is None or x>4 for x in latency) or any(false) else
    "V31_DEV_ONLY_UNVERIFIED_STRONG_CONTROL__NO_SCIENCE")
 print(json.dumps({"schema":"ygg.itd02.v31.dev_only.public_history.v1",
  "classification":classification,"holdout_evaluated":False,
  "scientific_first_use":False,"original_world_training":False,
  "source_only":True,"stream_count":len(result),
  "basic_return_latency":latency,"unchanged_target_false_source":false,
  "records_sha256":hashlib.sha256(canonical(result)).hexdigest(),
  "streams":[{k:v for k,v in row.items() if k!="events"} for row in result]},
  sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
