import json,os,collections
from yggdrasil.itd02_native_task_bridge_dev import (
  _temporal_public_bits, NativeTaskRingBridgeDev, RING
)
from yggdrasil.itd02_local_ring_memory_dev import OBSERVATIONS,ACTIONS,ACTION_SITES
pairs=[(o,a) for o in OBSERVATIONS for a in ACTIONS]
assert len(pairs)==15
out={}
for site in ACTION_SITES:
  left,right=RING[site]
  one=set()
  ordered=set()
  unordered=set()
  for o,a in pairs:
    x=_temporal_public_bits(o,a,0)
    y=_temporal_public_bits(o,a,1)
    first=(x[left],x[right])
    second=(y[left],y[right])
    one.add(first)
    ordered.add((first,second))
    unordered.add(tuple(sorted((first,second))))
    assert x[site]==y[site]==0
  assert len(one)<=4 and len(ordered)==15 and len(unordered)==9
  out[str(site)]={"single_phase_patterns":len(one),
                  "ordered_two_phase_patterns":len(ordered),
                  "unordered_averaged_patterns":len(unordered),
                  "neighbors":[left,right]}
model=NativeTaskRingBridgeDev()
for i in range(40):
  o=OBSERVATIONS[i%5];a=ACTIONS[i%3]
  model.start_observation(o)
  model.accept_public_transition(a,"Nothing",(-3,0,10)[i%3],terminal=True)
snap=model.checkpoint()
restored=NativeTaskRingBridgeDev.restore(snap)
assert model.model_identities()==restored.model_identities()
assert model.cell_trace==restored.cell_trace
assert model.action_credit==restored.action_credit
receipt={"schema":"itd02.neighbor-credit-prerequisite.v1",
 "source_sha":os.environ["SOURCE_SHA"],"scientific_first_use":False,
 "native_cells":8,"context_action_pairs":15,"reward_site_locality":out,
 "baseline_v7_checkpoint_bytes":len(snap),"cold_restore_identity_pass":True,
 "native_original_source_changed":False,
 "limitation":"Two-phase ordered distinguishability does not imply learned local conditional credit."}
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_neighbor_credit_prerequisite.json"),"w") as f:
 json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_NEIGHBOR_CREDIT_PREREQUISITE="+json.dumps(receipt,sort_keys=True))
