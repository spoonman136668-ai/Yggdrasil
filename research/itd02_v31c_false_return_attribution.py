"""External V31C attribution of false source selection, no detector change."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
from yggdrasil.itd02_v31b_public_surprise_dev import PublicSurpriseRingDev

def replay(name,stages,offset,source):
 m=PublicSurpriseRingDev(source);sha=m.bank.source_sha
 out=[];return_count=0;latency=None
 for stage,(family,n) in enumerate(stages):
  for i in range(n):
   case=context(i,offset);y=reward(family,case)
   m.start_observation(case[0]);m.accept_first(case[1])
   es=abs(y-m.bank.source_score(case[2]))
   ef=abs(y-m.bank.fast_score(case[2]))
   before=m.fast
   pre=list(m.recent)
   m.accept_second(case[2],y)
   window=(pre+[(es,ef)])[-3:]
   expect=before
   if not before and sum(s>=1 and s-f>=.15 for s,f in window)>=2:expect=True
   elif before and len(window)>=2 and all(f-s>=.15 for s,f in window[-2:]):expect=False
   assert m.fast==expect
   assert m.bank.slow.parameters_sha256()==sha
   returning=stage>0 and family=="source" and stages[stage-1][0]!="source"
   if returning:
    return_count+=1
    if latency is None and not m.fast:latency=return_count
   out.append({"stage_offline_only":stage,"event":i+1,"public":case,
     "reward":round(y,12),"source_error":round(es,12),
     "fast_error":round(ef,12),
     "prior_public_residuals":[[round(s,12),round(f,12)] for s,f in pre],
     "fast_before":before,"fast_after":m.fast,
     "source_return_predicate":before and len(window)>=2 and
       all(f-s>=.15 for s,f in window[-2:])})
 return out,latency

def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for pin in ("2febb606501886a72f679f8e4b44cb0d48a2a797",
             "0d97bd518fb7ca4044a97bf125292ba6f26a4e36"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 source=train_source()["pretrained_shared"]
 results={}
 for n,st,o in STREAMS:
  events,latency=replay(n,st,o,source)
  assert events==replay(n,st,o,source)[0]
  results[n]={"events":events,"return_latency":latency}
 assert [results[n]["return_latency"] for n in ("basic_t1","basic_t2")]==[1,4]
 false=[x for x in results["unchanged_t1"]["events"][-8:] if not x["fast_after"]]
 assert len(false)==3
 assert sum(not x["fast_after"] for x in results["unchanged_t2"]["events"][-8:])==0
 canon=canonical(results);digest=hashlib.sha256(canon).hexdigest()
 changed=json.loads(canon);changed["unchanged_t1"]["events"][12]["reward"]+=.001
 assert hashlib.sha256(canonical(changed)).hexdigest()!=digest
 print(json.dumps({"schema":"ygg.itd02.v31c.false_return_attribution.v1",
  "classification":"V31C_FALSE_RETURN_ATTRIBUTED__V31B_STILL_NO_GO__NO_SCIENCE",
  "source_only":True,"holdout_evaluated":False,"scientific_first_use":False,
  "return_latency":[1,4],"false_unchanged_t1":3,"false_unchanged_t2":0,
  "false_case_witness":false,
  "canonical_public_sha256":digest,
  "public_reward_digest_tamper_detected":True,
  "unchanged_model_source":True},sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
