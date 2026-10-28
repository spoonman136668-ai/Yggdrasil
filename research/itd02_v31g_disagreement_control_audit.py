"""V31G frozen disagreement versus full-matrix RLS uncertainty exploration."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source,features80
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev

def run(name,stages,offset,source,policy):
 m=DistinctReturnRingDev(source);sha=m.bank.source_sha
 P=[[100. if i==j else 0. for j in range(80)] for i in range(80)]
 w=[0.]*80;records=[];regret=0.;ret_err=0.;latency=None;rn=0;false=0
 for stage,(family,n) in enumerate(stages):
  for i in range(n):
   cue,first,scheduled=context(i,offset)
   m.start_observation(cue);m.accept_first(first)
   sp=[m.bank.source_score(x) for x in ACTIONS]
   fp=[m.bank.fast_score(x) for x in ACTIONS]
   xs=[features80(cue,first,x) for x in ACTIONS]
   pxs=[[sum(row[j]*x[j] for j in range(80)) for row in P] for x in xs]
   uncertainty=[sum(x[j]*px[j] for j in range(80)) for x,px in zip(xs,pxs)]
   if policy=="disagreement": k=max(range(3),key=lambda j:abs(sp[j]-fp[j]))
   elif policy=="uncertainty_rls":k=max(range(3),key=lambda j:uncertainty[j])
   else:k=ACTIONS.index(scheduled)
   action=ACTIONS[k];case=(cue,first,action)
   y=reward(family,case);r=sp[k] if not m.fast else fp[k]
   regret+=max(reward(family,(cue,first,x)) for x in ACTIONS)-y
   x=xs[k];px=pxs[k];denom=1+uncertainty[k];pred=sum(w[j]*x[j] for j in range(80))
   w=[w[j]+px[j]*(y-pred)/denom for j in range(80)]
   P=[[P[j][h]-px[j]*px[h]/denom for h in range(80)] for j in range(80)]
   m.accept_second(action,y)
   assert m.bank.slow.parameters_sha256()==sha
   returning=stage>0 and family=="source" and stages[stage-1][0]!="source"
   if returning:
    rn+=1;ret_err+=abs(y-r)
    if latency is None and not m.fast:latency=rn
   if name.startswith("unchanged_t") and stage==1 and i>=4:false+=int(not m.fast)
   records.append({"case":case,"reward":round(y,12),"selected_fast":m.fast,
     "uncertainty":round(uncertainty[k],12)})
 return {"stream":name,"policy":policy,"latency":latency,"false_source":false,
 "regret":round(regret,10),"return_error":round(ret_err,10),
 "source_sha_unchanged":True,"rls_stored_numbers":6480,"records":records}
def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for pin in ("c243487ec01180a40001f2cfe89d62ad24759544","49b659ff9a662dee2b9e6ba64c047dfe86c44725"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 source=train_source()["pretrained_shared"]
 chosen=[x for x in STREAMS if x[0] in ("basic_t1","basic_t2","unchanged_t1","unchanged_t2")]
 rows=[run(n,st,o,source,p) for n,st,o in chosen for p in ("scheduled","disagreement","uncertainty_rls")]
 dic={(x["stream"],x["policy"]):x for x in rows}
 behavioral=all(dic[(n,"disagreement")]["latency"] is not None and dic[(n,"disagreement")]["latency"]<=4 and dic[(n,"disagreement")]["regret"]<dic[(n,"scheduled")]["regret"] and dic[(n,"disagreement")]["regret"]<dic[(n,"uncertainty_rls")]["regret"] for n in ("basic_t1","basic_t2")) and all(dic[(n,"disagreement")]["false_source"]==0 for n in ("unchanged_t1","unchanged_t2"))
 label="V31G_QUALIFICATION_INCOMPLETE__NO_SCIENCE" if behavioral else "V31G_DISAGREEMENT_STRONG_CONTROL_NO_GO__NO_SCIENCE"
 print(json.dumps({"schema":"ygg.itd02.v31g.frozen_disagreement_control.dev_only.v1","classification":label,
 "source_only":True,"holdout_evaluated":False,"scientific_first_use":False,
 "complete_inherited_native_and_resource_qualification":False,
 "streams":len(chosen),"arms":3,
 "canonical_evidence_sha256":hashlib.sha256(canonical(rows)).hexdigest(),
 "summary":[{k:v for k,v in row.items() if k!="records"} for row in rows]},
 sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
