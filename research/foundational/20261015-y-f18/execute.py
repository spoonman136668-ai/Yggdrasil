"""Y-F18: frozen compositional role binding under all 24 symbol bijections.

New author-authored development cohorts, structurally distinct motifs.
Every graph/role query is relabeled by the ENTIRE symmetric group S4, not
merely a shift. Frozen Y-F10 learnable role binding / fixed 576B state and
variable-depth learned core remain unchanged. No F3 sealed first-use claim.
"""
from __future__ import annotations
import importlib.util,itertools,time,json
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf12_fixed",HERE.parent/"20261014-y-f12"/"execute.py")
assert spec and spec.loader
f12=importlib.util.module_from_spec(spec);spec.loader.exec_module(f12)
torch.set_num_threads(1)
FAMS=(100,101,102,103)
SEEDS=range(76200,76203)
DEPTHS=(7,8)
PERM=tuple(itertools.permutations(range(4)))
assert len(PERM)==24

def base(seed,fam,k):
 edges=[(i,i+1) for i in range(k)]
 variants={
 100:[(0,k-2),(k+8,k+9)],
 101:[(3,1),(k+7,k+8)],
 102:[(2,k-1),(k+6,k+7)],
 103:[(k,0),(k+5,k+6)]}
 edges+=variants[fam]
 n=0
 while len(edges)<12:
  edges.append((k+20+n,k+21+n));n+=1
 assert len(edges)==12 and len(set(edges))==12
 raw=[(seed*7+fam*5+3*i)%4 for i in range(12)]
 target=tuple(raw[:k])
 ids=[(f12.f10.f1.relabel(a,seed,2),f12.f10.f1.relabel(b,seed,2))
      for a,b in edges]
 for i in range(11,0,-1):
  j=(seed*13+fam*19+k*23+i*29)%(i+1)
  ids[i],ids[j]=ids[j],ids[i];raw[i],raw[j]=raw[j],raw[i]
 chain=[(f12.f10.f1.relabel(i,seed,2),f12.f10.f1.relabel(i+1,seed,2))
        for i in range(k)]
 chain_indices=[ids.index(edge) for edge in chain]
 desired=tuple(raw[i] for i in chain_indices)
 assert desired==target
 assert desired[0]!=desired[1]
 damaged_idx=chain_indices[k//2]
 q=(f12.f10.f1.relabel(0,seed,2),f12.f10.f1.relabel(k,seed,2))
 return ids,raw,q,desired,damaged_idx

def evaluate():
 start=time.perf_counter()
 m=f12.f11.model()
 rows=[]
 for seed in SEEDS:
  for fam in FAMS:
   for k in DEPTHS:
    edges,roles,q,seq,cut=base(seed,fam,k)
    for pi,perm in enumerate(PERM):
     wanted=tuple(perm[x] for x in seq)
     tags=[perm[x] for x in roles]
     changed=tags.copy()
     changed[cut]=(changed[cut]+1)%4
     wrong=list(wanted)
     wrong[0],wrong[1]=wrong[1],wrong[0]
     conditions=((tags,wanted,True),(changed,wanted,False),
                 (tags,tuple(wrong),False))
     correct=[f12.f10.typed_exact(edges,tag,*q,p)
              for tag,p,_ in conditions]
     if correct!=[True,False,False]:
      raise AssertionError(("INVALID_TYPED_ORACLE",seed,fam,k,pi,correct))
     fact=torch.tensor([edges]*3,dtype=torch.int32)
     tag=torch.tensor([x[0] for x in conditions],dtype=torch.int64)
     target=torch.tensor([x[1] for x in conditions],dtype=torch.int64)
     query=torch.tensor([q]*3,dtype=torch.int32)
     with torch.no_grad():
      score=f12.predict_variable(m,fact,tag,query,target).tolist()
     prediction=[s>=.5 for s in score]
     rolebag=[True,False,True]
     rows.append({"seed":seed,"family":fam,"depth":k,"permutation_index":pi,
       "permutation":list(perm),"truth":[True,False,False],
       "frozen_prediction":prediction,"frozen_scores":score,
       "bag_shortcut":rolebag,"coded_exact":correct,
       "label_rule":"all_24_global_bijections_symmetric_role_alphabet"})
 assert len(rows)==576
 total=sum(sum(p==v for p,v in zip(r["frozen_prediction"],r["truth"])) for r in rows)
 triplets=sum(r["frozen_prediction"]==r["truth"] for r in rows)
 fp=sum(int(r["frozen_prediction"][1])+int(r["frozen_prediction"][2]) for r in rows)
 perm_groups={}
 for p in range(24):
  subset=[r for r in rows if r["permutation_index"]==p]
  perm_groups[str(p)]={"graphs":len(subset),
    "complete_triples":sum(r["frozen_prediction"]==r["truth"] for r in subset),
    "correct_questions":sum(sum(a==b for a,b in zip(r["frozen_prediction"],r["truth"]))
                            for r in subset)}
 max_disagreement=sum(1 for key in {(r["seed"],r["family"],r["depth"]) for r in rows}
  if len({tuple(r["frozen_prediction"]) for r in rows if
     (r["seed"],r["family"],r["depth"])==key})>1)
 bag_triplets=sum(r["bag_shortcut"]==r["truth"] for r in rows)
 oracle_triplets=sum(r["coded_exact"]==r["truth"] for r in rows)
 valid=oracle_triplets==576 and bag_triplets==0
 passed=(triplets>=int(.95*len(rows)) and fp<=int(.05*(2*len(rows))) and
  max_disagreement==0 and
  all(x["complete_triples"]>=int(.95*x["graphs"]) for x in perm_groups.values()))
 return {"schema":"yggdrasil.f18.frozen-full-S4-role-ontology-transfer.v1",
  "stage":"DEVELOPMENT_ONLY","source_parent_F17":"a1ebf0ba4ef20cf93758cbb3cb25005f2d7c4e2b",
  "frozen_model_sha":"fbe0269a4b32c42c497aa22b856720d39733c521",
  "model_retrained":False,"learned_role_params":16,"learned_core_params":22,
  "typed_native_state_bytes":576,"query_role_bytes_per_symbol":1,
  "programmed_explicit_query_depth":True,"learned_automatic_halting":False,
  "new_families":list(FAMS),"new_seeds":[76200,76203],"depths":list(DEPTHS),
  "role_bijections":len(PERM),"base_graphs":len(SEEDS)*len(FAMS)*len(DEPTHS),
  "triples":len(rows),"questions":len(rows)*3,"negative_questions":len(rows)*2,
  "scores":{"frozen_correct":total,"frozen_accuracy":total/(len(rows)*3),
    "frozen_complete_triples":triplets,"frozen_complete_rate":triplets/len(rows),
    "frozen_false_positives":fp,"permutation_prediction_disagreement_groups":max_disagreement,
    "exact_oracle_complete_triples":oracle_triplets,"bag_control_complete_triples":bag_triplets},
  "by_permutation":perm_groups,"rows":rows,
  "registered_verdict":("INVALID_S4_ORACLE_OR_SHORTCUT" if not valid else
    "DEVELOPMENT_FROZEN_S4_ROLE_EQUIVARIANCE_TRANSFER" if passed else
    "DEVELOPMENT_NO_FROZEN_S4_ROLE_EQUIVARIANCE_TRANSFER"),
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_model_calls":0,
  "elapsed_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
