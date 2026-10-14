"""Y-F9: typed relation/variable-binding identifiability under role swaps.

Each pair has identical endpoint graph and source/destination query, but one
role label on a necessary edge changes. Typed-path truth changes, while the
frozen model sees exactly the same 576-byte untyped state and must remain
invariant. This is a DEV-only representation-capability diagnostic, not F3.
"""
from __future__ import annotations
import importlib.util, json, time
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
source=HERE.parent/"20261014-y-f7"/"execute.py"
spec=importlib.util.spec_from_file_location("yf7_frozen_for_role_probe",source)
assert spec and spec.loader
f7=importlib.util.module_from_spec(spec);spec.loader.exec_module(f7)
f1=f7.f1
torch.set_num_threads(1)

# Typed paths alternate two subjects/objects and four independently bound
# relation roles. A changed intermediate role invalidates the same query.
def typed_reach(edges,roles,start,target,requested):
 states={start}
 for required in requested:
  next_states=set()
  for (a,b),r in zip(edges,roles):
   if r==required and a in states:
    next_states.add(b)
  states=next_states
 return target in states

def construct(seed,family):
 assert family in (40,41,42,43)
 pattern=tuple((seed+family+j*3)%4 for j in range(4))
 core=[(0,1),(1,2),(2,3),(3,4)]
 if family==40:
  distractors=[(8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,8),(9,11)]
 elif family==41:
  distractors=[(8,9),(9,8),(10,11),(11,12),(12,10),(13,14),(14,13),(10,12)]
 elif family==42:
  distractors=[(8,9),(9,10),(10,8),(11,12),(12,13),(13,11),(14,8),(9,11)]
 else:
  distractors=[(8,9),(9,10),(10,11),(11,8),(12,13),(13,14),(14,12),(8,10)]
 original=core+distractors
 assert len(original)==12 and len(set(original))==12
 original_roles=list(pattern)+[(seed+i*7+family)%4 for i in range(8)]
 # A role swap can alter truth without touching ANY entity identity or edge.
 altered_roles=original_roles.copy()
 altered_roles[2]=(altered_roles[2]+1)%4
 encoded=[(f1.relabel(a,seed,2),f1.relabel(b,seed,2))
          for a,b in original]
 for i in range(11,0,-1):
  j=(seed*17+family*29+i*7)%(i+1)
  encoded[i],encoded[j]=encoded[j],encoded[i]
  original_roles[i],original_roles[j]=original_roles[j],original_roles[i]
  altered_roles[i],altered_roles[j]=altered_roles[j],altered_roles[i]
 src=f1.relabel(0,seed,2)
 dst=f1.relabel(4,seed,2)
 assert typed_reach(encoded,original_roles,src,dst,pattern) is True
 assert typed_reach(encoded,altered_roles,src,dst,pattern) is False
 assert f7.f6.reach(encoded,src,dst,4) is True
 return encoded,original_roles,altered_roles,(src,dst),pattern

def evaluate():
 started=time.perf_counter()
 facts,questions,rows=[],[],[]
 for seed in range(51400,51448):
  for family in range(40,44):
   edges,before,after,q,pattern=construct(seed,family)
   facts.append(edges)
   questions.append((q,q))
   rows.append({"seed":seed,"family":family,
    "edges":edges,"roles_positive":before,"roles_swapped":after,
    "question":q,"requested_role_sequence":pattern,
    "truth":[True,False]})
 assert len(rows)==192
 x=torch.tensor(facts,dtype=torch.int32)
 q=torch.tensor(questions,dtype=torch.int32)
 model=f7.frozen_model()
 with torch.no_grad():
  # The candidate HAS NO ROLE INPUT, so both worlds share the same logits.
  same=(f7.f6.model_forward(model,x,q)[0][:,0]>=.5)
  untyped=(f1.fixed_exact(x,q)[:,0]>=.5)
 for idx,row in enumerate(rows):
  row["predictions"]={
   "frozen_learned_role_blind":[bool(same[idx]),bool(same[idx])],
   "untyped_coded_reachability":[bool(untyped[idx]),bool(untyped[idx])],
   "typed_role_aware_oracle":[
     typed_reach(row["edges"],row["roles_positive"],*row["question"],row["requested_role_sequence"]),
     typed_reach(row["edges"],row["roles_swapped"],*row["question"],row["requested_role_sequence"])],
   "always_yes_shortcut":[True,True]}
 scores={}
 for name in rows[0]["predictions"]:
  good=sum(sum(int(a==b) for a,b in zip(row["predictions"][name],row["truth"])) for row in rows)
  paired=sum(int(row["predictions"][name]==[True,False]) for row in rows)
  fp=sum(int(row["predictions"][name][1]) for row in rows)
  scores[name]={"correct":good,"accuracy":good/384,
                "paired_correct":paired,"paired_accuracy":paired/192,
                "negative_false_positives":fp}
 verdict="INVALID_TYPED_ROLE_ORACLE"
 if scores["typed_role_aware_oracle"]["paired_correct"]==192:
  if scores["frozen_learned_role_blind"]["paired_correct"]==0:
   verdict="TYPED_RELATION_AND_VARIABLE_BINDING_INPUT_MISSING"
  else:
   verdict="INVALID_IDENTICAL_STATE_INVARIANCE_BROKEN"
 return {"schema":"yggdrasil.f9.typed-role-identifiability-dev.v1",
  "stage":"DEVELOPMENT_ONLY","source_F8_sha":"4fe4dda43a9e8ccad82df2fb56c9677b9fc62bb8",
  "frozen_source_F6_artifact_sha256":"46e3512f6b1b719dddb1e133fe85949ee07ff4dc39b7e69a5c168248441fe2ef",
  "seeds":[51400,51448],"families":[40,41,42,43],
  "graph_pairs":192,"question_count":384,"negative_questions":192,
  "requested_role_alphabet":4,"requested_relation_length":4,
  "native_state_bytes":576,"trainable_model_parameters":22,
  "same_untyped_edges_and_query_per_counterfactual":True,
  "role_swaps_change_only_relation_types":True,
  "candidate_state_contains_role_codes":False,"model_retrained":False,
  "typed_oracle_must_pass":True,"scores":scores,"rows":rows,
  "registered_verdict":verdict,"source_birth_independent":False,
  "sealed_first_use":False,"scientific_accepted":False,
  "accepted_ref_mutation":False,"external_llm_calls":0,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
