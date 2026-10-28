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
    control=LocalTaskRuntime()
    treatment=LocalTaskRuntime()
    # Controlled counterfactual differs ONLY in the chosen site's outcome
    # bit; all other seven labels, original source and initial genomes match.
    toggled=list(after)
    toggled[trained_site]=1-toggled[trained_site]
    control.observe(before,after)
    treatment.observe(before,toggled)
    p0=control.predict(before)
    p1=treatment.predict(before)
    direct=p1[trained_site]-p0[trained_site]
    collateral=sum(abs(p1[k]-p0[k]) for k in ACTION_SITES if k!=trained_site)
    rows.append({"obs":obs,"action":action,"reward":target_reward,
      "head":trained_site,"direct_change":direct,"total_head_collateral":collateral,
      "neighbor_reward_head_overlap":len(set(control.neighbors[trained_site])&set(ACTION_SITES))})
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
 "causal_scope":"Matched originals; flip only one reward output target before one full observe. Measures collateral response through shared expert genome; not native on-policy improvement.",
 "source_modified":False,"scientific_first_use":False}
p=os.path.join(os.environ["RUNNER_TEMP"],"native_crosscell_credit.json")
with open(p,"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_CROSSCELL_CREDIT="+json.dumps(receipt,sort_keys=True))
