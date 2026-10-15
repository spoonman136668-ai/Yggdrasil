"""Y-F26: learned budgeted observation acquisition for native typed reasoning.

Each unknown descriptor bit can be observed through only TWO of four sensors.
The controller chooses which sensors based on 24 public known-role anchor
observations, before any target observations are revealed. Training uses
known-primitive bits in distinct source identities, then freezes source scores.
The inference decoder accesses exactly the chosen two channels. This is
context-conditioned acquisition, NOT sequential conditioning on the first
target reading and NOT unconstrained information-value learning.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
ROOT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("prior_f20",ROOT.parent/"20261015-y-f20"/"execute.py")
f20=importlib.util.module_from_spec(sp);sp.loader.exec_module(f20)
f18=f20.f18;f10=f20.f10
torch.set_num_threads(1)
torch.manual_seed(2626)
TRAIN_SHIFTS=("identity","flip0","swap01","invert12","mask2")
TEST_SHIFTS=("new_flip03","new_swap12","new_mask01")
SEEDS=range(124000,124006)
FAMS=(100,101,102,103)
TRAIN_SEEDS=range(128000,128040)

def shift(signal,key):
 a,b,c,d=signal
 return {"identity":[a,b,c,d],"flip0":[1-a,b,c,d],
   "swap01":[b,a,c,d],"invert12":[a,1-b,1-c,d],
   "mask2":[a,b,.5,d],
   "new_flip03":[1-a,b,c,1-d],
   "new_swap12":[a,c,b,d],
   "new_mask01":[.5,.5,c,d]}[key]
def transform(words,key):
 return [[shift(bit,key) for bit in token] for token in words]
def known_anchor_stats(seed,key):
 # 4 known TRAIN primitives x two separately observed contexts, 24 labeled
 # bit readings (and 96 individual sensor observations). No test-query
 # descriptor bits or test source readings enter this estimate.
 rows=[[[] for j in range(4)] for bit in range(3)]
 missing=[[0 for j in range(4)] for bit in range(3)]
 for i,code in enumerate(f20.TRAIN):
  for rep in (0,1):
   ctx=f20.cues(code,seed*37+i*101+rep*311,500+i*19+rep)
   for bit in range(3):
    for j,reading in enumerate(shift(ctx[bit],key)):
     rows[bit][j].append((2*reading-1)*(2*code[bit]-1))
     missing[bit][j]+=int(reading==.5)
 corr=[[sum(rows[b][j])/len(rows[b][j]) for j in range(4)] for b in range(3)]
 absent=[[missing[b][j]/8 for j in range(4)] for b in range(3)]
 return corr,absent

class AcquisitionPolicy(nn.Module):
 def __init__(self):
  super().__init__()
  # Shared source-score slopes + four source-specific biases.
  self.w=nn.Parameter(torch.zeros(3))
  self.source_bias=nn.Parameter(torch.zeros(4))
 def logits(self,corr,missing):
  return (self.w[0]*corr.abs()+self.w[1]*corr.square()+
          self.w[2]*missing+self.source_bias)

def train():
 policy=AcquisitionPolicy()
 feats=[];raw=[];labels=[]
 # Disjoint TRAIN-only known primitive roles, TRAIN-only sensor interventions.
 for key in TRAIN_SHIFTS:
  for seed in TRAIN_SEEDS:
   corr,missing=known_anchor_stats(seed+2000,key)
   for code in f20.TRAIN:
    ctx=transform(f20.cues(code,seed*17+13000,333),key)
    for bit in range(3):
     feats.append((corr[bit],missing[bit]))
     raw.append(ctx[bit])
     labels.append(float(code[bit]))
 c=torch.tensor([x[0] for x in feats],dtype=torch.float32)
 miss=torch.tensor([x[1] for x in feats],dtype=torch.float32)
 obs=torch.tensor(raw,dtype=torch.float32)
 truth=torch.tensor(labels,dtype=torch.float32)
 opt=torch.optim.Adam(policy.parameters(),lr=.055)
 for epoch in range(260):
  opt.zero_grad()
  logits=policy.logits(c,miss)
  weights=torch.softmax(logits,dim=-1)
  # Train-time differentiable relaxation observes all training channels.
  # Test-time original enforces top-two actual sensor acquisition.
  votes=(2*obs-1)*torch.sign(c)
  pred=torch.sigmoid(4*(weights*votes).sum(-1))
  loss=nn.functional.binary_cross_entropy(pred.clamp(1e-6,1-1e-6),truth)
  loss.backward();opt.step()
 return policy,float(loss.detach()),len(labels)

def choose(corr,missing,policy,mode):
 idx=[];weights=[]
 for bit in range(3):
  c=torch.tensor(corr[bit],dtype=torch.float32)
  m=torch.tensor(missing[bit],dtype=torch.float32)
  if mode=="learned":
   with torch.no_grad():scores=policy.logits(c,m)
  elif mode=="calibrated_greedy":scores=c.abs()
  elif mode=="fixed_03":scores=torch.tensor([2.,0.,0.,1.])
  elif mode=="fixed_01":scores=torch.tensor([2.,1.,0.,0.])
  else:raise AssertionError("INVALID_ACTIVE_SENSOR_ARM")
  chosen=sorted(torch.topk(scores,2).indices.tolist())
  idx.append(chosen)
  weights.append([float(c[j]) for j in chosen])
 return idx,weights

class TwoObservationDecoder(nn.Module):
 def __init__(self,chosen,coeff):
  super().__init__()
  self.chosen=chosen
  self.coeff=coeff
  self.observation_budget=2
 def forward(self,context):
  # Context tensor is a provider-side bundle. Restrict actual reads to
  # selected indices, never access any unpurchased value.
  result=[]
  for bit in range(3):
   a,b=self.chosen[bit]
   values=context[...,bit,[a,b]]
   w=torch.tensor(self.coeff[bit],dtype=context.dtype)
   signal=((2*values-1)*w).sum(-1)/(w.abs().sum()+.02)
   result.append(torch.sigmoid(5*signal))
  return torch.stack(result,dim=-1)

def evaluate():
 began=time.perf_counter()
 policy,train_loss,n_train=train()
 core=f20.f12.f11.model().core
 metric=f20.frozen_metric()
 for p in core.parameters():p.requires_grad_(False)
 for p in metric.parameters():p.requires_grad_(False)
 rows=[]
 arms=("learned","calibrated_greedy","fixed_03","fixed_01","full_information_upper")
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    edges,roles,query,seq,cut=f18.base(seed,family,depth)
    for role_shift in (0,1):
     original=[(r+role_shift)%4 for r in roles]
     req=tuple((r+role_shift)%4 for r in seq)
     broken=original.copy();broken[cut]=(broken[cut]+1)%4
     wrong=list(req);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((original,req),(broken,req),(original,tuple(wrong)))
     truth=[f10.typed_exact(edges,rs,*query,p) for rs,p in variants]
     if truth!=[True,False,False]:
      raise AssertionError(("BAD_TYPED_SOURCE_YF26",seed,family,depth,role_shift))
     for sensor in TEST_SHIFTS:
      corr,missing=known_anchor_stats(seed+40000,sensor)
      input_edge=[transform([f20.cues(f20.UNSEEN[r],seed*19+role_shift,i)
                   for i,r in enumerate(rs)],sensor) for rs,p in variants]
      input_query=[transform([f20.cues(f20.UNSEEN[r],seed*23+role_shift+10000,i+150)
                    for i,r in enumerate(p)],sensor) for rs,p in variants]
      predictions={};choices={}
      with torch.no_grad():
       for arm in arms:
        if arm=="full_information_upper":
         res=f20.predict(core,metric,None,None,[edges]*3,input_edge,
            [query]*3,input_query,"oracle",
            [rs for rs,p in variants],[p for rs,p in variants])
        else:
         select,coeff=choose(corr,missing,policy,arm)
         decoder=TwoObservationDecoder(select,coeff)
         res=f20.predict(core,metric,decoder,decoder,
              [edges]*3,input_edge,[query]*3,input_query,"learned")
         choices[arm]=select
        predictions[arm]=(res>=.5).tolist()
      rows.append({"seed":seed,"family":family,"depth":depth,"role_shift":role_shift,
         "shift":sensor,"truth":truth,"predictions":predictions,
         "chosen_source_indices":choices,
         "anchor_correlations":corr,"anchor_missingness":missing,
         "sensor_observation_budget_per_primitive_bit":2})
 assert len(rows)==288
 def score(arm,part):
  n=len(part)
  correct=sum(sum(x==y for x,y in zip(r["predictions"][arm],r["truth"])) for r in part)
  fp=sum(bool(r["predictions"][arm][i]) for r in part for i in (1,2))
  fn=sum(not r["predictions"][arm][0] for r in part)
  return {"triples":n,"correct":correct,"accuracy":correct/(3*n),
    "false_positive":fp,"false_negative":fn,
    "complete_triples":sum(r["predictions"][arm]==r["truth"] for r in part)}
 scores={arm:score(arm,rows) for arm in arms}
 by={s:{arm:score(arm,[r for r in rows if r["shift"]==s]) for arm in arms}
     for s in TEST_SHIFTS}
 valid=scores["full_information_upper"]["correct"]==864
 a=scores["learned"]
 cheap=max(scores[x]["accuracy"] for x in ("calibrated_greedy","fixed_03","fixed_01"))
 passed=(a["accuracy"]>=.93 and a["accuracy"]-cheap>=.02 and
   all(by[s]["learned"]["accuracy"]>=.88 for s in TEST_SHIFTS))
 verdict=("INVALID_YF26_TYPED_SOURCE" if not valid else
   "DEVELOPMENT_LEARNED_ACTIVE_OBSERVATION_GAIN" if passed else
   "DEVELOPMENT_ACTIVE_OBSERVATION_NO_QUALIFIED_GAIN")
 return {"schema":"yggdrasil.f26.budgeted-observation-choice.dev.v1",
  "stage":"DEVELOPMENT_ONLY","source_parent_yf25":"3313ebfadc6a3e442e93db36565e93d5af150fe1",
  "training_only_scenarios":list(TRAIN_SHIFTS),
  "train_only_observed_bits":n_train,"trained_policy_parameters":7,
  "trained_policy_weights":policy.w.detach().tolist(),
  "trained_source_biases":policy.source_bias.detach().tolist(),
  "train_loss":train_loss,
  "sensor_choice_before_hidden_observation":True,
  "second_sensor_not_conditioned_on_first_reading":True,
  "provider_full_bundle_not_read_by_decoder":True,
  "known_anchor_truth_provided_for_calibration":True,
  "trained_selector_sees_only_anchor_statistics":True,
  "source_family_motifs_reused":list(FAMS),
  "new_test_seed_bounds":[124000,124006],
  "new_test_sensor_conditions":list(TEST_SHIFTS),
  "graph_states":96,"sensor_condition_triples":len(rows),
  "questions":3*len(rows),"native_state_bytes":576,
  "chosen_sensors_per_role_bit":2,"available_sensors_per_role_bit":4,
  "full_info_upper_knows_true_descriptors":True,
  "scores":scores,"by_shift":by,"rows":rows,
  "registered_verdict":verdict,
  "source_independently_born":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"paid_api_calls":0,
  "elapsed_ms":round((time.perf_counter()-began)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
