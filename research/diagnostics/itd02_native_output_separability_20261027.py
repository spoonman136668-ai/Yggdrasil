"""Frozen-source diagnosis of reward prediction separability, no source edits."""
import hashlib,json,math,os,statistics
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,public_bits,REWARDS
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,OBSERVATIONS,ACTION_SITES
OBS=("LRV","MRV","Nothing","docked_MRV","docked_LRV")
assert len(OBS)==5
all_rows=[]
for family in range(134,142):
 for seed in range(132,140):
  m=NativeTaskRingBridgeDev()
  old={o:hashlib.sha256(f"old:{family}:{seed}:{o}".encode()).digest()[0]%3 for o in OBS}
  new={o:hashlib.sha256(f"new:{family}:{seed}:{o}".encode()).digest()[0]%3 for o in OBS}
  for phase in ("initial","changed"):
   rows=[]
   for step in range(90):
    obs=OBS[(step+seed)% (3 if phase=="initial" else 5)]
    m.start_observation(obs)
    outputs=[m.native.predict(public_bits(obs,a)) for a in ACTIONS]
    scores=[sum(REWARDS[k]*out[ACTION_SITES[k]] for k in range(3)) for out in outputs]
    optimal=(old if phase=="initial" else new)[obs]
    action=ACTIONS[(step+seed)%3] if step%9==0 else m.choose()
    idx=ACTIONS.index(action)
    reward=10 if idx==optimal else (0 if idx==(optimal+1)%3 else -3)
    rows.append({"obs":obs,"action":action,"reward":reward,"correct":ACTIONS[optimal],
      "native_scores":scores,"native_reward_bits": [[out[k] for k in ACTION_SITES] for out in outputs],
      "range":max(scores)-min(scores),"best":ACTIONS[max(range(3),key=lambda k:scores[k])]})
    m.accept_public_transition(action,"Nothing",reward,terminal=True)
   all_rows.append({"family":family,"seed":seed,"phase":phase,"rows":rows})
assert len(all_rows)==128
result={}
for phase in ("initial","changed"):
 rows=[r for x in all_rows if x["phase"]==phase for r in x["rows"]]
 result[phase]={
  "events":len(rows),
  "top_action_counts":{a:sum(r["best"]==a for r in rows) for a in ACTIONS},
  "native_top_reward_correct":sum(r["best"]==r["correct"] for r in rows)/len(rows),
  "native_action_score_range_mean":statistics.mean(r["range"] for r in rows),
  "native_action_score_range_zero_count":sum(abs(r["range"])<1e-12 for r in rows),
  "reward_site_means_by_candidate_action":{
   action:[statistics.mean(r["native_reward_bits"][j][k] for r in rows) for k in range(3)]
   for j,action in enumerate(ACTIONS)},
  "own_action_cell_reward_bit_mean":{
   a:statistics.mean(r["native_reward_bits"][j][j] for r in rows)
   for j,a in enumerate(ACTIONS)},
  "chosen_reward_mean":statistics.mean(r["reward"] for r in rows)
 }
receipt={"schema":"itd02.native-original-output-separability.v1","source_sha":os.environ["SOURCE_SHA"],
"source_free":True,"first_use":False,"family_ids":list(range(134,142)),"seeds":list(range(132,140)),
"original_native_public_feedback_events":11520,"diagnostic":result,
"disclaimer":"Chosen events are source-free synthetic, no counterfactual rewards exposed to learner"}
assert sum(v["events"] for v in result.values())==11520
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_native_separability.json"),"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_NATIVE_SEPARABILITY="+json.dumps(receipt,sort_keys=True))
