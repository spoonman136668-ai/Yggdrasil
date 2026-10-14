"""Y-F15: frozen Y-F14 risk policy, real online stops and timing, new graph grammars.

Original Y-F14 archive omitted policy weights. Reconstruct from its frozen
TRAIN cohort and verify historical F14 outcomes BEFORE F15 new data exists;
this is reproducibility, not new training or validation-driven selection.
No future recurrent trajectory is computed before a stop. Development only.
"""
from __future__ import annotations
import importlib.util,hashlib,json,time,struct
from collections import Counter
from pathlib import Path
import torch
p=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("qualified_f14",p.parent/"20261014-y-f14"/"execute.py")
assert spec and spec.loader
f14=importlib.util.module_from_spec(spec);spec.loader.exec_module(f14)
f13=f14.f13;f10=f13.f10
torch.set_num_threads(1)
FAMS=(76,77,78,79)
SEEDS=range(65100,65106)

def recovered():
 torch.manual_seed(1435)
 core=f13.f11.model()
 tr=f13.gather_cases(f14.TRAIN_SEEDS,f14.TRAIN_FAMS,(4,5,6),(0,1))
 head,_,_=f14.train(f14.records(tr,core))
 limit,_=f14.choose_threshold(f14.records(tr,core),head)
 assert limit==.7,("historical risk threshold drift",limit)
 old=f13.gather_cases(f14.VALID_SEEDS,f14.VALID_FAMS,(7,8),(0,1))
 oldrows=f14.records(old,core)
 check=f14.metrics(oldrows,f14.simulate(oldrows,"risk",head,limit))
 assert check["correct"]==576 and check["actual_recurrence_steps"]==2458,check
 raw=b"".join(struct.pack("<f",float(x)) for _,v in sorted(head.state_dict().items()) for x in v.detach().flatten().tolist())
 return core,head,hashlib.sha256(raw).hexdigest()

def graph(seed,fam,k,shift):
 ed=[(i,i+1) for i in range(k)]
 extra={76:[(0,3),(k-1,1)],77:[(1,k-2),(k,0)],
        78:[(2,0),(0,k-3)],79:[(k-2,2),(2,5)]}[fam]
 ed+=extra
 for i in range(12-len(ed)):ed.append((k+12+i,k+13+i))
 roles=[(seed*13+fam*7+i*3+shift)%4 for i in range(12)]
 edges=[(f10.f1.relabel(a,seed,2),f10.f1.relabel(b,seed,2)) for a,b in ed]
 for i in range(11,0,-1):
  j=(seed*17+fam*31+k*11+shift*19+i*23)%(i+1)
  edges[i],edges[j]=edges[j],edges[i];roles[i],roles[j]=roles[j],roles[i]
 query=(f10.f1.relabel(0,seed,2),f10.f1.relabel(k,seed,2))
 chain=[(f10.f1.relabel(i,seed,2),f10.f1.relabel(i+1,seed,2)) for i in range(k)]
 loc=[edges.index(edge) for edge in chain]
 pattern=tuple(roles[i] for i in loc)
 assert pattern[0]!=pattern[1]
 wrong=(pattern[1],pattern[0])+pattern[2:]
 benign=edges.index((f10.f1.relabel(extra[0][0],seed,2),f10.f1.relabel(extra[0][1],seed,2)))
 assert benign not in loc
 def changed(idx):
  a=list(roles);a[idx]=(a[idx]+1)%4;return a
 plans=[(roles,pattern,True),(changed(loc[-1]),pattern,False),
  (changed(loc[1]),pattern,False),(roles,wrong,False),
  (roles,pattern[:-1],False),(changed(benign),pattern,True)]
 for variant,(rs,seq,truth) in enumerate(plans):
  actual=f10.typed_exact(edges,rs,*query,seq)
  assert actual==truth,("new topology oracle invalid",seed,fam,k,shift,variant)
 return [(edges,rs,query,seq,truth,v) for v,(rs,seq,truth) in enumerate(plans)]

def online(core,head,edges,roles,query,sequence,mode):
 with torch.no_grad():
  fact=torch.tensor([edges],dtype=torch.int32)
  typ=torch.tensor([roles],dtype=torch.int64)
  q=torch.tensor([query],dtype=torch.int32)
  state=core.encode(fact,typ)
  assert state.shape==(1,144) and state.element_size()==4
  packed=state[:,:12].contiguous().view(torch.int32).long()
  src=(packed>>16)&65535;dst=packed&65535
  rel=state[:,12:24].long()
  if mode=="static":
   if not bool(((src[0]==query[0])&(rel[0]==sequence[0])).any()):
    return {"answer":False,"steps":0,"halt":True}
  link=core.core.similarity(dst[:,:,None],src[:,None,:])*f10.f6.f4.MASK.to(src)
  active=core.core.similarity(q[:,0,None],src)
  terminal=core.core.similarity(dst,q[:,1,None])
  prior=0.;k=len(sequence)
  for t,role in enumerate(sequence):
   gate=torch.sigmoid(core.role_logits[rel,torch.tensor([[role]])])
   if t:
    msg=torch.bmm(active.unsqueeze(1),link).squeeze(1)
    active=torch.sigmoid(core.core.message_gain*msg+
      core.core.recurrent_gain*active+core.core.activation_bias)
   active=active*gate
   prob=float(torch.sigmoid(core.core.output_gain*(active*terminal).sum(-1)+core.core.output_bias))
   stop=False
   if mode=="risk" and prob<.5:
    if t+1<k:
     maxnext=float(torch.sigmoid(core.role_logits[rel,sequence[t+1]]).max())
    else:maxnext=0.
    features=[prob,prob-prior,float(active.max()),float(active.mean()),
      float(active.std(unbiased=False)),(t+1)/k,1-(t+1)/k,maxnext]
    risk=float(torch.sigmoid(head(torch.tensor([features],dtype=torch.float32)))[0])
    stop=risk>=.7
   if stop or t==k-1:return {"answer":prob>=.5,"steps":t+1,"halt":bool(stop and t<k-1)}
   prior=prob
 raise RuntimeError("unreachable")

def aggregate(rows,mode):
 accuracy=fp=fn=steps=full=ns=0
 positive=negative=0
 by=Counter()
 for row in rows:
  truth=row["truth"];o=row["arms"][mode]
  accuracy+=int(o["answer"]==truth)
  if truth:
   positive+=1
   if not o["answer"]:fn+=1;by[(row["family"],"fn")]+=1
  else:
   negative+=1
   if o["answer"]:fp+=1;by[(row["family"],"fp")]+=1
  steps+=o["steps"];full+=row["depth"];ns+=row["ns"][mode]
 return {"correct":accuracy,"accuracy":accuracy/len(rows),
  "false_negatives":fn,"false_negative_rate":fn/positive,
  "false_positives":fp,"false_positive_rate":fp/negative,
  "worst_family_FNR":max(by[(fam,"fn")]/48 for fam in FAMS),
  "worst_family_FPR":max(by[(fam,"fp")]/96 for fam in FAMS),
  "actual_steps":steps,"full_steps":full,"step_saving":1-steps/full,
  "online_wall_ns":ns}

def evaluate():
 started=time.perf_counter()
 core,head,frozen_hash=recovered()
 rows=[]
 for seed in SEEDS:
  for fam in FAMS:
   for depth in (7,8):
    for shift in (0,1):
     for ed,roles,q,seq,truth,variant in graph(seed,fam,depth,shift):
      row={"seed":seed,"family":fam,"depth":len(seq),"shift":shift,
       "variant":variant,"truth":truth,"arms":{},"ns":{}}
      for name in ("risk","full","static"):online(core,head,ed,roles,q,seq,name)
      order=("risk","full") if (seed+fam+variant)%2==0 else ("full","risk")
      for name in (*order,"static"):
       t=time.perf_counter_ns()
       row["arms"][name]=online(core,head,ed,roles,q,seq,name)
       row["ns"][name]=time.perf_counter_ns()-t
      rows.append(row)
 assert len(rows)==576
 scores={n:aggregate(rows,n) for n in ("risk","full","static")}
 a,b=scores["risk"],scores["full"]
 a["wall_fraction_saved"]=1-a["online_wall_ns"]/b["online_wall_ns"]
 scores["static"]["wall_fraction_saved"]=1-scores["static"]["online_wall_ns"]/b["online_wall_ns"]
 if b["accuracy"]<.95:verdict="INVALID_FROZEN_FULL_CORE_REFERENCE"
 else:
  robust=(a["accuracy"]>=.95 and a["false_negative_rate"]<=.05 and
   a["false_positive_rate"]<=.05 and a["worst_family_FNR"]<=.05 and
   a["worst_family_FPR"]<=.05 and a["accuracy"]>=b["accuracy"]-.03)
  fast=(a["step_saving"]>=.15 and a["wall_fraction_saved"]>=.05)
  verdict=("DEVELOPMENT_FROZEN_ONLINE_RISK_ROBUST_AND_EFFICIENT" if robust and fast else
    "DEVELOPMENT_NO_FROZEN_RISK_ROBUSTNESS" if not robust else
    "DEVELOPMENT_ROBUST_BUT_NO_ONLINE_WALL_EFFICIENCY")
 return {"schema":"yggdrasil.f15.frozen-online-risk-cost-dev.v1",
  "stage":"DEVELOPMENT_ONLY","source_F14_sha":"2204e66e0e2866f8e712b74d91ee160fe216f136",
  "F14_original_json_sha256":"f2e2599d81cbe77a12d917287c1acd1e07e7bd49a5980d216251cd48bd273ad6",
  "F14_original_omitted_head_weights":True,"training_only_weight_replay":True,
  "recovered_F14_history_correct":576,"recovered_F14_history_steps":2458,
  "frozen_head_weight_sha256":frozen_hash,"frozen_threshold":.7,
  "families":list(FAMS),"seed_bounds":[65100,65106],"graphs":96,
  "questions":576,"positives":192,"negatives":384,"resident_state_bytes":576,
  "genuine_online_stop":True,"no_future_rollout_oracle_in_policy":True,
  "wall_scope":"per-call perf_counter_ns includes encode, recurrent inference, policy features and NN decisions; excludes dataset preparation and fixed original TRAIN-only head recovery. One warmup and alternating one timed pass.",
  "timing_not_portable_across_hardware":True,"scientific_f3_sealed_first_use":False,
  "independent_source_birth":False,"accepted_ref_mutation":False,
  "scores":scores,"rows":rows,"verdict":verdict,
  "original_wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))
