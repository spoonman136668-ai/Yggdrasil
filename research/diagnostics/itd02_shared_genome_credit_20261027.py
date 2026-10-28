"""Frozen original runtime causal one-step credit and collateral output change."""
import json,os,statistics
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.itd02_native_task_bridge_dev import public_bits,public_outcome
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,OBSERVATIONS,ACTION_SITES
rows=[]
for obs in OBSERVATIONS:
 for action in ACTIONS:
  before=public_bits(obs,action)
  for target_reward in (-3,0,10):
   after=public_outcome("Nothing",target_reward)
   for trained_site in ACTION_SITES:
    runtime=LocalTaskRuntime()
    src=[0]*8
    for i in range(8):src[i]=after[i] if i==trained_site else runtime.predict(before)[i]>=.5
    # Measure precisely the effect of one original observe, preserving fixed native source.
    old=runtime.predict(before)
    runtime.observe(before,after)
    new=runtime.predict(before)
    direct=new[trained_site]-old[trained_site]
    collateral=sum(abs(new[k]-old[k]) for k in ACTION_SITES if k!=trained_site)
    rows.append({"obs":obs,"action":action,"reward":target_reward,
      "head":trained_site,"direct_change":direct,"total_head_collateral":collateral,
      "neighbor_reward_head_overlap":len(set(runtime.neighbors[trained_site])&set(ACTION_SITES))})
assert len(rows)==135
by_head={}
for site in ACTION_SITES:
 v=[r for r in rows if r["head"]==site]
 by_head[str(site)]={"trials":len(v),"mean_abs_direct":statistics.mean(abs(r["direct_change"]) for r in v),
 "mean_abs_cross_head":statistics.mean(r["total_head_collateral"] for r in v),
 "cross_head_nonzero":sum(r["total_head_collateral"]>1e-12 for r in v)}
receipt={"schema":"itd02.original-native-shared-genome-collateral.v1",
 "source_sha":os.environ["SOURCE_SHA"],"observations":len(OBSERVATIONS),
 "actions":len(ACTIONS),"reward_labels":3,"controlled_pairs":len(rows),
 "head_site_analysis":by_head,"shared_expert_genome":True,
 "causal_scope":"One local training event updates all sites via shared expert genome; mechanism audit only, not chosen-action task performance.",
 "source_modified":False,"scientific_first_use":False}
p=os.path.join(os.environ["RUNNER_TEMP"],"native_crosscell_credit.json")
with open(p,"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_CROSSCELL_CREDIT="+json.dumps(receipt,sort_keys=True))
