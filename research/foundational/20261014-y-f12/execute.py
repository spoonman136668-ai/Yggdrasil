"""Y-F12 frozen typed-role variable-depth transfer; DEVELOPMENT ONLY.

Test model weights frozen at Y-F10 through Y-F11 on longer role chains.
Counterfactuals preserve graph and query endpoints: changed necessary edge role,
or a permutation of the query's required role *order* holding its multiset.
Input-controlled recurrence count is not learned halting. No F3 source used.
"""
from __future__ import annotations
import importlib.util, json, time
from collections import Counter
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
parent=HERE.parent/"20261014-y-f11"/"execute.py"
spec=importlib.util.spec_from_file_location("yf11_frozen",parent)
assert spec and spec.loader
f11=importlib.util.module_from_spec(spec);spec.loader.exec_module(f11)
f10=f11.f10
torch.set_num_threads(1)
FAMILY=(56,57,58,59)
DEPTHS=(6,7,8)
SEEDS=range(55700,55708)

def construct(seed,family,k,role_shift):
 assert family in FAMILY and k in DEPTHS
 edges=[(i,i+1) for i in range(k)]
 # Unique simple directed chain 0..k; all extra edges are shortcuts, loops,
 # or disjoint graph noise chosen before classification.
 if family==56: edges.extend([(0,k-2),(k+2,k+3)])
 if family==57: edges.extend([(k-2,2),(k+3,k+4)])
 if family==58: edges.extend([(1,k-1),(k+2,k+3)])
 if family==59: edges.extend([(k,0),(k+2,k+3)])
 j=0
 while len(edges)<12:
  candidate=(k+6+j,k+7+j)
  if candidate not in edges: edges.append(candidate)
  j+=1
 assert len(edges)==12 and len(set(edges))==12
 # Exact role word is encoded as four learnable symbol IDs, not coded match.
 raw=[(seed*7+family*5+i*3)%4 for i in range(k)]
 mapper=lambda x:(x+role_shift)%4
 desired=tuple(mapper(r) for r in raw)
 roles=list(desired)+[mapper((seed+family+3*j)%4) for j in range(12-k)]
 ids=[(f10.f1.relabel(a,seed,2),f10.f1.relabel(b,seed,2)) for a,b in edges]
 altered=roles.copy()
 # Necessary chain edge at k//2 remains but its role changes.
 cut_idx=k//2
 altered[cut_idx]=(altered[cut_idx]+1)%4
 # Swap two positions to preserve multiset, changing order.
 a,b=next(((i,j) for i in range(k) for j in range(i+1,k)
           if desired[i]!=desired[j]),(None,None))
 assert a is not None
 reordered=list(desired)
 reordered[a],reordered[b]=reordered[b],reordered[a]
 # Permute edge order, keeping the role attached to its own edge.
 for i in range(11,0,-1):
  j=(seed*17+family*23+i*31+k*7+role_shift*13)%(i+1)
  ids[i],ids[j]=ids[j],ids[i]
  roles[i],roles[j]=roles[j],roles[i]
  altered[i],altered[j]=altered[j],altered[i]
 src,dst=f10.f1.relabel(0,seed,2),f10.f1.relabel(k,seed,2)
 truth=lambda rolelist,query:f10.typed_exact(ids,rolelist,src,dst,query)
 assert truth(roles,desired) and not truth(altered,desired)
 assert not truth(roles,reordered)
 return {"seed":seed,"family":family,"depth":k,"role_shift":role_shift,
         "edges":ids,"roles":roles,"altered_roles":altered,
         "query":[src,dst],"required":desired,"permuted_required":reordered,
         "truth":[True,False,False]}

def predict_variable(model,edges,roles,query,role_seq):
 # Use the EXACT 576-byte Y-F10 state and frozen model parameters.
 state=model.encode(edges,roles)
 assert state.shape==(edges.shape[0],144) and state.element_size()==4
 packed=state[:,:12].contiguous().view(torch.int32).long()
 src=(packed>>16)&65535
 dst=packed&65535
 edge_role=state[:,12:24].long()
 link=model.core.similarity(dst[:,:,None],src[:,None,:])
 link=link*f10.f6.f4.MASK.to(link)
 active=model.core.similarity(query[:,0,None],src)
 for hop in range(role_seq.shape[1]):
  want=role_seq[:,hop]
  gate=torch.sigmoid(model.role_logits[edge_role,want[:,None]])
  if hop:
   message=torch.bmm(active.unsqueeze(1),link).squeeze(1)
   active=torch.sigmoid(model.core.message_gain*message+
       model.core.recurrent_gain*active+model.core.activation_bias)
  active=active*gate
 terminal=model.core.similarity(dst,query[:,1,None])
 return torch.sigmoid(model.core.output_gain*(active*terminal).sum(-1)+
                      model.core.output_bias)

def evaluate():
 start=time.perf_counter()
 cases=[construct(seed,fam,k,shift)
        for seed in SEEDS for fam in FAMILY for k in DEPTHS for shift in (0,1)]
 assert len(cases)==192
 model=f11.model()
 scores={k:{"correct":0,"paired_triples":0,"false_positives":0}
         for k in ("frozen_variable_typed_composition","fixed_four_round_typed_control",
                   "untyped_graph_reachability","exact_typed_oracle",
                   "bag_of_roles_shortcut")}
 rows=[]
 with torch.no_grad():
  for case in cases:
   fact=torch.tensor([case["edges"]]*3,dtype=torch.int32)
   roles=torch.tensor([case["roles"],case["altered_roles"],case["roles"]],
                      dtype=torch.int64)
   query=torch.tensor([case["query"]]*3,dtype=torch.int32)
   patterns=[case["required"],case["required"],case["permuted_required"]]
   k=case["depth"]
   req=torch.tensor(patterns,dtype=torch.int64)
   predicted=(predict_variable(model,fact,roles,query,req)>=.5).tolist()
   # Invalid interface: legacy exactly four-step computation is incompatible
   # with novel six-to-eight symbol role queries. Baseline is role-blind.
   control=f11.f7.f6.model_forward(f11.f7.frozen_model(),fact,
                  query.unsqueeze(1).repeat(1,2,1))[0][:,0]>=.5
   graphblind=[bool(q) for q in control]
   typed=[f10.typed_exact(case["edges"],r,*case["query"],p)
          for r,p in zip(roles.tolist(),patterns)]
   # Coded order-INSENSITIVE comparator on original 0..k chain roles.
   chain_ids=[(f10.f1.relabel(i,case["seed"],2),f10.f1.relabel(i+1,case["seed"],2))
              for i in range(k)]
   chain_ix=[case["edges"].index(edge) for edge in chain_ids]
   actual_roles=[case["roles"][ix] for ix in chain_ix]
   changed_roles=[case["altered_roles"][ix] for ix in chain_ix]
   bag=[Counter(actual_roles)==Counter(case["required"]),
        Counter(changed_roles)==Counter(case["required"]),
        Counter(actual_roles)==Counter(case["permuted_required"])]
   choices={
      "frozen_variable_typed_composition":predicted,
      "fixed_four_round_typed_control":graphblind,
      "untyped_graph_reachability":graphblind,
      "exact_typed_oracle":typed,
      "bag_of_roles_shortcut":bag}
   row={**case,"predictions":choices}
   rows.append(row)
   for name,p in choices.items():
    counts=scores[name]
    counts["correct"]+=sum(a==b for a,b in zip(p,case["truth"]))
    counts["paired_triples"]+=p==case["truth"]
    counts["false_positives"]+=int(p[1])+int(p[2])
 for s in scores.values():
  s["accuracy"]=s["correct"]/(3*len(cases))
  s["triple_rate"]=s["paired_triples"]/len(cases)
  s["negative_fp_rate"]=s["false_positives"]/(2*len(cases))
 verdict="INVALID_TYPED_REFERENCE_OR_BAG_SHORTCUT"
 exact=scores["exact_typed_oracle"]
 shortcut=scores["bag_of_roles_shortcut"]
 if exact["paired_triples"]==192 and shortcut["paired_triples"]==0:
  c=scores["frozen_variable_typed_composition"]
  verdict=("DEVELOPMENT_FROZEN_TYPED_VARIABLE_DEPTH_TRANSFER"
   if c["triple_rate"]>=.85 and c["accuracy"]>=.9 and c["negative_fp_rate"]<=.10
   else "DEVELOPMENT_NO_FROZEN_TYPED_VARIABLE_DEPTH_TRANSFER")
 return {"schema":"yggdrasil.f12.frozen-typed-variable-depth.dev.v1",
  "stage":"DEVELOPMENT_ONLY","frozen_F11_sha":"9b7de66aef38d3ee3ea47f1d088417e8065f88d3",
  "new_families":list(FAMILY),"new_seeds":[55700,55708],"depths":list(DEPTHS),
  "paired_graphs":len(cases),"questions":3*len(cases),
  "negative_questions":2*len(cases),
  "resident_state_bytes":576,"query_role_side_bytes_per_symbol":1,
  "frozen_role_params":16,"frozen_core_params":22,"model_retrained":False,
  "programmed_query_length_loop":True,"learned_halting":False,
  "independently_witnessed_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_model_calls":0,
  "scores":scores,"rows":rows,"registered_verdict":verdict,
  "elapsed_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
