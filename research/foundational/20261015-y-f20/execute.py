"""Y-F20: infer latent relation descriptors from imperfect contextual cues.
F19's 4-weight descriptor comparison and 22-weight recurrent core are FROZEN
at the exact historical F19 original values. Only a newly trained 15-weight
context sensor decoder is fitted on four KNOWN even-parity role primitives.
Heldout graphs use four ODD-parity primitives; their actual descriptors
generate observations but are never passed to candidate inference.
All cues are synthetic and the sensor error grammar is fixed, not discovered.
"""
from __future__ import annotations
import importlib.util,hashlib,json,time,math
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf19_verified",HERE.parent/"20261015-y-f19"/"execute.py")
assert spec and spec.loader
f19=importlib.util.module_from_spec(spec);spec.loader.exec_module(f19)
f18=f19.f18;f12=f19.f12;f10=f19.f10
torch.set_num_threads(1)
torch.manual_seed(2020)
TRAIN=f19.TRAIN
UNSEEN=f19.UNSEEN
SEEDS=range(81600,81612)
FAMS=f19.FAMS
NOISE=(28,22,58,66)
DROPOUT=(56,45,36,30)

def cues(code,seed,position):
 # Repeated, imperfect contextual evidence; two channels invert attributes.
 # The ID/code are used by SOURCE GENERATION ONLY, not passed to model.
 out=[]
 for bit,truth in enumerate(code):
  stream=[]
  for sensor in range(4):
   base=int(truth) if sensor in (0,3) else 1-int(truth)
   prefix=f"YF20|{seed}|{position}|{bit}|{sensor}|{''.join(map(str,code))}"
   digest=hashlib.sha256(prefix.encode()).digest()
   if digest[0]<DROPOUT[sensor]:
    stream.append(.5)
   else:
    values=[]
    for repeat in range(4):
     b=hashlib.sha256((prefix+"|"+str(repeat)).encode()).digest()[0]
     values.append(float(base if b>=NOISE[sensor] else 1-base))
    stream.append(sum(values)/4)
  out.append(stream)
 return out

class ContextDecoder(nn.Module):
 def __init__(self):
  super().__init__()
  self.w=nn.Parameter(torch.zeros(3,4))
  self.bias=nn.Parameter(torch.zeros(3))
 def forward(self,ctx):
  # ctx shape (...,3,4); predicts a three-attribute role description.
  return torch.sigmoid((ctx*self.w).sum(-1)+self.bias)

def train_decoder():
 examples=[];targets=[]
 for code in TRAIN:
  for seed in range(82700,82900):
   for position in (0,1):
    examples.append(cues(code,seed,position))
    targets.append(code)
 x=torch.tensor(examples,dtype=torch.float32)
 y=torch.tensor(targets,dtype=torch.float32)
 learned=ContextDecoder();untrained=ContextDecoder()
 optimizer=torch.optim.Adam(learned.parameters(),lr=.11)
 for epoch in range(220):
  optimizer.zero_grad()
  p=learned(x)
  loss=nn.functional.binary_cross_entropy(p.clamp(1e-5,1-1e-5),y)
  loss.backward()
  nn.utils.clip_grad_norm_(learned.parameters(),5.)
  optimizer.step()
 return learned,untrained,float(loss.detach())

def frozen_metric():
 metric=f19.LearnedMetric()
 with torch.no_grad():
  metric.w.copy_(torch.tensor([-4.680594444274902]*3,dtype=torch.float32))
  metric.b.copy_(torch.tensor(3.816532850265503,dtype=torch.float32))
 for p in metric.parameters():p.requires_grad_(False)
 return metric

def decode(ctx,mode,learned,untrained):
 if mode=="learned":return learned(ctx)
 if mode=="untrained":return untrained(ctx)
 if mode=="sensor0":return ctx[...,0]
 if mode=="two_sensor":return (ctx[...,0]+(1-ctx[...,1]))/2
 raise ValueError(mode)

def predict(core,metric,decoder,untrained,edges,edge_cues,q,query_cues,
            mode,oracle_edge_codes=None,oracle_query_codes=None):
 b=len(edges)
 facts=torch.tensor(edges,dtype=torch.int32)
 query=torch.tensor(q,dtype=torch.int32)
 if mode=="oracle":
  assert oracle_edge_codes is not None and oracle_query_codes is not None
  rolevec=torch.tensor([[UNSEEN[v] for v in row] for row in oracle_edge_codes],
                       dtype=torch.float32)
  wanted=torch.tensor([[UNSEEN[v] for v in row] for row in oracle_query_codes],
                      dtype=torch.float32)
 else:
  rolevec=decode(torch.tensor(edge_cues,dtype=torch.float32),mode,decoder,untrained)
  wanted=decode(torch.tensor(query_cues,dtype=torch.float32),mode,decoder,untrained)
 packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
 native=torch.cat((packed,rolevec.flatten(1),torch.zeros((b,96))),dim=1)
 assert tuple(native.shape)==(b,144) and native.element_size()==4
 bits=native[:,:12].contiguous().view(torch.int32).long()
 src=(bits>>16)&65535;dst=bits&65535
 roles=native[:,12:48].reshape(b,12,3)
 link=core.similarity(dst[:,:,None],src[:,None,:])*f10.f6.f4.MASK.to(src)
 active=core.similarity(query[:,0,None],src)
 for step in range(wanted.shape[1]):
  gate=metric(roles,wanted[:,step,:])
  if step:
   msg=torch.bmm(active.unsqueeze(1),link).squeeze(1)
   active=torch.sigmoid(core.message_gain*msg+
       core.recurrent_gain*active+core.activation_bias)
  active=active*gate
 terminal=core.similarity(dst,query[:,1,None])
 return torch.sigmoid(core.output_gain*(active*terminal).sum(-1)+core.output_bias)

def evaluate():
 began=time.perf_counter()
 trained,untrained,loss=train_decoder()
 metric=frozen_metric()
 core=f12.f11.model().core
 for p in core.parameters():p.requires_grad_(False)
 rows=[]
 modes=("learned","untrained","sensor0","two_sensor","oracle")
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    edges,roles,q,seq,cut=f18.base(seed,family,depth)
    for shift in (0,1):
     base_roles=[(r+shift)%4 for r in roles]
     requested=tuple((r+shift)%4 for r in seq)
     mutated=base_roles.copy();mutated[cut]=(mutated[cut]+1)%4
     wrong=list(requested);wrong[0],wrong[1]=wrong[1],wrong[0]
     cases=((base_roles,requested),(mutated,requested),(base_roles,tuple(wrong)))
     truth=[True,False,False]
     check=[f10.typed_exact(edges,rs,*q,p) for rs,p in cases]
     if check!=truth:raise AssertionError(("INVALID_YF20_SOURCE",seed,family,depth,shift,check))
     # Contexts are generated independently for edge and query evidence,
     # so matching cannot rely on copying the same observation vectors.
     context_edge=[[cues(UNSEEN[r],seed*19+shift,idx) for idx,r in enumerate(rs)]
                    for rs,p in cases]
     context_request=[[cues(UNSEEN[r],seed*23+shift+10000,idx+150) for idx,r in enumerate(p)]
                      for rs,p in cases]
     guesses={}
     with torch.no_grad():
      for name in modes:
       guesses[name]=(predict(core,metric,trained,untrained,[edges]*3,
           context_edge,[q]*3,context_request,name,
           [rs for rs,p in cases] if name=="oracle" else None,
           [p for rs,p in cases] if name=="oracle" else None)>=.5).tolist()
     rows.append({"seed":seed,"family":family,"depth":depth,"shift":shift,
       "truth":truth,"guesses":guesses,"exact_coded_oracle":check,
       "edge_contexts":context_edge,"query_contexts":context_request})
 assert len(rows)==192
 def score(name):
  correct=sum(sum(a==b for a,b in zip(r["guesses"][name],r["truth"])) for r in rows)
  triple=sum(r["guesses"][name]==r["truth"] for r in rows)
  fp=sum(int(r["guesses"][name][i]) for r in rows for i in (1,2))
  return {"correct":correct,"accuracy":correct/576,"complete_triples":triple,
   "complete_fraction":triple/192,"false_positives":fp,"false_positive_rate":fp/384}
 scores={name:score(name) for name in modes}
 byfam={str(f):{"total":sum(r["family"]==f for r in rows),
  "learned_complete":sum(r["family"]==f and r["guesses"]["learned"]==r["truth"] for r in rows)}
  for f in FAMS}
 valid=(scores["oracle"]["complete_triples"]==192 and
   all(r["exact_coded_oracle"]==r["truth"] for r in rows))
 a=scores["learned"]
 passed=(a["accuracy"]>=.9 and a["complete_fraction"]>=.85 and
   a["false_positive_rate"]<=.1 and
   a["complete_fraction"]-scores["untrained"]["complete_fraction"]>=.15 and
   all(x["learned_complete"]>=.8*x["total"] for x in byfam.values()))
 verdict=("INVALID_CONTEXT_EXACT_DESCRIPTOR_UPPER" if not valid else
   "DEVELOPMENT_CONTEXT_INFERRED_UNSEEN_RELATION_TRANSFER" if passed else
   "DEVELOPMENT_NO_CONTEXT_INFERRED_RELATION_TRANSFER")
 return {"schema":"yggdrasil.f20.context-inferred-unseen-primitive.dev.v1",
  "stage":"DEVELOPMENT_ONLY","F19_source_sha":"8750943012d7555f34da6dfd3db4819963d1b8f0",
  "prior_descriptor_metric_frozen_weights":[-4.680594444274902]*3,
  "prior_descriptor_metric_frozen_bias":3.816532850265503,
  "old_metric_retrained":False,"old_core_retrained":False,
  "learned_context_decoder_weights":trained.w.detach().tolist(),
  "learned_context_decoder_bias":trained.bias.detach().tolist(),
  "learned_context_decoder_params":15,"train_loss":loss,
  "train_known_role_descriptors":[list(x) for x in TRAIN],
  "validation_unseen_role_descriptors":[list(x) for x in UNSEEN],
  "train_only_context_seeds":[82700,82900],
  "validation_context_seeds":[81600,81612],
  "heldout_descriptors_never_supplied_to_candidate":True,
  "context_channel_noise_counts":list(NOISE),
  "context_channel_dropouts":list(DROPOUT),
  "graph_families_reused":list(FAMS),"graphs":192,"questions":576,
  "resident_state_bytes":576,"role_descriptor_state_bytes":144,
  "comparators_include_cheap_context_decoders":True,
  "scores":scores,"by_family":byfam,"rows":rows,
  "registered_verdict":verdict,
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"external_paid_API_calls":0,
  "elapsed_ms":round((time.perf_counter()-began)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
