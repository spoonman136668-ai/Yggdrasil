"""Y-F10: native typed-role binding in exactly 576 resident state bytes.

Learned 4x4 type-compatibility logits gate F6's frozen task-trained entity
matcher/recurrent transitions. No explicit role equality or reachability oracle
is used in candidate inference. Role IDs occupy a 12-float state slice; 120
reserved floats keep the native state budget exactly 576 bytes. Query roles
are separately accounted external inputs. Path recurrence remains four-step
programmed, not dynamically learned halting. DEVELOPMENT ONLY; F3 untouched.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
source=HERE.parent/"20261014-y-f7"/"execute.py"
spec=importlib.util.spec_from_file_location("yf7_preserved",source)
assert spec and spec.loader
f7=importlib.util.module_from_spec(spec);spec.loader.exec_module(f7)
f6=f7.f6;f1=f7.f1
torch.set_num_threads(1)
MOTIFS={
44:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(8,9),(9,10),(10,11),(11,8)),
45:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(8,9),(9,8),(10,11),(11,10)),
46:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(8,9),(9,10),(10,8),(11,12)),
47:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(8,9),(9,10),(10,11),(12,13)),
48:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(0,8),(8,9),(9,10),(10,11)),
49:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(1,8),(8,9),(9,10),(10,8)),
50:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(2,8),(8,9),(9,10),(10,8)),
51:((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,4),(3,8),(8,9),(9,10),(10,11)),
}
TRAIN_FAM=(44,45,46,47)
VALID_FAM=(48,49,50,51)
def typed_exact(edges,types,start,target,request):
 reached={start}
 for required in request:
  reached={b for (a,b),role in zip(edges,types) if a in reached and role==required}
 return target in reached

def make_pair(seed,family,renaming):
 # Fresh graphs; two paths share endpoints. Only one has the correct
 # ordered roles; mutation invalidates it while preserving a distractor path.
 motif=MOTIFS[family]
 perm=lambda x: (x+renaming)%4
 main=tuple((seed*7+family*11+j*3)%4 for j in range(4))
 types=list(main)+[perm((main[j]+1+((seed+family+j)%3))%4) for j in range(4)]
 types += [(seed+family+j*7)%4 for j in range(4)]
 types=[perm(r) for r in types]
 request=tuple(perm(r) for r in main)
 # Explicitly guarantee the alternate 4-hop route does NOT satisfy requested
 # relation order under any renaming.
 if all(types[4+i]==request[i] for i in range(4)):
  raise AssertionError("distractor path accidentally matched typed query")
 ids=[(f1.relabel(a,seed,2),f1.relabel(b,seed,2)) for a,b in motif]
 for i in range(11,0,-1):
  j=(seed*29+family*17+i*31+renaming*5)%(i+1)
  ids[i],ids[j]=ids[j],ids[i];types[i],types[j]=types[j],types[i]
 modified=types.copy()
 main_edge=(f1.relabel(2,seed,2),f1.relabel(3,seed,2))
 pos=ids.index(main_edge)
 # Role change only; no changes to edge identities, order or query.
 modified[pos]=(modified[pos]+1)%4
 query=(f1.relabel(0,seed,2),f1.relabel(4,seed,2))
 assert len(ids)==12 and len(set(ids))==12
 assert typed_exact(ids,types,*query,request)
 assert not typed_exact(ids,modified,*query,request)
 return ids,types,modified,query,request

def dataset(seeds,families,role_renamings):
 pairs=[]
 for seed in seeds:
  for fam in families:
   for rename in role_renamings:
    edges,before,after,query,requested=make_pair(seed,fam,rename)
    pairs.append({"seed":seed,"family":fam,"renaming":rename,"edges":edges,
                  "before_roles":before,"after_roles":after,
                  "query":query,"requested":requested})
 return pairs

def tensors(pairs):
 src=[];types=[];q=[];role_query=[];y=[]
 for row in pairs:
  for roles,label in ((row["before_roles"],1.),(row["after_roles"],0.)):
   src.append(row["edges"]);types.append(roles)
   q.append(row["query"]);role_query.append(row["requested"]);y.append(label)
 return (torch.tensor(src,dtype=torch.int32),
         torch.tensor(types,dtype=torch.int64),
         torch.tensor(q,dtype=torch.int32),
         torch.tensor(role_query,dtype=torch.int64),
         torch.tensor(y,dtype=torch.float32))

class TypedComposer(nn.Module):
 def __init__(self):
  super().__init__()
  self.core=f7.frozen_model()
  for p in self.core.parameters():
   p.requires_grad_(False)
  # All role pairs initially indistinguishable; matching is learned from task.
  self.role_logits=nn.Parameter(torch.zeros(4,4,dtype=torch.float32))
 def encode(self,facts,roles):
  packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
  role_float=roles.to(torch.float32)
  pad=torch.zeros((facts.shape[0],120),dtype=torch.float32)
  state=torch.cat((packed,role_float,pad),dim=1)
  assert state.shape==(facts.shape[0],144) and state.element_size()==4
  return state
 def predict(self,state,query,role_request):
  packed=state[:,:12].contiguous().view(torch.int32).long()
  src=(packed>>16)&65535
  dst=packed&65535
  edge_role=state[:,12:24].long()
  b=state.shape[0]
  # Learn identity transition from frozen native Y-F6 comparator weights.
  link=self.core.similarity(dst[:,:,None],src[:,None,:])
  link=link*f6.f4.MASK.to(link)
  active=self.core.similarity(query[:,0,None],src)
  for hop in range(4):
   requested=role_request[:,hop]
   gate=torch.sigmoid(self.role_logits[edge_role,requested[:,None]])
   if hop:
    message=torch.bmm(active.unsqueeze(1),link).squeeze(1)
    active=torch.sigmoid(self.core.message_gain*message+
        self.core.recurrent_gain*active+self.core.activation_bias)
   active=active*gate
  terminal=self.core.similarity(dst,query[:,1,None])
  return torch.sigmoid(self.core.output_gain*(active*terminal).sum(-1)+
                       self.core.output_bias)

def score(name,pred,truth,pair_count):
 assert len(pred)==pair_count*2
 correct=int((pred==truth).sum())
 fp=int((pred[1::2]).sum())
 pair=int((pred[0::2]&(~pred[1::2])).sum())
 return {"correct":correct,"accuracy":correct/(pair_count*2),
         "false_positives":fp,"negative_false_positive_rate":fp/pair_count,
         "paired_correct":pair,"paired_accuracy":pair/pair_count}

def evaluate():
 started=time.perf_counter()
 torch.manual_seed(1048)
 training=dataset(range(52700,52724),TRAIN_FAM,[0])
 # Only after model training is complete are new validation families materialized.
 tr=tensors(training)
 assert len(training)==96
 model=TypedComposer()
 with torch.no_grad():
  initialized=(model.predict(model.encode(tr[0],tr[1]),tr[2],tr[3])>=.5)
 optimizer=torch.optim.Adam([model.role_logits],lr=.1)
 train_start=time.perf_counter()
 for epoch in range(170):
  optimizer.zero_grad()
  pred=model.predict(model.encode(tr[0],tr[1]),tr[2],tr[3]).clamp(.00001,.99999)
  loss=nn.functional.binary_cross_entropy(pred,tr[4])
  loss.backward()
  nn.utils.clip_grad_norm_([model.role_logits],10.)
  optimizer.step()
 train_ms=round((time.perf_counter()-train_start)*1000)
 validation=dataset(range(53100,53112),VALID_FAM,[0,1])
 val=tensors(validation)
 assert len(validation)==96
 with torch.no_grad():
  encoded=model.encode(val[0],val[1])
  learned=(model.predict(encoded,val[2],val[3])>=.5)
  # Initialize same-capacity model without training, keep frozen core exact.
  fresh=TypedComposer()
  initial=(fresh.predict(fresh.encode(val[0],val[1]),val[2],val[3])>=.5)
  # Role-blind F9 model gets identical untyped graph inputs per positive/negative.
  untyped=f6.model_forward(f7.frozen_model(),val[0],val[2].unsqueeze(1).repeat(1,2,1))[0][:,0]>=.5
  oracle=torch.tensor([typed_exact(x["edges"],roles,*x["query"],x["requested"])
      for x in validation for roles in (x["before_roles"],x["after_roles"])],dtype=torch.bool)
 labels=val[4].bool()
 assert torch.equal(oracle,labels)
 candidates={"trained_typed_role_composer":learned,
   "same_arch_initialized":initial,
   "frozen_F9_untyped_role_blind":untyped,
   "coded_typed_exact_reference":oracle}
 scores={k:score(k,v,labels,len(validation)) for k,v in candidates.items()}
 rows=[]
 for i,row in enumerate(validation):
  rows.append({**row,"truth":[True,False],
     "predictions":{k:v[2*i:2*i+2].tolist() for k,v in candidates.items()}})
 target=scores["trained_typed_role_composer"]
 initialized=scores["same_arch_initialized"]
 verdict="INVALID_TYPED_REFERENCE"
 if scores["coded_typed_exact_reference"]["paired_correct"]==96:
  passed=(target["paired_accuracy"]>=.85 and target["accuracy"]>=.90 and
          target["negative_false_positive_rate"]<=.10 and
          target["paired_accuracy"]-initialized["paired_accuracy"]>=.15)
  verdict=("DEVELOPMENT_LEARNED_ROLE_BINDING_TRANSFER" if passed else
           "DEVELOPMENT_NO_ROLE_BINDING_TRANSFER")
 return {"schema":"yggdrasil.f10.learned-typed-role-composition-dev.v1",
  "stage":"DEVELOPMENT_ONLY",
  "source_F9_sha":"714e10f9df0d036f66e4baea229470ed4fe86f04",
  "train_family_ids":list(TRAIN_FAM),"validation_family_ids":list(VALID_FAM),
  "train_seed_bounds":[52700,52724],"validation_seed_bounds":[53100,53112],
  "training_paired_graphs":len(training),"validation_paired_graphs":len(validation),
  "validation_questions":len(validation)*2,"negative_questions":len(validation),
  "native_state_bytes":576,"resident_roles_float32_bytes":48,
  "query_role_side_input_bytes":4,"query_endpoint_side_input_bytes":4,
  "frozen_untyped_core_params":22,"new_trainable_role_params":16,
  "train_steps":170,"train_wall_ms":train_ms,"train_loss":float(loss.detach()),
  "trained_role_logit_matrix":model.role_logits.detach().tolist(),
  "trained_role_conditioning":True,"role_equality_programmed_in_candidate":False,
  "programmed_four_step_schedule":True,"learned_halting":False,
  "scored_on_role_renamed_validation":True,
  "scores":scores,"rows":rows,"registered_verdict":verdict,
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_llm_calls":0,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
