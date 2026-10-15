"""Y-F23: train-only learned robust anchor calibration with sparse/poisoned labels.

Evidence includes SUPERVISED known-primitive anchors and supplied sensor
streams, not heldout relation truth or shift identity. Train robust reliability
features (mean+median observed anchor correlation), freeze BEFORE testing on
untrained sensor operations and NEW graph seeds. Track honest negative if
learned complexity does not beat frozen and cheap controls.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("yf22_prior",HERE.parent/"20261015-y-f22"/"execute.py")
prior=importlib.util.module_from_spec(sp);sp.loader.exec_module(prior)
f20=prior.f20;f18=prior.f18;f10=prior.f10
torch.set_num_threads(1)
torch.manual_seed(2323)
TRAIN=prior.TRAIN
TEST=("novel_swap13","novel_rotate_flip2")
COUNTS=(2,6,12)
CONTAM=(0,.25)
SEEDS=range(95700,95703)
FAMS=(100,101,102,103)
Y22_W=[5.8838210105896,5.688408851623535,5.415320873260498,6.171670913696289]
Y22_B=.05826564505696297

def transform(bit,key):
 if key=="novel_swap13":
  a,b,c,d=bit;return [a,d,c,b]
 if key=="novel_rotate_flip2":
  a,b,c,d=bit;return [b,c,1-d,a]
 return prior.change(bit,key)
def transform_rows(rows,key):
 return [[transform(bit,key) for bit in edge] for edge in rows]
def summaries(seed,key,count,contamination):
 correlations=[[] for _ in range(4)]
 for idx in range(count):
  code=f20.TRAIN[(idx+seed)%4]
  observations=f20.cues(code,seed*37+idx*79,idx*11+250)
  for b,(observed,ground_truth) in enumerate(zip(observations,code)):
   known=ground_truth
   # Deterministic corruption of an anchor label. Test task answers remain
   # completely separate. The candidate is NOT given the poison mask.
   if contamination and (idx+b+seed)%4==0:known=1-known
   for j,x in enumerate(transform(observed,key)):
    correlations[j].append((2*x-1)*(2*known-1))
 mean=[sum(z)/len(z) for z in correlations]
 median=[]
 for z in correlations:
  q=sorted(z);i=len(q)//2
  median.append(q[i] if len(q)%2 else (q[i-1]+q[i])/2)
 return mean,median

class LearnedRobust(nn.Module):
 def __init__(self,trainable):
  super().__init__()
  self.average_gain=nn.Parameter(torch.ones(4),requires_grad=trainable)
  self.median_gain=nn.Parameter(torch.zeros(4),requires_grad=trainable)
  self.bias=nn.Parameter(torch.zeros(()),requires_grad=trainable)
  self.mean=torch.ones(4);self.median=torch.zeros(4)
 def bind(self,mean,median):
  self.mean=torch.tensor(mean,dtype=torch.float32)
  self.median=torch.tensor(median,dtype=torch.float32)
 def forward(self,obs):
  reliabilities=self.mean*self.average_gain+self.median*self.median_gain
  return torch.sigmoid(((2*obs-1)*reliabilities).sum(-1)+self.bias)
def train():
 observations=[];targets=[];mean=[];median=[]
 for shift in TRAIN:
  for seed in range(96800,96820):
   for count in COUNTS:
    for contamination in CONTAM:
     mu,med=summaries(seed+2000,shift,count,contamination)
     for i,code in enumerate(f20.TRAIN):
      x=f20.cues(code,seed*41+i*83,i+30)
      observations.append([transform(bit,shift) for bit in x])
      targets.append(code);mean.append(mu);median.append(med)
 x=torch.tensor(observations,dtype=torch.float32)
 y=torch.tensor(targets,dtype=torch.float32)
 m=torch.tensor(mean,dtype=torch.float32)
 med=torch.tensor(median,dtype=torch.float32)
 net=LearnedRobust(True)
 opt=torch.optim.Adam(net.parameters(),lr=.055)
 for _ in range(180):
  opt.zero_grad()
  rel=m*net.average_gain+med*net.median_gain
  logit=((2*x-1)*rel[:,None,:]).sum(-1)+net.bias
  loss=nn.functional.binary_cross_entropy_with_logits(logit,y)
  loss.backward();nn.utils.clip_grad_norm_(net.parameters(),5.);opt.step()
 return net,float(loss.detach()),len(observations)
def frozen_y22():
 m=prior.Calibrated(False)
 with torch.no_grad():
  m.w.copy_(torch.tensor(Y22_W,dtype=torch.float32))
  m.bias.copy_(torch.tensor(Y22_B,dtype=torch.float32))
 return m
def test():
 begin=time.perf_counter()
 learned,loss,train_count=train()
 naive=LearnedRobust(False)
 baseline=frozen_y22()
 frozen=f20.frozen_metric()
 core=f20.f12.f11.model().core
 old_decoder=prior.prior.model()[0] if hasattr(prior,"prior") else prior.f20.ContextDecoder()
 # The earlier Y-F20 exact saved decoder is available as prior's import,
 # via the older Y-F21 module from Y-F22.
 old_decoder=prior.f21.model()[0] if hasattr(prior,"f21") else prior.f20.ContextDecoder()
 rows=[]
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    graph,roles,q,seq,cut=f18.base(seed,family,depth)
    for shift in (0,1):
     original=[(r+shift)%4 for r in roles]
     requested=tuple((r+shift)%4 for r in seq)
     damaged=original.copy();damaged[cut]=(damaged[cut]+1)%4
     wrong=list(requested);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((original,requested),(damaged,requested),(original,tuple(wrong)))
     oracle=[f10.typed_exact(graph,rs,*q,p) for rs,p in variants]
     if oracle!=[True,False,False]:raise AssertionError("YF23_SOURCE_ORACLE_DRIFT")
     contexts=[[f20.cues(f20.UNSEEN[v],seed*19+shift,j) for j,v in enumerate(rs)]
               for rs,p in variants]
     desired=[[f20.cues(f20.UNSEEN[v],seed*23+shift+10000,j+150) for j,v in enumerate(p)]
              for rs,p in variants]
     for key in TEST:
      for n in COUNTS:
       for poison in CONTAM:
        mu,med=summaries(seed+40000,key,n,poison)
        learned.bind(mu,med);naive.bind(mu,med);baseline.bind(mu)
        e=[transform_rows(z,key) for z in contexts]
        targets=[transform_rows(z,key) for z in desired]
        answers={}
        with torch.no_grad():
         for arm in ("learned","fixed_robust","prior_y22","descriptor_oracle"):
          if arm=="descriptor_oracle":
           v=f20.predict(core,frozen,old_decoder,naive,[graph]*3,
             e,[q]*3,targets,"oracle",
             [rs for rs,p in variants],[p for rs,p in variants])
          else:
           decoder={"learned":learned,"fixed_robust":naive,
                    "prior_y22":baseline}[arm]
           v=f20.predict(core,frozen,decoder,naive,[graph]*3,
             e,[q]*3,targets,"learned")
          answers[arm]=(v>=.5).tolist()
        rows.append({"seed":seed,"family":family,"depth":depth,"shift":shift,
          "sensor_shift":key,"anchor_count":n,"poison_fraction":poison,
          "anchor_mean":mu,"anchor_median":med,"answers":answers,
          "truth":oracle})
 assert len(rows)==576
 def score(name,part):
  n=len(part)
  good=sum(sum(a==b for a,b in zip(x["answers"][name],x["truth"])) for x in part)
  fp=sum(x["answers"][name][i] for x in part for i in (1,2))
  fn=sum(not x["answers"][name][0] for x in part)
  return {"groups":n,"correct":good,"accuracy":good/(3*n),
     "false_positive":fp,"false_negative":fn,"fpr":fp/(2*n),"fnr":fn/n}
 arms=("learned","fixed_robust","prior_y22","descriptor_oracle")
 totals={name:score(name,rows) for name in arms}
 by={str(n)+"_"+str(p):{name:score(name,[r for r in rows
      if r["anchor_count"]==n and r["poison_fraction"]==p]) for name in arms}
      for n in COUNTS for p in CONTAM}
 good=(totals["descriptor_oracle"]["correct"]==1728 and
       all(x["truth"]==[True,False,False] for x in rows))
 a=totals["learned"]
 passed=(a["accuracy"]>=.95 and
    a["accuracy"]-max(totals["fixed_robust"]["accuracy"],
                      totals["prior_y22"]["accuracy"])>=.03 and
    all(entry["learned"]["accuracy"]>=.90 and
        entry["learned"]["fpr"]<=.05 and entry["learned"]["fnr"]<=.10
        for entry in by.values()))
 verdict=("INVALID_SPARSE_ANCHOR_REFERENCE" if not good else
    "DEVELOPMENT_LEARNED_SPARSE_POISONED_ANCHOR_TRANSFER" if passed else
    "DEVELOPMENT_SPARSE_POISONED_ANCHOR_ROBUSTNESS_NEGATIVE")
 return {"schema":"yggdrasil.f23.sparse-and-poisoned-anchor-shift.dev.v1",
  "stage":"DEVELOPMENT_ONLY","parent_y22":"13a7bb1c0491ee2a8124cd2dee162670515dd11e",
  "old_gain_source_sha256":"281b69fb3182e2219c16ea7a956de438c0041260ed5044737b7f82d68cd8c304",
  "learned_mean_gains":learned.average_gain.detach().tolist(),
  "learned_median_gains":learned.median_gain.detach().tolist(),
  "learned_bias":float(learned.bias.detach()),
  "new_trainable_parameters":9,"train_loss":loss,"train_only_examples":train_count,
  "known_anchor_labels_supervised":True,"anchor_mean_and_median_programmed":True,
  "test_role_truth_given_to_candidate":False,
  "test_sensor_shift_label_given_to_candidate":False,
  "new_test_shifts":list(TEST),"anchor_counts":list(COUNTS),
  "poisoned_anchor_rates":list(CONTAM),
  "test_seed_bounds":[95700,95703],"motifs_reused":list(FAMS),
  "base_graphs":48,"condition_groups":len(rows),"questions":1728,
  "resident_state_bytes":576,"scores":totals,"by_count_poison":by,
  "rows":rows,"registered_verdict":verdict,
  "source_independently_born":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"paid_api_calls":0,
  "elapsed_ms":round((time.perf_counter()-begin)*1000)}
if __name__=="__main__":print(json.dumps(test(),sort_keys=True,indent=2))
