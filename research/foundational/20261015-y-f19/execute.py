"""Y-F19: four unseen primitive-role descriptors, new learned metric.
The trained F10 4x4 role lookup cannot extend to unknown primitives. Train
a separate 4-weight role-attribute metric on four known EVEN parity 3-bit
descriptions only, freeze and test four ODD parity descriptions. Only the
learned 22-parameter Y-F6 core is inherited. Descriptor bits are SUPPLIED,
not discovered; squared differences are programmed inductive features.
Development evidence, not independent sealed F3 source.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y_f18_source",HERE.parent/"20261015-y-f18"/"execute.py")
assert spec and spec.loader
f18=importlib.util.module_from_spec(spec);spec.loader.exec_module(f18)
f12=f18.f12;f10=f12.f10
torch.set_num_threads(1)
torch.manual_seed(1919)
TRAIN=((0,0,0),(0,1,1),(1,0,1),(1,1,0))
UNSEEN=((0,0,1),(0,1,0),(1,0,0),(1,1,1))
SEEDS=range(78100,78112)
FAMS=(100,101,102,103)
class LearnedMetric(nn.Module):
 def __init__(self):
  super().__init__()
  self.w=nn.Parameter(torch.zeros(3))
  self.b=nn.Parameter(torch.zeros(()))
 def forward(self,edges,desired):
  dist=(edges-desired[:,None,:]).square()
  return torch.sigmoid((dist*self.w).sum(-1)+self.b)
def train():
 pairs=[(a,b) for a in TRAIN for b in TRAIN]
 x=torch.tensor([p[0] for p in pairs],dtype=torch.float32)
 y=torch.tensor([p[1] for p in pairs],dtype=torch.float32)
 truth=torch.tensor([float(a==b) for a,b in pairs])
 learned=LearnedMetric()
 fresh=LearnedMetric()
 optim=torch.optim.Adam(learned.parameters(),lr=.09)
 for epoch in range(240):
  optim.zero_grad()
  prob=learned(x[:,None,:],y).flatten()
  loss=nn.functional.binary_cross_entropy(prob.clamp(1e-6,1-1e-6),truth)
  loss.backward();optim.step()
 return learned,fresh,float(loss.detach())
def predict(core,metric,facts,roles,query,patterns):
 b=len(facts)
 x=torch.tensor(facts,dtype=torch.int32)
 q=torch.tensor(query,dtype=torch.int32)
 req=torch.tensor(patterns,dtype=torch.int64)
 packed=((x[:,:,0]<<16)|x[:,:,1]).to(torch.int32).view(torch.float32)
 attrs=torch.tensor([[UNSEEN[r] for r in row] for row in roles],dtype=torch.float32)
 state=torch.cat((packed,attrs.flatten(1),torch.zeros((b,96))),dim=1)
 assert state.shape==(b,144) and state.element_size()==4
 ids=state[:,:12].contiguous().view(torch.int32).long()
 src=(ids>>16)&65535;dst=ids&65535
 attr=state[:,12:48].reshape(b,12,3)
 link=core.similarity(dst[:,:,None],src[:,None,:])*f10.f6.f4.MASK.to(src)
 active=core.similarity(q[:,0,None],src)
 for step in range(req.shape[1]):
  desired=torch.tensor([UNSEEN[int(r)] for r in req[:,step]],dtype=torch.float32)
  gate=metric(attr,desired)
  if step:
   msg=torch.bmm(active.unsqueeze(1),link).squeeze(1)
   active=torch.sigmoid(core.message_gain*msg+core.recurrent_gain*active+core.activation_bias)
  active=active*gate
 terminal=core.similarity(dst,q[:,1,None])
 return torch.sigmoid(core.output_gain*(active*terminal).sum(-1)+core.output_bias)
def evaluate():
 started=time.perf_counter()
 learned,untrained,loss=train()
 frozen_weights=[float(v) for v in learned.w.detach()]
 frozen_bias=float(learned.b.detach())
 core=f12.f11.model().core
 rows=[]
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    facts,base_roles,query,req,cut=f18.base(seed,family,depth)
    for shift in (0,1):
     roles=[(r+shift)%4 for r in base_roles]
     pattern=tuple((r+shift)%4 for r in req)
     altered=roles.copy();altered[cut]=(altered[cut]+1)%4
     wrong=list(pattern);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=[(roles,pattern),(altered,pattern),(roles,tuple(wrong))]
     truth=[True,False,False]
     exact=[f10.typed_exact(facts,r,*query,p) for r,p in variants]
     if exact!=truth:raise AssertionError(("INVALID_HELDOUT_PRIMITIVE_ORACLE",seed,family,depth,shift,exact))
     with torch.no_grad():
      guess=(predict(core,learned,[facts]*3,[r for r,p in variants],
        [query]*3,[p for r,p in variants])>=.5).tolist()
      ctl=(predict(core,untrained,[facts]*3,[r for r,p in variants],
        [query]*3,[p for r,p in variants])>=.5).tolist()
     rows.append({"seed":seed,"family":family,"depth":depth,"shift":shift,
       "truth":truth,"learned":guess,"untrained":ctl,"exact_oracle":exact,
       "role_bag_shortcut":[True,False,True]})
 assert len(rows)==192
 def scores(field):
  correct=sum(sum(p==t for p,t in zip(r[field],r["truth"])) for r in rows)
  full=sum(r[field]==r["truth"] for r in rows)
  fp=sum(int(r[field][i]) for r in rows for i in (1,2))
  return {"correct":correct,"accuracy":correct/576,"complete_triples":full,
    "complete_rate":full/192,"false_positives":fp,"negative_FPR":fp/384}
 s={key:scores(key) for key in ("learned","untrained","exact_oracle","role_bag_shortcut")}
 by={str(f):{"complete_triples":sum(r["family"]==f and r["learned"]==r["truth"] for r in rows),
   "total_triples":sum(r["family"]==f for r in rows)} for f in FAMS}
 valid=s["exact_oracle"]["complete_triples"]==192 and s["role_bag_shortcut"]["complete_triples"]==0
 learned_ok=(s["learned"]["complete_rate"]>=.85 and s["learned"]["accuracy"]>=.9
   and s["learned"]["negative_FPR"]<=.1
   and s["learned"]["complete_rate"]-s["untrained"]["complete_rate"]>=.15
   and all(v["complete_triples"]>=.8*v["total_triples"] for v in by.values()))
 return {"schema":"yggdrasil.f19.odd-parity-unseen-role-descriptors.dev.v1",
  "stage":"DEVELOPMENT_ONLY","frozen_parent_F18":"8d6ada97f227785599f4d338ec9c00c85414cf72",
  "train_only_known_descriptors":[list(x) for x in TRAIN],
  "heldout_unseen_descriptors":[list(x) for x in UNSEEN],
  "metric_parameter_count":4,"trained_metric_weights":frozen_weights,
  "trained_metric_bias":frozen_bias,"train_only_loss":loss,
  "no_fitting_on_unseen_roles":True,"core_frozen_params":22,
  "native_state_bytes":576,"attribute_descriptor_bytes":144,
  "zero_reserve_bytes":384,"attributes_given_not_discovered":True,
  "squared_difference_features_programmed":True,
  "graph_grammar_families_reused":list(FAMS),"new_seed_bounds":[78100,78112],
  "graph_triples":192,"questions":576,"positives":192,"negatives":384,
  "scores":s,"by_family":by,"rows":rows,
  "registered_verdict":("INVALID_UNSEEN_ROLE_REFERENCE" if not valid else
    "DEVELOPMENT_UNSEEN_ROLE_DESCRIPTOR_BINDING_TRANSFER" if learned_ok else
    "DEVELOPMENT_NO_UNSEEN_ROLE_DESCRIPTOR_BINDING_TRANSFER"),
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_model_calls":0,
  "elapsed_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
