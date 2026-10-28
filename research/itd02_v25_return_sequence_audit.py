"""V25 source-only preregistered unlabeled return sequence audit.

Two original V22 learned ring banks, same legal public terminal feedback. The
evaluator knows synthetic regimes; the learner and controller do not.
"""
import hashlib,itertools,json,subprocess
from pathlib import Path
from research.itd02_v18_intermediate_plasticity_audit import target
from research.itd02_v23_unfamiliar_mapping_audit import new_target,train_source,features80
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v25_unlabeled_return_dev import UnlabeledReturnRingDev

STREAMS=(("basic_t1",(("cue_second",12),("source",12)),0),
 ("basic_t2",(("triple_parity",12),("source",12)),3),
 ("long_t1_t2",(("cue_second",8),("triple_parity",10),("source",12)),6),
 ("long_t2_t1",(("triple_parity",10),("cue_second",8),("source",12)),9),
 ("unchanged_source",(("source",12),("source",12)),0),
 ("unchanged_t1",(("cue_second",12),("cue_second",12)),3),
 ("unchanged_t2",(("triple_parity",12),("triple_parity",12)),6))
def reward(regime,case):
 return target(*case,nonlinear=True) if regime=="source" else new_target(regime,*case)
def context(i,o):
 j=i+o
 return (PUBLIC_CUES[j%4],ACTIONS[(2*j+1)%3],ACTIONS[(j+j//4)%3])
def public_step(model,case,y=None):
 model.start_observation(case[0]);model.accept_first(case[1])
 p=model.score(case[2])
 model.accept_second(case[2],y if y is not None else 0.0,learning=y is not None)
 return p
class RidgeCUSUM:
 def __init__(self,source):
  self.source=SharedContextRingDev.restore(source)
  self.weights=[0.0]*80
  self.diag=[100.0]*80
  self.cusum=0.0
  self.use_ridge=False
  self.source_loss=0.0;self.ridge_loss=0.0;self.events=0
 def predictions(self,case):
  s=public_step(self.source,case)
  x=features80(*case)
  r=sum(v*w for v,w in zip(x,self.weights))
  return s,r,(r if self.use_ridge else s),(
      r if self.events and self.ridge_loss<=self.source_loss else s)
 def observe(self,case,y,s,r):
  es=abs(y-s);er=abs(y-r)
  self.source_loss+=es;self.ridge_loss+=er
  self.cusum=max(0.0,self.cusum+es-0.75)
  if self.cusum>2:self.use_ridge=True
  if self.cusum<0.25:self.use_ridge=False
  x=features80(*case)
  denom=1.0+sum(d*v*v for d,v in zip(self.diag,x))
  err=y-r
  self.weights=[w+err*d*v/denom for w,d,v in zip(self.weights,self.diag,x)]
  self.diag=[max(0.01,d-d*d*v*v/denom) for d,v in zip(self.diag,x)]
  self.events+=1

def run(name,stages,offset,source):
 model=UnlabeledReturnRingDev(source)
 fast=SharedContextRingDev()
 destructive=SharedContextRingDev.restore(source)
 conventional=RidgeCUSUM(source)
 sha=model.bank.source_sha
 rec=[];first_return=None;return_count=0;false_source=0
 return_error={"active":0.0,"fast":0.0,"conventional":0.0}
 for stage,(regime,count) in enumerate(stages):
  for i in range(count):
   case=context(i,offset);y=reward(regime,case)
   model.start_observation(case[0]);model.accept_first(case[1])
   active=model.score(case[2])
   sp,rp,cp,tp=conventional.predictions(case)
   fp=public_step(fast,case,y)
   dp=public_step(destructive,case,y)
   model.accept_second(case[2],y)
   conventional.observe(case,y,sp,rp)
   assert model.bank.slow.parameters_sha256()==sha
   assert model.bank.fast.parameters_sha256()==fast.parameters_sha256()
   is_return=stage>0 and regime=="source" and stages[stage-1][0]!="source"
   if is_return:
    return_count+=1
    if first_return is None and not model.use_fast:first_return=return_count
    return_error["active"]+=abs(active-y)
    return_error["fast"]+=abs(fp-y)
    return_error["conventional"]+=abs(cp-y)
   if name.startswith("unchanged_t") and stage==1 and i>=4:
    false_source+=int(not model.use_fast)
   rec.append({"stage_evaluator_only":stage,"index":i+1,"public":case,
     "reward":round(y,12),"active_pre":round(active,12),
     "fast_pre":round(fp,12),"conventional_pre":round(cp,12),
     "selected_fast_after":model.use_fast,"recent_votes":list(model.recent)})
 assert UnlabeledReturnRingDev.restore(model.checkpoint()).checkpoint()==model.checkpoint()
 assert len(model.checkpoint())<=12288
 return {"stream":name,"events":len(rec),"return_latency":first_return,
 "return_events":return_count,"false_source_unchanged_target":false_source,
 "return_preupdate_error":return_error,"source_sha_unchanged":True,
 "checkpoint_bytes":len(model.checkpoint()),"records":rec}

def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for sha in ("671d8c3def0ef6cbe60e52eaf66d28ead8475e66",
             "089918a7bdefbdd19cf4b817bf191a60c2e76805"):
  assert git("merge-base","--is-ancestor",sha,"HEAD")==""
 source=train_source()["pretrained_shared"]
 results=[run(n,stages,o,source) for n,stages,o in STREAMS]
 return_ok=all(x["return_latency"] is not None and x["return_latency"]<=4
               for x in results[:2])
 no_false=all(x["false_source_unchanged_target"]==0 for x in results[-2:])
 gain=all(x["return_preupdate_error"]["active"]<=.9*x["return_preupdate_error"]["fast"]
         and x["return_preupdate_error"]["active"]<=.9*x["return_preupdate_error"]["conventional"]
         for x in results[:2])
 label=("V25_RETURN_REACTIVATION_NOT_ESTABLISHED__NO_SCIENCE"
        if not return_ok or not no_false else
        "V25_REACTIVATION_WITHOUT_STRONG_CONTROL_GAIN__NO_SCIENCE")
 print(json.dumps({"schema":"ygg.itd02.v25.unlabeled_return.source_only.v1",
 "classification":label,"source_only":True,"scientific_first_use":False,
 "original_world_training":False,"candidate_scalars":326,
 "full_behavioral_science_qualification":False,
 "basic_reactivation_within_four":return_ok,"unchanged_target_no_false_source":no_false,
 "return_error_10pct_better_both":gain,
 "streams":[{k:v for k,v in x.items() if k!="records"} for x in results],
 "canonical_public_evidence_sha256":hashlib.sha256(canonical(
 [{"name":x["stream"],"records":x["records"]} for x in results])).hexdigest()},
 sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
