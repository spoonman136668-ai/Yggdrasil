"""Frozen source, original native learning vs isolated per-cell gradient reference.

Engineering diagnostic, not promotion or original model modification.
"""
import json,os,statistics,math
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import softmax,sig,K,D,N
from yggdrasil.itd02_native_task_bridge_dev import public_bits,public_outcome
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,OBSERVATIONS,ACTION_SITES
def private_cell_update(model,bits,outcome,rate=.035):
    # A separately instantiated cell-owned expert copy, used ONLY for this
    # diagnostic; inherited native roles and two immediate-neighbor features.
    for i,target in enumerate(outcome):
        f=model.features(bits,i)
        guesses=[sig(sum(w*x for w,x in zip(row,f))) for row in model.private_genomes[i]]
        gate=softmax(model.core.roles[i]);losses=[(target-p)**2 for p in guesses]
        avg=sum(g*l for g,l in zip(gate,losses))
        for k in range(K):
            model.core.roles[i][k]=max(-20.,min(20.,model.core.roles[i][k]+rate*2*(avg-losses[k])))
            delta=rate*gate[k]*(target-guesses[k])
            for j in range(D):
                model.private_genomes[i][k][j]=max(-15.,min(15.,model.private_genomes[i][k][j]+delta*f[j]))
def private_predict(model,bits):
    result=[]
    for i in range(N):
        f=model.features(bits,i)
        gate=softmax(model.core.roles[i])
        result.append(sum(g*sig(sum(w*x for w,x in zip(row,f)))
                          for g,row in zip(gate,model.private_genomes[i])))
    return result
import copy
trials=[]
for obs in OBSERVATIONS:
 for action in ACTIONS:
  bits=public_bits(obs,action)
  for reward in (-3,0,10):
   outcome=public_outcome("Nothing",reward)
   shared=LocalTaskRuntime()
   local=LocalTaskRuntime()
   local.private_genomes=[copy.deepcopy(local.core.genome) for _ in range(N)]
   shared.observe(bits,outcome)
   private_cell_update(local,bits,outcome)
   # Matched initial predictions and training labels; compare response to
   # counterfactual changed label ONLY at reward site 5.
   baseline_local=private_predict(local,bits)
   baseline_shared=shared.predict(bits)
   variation=list(outcome);variation[5]=1-variation[5]
   shared2=LocalTaskRuntime()
   local2=LocalTaskRuntime()
   local2.private_genomes=[copy.deepcopy(local2.core.genome) for _ in range(N)]
   shared2.observe(bits,variation)
   private_cell_update(local2,bits,variation)
   sh=shared2.predict(bits)
   lo=private_predict(local2,bits)
   non_target=[site for site in ACTION_SITES if site!=5]
   trials.append({"shared_cross":sum(abs(sh[j]-baseline_shared[j]) for j in non_target),
                  "local_cross":sum(abs(lo[j]-baseline_local[j]) for j in non_target),
                  "shared_target":abs(sh[5]-baseline_shared[5]),
                  "local_target":abs(lo[5]-baseline_local[5])})
assert len(trials)==45
assert all(abs(row["local_cross"])<1e-12 for row in trials)
assert any(row["shared_cross"]>1e-12 for row in trials)
receipt={"schema":"itd02.source-frozen-cell-owned-gradient-probe.v1",
"source_sha":os.environ["SOURCE_SHA"],"cases":len(trials),
"identical_observed_outcomes":True,"original_training_source_changed":False,
"shared_expert_coefficients":K*D,"private_expert_coefficients":N*K*D,
"parameter_budget_matched":False,"controlled_target_site":5,
"mean_shared_cross":statistics.mean(t["shared_cross"] for t in trials),
"mean_local_cross":statistics.mean(t["local_cross"] for t in trials),
"mean_shared_target":statistics.mean(t["shared_target"] for t in trials),
"mean_local_target":statistics.mean(t["local_target"] for t in trials),
"interpretation":"Mechanism proof only; 8x expert weights is not a fair efficiency or performance comparison.",
"scientific_first_use":False}
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_cell_owned_gradient.json"),"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_CELL_OWNED_GRADIENT="+json.dumps(receipt,sort_keys=True))
