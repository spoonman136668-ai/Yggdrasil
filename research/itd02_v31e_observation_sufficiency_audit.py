"""V31E external-only finite public feedback sufficiency witness."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS,context,reward
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev

def replay(name,stages,offset,source):
 m=DistinctReturnRingDev(source);sha=m.bank.source_sha;events=[]
 for stage,(family,n) in enumerate(stages):
  for i in range(n):
   case=context(i,offset);y=reward(family,case)
   m.start_observation(case[0]);m.accept_first(case[1])
   es=abs(y-m.bank.source_score(case[2]));ef=abs(y-m.bank.fast_score(case[2]))
   m.accept_second(case[2],y)
   assert m.bank.slow.parameters_sha256()==sha
   privileged=[reward(family,(case[0],case[1],a)) for a in ACTIONS]
   events.append({"public":list(case),"reward":round(y,12),
                  "source_error":round(es,12),"fast_error":round(ef,12),
                  "family_offline_only":family,
                  "privileged_unselected_reward_vector":[round(x,12) for x in privileged]})
 return events

def audit():
 source=train_source()["pretrained_shared"]
 samples={}
 for name,stages,offset in STREAMS:
  samples[name]=replay(name,stages,offset,source)
 windows=[];seen={};collisions=[]
 for name,events in samples.items():
  for index in range(3,len(events)):
   w=events[index-3:index+1]
   public=[[e["public"],e["reward"]] for e in w]
   family=w[-1]["family_offline_only"]
   key=hashlib.sha256(canonical(public)).hexdigest()
   if key in seen and seen[key]["family"]!=family:
    collisions.append({"first":seen[key]["name"],"second":name,"sha":key})
   seen.setdefault(key,{"name":name,"family":family})
   windows.append({"stream":name,"end_event":index+1,"public_history":public,
                   "offline_family":family})
 # The privileged vector is external; never provided to candidate.
 missing=0;observed=0
 for events in samples.values():
  for e in events:
   observed+=1
   missing+=sum(a!=e["public"][2] for a in ACTIONS)
 assert missing==2*observed
 assert samples["basic_t2"][12]["family_offline_only"]=="source"
 digest=hashlib.sha256(canonical(windows)).hexdigest()
 altered=json.loads(canonical(windows));altered[0]["public_history"][0][1]+=.001
 assert hashlib.sha256(canonical(altered)).hexdigest()!=digest
 t2=samples["basic_t2"][12:16]
 wrong=samples["unchanged_t1"][18:22]
 matched=sum(a["public"]==b["public"] for a,b in zip(t2,wrong))
 return {"schema":"ygg.itd02.v31e.source_observation_sufficiency.v1",
 "classification":("V31E_FINITE_PUBLIC_HISTORY_COLLISION__NO_SCIENCE" if collisions else
 "V31E_NO_HARD_COLLISION_OBSERVED__DETECTOR_UNPROVEN__NO_SCIENCE"),
 "source_only":True,"scientific_first_use":False,"heldout_evaluated":False,
 "streams":len(samples),"four_event_windows":len(windows),
 "cross_family_public_history_collisions":len(collisions),
 "collision_examples":collisions[:8],
 "actual_selected_reward_observations":observed,
 "privileged_unselected_reward_values_withheld":missing,
 "t2_first_four_source_error_advantages":[round(e["fast_error"]-e["source_error"],10) for e in t2],
 "unchanged_t1_false_switch_window_advantages":[round(e["fast_error"]-e["source_error"],10) for e in wrong],
 "aligned_public_identities_between_witness_windows":matched,
 "tamper_evidence_digest_detected":True,"canonical_public_history_sha256":digest}

def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for pin in ("1b0627cb461152ffe42d721ba5c6ee4d3a0b7057","f64ba4ca924d1da2262e568258df94428f1e6507"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 print(json.dumps(audit(),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
