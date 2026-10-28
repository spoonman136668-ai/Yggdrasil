"""Original-native 21-coefficient budget-matched cell-local gradient projection.

Interference mechanism audit only: original frozen source not modified.
"""
import json,os,statistics
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import K,D,sig,softmax
from yggdrasil.itd02_native_task_bridge_dev import public_bits,public_outcome
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,OBSERVATIONS,ACTION_SITES
import copy
def projected_update(model,bits,outcome,selected_site,rate=.035):
    # Shared 21 coefficients, but selected reward cell controls ONLY its
    # own local role gate. Genome gradients from the other sites are
    # prevented from mutating global weights during this intervention.
    f=model.features(bits,selected_site)
    guesses=[sig(sum(w*x for w,x in zip(row,f))) for row in model.core.genome]
    gate=softmax(model.core.roles[selected_site])
    target=outcome[selected_site]
    losses=[(target-p)**2 for p in guesses]
    avg=sum(g*l for g,l in zip(gate,losses))
    for k in range(K):
        model.core.roles[selected_site][k]=max(-20.,min(20.,
            model.core.roles[selected_site][k]+rate*2*(avg-losses[k])))
        delta=rate*gate[k]*(target-guesses[k])
        for j in range(D):
            model.core.genome[k][j]=max(-15.,min(15.,
                model.core.genome[k][j]+delta*f[j]))
records=[]
for obs in OBSERVATIONS:
 for action in ACTIONS:
  bits=public_bits(obs,action)
  for reward in (-3,0,10):
   outcome=public_outcome("Nothing",reward)
   original=LocalTaskRuntime()
   local=LocalTaskRuntime()
   original.observe(bits,outcome)
   for site in ACTION_SITES:
    projected_update(local,bits,outcome,site)
   native=original.predict(bits)
   projected=local.predict(bits)
   records.append({"native_score":sum(v*native[s] for v,s in zip((-3,0,10),ACTION_SITES)),
                   "projected_score":sum(v*projected[s] for v,s in zip((-3,0,10),ACTION_SITES)),
                   "prediction_delta":sum(abs(native[s]-projected[s]) for s in ACTION_SITES),
                   "params_original":K*D,"params_projected":K*D})
assert len(records)==45
assert all(x["params_original"]==x["params_projected"] for x in records)
receipt={"schema":"itd02.shared-budget-local-gradient-control.v1",
"source_sha":os.environ["SOURCE_SHA"],"cases":len(records),
"original_expert_coefficients":K*D,"projected_expert_coefficients":K*D,
"resource_budget":"equal expert coefficient count; operation count and runtime NOT matched",
"mean_reward_head_prediction_delta":statistics.mean(x["prediction_delta"] for x in records),
"mean_original_score":statistics.mean(x["native_score"] for x in records),
"mean_projected_score":statistics.mean(x["projected_score"] for x in records),
"important":"Selected-only updates to shared coefficients do not eliminate cross-cell interference; source-only mechanism comparison, not acting learning/transfer.",
"scientific_first_use":False}
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_budget_local.json"),"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_BUDGET_LOCAL="+json.dumps(receipt,sort_keys=True))
