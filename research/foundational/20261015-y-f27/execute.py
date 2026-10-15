"""Y-F27 -- choose the SECOND sensor after observing the FIRST.

Seven-parameter train-only policy ranks second sensor conditional on the
first hidden-target reading and calibrated known-anchor estimates. It uses
no unseen target labels or unpurchased second-channel readings in decisions.
The training-time differentiable relaxation may inspect all TRAIN source
measurements. DEVELOPMENT-ONLY synthetic source, native 576B reasoning.
"""
from __future__ import annotations
import importlib.util,json,time,math
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("y_f26_prior",HERE.parent/"20261015-y-f26"/"execute.py")
p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
f20=p.f20;f18=p.f18;f10=p.f10
torch.set_num_threads(1)
torch.manual_seed(2727)
TRAIN_SHIFTS=p.TRAIN_SHIFTS
TEST_SHIFTS=("unseen_invert02","unseen_swap03","unseen_drop12")
FAMS=(100,101,102,103)
SEEDS=range(130200,130206)
def shifted(bit,key):
 a,b,c,d=bit
 if key=="unseen_invert02":return [1-a,b,1-c,d]
 if key=="unseen_swap03":return [d,b,c,a]
 if key=="unseen_drop12":return [a,.5,.5,d]
 return p.shift(bit,key)
def anchors(seed,key):
 # Independent labeled known-primitive observations. Correctness estimates
 # are trained on known source only, not the hidden test-role descriptors.
 corr=[[] for _ in range(3)]
 miss=[[] for _ in range(3)]
 for bit in range(3):
  corr[bit]=[0.]*4
  miss[bit]=[0.]*4
 for i,code in enumerate(f20.TRAIN):
  for repeat in range(3):
   obs=f20.cues(code,seed*31+i*67+repeat*117,i+repeat*500)
   for b,truth in enumerate(code):
    for j,x in enumerate(shifted(obs[b],key)):
     corr[b][j]+=(2*x-1)*(2*truth-1)
     miss[b][j]+=int(x==.5)
 return [[v/12 for v in c] for c in corr],[[v/12 for v in c] for c in miss]
def first_choice(corr,missing,bit):
 # Fixed strong calibrated initial source selection; same first sensor
 # in all learned, greedy and fixed-first sequential comparator arms.
 return max(range(4),key=lambda j:(abs(corr[bit][j])-.1*missing[bit][j],-j))
def bit_confidence(v,c):
 return (2*v-1)*(1 if c>=0 else -1)
class LearnSecond(nn.Module):
 def __init__(self):
  super().__init__()
  self.weights=nn.Parameter(torch.zeros(5))
  self.source_bias=nn.Parameter(torch.zeros(4))
 def features(self,corr,missing,first_read,first_c,bit,second):
  # No second target value is accessed here. Features consist ONLY of
  # known-anchor reliability and already observed first target value.
  strength=abs(corr[bit][second])
  uncertainty=1-abs(2*first_read-1)
  sign=bit_confidence(first_read,first_c)
  return [strength,missing[bit][second],strength*uncertainty,
          strength*sign,1. if second==0 else 0.]
 def scores(self,corr,missing,bit,first,first_read):
  vals=[]
  for j in range(4):
   if j==first:
    vals.append(None);continue
   x=self.features(corr,missing,first_read,corr[bit][first],bit,j)
   vals.append(sum(self.weights[k]*x[k] for k in range(5))+self.source_bias[j])
  return vals
def prediction(first_value,second_value,cfirst,csecond):
 votes=bit_confidence(first_value,cfirst)*abs(cfirst)+bit_confidence(second_value,csecond)*abs(csecond)
 return torch.sigmoid(torch.as_tensor(5*votes/(abs(cfirst)+abs(csecond)+.02)))
def train():
 m=LearnSecond()
 data=[]
 for shift in TRAIN_SHIFTS:
  for seed in range(136000,136035):
   corr,missing=anchors(seed+10000,shift)
   for role in f20.TRAIN:
    obs=[shifted(bit,shift) for bit in f20.cues(role,seed*23+1000,seed%11+100)]
    for bit in range(3):
     first=first_choice(corr,missing,bit)
     options=[j for j in range(4) if j!=first]
     data.append((corr,missing,bit,first,obs[bit][first],
                  [obs[bit][j] for j in options],options,role[bit]))
 opt=torch.optim.Adam(m.parameters(),lr=.06)
 for epoch in range(180):
  opt.zero_grad()
  losses=[]
  for corr,missing,bit,first,firstval,secondvals,options,truth in data:
   candidate_logits=m.scores(corr,missing,bit,first,firstval)
   logits=torch.stack([candidate_logits[j] for j in options])
   mix=torch.softmax(logits,dim=0)
   probabilities=torch.stack([prediction(firstval,secondvals[i],
       corr[bit][first],corr[bit][j]) for i,j in enumerate(options)])
   prob=(mix*probabilities).sum().clamp(1e-6,1-1e-6)
   target=torch.tensor(float(truth))
   losses.append(nn.functional.binary_cross_entropy(prob,target))
  loss=torch.stack(losses).mean()
  loss.backward()
  nn.utils.clip_grad_norm_(m.parameters(),5.)
  opt.step()
 return m,float(loss.detach()),len(data)
class SequentialDecoder(nn.Module):
 def __init__(self,corr,missing,policy,mode):
  super().__init__()
  self.corr=corr;self.missing=missing;self.policy=policy
  self.mode=mode
  self.count=0
  self.transitions=[]
 def forward(self,context):
  # Native inference with individual first observation before second action.
  # Does not inspect the other two, unpurchased, target sensor values.
  result=[]
  for bit in range(3):
   first=first_choice(self.corr,self.missing,bit)
   initial=context[...,bit,first]
   flattened=initial.flatten().tolist()
   indexes=[]
   for observed in flattened:
    others=[j for j in range(4) if j!=first]
    if self.mode=="learned":
     with torch.no_grad():
      values=self.policy.scores(self.corr,self.missing,bit,first,observed)
      second=max(others,key=lambda j:(float(values[j]),-j))
    elif self.mode=="conditional_greedy":
     second=max(others,key=lambda j:(abs(self.corr[bit][j])*
        (1+.12*int(abs(2*observed-1)<.5))-.1*self.missing[bit][j],-j))
    elif self.mode=="static_greedy":
     second=max(others,key=lambda j:(abs(self.corr[bit][j])-.1*self.missing[bit][j],-j))
    elif self.mode=="fixed_03":
     second=3 if first!=3 else 0
    else:raise AssertionError("unrecognized mode")
    indexes.append(second)
    if len(self.transitions)<40:self.transitions.append([bit,first,second,float(observed)])
   picks=torch.tensor(indexes,dtype=torch.long).reshape(initial.shape)
   purchased=context[...,bit,:].gather(-1,picks.unsqueeze(-1)).squeeze(-1)
   a=self.corr[bit][first]
   b=torch.tensor([self.corr[bit][j] for j in indexes]).reshape(initial.shape)
   # Important: second sensor value is used only AFTER its action chosen.
   values=(2*initial-1)*a+(2*purchased-1)*b
   outcome=torch.sigmoid(5*values/(abs(a)+b.abs()+.02))
   result.append(outcome)
   self.count+=2*len(indexes)
  return torch.stack(result,dim=-1)
def evaluate():
 start=time.perf_counter()
 model,loss,train_records=train()
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 rows=[]
 methods=("learned","conditional_greedy","static_greedy","fixed_03","descriptor_oracle")
 for seed in SEEDS:
  for fam in FAMS:
   for depth in (7,8):
    graph,roles,q,req,cut=f18.base(seed,fam,depth)
    for shift in (0,1):
     tags=[(v+shift)%4 for v in roles]
     wanted=tuple((v+shift)%4 for v in req)
     changed=tags.copy();changed[cut]=(changed[cut]+1)%4
     wrong=list(wanted);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((tags,wanted),(changed,wanted),(tags,tuple(wrong)))
     truth=[f10.typed_exact(graph,r,*q,s) for r,s in variants]
     if truth!=[True,False,False]:raise AssertionError("INVALID_NEW_SOURCE")
     for sensor in TEST_SHIFTS:
      corr,missing=anchors(seed+50000,sensor)
      e=[[shifted(bit,sensor) for role in rs
          for bit in f20.cues(f20.UNSEEN[role],seed*19+shift,rs.index(role))] for rs,req in ()]
      edges=[[ [shifted(bit,sensor) for bit in f20.cues(f20.UNSEEN[v],seed*19+shift,i)]
        for i,v in enumerate(rs)] for rs,rq in variants]
      queries=[[ [shifted(bit,sensor) for bit in f20.cues(f20.UNSEEN[v],
          seed*23+shift+10000,i+150)] for i,v in enumerate(rq)] for rs,rq in variants]
      outputs={};observation_counts={};examples={}
      with torch.no_grad():
       for arm in methods:
        if arm=="descriptor_oracle":
         val=f20.predict(core,metric,None,None,[graph]*3,edges,
          [q]*3,queries,"oracle",
          [rs for rs,rq in variants],[rq for rs,rq in variants])
        else:
         decoder=SequentialDecoder(corr,missing,model,arm)
         val=f20.predict(core,metric,decoder,decoder,[graph]*3,
           edges,[q]*3,queries,"learned")
         observation_counts[arm]=decoder.count
         examples[arm]=decoder.transitions[:8]
        outputs[arm]=(val>=.5).tolist()
      rows.append({"seed":seed,"family":fam,"depth":depth,"role_shift":shift,
       "sensor_shift":sensor,"truth":truth,"answers":outputs,
       "observation_counts":observation_counts,"action_samples":examples,
       "two_sensors_per_descriptor_bit":True})
 assert len(rows)==288
 def score(name,records):
  n=len(records)
  good=sum(sum(a==b for a,b in zip(r["answers"][name],r["truth"])) for r in records)
  fp=sum(r["answers"][name][i] for r in records for i in (1,2))
  fn=sum(not r["answers"][name][0] for r in records)
  return {"triples":n,"correct":good,"accuracy":good/(3*n),
    "false_positives":fp,"false_negatives":fn,
    "complete":sum(r["answers"][name]==r["truth"] for r in records)}
 scores={name:score(name,rows) for name in methods}
 by={key:{name:score(name,[r for r in rows if r["sensor_shift"]==key])
      for name in methods} for key in TEST_SHIFTS}
 a=scores["learned"]
 control=max(scores[name]["accuracy"] for name in
   ("conditional_greedy","static_greedy","fixed_03"))
 valid=scores["descriptor_oracle"]["correct"]==864
 passed=(a["accuracy"]>=.93 and a["accuracy"]-control>=.02 and
   all(by[c]["learned"]["accuracy"]>=.88 for c in TEST_SHIFTS))
 verdict=("INVALID_YF27_SOURCE_REFERENCE" if not valid else
   "DEVELOPMENT_LEARNED_SEQUENTIAL_OBSERVATION_GAIN" if passed else
   "DEVELOPMENT_SEQUENTIAL_OBSERVATION_NO_QUALIFIED_GAIN")
 return {"schema":"yggdrasil.f27.sequential-budgeted-observation.dev.v1",
  "stage":"DEVELOPMENT_ONLY","parent_yf26":"7315d9c87f028d7ff33b7d53e0b799caf727cf2c",
  "train_only_shifts":list(TRAIN_SHIFTS),"new_shifts":list(TEST_SHIFTS),
  "train_only_target_bits":train_records,"learned_policy_params":9,
  "trained_policy_weights":model.weights.detach().tolist(),
  "trained_source_bias":model.source_bias.detach().tolist(),
  "training_loss":loss,"actual_first_observation_before_second_decision":True,
  "policy_second_action_uses_first_target_reading":True,
  "unobserved_channels_not_read_in_action_decision":True,
  "training_relaxation_uses_all_training_sensors":True,
  "first_source_selected_by_programmed_calibration":True,
  "known_anchor_labels_available":True,
  "two_sensors_per_target_bit":True,"source_sensor_count":4,
  "graph_states":96,"groups":len(rows),"questions":len(rows)*3,
  "new_seed_bounds":[130200,130206],"reused_families":list(FAMS),
  "native_state_bytes":576,"scores":scores,"by_shift":by,
  "rows":rows,"registered_verdict":verdict,
  "independent_source_birth":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"paid_api_calls":0,
  "elapsed_ms":round((time.perf_counter()-start)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
