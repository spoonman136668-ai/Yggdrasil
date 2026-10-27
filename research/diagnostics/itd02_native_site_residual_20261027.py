"""Original source-only native reward-site residual and decoder attribution."""
import hashlib,json,os,statistics,collections
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,public_bits,REWARDS
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,ACTION_SITES
OBS=("LRV","MRV","Nothing","docked_MRV","docked_LRV")
families=range(142,150);seeds=range(140,148)
rows=[]
for f in families:
 for seed in seeds:
  m=NativeTaskRingBridgeDev()
  laws={}
  for stage in ("initial","changed"):
   laws[stage]={o:hashlib.sha256(f"{stage}:{f}:{seed}:{o}".encode()).digest()[0]%3 for o in OBS}
  for stage in ("initial","changed"):
   for step in range(90):
    obs=OBS[(step+seed)%(3 if stage=="initial" else 5)]
    m.start_observation(obs)
    predictions=[m.native.predict(public_bits(obs,a)) for a in ACTIONS]
    native=[sum(REWARDS[k]*p[ACTION_SITES[k]] for k in range(3)) for p in predictions]
    actor=m.choose()
    chosen=ACTIONS[(step+seed)%3] if step%9==0 else actor
    actionidx=ACTIONS.index(chosen)
    target=laws[stage][obs]
    reward=10 if actionidx==target else (0 if actionidx==(target+1)%3 else -3)
    label=REWARDS.index(reward)
    own=predictions[actionidx]
    rows.append({"stage":stage,"action":chosen,"reward":reward,"native_score":native[actionidx],
      "bits":[own[site] for site in ACTION_SITES],
      "target":[int(label==j) for j in range(3)],
      "best":ACTIONS[max(range(3),key=lambda j:native[j])],
      "optimal":ACTIONS[target],
      "score_margin":max(native)-min(native)})
    m.accept_public_transition(chosen,"Nothing",reward,terminal=True)
assert len(rows)==11520
out={}
for stage in ("initial","changed"):
 stage_rows=[r for r in rows if r["stage"]==stage]
 out[stage]={"events":len(stage_rows),"native_best_correct_rate":statistics.mean(r["best"]==r["optimal"] for r in stage_rows),
   "candidate_top_actions":dict(collections.Counter(r["best"] for r in stage_rows)),
   "chosen_action_counts":dict(collections.Counter(r["action"] for r in stage_rows)),
   "reward_site_by_selected_action":{}}
 for action in ACTIONS:
  subset=[r for r in stage_rows if r["action"]==action]
  out[stage]["reward_site_by_selected_action"][action]={
    str(REWARDS[k]):{
      "count":len(subset),
      "pre_outcome_predicted_site_mean":statistics.mean(r["bits"][k] for r in subset),
      "public_true_label_rate":statistics.mean(r["target"][k] for r in subset),
      "signed_site_error":statistics.mean(r["bits"][k]-r["target"][k] for r in subset),
      "site_brier":statistics.mean((r["bits"][k]-r["target"][k])**2 for r in subset)
    } for k in range(3)
  }
receipt={"schema":"itd02.original-native-reward-site-residual.v1","source_sha":os.environ["SOURCE_SHA"],
"authority":"synthetic-public-original-source-only-no-FSA","cases":len(rows),
"families":list(families),"seeds":list(seeds),"metrics":out,
"scope":"Chosen-action pre-outcome reward-label bits only. No reward oracle, no counterfactual credit, no model promotion."}
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_native_site_residual.json"),"w") as file:json.dump(receipt,file,sort_keys=True,indent=2)
print("ITD02_NATIVE_SITE_RESIDUAL="+json.dumps(receipt,sort_keys=True))
