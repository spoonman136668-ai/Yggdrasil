"""Y-F22: learn sensor gains from known-anchor calibration, test unseen shifts.

Uses 4 known training-only role descriptions as calibration anchors. Heldout
relation descriptions, test intervention identity and test labels never reach
model inference. Anchor correlation is an explicitly programmed feature, not
automatically discovered provenance. Development only; sealed F3 untouched.
"""
import importlib.util,json,time
from pathlib import Path
import torch
from torch import nn
ROOT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("prior",ROOT.parent/"20261015-y-f21"/"execute.py")
prior=importlib.util.module_from_spec(sp);sp.loader.exec_module(prior)
f20=prior.f20;f18=prior.f18;f10=prior.f10
torch.set_num_threads(1)
torch.manual_seed(2222)
TRAIN=("identity","flip0","swap01","flip12","swap03")
TEST=("flip03","flipall","rotateflip","swap02","mask0")
SEEDS=range(91700,91706)
FAMS=(100,101,102,103)
def change(bit,key):
 a,b,c,d=bit
 return {"identity":[a,b,c,d],"flip0":[1-a,b,c,d],
   "swap01":[b,a,c,d],"flip12":[a,1-b,1-c,d],
   "swap03":[d,b,c,a],"flip03":[1-a,b,c,1-d],
   "flipall":[1-a,1-b,1-c,1-d],"rotateflip":[c,d,1-a,b],
   "swap02":[c,b,a,d],"mask0":[.5,b,c,d]}[key]
def change_rows(rows,key):
 return [[change(bits,key) for bits in edge] for edge in rows]
def anchors(seed,key):
 # 4 known primitive codes x 4 independent contextual readings, 48
 # labeled training-anchor bits; no heldout task answers are used.
 values=[0.]*4
 for i,code in enumerate(f20.TRAIN):
  for rep in range(4):
   obs=f20.cues(code,seed*31+i*19+rep*23,rep+i*50)
   for bits,truth in zip(obs,code):
    for j,a in enumerate(change(bits,key)):
     values[j]+=(2*a-1)*(2*truth-1)
 return [x/48 for x in values]
class Calibrated(nn.Module):
 def __init__(self,trainable):
  super().__init__()
  self.w=nn.Parameter(torch.ones(4),requires_grad=trainable)
  self.bias=nn.Parameter(torch.zeros(()),requires_grad=trainable)
  self.coeff=torch.ones(4)
 def bind(self,c):self.coeff=torch.tensor(c,dtype=torch.float32)
 def forward(self,obs):
  return torch.sigmoid(((2*obs-1)*self.coeff*self.w).sum(-1)+self.bias)
def fit():
 obs=[];truth=[];coeff=[]
 for key in TRAIN:
  for seed in range(92400,92450):
   c=anchors(seed+2000,key)
   for code in f20.TRAIN:
    raw=f20.cues(code,seed*23,7)
    obs.append([change(bits,key) for bits in raw])
    truth.append(code);coeff.append(c)
 x=torch.tensor(obs,dtype=torch.float32)
 y=torch.tensor(truth,dtype=torch.float32)
 a=torch.tensor(coeff,dtype=torch.float32)
 m=Calibrated(True);opt=torch.optim.Adam(m.parameters(),lr=.09)
 for _ in range(180):
  opt.zero_grad()
  logits=((2*x-1)*a[:,None,:]*m.w).sum(-1)+m.bias
  loss=nn.functional.binary_cross_entropy_with_logits(logits,y)
  loss.backward();opt.step()
 return m,float(loss.detach()),len(obs)
def run():
 started=time.perf_counter()
 learned,loss,train_count=fit()
 fixed=Calibrated(False)
 frozen=prior.model()[0]
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 for p in core.parameters():p.requires_grad_(False)
 rows=[]
 for seed in SEEDS:
  for fam in FAMS:
   for depth in (7,8):
    edges,roles,q,seq,cut=f18.base(seed,fam,depth)
    for shift in (0,1):
     tags=[(v+shift)%4 for v in roles]
     request=tuple((v+shift)%4 for v in seq)
     mut=tags.copy();mut[cut]=(mut[cut]+1)%4
     wrong=list(request);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((tags,request),(mut,request),(tags,tuple(wrong)))
     oracle=[f10.typed_exact(edges,r,*q,t) for r,t in variants]
     if oracle!=[True,False,False]:raise AssertionError("INVALID_TYPED_ORACLE")
     e=[[f20.cues(f20.UNSEEN[v],seed*19+shift,i) for i,v in enumerate(r)]
        for r,t in variants]
     targets=[[f20.cues(f20.UNSEEN[v],seed*23+shift+10000,i+150)
               for i,v in enumerate(t)] for r,t in variants]
     for key in TEST:
      c=anchors(seed+40000,key)
      learned.bind(c);fixed.bind(c)
      ee=[change_rows(v,key) for v in e]
      tt=[change_rows(v,key) for v in targets]
      answers={}
      with torch.no_grad():
       for arm in ("adaptive","anchor_heuristic","frozen_f20","descriptor_oracle"):
        if arm=="descriptor_oracle":
         score=f20.predict(core,metric,frozen,fixed,[edges]*3,
            ee,[q]*3,tt,"oracle",[r for r,t in variants],[t for r,t in variants])
        else:
         module={"adaptive":learned,"anchor_heuristic":fixed,
                 "frozen_f20":frozen}[arm]
         score=f20.predict(core,metric,module,fixed,[edges]*3,ee,[q]*3,tt,"learned")
        answers[arm]=(score>=.5).tolist()
      rows.append({"seed":seed,"family":fam,"depth":depth,"shift":shift,
        "sensor_condition":key,"anchor":c,"truth":oracle,"answers":answers})
 assert len(rows)==480
 modes=("adaptive","anchor_heuristic","frozen_f20","descriptor_oracle")
 def score(mode,rs):
  n=len(rs)
  c=sum(sum(x==y for x,y in zip(r["answers"][mode],r["truth"])) for r in rs)
  fp=sum(r["answers"][mode][i] for r in rs for i in (1,2))
  fn=sum(not r["answers"][mode][0] for r in rs)
  return {"triples":n,"correct":c,"accuracy":c/(3*n),
    "false_positive":fp,"false_negative":fn,"fpr":fp/(2*n),"fnr":fn/n}
 totals={m:score(m,rows) for m in modes}
 by={key:{m:score(m,[r for r in rows if r["sensor_condition"]==key])
     for m in modes} for key in TEST}
 valid=totals["descriptor_oracle"]["correct"]==1440
 a=totals["adaptive"]
 better=(a["accuracy"]>=.95 and
   a["accuracy"]-max(totals["anchor_heuristic"]["accuracy"],
                      totals["frozen_f20"]["accuracy"])>=.03
   and all(by[k]["adaptive"]["accuracy"]>=.90 and
           by[k]["adaptive"]["fpr"]<=.05 and by[k]["adaptive"]["fnr"]<=.10 for k in TEST))
 verdict=("INVALID_ANCHOR_ORACLE" if not valid else
   "DEVELOPMENT_LEARNED_ANCHOR_RELIABILITY_TRANSFER" if better else
   "DEVELOPMENT_ANCHOR_RELIABILITY_NO_QUALIFIED_GAIN")
 return {"schema":"yggdrasil.f22.anchor-calibrated-unseen-sensor.dev.v1",
  "stage":"DEVELOPMENT_ONLY","parent":"31d1f2afa4bc073464fa1d02208d57cc7362c596",
  "training_shifts":list(TRAIN),"unseen_test_shifts":list(TEST),
  "training_only_examples":train_count,"learned_weights":learned.w.detach().tolist(),
  "learned_bias":float(learned.bias.detach()),"training_loss":loss,
  "anchor_true_labels_known":True,"anchor_correlation_programmed":True,
  "test_task_truth_given_to_model":False,"test_intervention_label_given_to_model":False,
  "test_role_descriptors_given_to_model":False,
  "parameter_count":5,"prior_reasoning_weights_frozen":True,
  "native_state_bytes":576,"fresh_seeds":[91700,91706],
  "graph_motifs_reused":list(FAMS),"graph_count":96,
  "condition_groups":len(rows),"questions":len(rows)*3,
  "scores":totals,"by_condition":by,"rows":rows,"registered_verdict":verdict,
  "source_independently_born":False,"sealed_first_use":False,
  "accepted_ref_mutation":False,"paid_api_calls":0,
  "elapsed_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
