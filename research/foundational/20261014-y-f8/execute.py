"""Y-F8: paired causal edge-break falsification of frozen Y-F6/Y-F7 weights.

Original and altered graph use exact same source/destination query and entity
IDs, but one necessary bridge fact is redirected to a distractor. Learned
candidate's inference never sees an explicit oracle label or coded equality.
Author-generated development only; no F3 sealed first-use or retraining.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
source=HERE.parent/"20261014-y-f7"/"execute.py"
spec=importlib.util.spec_from_file_location("y_f7_frozen",source)
assert spec and spec.loader
f7=importlib.util.module_from_spec(spec);spec.loader.exec_module(f7)
f1=f7.f1
torch.set_num_threads(1)
TOPOLOGIES={
36:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(12,13)),
37:((0,1),(1,2),(2,3),(3,4),(1,5),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(12,9)),
38:((0,1),(1,2),(2,3),(3,4),(3,0),(0,5),(5,6),(6,7),(7,1),(8,9),(9,10),(10,11)),
39:((0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(6,7),(7,8),(8,2),(9,10),(10,11),(11,9)),
}
def make_pair(seed,family):
 facts=[(f1.relabel(a,seed,1),f1.relabel(b,seed,1))
        for a,b in TOPOLOGIES[family]]
 for i in range(11,0,-1):
  k=(seed*31+family*17+i*13)%(i+1)
  facts[i],facts[k]=facts[k],facts[i]
 assert len(set(facts))==12
 start,target=f1.relabel(0,seed,1),f1.relabel(4,seed,1)
 bridge=(f1.relabel(2,seed,1),f1.relabel(3,seed,1))
 assert facts.count(bridge)==1
 mutated=list(facts)
 mutated[mutated.index(bridge)]=(bridge[0],f1.relabel(15,seed,1))
 assert len(set(mutated))==12
 assert f7.f6.reach(facts,start,target,4) is True
 assert f7.f6.reach(mutated,start,target,4) is False
 return facts,mutated,(start,target),bridge

def probability(model,edges,query):
 q=torch.tensor([[v,v] for v in query],dtype=torch.int32)
 with torch.no_grad():
  return f7.f6.model_forward(model,edges,q)[0][:,0]>=.5

def evaluate():
 begun=time.perf_counter()
 old,cut,questions,keys=[],[],[],[]
 for seed in range(50500,50548):
  for family in range(36,40):
   a,b,q,bridge=make_pair(seed,family)
   old.append(a);cut.append(b);questions.append(q);keys.append((seed,family,bridge))
 assert len(keys)==192
 original=torch.tensor(old,dtype=torch.int32)
 changed=torch.tensor(cut,dtype=torch.int32)
 question=torch.tensor(questions,dtype=torch.int32)
 both=torch.stack((question,question),dim=1)
 learned=f7.frozen_model()
 with torch.no_grad():
  a=(f7.f6.model_forward(learned,original,both)[0][:,0]>=.5)
  b=(f7.f6.model_forward(learned,changed,both)[0][:,0]>=.5)
  coded_a=(f1.fixed_exact(original,both)[:,0]>=.5)
  coded_b=(f1.fixed_exact(changed,both)[:,0]>=.5)
  # Negative: no observation of graph, predicts yes under either version.
  always_a=torch.ones_like(a)
  always_b=torch.ones_like(b)
 predictions={"frozen_YF6_learned_recurrence":(a,b),
              "fixed_exact_coded_causal_upper":(coded_a,coded_b),
              "constant_always_true_negative_control":(always_a,always_b)}
 scores={}
 for name,(pos,neg) in predictions.items():
  positive=int(pos.sum())
  negative=int((~neg).sum())
  paired=int((pos&(~neg)).sum())
  scores[name]={
    "accuracy":(positive+negative)/384,
    "correct":positive+negative,
    "causal_pair_correct":paired,
    "causal_pair_rate":paired/192,
    "baseline_positive_count":positive,
    "cut_negative_count":negative,
    "cut_false_positives":192-negative}
 rows=[]
 for i,(seed,fam,bridge) in enumerate(keys):
  rows.append({"seed":seed,"family":fam,"question":question[i].tolist(),
               "original_edges":old[i],"removed_bridge":bridge,
               "replacement_bridge":cut[i][old[i].index(bridge)],
               "truth":[True,False],
               "predictions":{n:[bool(values[0][i]),bool(values[1][i])]
                   for n,values in predictions.items()}})
 exact=scores["fixed_exact_coded_causal_upper"]
 ours=scores["frozen_YF6_learned_recurrence"]
 verdict="INVALID_CODED_CAUSAL_CONTROL"
 if exact["causal_pair_correct"]==192:
  passed=(ours["causal_pair_rate"]>=.95 and ours["accuracy"]>=.95 and
          ours["cut_false_positives"]<=10)
  verdict=("DEVELOPMENT_FROZEN_NATIVE_CAUSAL_BRIDGE_SENSITIVITY"
           if passed else "DEVELOPMENT_NO_FROZEN_NATIVE_CAUSAL_BRIDGE_SENSITIVITY")
 return {"schema":"yggdrasil.foundation.f8.causal-bridge-development.v1",
  "stage":"DEVELOPMENT_ONLY","source_F7_sha":"20d8b2dac16893456d8e409db3bf851e04ee367a",
  "frozen_F6_original_result_sha256":"46e3512f6b1b719dddb1e133fe85949ee07ff4dc39b7e69a5c168248441fe2ef",
  "new_families":[36,37,38,39],"new_seed_bounds":[50500,50548],
  "paired_states":len(rows),"question_count":384,"negative_questions":192,
  "candidate_parameter_count":22,"native_state_bytes":576,
  "candidate_retrained":False,"source_birth_witnessed":False,
  "fixed_exact_coded_must_pass":True,"scores":scores,"rows":rows,
  "registered_verdict":verdict,"sealed_first_use":False,
  "scientific_accepted":False,"accepted_ref_mutation":False,
  "external_llm_calls":0,"original_wall_ms":round((time.perf_counter()-begun)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
