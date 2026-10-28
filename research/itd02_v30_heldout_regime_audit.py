"""V30 precommitted heldout synthetic reward laws with frozen V26 return selector.

Two original V22 learned ring banks, same legal public terminal feedback. The
evaluator knows synthetic regimes; the learner and controller do not.
"""
import hashlib,itertools,json,subprocess
from pathlib import Path
from research.itd02_v18_intermediate_plasticity_audit import target
from research.itd02_v23_unfamiliar_mapping_audit import new_target,train_source,features80
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev

STREAMS=(
 ("heldout_h1",(("heldout_h1",12),("source",12)),1),
 ("heldout_h2",(("heldout_h2",12),("source",12)),2),
 ("heldout_h3",(("heldout_h3",12),("source",12)),4),
 ("unchanged_h1",(("heldout_h1",12),("heldout_h1",12)),1),
 ("unchanged_h2",(("heldout_h2",12),("heldout_h2",12)),2),
 ("unchanged_h3",(("heldout_h3",12),("heldout_h3",12)),4))
def reward(regime,case):
 if regime=="source":
  return target(*case,nonlinear=True)
 cue,first,second=case
 ci=PUBLIC_CUES.index(cue);ai=ACTIONS.index(first);bi=ACTIONS.index(second)
 if regime=="heldout_h1":
  return 0.25+.6*(1 if (ci+ai)%2==0 else -1)+.45*(bi-1)-.35*(1 if (ci*bi)%3==0 else 0)
 if regime=="heldout_h2":
  return -.2+.55*(1 if ((ci+1)*(ai+1)+bi)%4==0 else -1)+.4*(1 if ai==bi else -1)+.15*ci
 if regime=="heldout_h3":
  return .1+.7*(1 if (ci+2*bi)%3==ai else -1)+.3*(1 if ci%2==bi%2 else -1)-.1*ai
 raise ValueError("INVALID_HELDOUT_FAMILY")
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
  self.precision=[[100.0 if i==j else 0.0 for j in range(80)] for i in range(80)]
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
  px=[sum(v*t for v,t in zip(row,x)) for row in self.precision]
  denom=1.0+sum(v*t for v,t in zip(x,px))
  assert denom>0
  err=y-r
  self.weights=[w+err*v/denom for w,v in zip(self.weights,px)]
  self.precision=[[self.precision[i][j]-px[i]*px[j]/denom for j in range(80)]
                  for i in range(80)]
  self.events+=1

def readout_regret(model,fast,destructive,conventional,regime):
 # External evaluator only: never passes counterfactual outcomes to a learner.
 a=CalibratedReturnRingDev.restore(model.checkpoint())
 b=SharedContextRingDev.restore(fast.checkpoint())
 d=SharedContextRingDev.restore(destructive.checkpoint())
 regret={k:0.0 for k in ("active","always_fast","destructive","conventional","two_expert","source")}
 error={k:0.0 for k in regret}
 for cue in PUBLIC_CUES:
  for first in ACTIONS:
   scores={k:[] for k in regret}
   actual=[]
   for second in ACTIONS:
    case=(cue,first,second)
    a.start_observation(cue);a.accept_first(first)
    scores["active"].append(a.score(second))
    scores["source"].append(a.bank.source_score(second))
    a.accept_second(second,0.0,learning=False)
    scores["always_fast"].append(public_step(b,case))
    scores["destructive"].append(public_step(d,case))
    _,_,cp,tp=conventional.predictions(case)
    scores["conventional"].append(cp)
    scores["two_expert"].append(tp)
    actual.append(reward(regime,case))
   best=max(actual)
   for key,values in scores.items():
    idx=max(range(3),key=lambda i:values[i])
    regret[key]+=best-actual[idx]
    error[key]+=sum(abs(p-y) for p,y in zip(values,actual))
 return {"regret":{k:round(v,10) for k,v in regret.items()},
         "error":{k:round(v,10) for k,v in error.items()}}

def run(name,stages,offset,source):
 model=CalibratedReturnRingDev(source)
 fast=SharedContextRingDev()
 destructive=SharedContextRingDev.restore(source)
 conventional=RidgeCUSUM(source)
 sha=model.bank.source_sha
 rec=[];snapshots=[];first_return=None;return_count=0;false_source=0
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
    if first_return is None and not model.fast:first_return=return_count
    return_error["active"]+=abs(active-y)
    return_error["fast"]+=abs(fp-y)
    return_error["conventional"]+=abs(cp-y)
   if name.startswith("unchanged_h") and stage==1 and i>=4:
    false_source+=int(not model.fast)
   if i+1 in (1,4,8,12):
    snapshots.append({"stage":stage,"event":i+1,"family_evaluator_only":regime,
                      **readout_regret(model,fast,destructive,conventional,regime)})
   rec.append({"stage_evaluator_only":stage,"index":i+1,"public":case,
     "reward":round(y,12),"active_pre":round(active,12),
     "fast_pre":round(fp,12),"conventional_pre":round(cp,12),
     "selected_fast_after":model.fast,"recent_votes":list(model.evidence)})
 assert CalibratedReturnRingDev.restore(model.checkpoint()).checkpoint()==model.checkpoint()
 assert len(model.checkpoint())<=12288
 return {"stream":name,"events":len(rec),"return_latency":first_return,
 "return_events":return_count,"false_source_unchanged_target":false_source,
 "return_preupdate_error":return_error,"source_sha_unchanged":True,
 "checkpoint_bytes":len(model.checkpoint()),"records":rec,"snapshots":snapshots}

def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for sha in ("671d8c3def0ef6cbe60e52eaf66d28ead8475e66",
             "089918a7bdefbdd19cf4b817bf191a60c2e76805"):
  assert git("merge-base","--is-ancestor",sha,"HEAD")==""
 source=train_source()["pretrained_shared"]
 results=[run(n,stages,o,source) for n,stages,o in STREAMS]
 return_ok=all(x["return_latency"] is not None and x["return_latency"]<=4
               for x in results[:3])
 no_false=all(x["false_source_unchanged_target"]==0 for x in results[-3:])
 gain=all(x["return_preupdate_error"]["active"]<=.9*x["return_preupdate_error"]["fast"]
         and x["return_preupdate_error"]["active"]<=.9*x["return_preupdate_error"]["conventional"]
         for x in results[:3])
 label=("V30_FROZEN_DETECTOR_UNSEEN_FAMILY_NO_GO__NO_SCIENCE"
        if not return_ok or not no_false else
        "V30_FROZEN_DETECTOR_STRONG_CONTROL_NO_GO__NO_SCIENCE")
 print(json.dumps({"schema":"ygg.itd02.v30.heldout_regime_frozen_v26.source_only.v1",
 "classification":label,"source_only":True,"scientific_first_use":False,
 "original_world_training":False,"candidate_scalars":326,
 "full_behavioral_science_qualification":False,
 "basic_reactivation_within_four":return_ok,"unchanged_target_no_false_source":no_false,
 "return_error_10pct_better_both":gain,
 "action_regret_measured":True,
 "streams":[{k:v for k,v in x.items() if k not in ("records","snapshots")} for x in results],
 "canonical_public_evidence_sha256":hashlib.sha256(canonical(
 [{"name":x["stream"],"records":x["records"],"snapshots":x["snapshots"]} for x in results])).hexdigest()},
 sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
