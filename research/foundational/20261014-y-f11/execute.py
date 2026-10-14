"""Y-F11 frozen role-order transfer test on competing paths and permutations.

Two 4-hop routes share start/end and have IDENTICAL bags of four relation
types but different ordered role sequences. The query asks for a particular
ordered sequence. Frozen Y-F10 must distinguish exact order, not detect a bag
of roles or graph reachability. No retraining, development source only.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
src=HERE.parent/"20261014-y-f10"/"execute.py"
spec=importlib.util.spec_from_file_location("yf10_frozen_role",src)
assert spec and spec.loader
f10=importlib.util.module_from_spec(spec);spec.loader.exec_module(f10)
f7=f10.f7;f1=f10.f1
torch.set_num_threads(1)
FROZEN=[
 [3.2071902751922607,.24742856621742249,.27722424268722534,-2.37184476852417],
 [-2.372128486633301,3.207536458969116,.24348078668117523,.2726326882839203],
 [.286793977022171,-2.3733959197998047,3.208224296569824,.25642478466033936],
 [.24700559675693512,.28178325295448303,-2.3747541904449463,3.2073140144348145]]
MOTIFS={
52:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(8,9),(9,10),(10,11),(11,8)),
53:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(1,8),(8,9),(9,10),(10,9)),
54:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(2,8),(8,9),(9,8),(10,11)),
55:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(0,8),(8,9),(9,10),(10,11)),
}
def datum(seed,family,role_shift):
 motif=MOTIFS[family]
 # A and B are valid but nonidentical role orderings; C has exactly
 # their bag of roles but is invalid for BOTH routes.
 transform=lambda x:(x+role_shift+(seed+family)%4)%4
 A=tuple(transform(i) for i in (0,1,2,3))
 B=tuple(transform(i) for i in (0,2,1,3))
 C=tuple(transform(i) for i in (3,2,1,0))
 assert sorted(A)==sorted(B)==sorted(C) and A!=B and A!=C and B!=C
 edges=[(f1.relabel(a,seed,2),f1.relabel(b,seed,2)) for a,b in motif]
 roles=list(A)+list(B)+[transform((seed+i*3)%4) for i in range(4)]
 for i in range(11,0,-1):
  j=(seed*13+family*19+i*7+role_shift*31)%(i+1)
  edges[i],edges[j]=edges[j],edges[i]
  roles[i],roles[j]=roles[j],roles[i]
 start,end=f1.relabel(0,seed,2),f1.relabel(4,seed,2)
 assert f10.typed_exact(edges,roles,start,end,A)
 assert f10.typed_exact(edges,roles,start,end,B)
 assert not f10.typed_exact(edges,roles,start,end,C)
 assert f7.f6.reach(edges,start,end,4)
 return {"seed":seed,"family":family,"role_shift":role_shift,
  "edges":edges,"roles":roles,"query":[start,end],
  "true_order":A,"second_valid_order":B,"hard_negative_order":C,
  "truth":[True,False]}

def model():
 m=f10.TypedComposer()
 with torch.no_grad():m.role_logits.copy_(torch.tensor(FROZEN,dtype=torch.float32))
 assert sum(p.numel() for p in m.parameters() if p.requires_grad)==16
 return m

def evaluate():
 started=time.perf_counter()
 rows=[]
 for seed in range(54600,54624):
  for family in range(52,56):
   for role_shift in (0,1):
    rows.append(datum(seed,family,role_shift))
 assert len(rows)==192
 facts=torch.tensor([r["edges"] for r in rows],dtype=torch.int32)
 roles=torch.tensor([r["roles"] for r in rows],dtype=torch.int64)
 query=torch.tensor([r["query"] for r in rows],dtype=torch.int32)
 reqA=torch.tensor([r["true_order"] for r in rows],dtype=torch.int64)
 reqC=torch.tensor([r["hard_negative_order"] for r in rows],dtype=torch.int64)
 trained=model()
 untrained=f10.TypedComposer()
 with torch.no_grad():
  encoded=trained.encode(facts,roles)
  learnedA=trained.predict(encoded,query,reqA)>=.5
  learnedC=trained.predict(encoded,query,reqC)>=.5
  initialized_state=untrained.encode(facts,roles)
  untrainedA=untrained.predict(initialized_state,query,reqA)>=.5
  untrainedC=untrained.predict(initialized_state,query,reqC)>=.5
  q2=query.unsqueeze(1).repeat(1,2,1)
  roleblind=f7.f6.model_forward(f7.frozen_model(),facts,q2)[0][:,0]>=.5
 candidates={
  "frozen_YF10_ordered_role_model":(learnedA,learnedC),
  "same_arch_untrained_role_model":(untrainedA,untrainedC),
  "frozen_YF9_untyped_reachability":(roleblind,roleblind),
  "coded_typed_exact_order_reference":(
   torch.tensor([f10.typed_exact(r["edges"],r["roles"],*r["query"],r["true_order"]) for r in rows]),
   torch.tensor([f10.typed_exact(r["edges"],r["roles"],*r["query"],r["hard_negative_order"]) for r in rows])),
  "role_bag_order_insensitive_shortcut":(
   torch.ones(len(rows),dtype=torch.bool),torch.ones(len(rows),dtype=torch.bool))}
 stats={}
 for name,(a,b) in candidates.items():
  pos=int(a.sum());neg=int((~b).sum());paired=int((a&(~b)).sum())
  stats[name]={"correct":pos+neg,"accuracy":(pos+neg)/(len(rows)*2),
   "paired_correct":paired,"paired_accuracy":paired/len(rows),
   "false_positives":len(rows)-neg}
 for i,row in enumerate(rows):
  row["predictions"]={name:[bool(ab[0][i]),bool(ab[1][i])]
                      for name,ab in candidates.items()}
 assert all(row["truth"]==[True,False] for row in rows)
 verdict="INVALID_TYPED_ORDER_REFERENCE_OR_BAG_CONTROL"
 if (stats["coded_typed_exact_order_reference"]["paired_correct"]==192 and
     stats["role_bag_order_insensitive_shortcut"]["paired_correct"]==0):
  target=stats["frozen_YF10_ordered_role_model"]
  baseline=stats["same_arch_untrained_role_model"]
  if (target["paired_accuracy"]>=.85 and target["accuracy"]>=.90 and
      target["false_positives"]<=19 and
      target["paired_accuracy"]-baseline["paired_accuracy"]>=.15):
   verdict="DEVELOPMENT_FROZEN_ORDERED_ROLE_TRANSFER"
  else:verdict="DEVELOPMENT_NO_FROZEN_ORDERED_ROLE_TRANSFER"
 return {"schema":"yggdrasil.f11.frozen-role-order-generalization-dev.v1",
  "stage":"DEVELOPMENT_ONLY",
  "source_F10_sha":"7c488e0ddcab1dd4ad20d5d7b90285756c945b9c",
  "source_F10_original_sha256":"b3391985417eaa72832610ee9ec69826941a21b06ce94dd0f78ca98f322f22db",
  "frozen_role_logits":FROZEN,
  "seed_bounds":[54600,54624],"new_families":[52,53,54,55],
  "role_renamings":[0,1],"paired_graphs":len(rows),
  "questions":len(rows)*2,"negative_questions":len(rows),
  "native_state_bytes":576,"side_query_role_bytes":4,
  "frozen_pretrained_core_parameters":22,
  "frozen_role_binding_parameters":16,"no_retraining":True,
  "scores":stats,"rows":rows,"registered_verdict":verdict,
  "coded_equality_in_candidate":False,"programmed_four_rounds":True,
  "source_birth_independent":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_llm_calls":0,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
