"""V27 negative-case explanation, no new learner or decision thresholds."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward,RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev

PARENT="699b42d554aab67a5f5a4b6c366bcc897cb48ece"
PREREG="802a4a5604ffe858bc17c79eae1b7f6d83f3aeb0"
PINS={
"yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
"yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
"yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
"yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
"research/itd02_v26_calibrated_return_audit.py":"a6f446c55e67c66bc58e88ce4cd52020fa9b94fe",
}
def replay(name,segments,offset,source,*,offline_labels_reversed=False):
 model=CalibratedReturnRingDev(source)
 control=RidgeCUSUM(source)
 sha=model.bank.source_sha
 evidence=[]
 for stage,(family,length) in enumerate(segments):
  for i in range(length):
   case=context(i,offset);actual=reward(family,case)
   model.start_observation(case[0]);model.accept_first(case[1])
   slow=model.bank.source_score(case[2])
   fast=model.bank.fast_score(case[2])
   conv_s,conv_r,_,_=control.predictions(case)
   before=model.fast
   model.accept_second(case[2],actual)
   control.observe(case,actual,conv_s,conv_r)
   d=max(-4.0,min(4.0,abs(actual-fast)-abs(actual-slow)))
   assert model.evidence[-1]==d and model.bank.slow.parameters_sha256()==sha
   window=list(model.evidence)
   must_source=before and len(window)>=3 and all(x>=.15 for x in window[-2:]) and sum(x>=.05 for x in window)>=3
   must_fast=not before and len(window)>=3 and all(x<=-.15 for x in window[-2:]) and sum(x<=-.05 for x in window)>=3
   assert model.fast==(False if must_source else True if must_fast else before)
   evidence.append({
    "public":case,"reward":round(actual,12),
    "source_pre_error":round(abs(actual-slow),12),
    "fast_pre_error":round(abs(actual-fast),12),
    "conventional_source_pre_error":round(abs(actual-conv_s),12),
    "conventional_ridge_pre_error":round(abs(actual-conv_r),12),
    "advantage":round(d,12),
    "window":[round(x,12) for x in window],
    "source_votes_005":sum(x>=.05 for x in window),
    "source_last_two_015":len(window)>=2 and all(x>=.15 for x in window[-2:]),
    "selector_before_fast":before,"selector_after_fast":model.fast,
    # Offline stage descriptors are deliberately omitted from evidence.
   })
 assert CalibratedReturnRingDev.restore(model.checkpoint()).checkpoint()==model.checkpoint()
 return evidence
def extract(events):
 return [{"i":i+1,"events":events[max(0,i-3):i+1]}
         for i,e in enumerate(events) if e["selector_before_fast"] and not e["selector_after_fast"]]
def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
 for sha in (PARENT,PREREG):assert git("merge-base","--is-ancestor",sha,"HEAD")==""
 for path,sha in PINS.items():assert git("hash-object",path)==sha,("SOURCE_DRIFT",path)
 source=train_source()["pretrained_shared"]
 observations={}
 for name,segments,offset in STREAMS:
  events=replay(name,segments,offset,source)
  assert events==replay(name,segments,offset,source,offline_labels_reversed=True)
  observations[name]=events
 basic2=observations["basic_t2"]
 unchanged=observations["unchanged_t1"]
 basic2_return=basic2[-12:]
 first_source=next((i+1 for i,e in enumerate(basic2_return) if not e["selector_after_fast"]),None)
 false_return=sum(not e["selector_after_fast"] for e in unchanged[-8:])
 # Frozen original V26 result is a falsification constraint, not a tuned threshold.
 assert first_source==5 and false_return==4
 assert next((i+1 for i,e in enumerate(observations["basic_t1"][-12:])
              if not e["selector_after_fast"]),None)==1
 # Counterfactual stage-label reassignment cannot enter a model or the
 # canonical payload; mutating a PUBLIC reward must change its digest.
 digest=hashlib.sha256(canonical(observations)).hexdigest()
 mutated=json.loads(canonical(observations))
 mutated["unchanged_t1"][12]["reward"]+=0.001
 assert hashlib.sha256(canonical(mutated)).hexdigest()!=digest
 result={
  "schema":"ygg.itd02.v27.source_only.evidence_falsification.v1",
  "classification":"V27_FALSE_RETURN_AND_LATE_RETURN_CAUSAL_WITNESS_PASS__NO_SCIENCE",
  "original_v26_reactivation_success":False,
  "native_model_unchanged":True,"scientific_first_use":False,
  "original_world_training":False,
  "source_pretraining_events":576,"public_streams":len(STREAMS),
  "t2_return_latency":first_source,
  "unchanged_t1_false_source_selections":false_return,
  "t2_return_windows":[{"return_event":i+1,
       "prior_four":basic2[max(0,len(basic2)-12+i-3):len(basic2)-12+i+1]}
      for i in range(5)],
  "unchanged_t1_false_windows":[{"event":i+1,
      "prior_four":unchanged[max(0,12+i-3):12+i+1]}
      for i in range(12) if not unchanged[12+i]["selector_after_fast"]],
  "all_streams_sha256":digest,
  "offline_stage_label_swap_invariant":True,
  "public_reward_digest_tamper_detected":True,
 }
 print(json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
