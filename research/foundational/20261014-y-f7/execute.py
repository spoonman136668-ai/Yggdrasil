"""Y-F7: freeze path-supervised Y-F6 model and test unseen structural grammars.

Strict no-retraining development transfer: frozen original 22-parameter model,
new topology families 28-31 with different seed and edge order permutations.
No training or validation trace supervision on this cohort, no F3 data.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
source=HERE.parent/"20261014-y-f6"/"execute.py"
spec=importlib.util.spec_from_file_location("y_f6_original",source)
assert spec and spec.loader
f6=importlib.util.module_from_spec(spec);spec.loader.exec_module(f6)
f4=f6.f4;f1=f6.f1
torch.set_num_threads(1)
MOTIFS={
28:((0,1),(1,2),(2,3),(3,4),(1,6),(6,3),(0,7),(7,8),(8,2),(9,10),(10,11),(11,12)),
29:((0,1),(1,2),(2,3),(3,4),(0,5),(5,1),(1,6),(6,7),(7,2),(2,8),(8,9),(9,10)),
30:((0,1),(1,2),(2,3),(3,4),(1,5),(5,6),(6,7),(7,3),(3,8),(8,2),(9,10),(10,11)),
31:((0,1),(1,2),(2,3),(3,4),(0,6),(6,7),(7,8),(8,3),(2,9),(9,10),(10,0),(11,12)),
}
FROZEN={
 "activation_bias":-2.8193814754486084,
 "identity_bias":2.7766518592834473,
 "message_gain":6.57424259185791,
 "output_bias":-3.574496269226074,
 "output_gain":7.382160663604736,
 "raw_weights":[3.040975570678711,2.7650673389434814,
 2.487110137939453,1.8289515972137451,.3033924996852875,
 .5809708833694458,1.9110623598098755,1.5663293600082397,
 2.613182544708252,1.7118607759475708,.014999818056821823,
 .014999818056821823,-1.,-1.,-1.,-1.],
 "recurrent_gain":-1.2088814973831177,
}
def make_case(seed,family,variant,perm):
 source=[(f1.relabel(a,seed,variant),f1.relabel(b,seed,variant))
         for a,b in MOTIFS[family]]
 for i in range(11,0,-1):
  j=(seed*47+i*17+family*13+perm*29)%(i+1)
  source[i],source[j]=source[j],source[i]
 assert len(source)==12 and len(set(source))==12
 a,b=(f1.relabel(0,seed,variant),f1.relabel(4,seed,variant))
 assert f6.reach(source,a,b,4)
 used={x for edge in source for x in edge}
 negative=sorted(x for x in used if x!=b and not f6.reach(source,a,x,4))
 assert negative
 c=negative[(seed+family+perm)%len(negative)]
 pairs=((a,b),(a,c)) if (seed+family+perm)%2==0 else ((a,c),(a,b))
 truth=tuple(f6.reach(source,*q,4) for q in pairs)
 assert sum(truth)==1
 return source,pairs,truth
def dataset():
 facts,queries,labels,keys=[],[],[],[]
 for seed in range(49500,49524):
  for family in range(28,32):
   for perm in range(2):
    edges,qs,truth=make_case(seed,family,2,perm)
    facts.append(edges);queries.append(qs);labels.append(truth)
    keys.append((seed,family,perm))
 return (torch.tensor(facts,dtype=torch.int32),
         torch.tensor(queries,dtype=torch.int32),
         torch.tensor(labels,dtype=torch.float32),keys)
def frozen_model():
 m=f4.RecurrentComposer()
 with torch.no_grad():
  state=m.state_dict()
  assert set(state)==set(FROZEN)
  for name,weights in FROZEN.items():
   tensor=torch.tensor(weights,dtype=state[name].dtype)
   assert tensor.shape==state[name].shape
   state[name]=tensor
  m.load_state_dict(state,strict=True)
 return m
def evaluate():
 start=time.perf_counter()
 x,q,y,keys=dataset()
 assert x.shape==(192,12,2) and q.shape==(192,2,2)
 frozen=frozen_model()
 with torch.no_grad():
  preds=(f6.model_forward(frozen,x,q)[0]>=.5)
  coded=(f1.fixed_exact(x,q)>=.5)
  f2=f4.f2
  old=f2.BitComparator()
  old.raw_weight.copy_(torch.tensor([
   1.2161805629730225,.8829572796821594,1.2392035722732544,
   2.430713415145874,3.4044041633605957,1.525221586227417,
   2.416123390472412,1.9606653451919556,2.265116930007934,
   1.659049153327942,1.053269624710083,2.638160467147827,
   2.233046293258667,3.9128310680389404,-1.,-1.]))
  old.bias.copy_(torch.tensor(4.553725719451904))
  coded_composer=(f1.answer(old.make_state(x),q)>=.5)
 labels=y.bool()
 outcomes={"frozen_YF6_native_recurrent_composition":preds,
           "frozen_YF2_coded_or_control":coded_composer,
           "fixed_coded_exact_equality_upper":coded}
 scores={}
 for name,pred in outcomes.items():
  neg=~labels
  scores[name]={"correct":int((pred==labels).sum()),
               "accuracy":float((pred==labels).float().mean()),
               "false_positives":int((pred&neg).sum()),
               "negative_fp_rate":float((pred&neg).sum().item()/neg.sum().item())}
 rows=[]
 for i,(seed,family,perm) in enumerate(keys):
  rows.append({"seed":seed,"family":family,"permutation":perm,
               "truth":labels[i].tolist(),
               "predictions":{n:p[i].tolist() for n,p in outcomes.items()}})
 assert len(rows)==192 and sum(not t for row in rows for t in row["truth"])==192
 # Exact coded reference must be correct; a failure invalidates this experiment.
 if scores["fixed_coded_exact_equality_upper"]["correct"]!=384:
  verdict="INVALID_CODED_REFERENCE_CONTROL"
 else:
  ours=scores["frozen_YF6_native_recurrent_composition"]
  code=scores["fixed_coded_exact_equality_upper"]
  valid=(ours["accuracy"]>=.85 and ours["negative_fp_rate"]<=.15 and
         code["accuracy"]-ours["accuracy"]<=.15)
  verdict=("DEVELOPMENT_FROZEN_PATH_TRAINED_GRAMMAR_TRANSFER" if valid else
           "DEVELOPMENT_NO_FROZEN_PATH_TRAINED_GRAMMAR_TRANSFER")
 return {"schema":"yggdrasil.foundation.f7.frozen-path-trained-transfer-dev.v1",
  "stage":"DEVELOPMENT_ONLY","source_F6_sha":"aa502051b009f20c592c577e80b7614e5be6e205",
  "F6_original_artifact_id":11930934002,
  "F6_result_sha256":"46e3512f6b1b719dddb1e133fe85949ee07ff4dc39b7e69a5c168248441fe2ef",
  "new_graph_families":[28,29,30,31],"seed_bounds":[49500,49524],
  "graph_states":192,"questions":384,"negative_questions":192,
  "resident_state_bytes":576,"model_parameters":22,
  "candidate_retrained":False,"candidate_weights":FROZEN,
  "no_coded_identity_or_OR_in_candidate":True,
  "coded_reference_required_correct":True,
  "author_created_development_source":True,
  "independently_witnessed_source_birth":False,
  "sealed_first_use":False,"scientific_acceptance":False,
  "accepted_ref_mutation":False,"external_model_calls":0,
  "scores":scores,"rows":rows,"registered_verdict":verdict,
  "original_wall_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
