#!/usr/bin/env python3
"""CS21 original POPGym true source-reward local native rank relevance screen.

Unmodified R7 LocalCell, actual external-source returned signed reward and public
observation, shared FIT original native histories, strong source-qualified CS20.
"""
from __future__ import annotations
from dataclasses import asdict
import argparse,hashlib,json,math,inspect,resource,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"r7"))
from native_cells import LocalCell
from run_cs20_original_depletion_belief import (
 original_class,LearnedDepletion,TrainedRank,SourceKnownFull,total_cards,mass,
 higher_or_lower_from_mass
)
FIRST="27e944e683007635cfcd9d87764d3b6995666505"
ORIGINAL="proroklab/popgym@410d5aa626dae8024f498354d8781a0d1870c399"
NATIVE_BLOB="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
DECKS=(1,3)
REPS=(0,1)
FIT_N=64
DEV_N=64
LAMBDA_GRID=(0.,.25,.5,.75,1.)
GAMMA=.75
ARMS=("actual_native_local_reward_relevance",
      "matched_conventional_CS20_depletion",
      "actual_native_LOCALCELLS_ZEROED",
      "actual_native_LOCALCELLS_INDEX_PERMUTED",
      "matched_trained_rank_only_Laplace",
      "source_known_full_public_deck_oracle")
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def compact(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):return hashlib.sha256(compact(x).encode()).hexdigest()
def seed(role,deck,rep,i):
 return (7100000 if role=="FIT" else 7300000)+400000*deck+10000*rep+i
def sensor(hist,t,j):
 return bool(hist[j]>(t+1)/13.)
class TrueNativeRankRelevance:
 def __init__(self,c,lam,permutation=0,blank=False):
  self.c=tuple(c);self.lam=float(lam)
  self.cells=[LocalCell() for _ in range(13)]
  self.feedback=0
  self.permutation=permutation
  self.blank=blank
 def learn(self,public_row):
  y=public_row["real_source_next_higher"]
  if y is None:return
  h=public_row["public_seen_rank_hist"]
  t=public_row["public_time_step"]
  for j,cell in enumerate(self.cells):
   cell.feel(sensor(h,t,j),bool(y))
  self.feedback+=1
 def choose(self,rank,seen,num_decks,t):
  w=mass(self.c,seen,self.lam)
  base=sum(w[rank+1:])-sum(w[:rank])
  signal=0.
  if not self.blank:
   for j in range(13):
    cell=self.cells[(j+self.permutation)%13]
    if cell.updates:
     z=(.75*cell.fast+.25*cell.slow)/cell.updates
     z=max(-1.,min(1.,z))
     signal+=z*(1 if sensor(seen,t,j) else -1)
  return 0 if base+GAMMA*signal>=0 else 1
 def state(self):
  return {"c":self.c,"lambda":self.lam,
          "native_R7_original_LocalCell_fields":[asdict(z) for z in self.cells],
          "actual_genuine_completed_source_outcomes":self.feedback,
          "index_permutation":self.permutation,"source_returned_outcome_weight":GAMMA,
          "cells_blank_at_inference":self.blank}
 def checkpoint(self):
  body=self.state()
  raw=compact(body).encode()
  out=compact({"body":body,"sha256":hashlib.sha256(raw).hexdigest()}).encode()
  require(len(out)<=32768,"NATIVE_ORIGINAL_PERSISTENT_CHECKPOINT_TOO_LARGE")
  return out
 @classmethod
 def restore(cls,raw):
  require(type(raw) is bytes and 0<len(raw)<=32768,
          "ORIGINAL_NATIVE_CHECKPOINT_BYTES_INVALID")
  obj=json.loads(raw)
  require(set(obj)=={"body","sha256"} and
          hashlib.sha256(compact(obj["body"]).encode()).hexdigest()==obj["sha256"],
          "ORIGINAL_NATIVE_COLD_CHECKPOINT_DIGEST_INVALID")
  d=obj["body"]
  require(len(d["native_R7_original_LocalCell_fields"])==13,
          "ORIGINAL_NATIVE_RANK_CELL_COUNT_DRIFT")
  x=cls(d["c"],d["lambda"],d["index_permutation"],d["cells_blank_at_inference"])
  x.cells=[LocalCell(**z) for z in d["native_R7_original_LocalCell_fields"]]
  x.feedback=d["actual_genuine_completed_source_outcomes"]
  require(all(z.updates==x.feedback for z in x.cells) and
          x.checkpoint()==raw,"R7_NATIVE_COLD_RESTORE_FIELDS_OR_BYTES_INVALID")
  return x

def original_episode(Source,deck_idx,rep,i,role,num_decks,policy=None):
 env=Source(num_decks=num_decks)
 beginning=time.process_time_ns()
 init,unused_info=env.reset(seed=seed(role,deck_idx,rep,i))
 del unused_info
 rank=int(init)
 require(0<=rank<13 and env.action_space.n==2,
         "SOURCE_ORIGINAL_RESET_PUBLIC_RANK_OR_ACTION_INVALID")
 seen=[0]*13
 obs=[rank];fit_rows=[];trace=[];score=0;ties=0
 for t in range(total_cards(num_decks)-1):
  seen[rank]+=1
  require(sum(seen)==t+1 and all(0<=x<=4*num_decks for x in seen),
          "ORIGINAL_PUBLIC_HISTORY_SOURCE_CARD_COUNT_DRIFT")
  hist=tuple(seen)
  a=(t+i)%2 if policy is None else int(policy.choose(rank,hist,num_decks,t))
  require(a in (0,1) and env.action_space.contains(a),"SOURCE_ILLEGAL_ORIGINAL_BINARY_ACTION")
  nxt,r,done,truncated,info=env.step(a)
  del info
  next_rank=int(nxt)
  require(0<=next_rank<13 and bool(done)==(t==total_cards(num_decks)-2)
          and truncated is False,"EXTERNAL_SOURCE_TERMINAL_OR_NEXT_PUBLIC_RANK_INVALID")
  sign=float(r)*total_cards(num_decks)
  require(min(abs(sign-v) for v in (-1.,0.,1.))<1e-8,
          "SOURCE_NATIVE_REWARD_UNEXPECTED")
  y=round(sign);score+=y;ties+=int(y==0)
  next_higher=None if y==0 else bool((a==0)==(y>0))
  fit_rows.append({
    "public_current_rank":rank,"public_seen_rank_hist":hist,
    "public_time_step":t,"genuine_executed_source_action":a,
    "real_original_returned_signed_reward":y,
    "real_source_next_higher":next_higher,
    "actual_source_returned_next_public_rank":next_rank})
  trace.append((rank,a,y,next_rank))
  rank=next_rank;obs.append(next_rank)
 require(len(fit_rows)==total_cards(num_decks)-1,
         "SOURCE_EPISODE_ACTION_COUNT_INCORRECT")
 return {"role":role,"source_seed":seed(role,deck_idx,rep,i),
         "true_source_legal_action_calls":len(fit_rows),
         "real_external_source_signed_reward_sum":score,
         "real_external_source_normalized_reward_per_episode":score/total_cards(num_decks),
         "real_original_source_tie_action_count":ties,
         "actual_public_rank_observation_SHA256":digest(obs),
         "true_external_source_action_reward_trace_SHA256":digest(trace),
         "genuine_source_FIT_rows":fit_rows if role=="FIT" else [],
         "genuine_source_DEV_action_reward_trace":trace if role=="DEV" else [],
         "source_and_model_process_CPU_ns":time.process_time_ns()-beginning}

def fit_shared_base(fit):
 require(len(fit)==len(REPS)*FIT_N,"SHARED_SOURCE_FIT_EPISODE_COUNT_INVALID")
 counts=[0]*13;events=[]
 for ep in fit:
  rows=ep["genuine_source_FIT_rows"]
  counts[rows[0]["public_current_rank"]]+=1
  for row in rows:
   counts[row["actual_source_returned_next_public_rank"]]+=1
   events.append(row)
 c=tuple(z/len(fit) for z in counts)
 require(all(x>0 for x in c),"PUBLIC_SOURCE_FIT_EMPTY_RANK_COUNT")
 scores={}
 for lam in LAMBDA_GRID:
  ll=0.
  for row in events:
   w=[max(1e-9,c[j]-lam*row["public_seen_rank_hist"][j]) for j in range(13)]
   ll+=math.log(w[row["actual_source_returned_next_public_rank"]]/sum(w))
  scores[str(lam)]=ll
 lam=max(LAMBDA_GRID,key=lambda z:(scores[str(z)],-z))
 return c,lam,scores,events

def models_from_fit(fit):
 t=time.process_time_ns()
 c,lam,ll,events=fit_shared_base(fit)
 base_cpu=time.process_time_ns()-t
 native=TrueNativeRankRelevance(c,lam)
 t=time.process_time_ns()
 for row in events:native.learn(row)
 native_cpu=time.process_time_ns()-t
 expected=sum(row["real_source_next_higher"] is not None for row in events)
 require(native.feedback==expected and
         all(cell.updates==expected for cell in native.cells),
         "ORIGINAL_NATIVE_REWARDED_OUTCOME_UPDATES_NOT_EQUAL_SOURCE")
 original=native.checkpoint()
 cold=TrueNativeRankRelevance.restore(original)
 require(original==cold.checkpoint(),"ORIGINAL_NATIVE_COLD_CHECKPOINT_MISMATCH")
 permuted=TrueNativeRankRelevance.restore(original)
 permuted.permutation=1
 erased=TrueNativeRankRelevance.restore(original)
 erased.blank=True
 rank=TrainedRank();t=time.process_time_ns()
 for row in events:
  rank.learn({"public_current_rank":row["public_current_rank"],
              "original_binary_next_higher":row["real_source_next_higher"]})
 rank_cpu=time.process_time_ns()-t
 ms={ARMS[0]:cold,ARMS[1]:LearnedDepletion(c,lam),
     ARMS[2]:erased,ARMS[3]:permuted,ARMS[4]:rank,
     ARMS[5]:SourceKnownFull()}
 resources={}
 for name,m in ms.items():
  serialized=original if name==ARMS[0] else compact(m.state()).encode()
  resources[name]={
    "FIT_original_genuine_episode_count":len(fit) if name!=ARMS[5] else 0,
    "source_legal_completed_feedback_events":expected if name in ARMS[:4] else 0,
    "source_r7_native_cell_count":13 if name in (ARMS[0],ARMS[2],ARMS[3]) else 0,
    "source_fitted_parameter_or_checkpoint_bytes":len(serialized),
    "source_native_or_conventional_training_CPU_ns":{
       ARMS[0]:native_cpu,ARMS[4]:rank_cpu}.get(name,"shared_c_lambda_SOURCE_FIT_model"),
    "online_public_rank_history_counter_slots":0 if name==ARMS[4] else 13,
    "original_fitted_model_sha256":hashlib.sha256(serialized).hexdigest()}
  }
 return ms,resources,{"shared_true_original_c":c,
    "shared_true_source_fit_lambda":lam,
    "shared_source_original_next_rank_likelihood_grid":ll,
    "actual_original_R7_native_FIT_completed_feedback_events":expected,
    "source_R7_checkpoint_SHA256":hashlib.sha256(original).hexdigest(),
    "source_R7_checkpoint_bytes":len(original),
    "native_true_original_LocalCells_used":True,
    "shared_fit_source_model_cpu_ns":base_cpu,
    "actual_native_fit_source_reward_process_cpu_ns":native_cpu}

def evaluate(Source,di,num_decks,models):
 states={n:digest(m.state()) for n,m in models.items()}
 scores={}
 for name,m in models.items():
  records=[original_episode(Source,di,rep,i,"DEV",num_decks,m)
           for rep in REPS for i in range(DEV_N)]
  denom=len(records)*(total_cards(num_decks)-1)
  mean=sum(z["real_external_source_signed_reward_sum"] for z in records)/denom
  byrep=[sum(z["real_external_source_signed_reward_sum"]
          for z in records[rep*DEV_N:(rep+1)*DEV_N])/
          (DEV_N*(total_cards(num_decks)-1)) for rep in REPS]
  scores[name]={
   "genuine_original_source_DEV_reset_episodes":len(records),
   "genuine_original_source_DEV_native_actions":denom,
   "real_external_source_reward_per_step":mean,
   "true_source_reward_per_step_by_replica":byrep,
   "original_source_DEV_episode_receipts":records,
   "original_source_real_observation_and_reward_SHA256":digest(records),
   "native_SOURCE_inclusive_source_plus_model_DEV_CPU_ns":sum(
      z["source_and_model_process_CPU_ns"] for z in records)}
 require(states=={n:digest(m.state()) for n,m in models.items()},
         "FIT_MODEL_MUTATED_BY_ACTUAL_ORIGINAL_DEV_REWARDS")
 baseline=scores[ARMS[1]]["original_source_DEV_episode_receipts"]
 counters={"native_vs_CS20_baseline":0,"native_vs_permuted":0,
           "native_vs_erased":0}
 for i in range(len(baseline)):
  streams={scores[name]["original_source_DEV_episode_receipts"][i]
           ["actual_public_rank_observation_SHA256"] for name in ARMS}
  require(len(streams)==1,"ORIGINAL_SOURCE_DEV_PAIRED_PUBLIC_RANK_STREAM_DRIFT")
  native=scores[ARMS[0]]["original_source_DEV_episode_receipts"][i]["genuine_source_DEV_action_reward_trace"]
  for n,label in ((ARMS[1],"native_vs_CS20_baseline"),
                  (ARMS[2],"native_vs_erased"),(ARMS[3],"native_vs_permuted")):
   other=scores[n]["original_source_DEV_episode_receipts"][i]["genuine_source_DEV_action_reward_trace"]
   counters[label]+=sum(x[1]!=y[1] for x,y in zip(native,other))
 require(scores[ARMS[1]]["original_source_DEV_episode_receipts"]==
         scores[ARMS[2]]["original_source_DEV_episode_receipts"],
         "COLD_ERASED_NATIVE_SHOULD_EXACTLY_EQUAL_CS20_CONVENTIONAL_REWARD")
 return scores,counters

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--upstream",required=True);p.add_argument("--out",required=True)
 a=p.parse_args()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 receipt={"schema":"mass.cs21.native_genuine_localcell_reward_relevance.v1",
          "frozen_FIRST_prereg":FIRST,"external_original_POPgym":ORIGINAL,
          "native_original_R7_source_git_blob":NATIVE_BLOB,
          "source_private_deck_or_info_consumed":False,
          "independent_sealed_original_first_use":False,
          "original_R7_frozen_integration":"FAILED_UNCHANGED",
          "disposition":"PUBLIC_CS21_SOURCE_NATIVE_PROTOCOL_INVALID","strata":[]}
 fitarchive={"schema":"mass.cs21.original_external_public_FIT_histories.v1",
             "strata":[]}
 t0=time.process_time_ns()
 try:
  Source=original_class(Path(a.upstream).resolve())
  require(Path(inspect.getfile(LocalCell)).resolve()==
          (HERE.parent/"r7"/"native_cells.py").resolve(),
          "ORIGINAL_R7_LOCALCELL_ACTUAL_SOURCE_ID_DRIFT")
  import subprocess
  p=subprocess.run(["git","hash-object",str(HERE.parent/"r7"/"native_cells.py")],
      text=True,capture_output=True,timeout=20)
  require(p.returncode==0 and p.stdout.strip()==NATIVE_BLOB,
          "FROZEN_R7_ORIGINAL_NATIVE_GIT_BLOB_DIFFERENT")
  allseeds=[seed(role,di,rep,i) for role,n in (("FIT",FIT_N),("DEV",DEV_N))
            for di in range(2) for rep in REPS for i in range(n)]
  require(len(allseeds)==len(set(allseeds))==2*len(REPS)*(FIT_N+DEV_N),
          "ORIGINAL_FIT_DEV_ROLE_SEED_COLLISION")
  passes=[]
  for di,num_decks in enumerate(DECKS):
   start=time.process_time_ns()
   fit=[original_episode(Source,di,rep,i,"FIT",num_decks)
       for rep in REPS for i in range(FIT_N)]
   fit_source_cpu=time.process_time_ns()-start
   models,resources,info=models_from_fit(fit)
   scores,disagreements=evaluate(Source,di,num_decks,models)
   r=lambda name:scores[name]["real_external_source_reward_per_step"]
   n=r(ARMS[0])
   gain=n-r(ARMS[1])
   inv=n-r(ARMS[3])
   erased=n-r(ARMS[2])
   rep_gains=[scores[ARMS[0]]["true_source_reward_per_step_by_replica"][i]-
              scores[ARMS[1]]["true_source_reward_per_step_by_replica"][i]
              for i in REPS]
   ok=(gain>=.005 and inv>=.005 and erased>=.005 and
        all(d>0 for d in rep_gains) and n>=r(ARMS[5])-.015 and
        disagreements["native_vs_CS20_baseline"]>=10)
   passes.append(ok)
   fitarchive["strata"].append({"original_num_decks":num_decks,
                                "actual_original_source_SHARED_FIT":fit})
   receipt["strata"].append({
       "original_num_decks":num_decks,
       "source_original_FIT_real_reset_count":len(fit),
       "source_original_FIT_true_actions":len(fit)*(total_cards(num_decks)-1),
       "source_original_FIT_CPU_ns":fit_source_cpu,
       "original_source_shared_FIT_SHA256":digest(fit),
       "actual_native_fit_relevance_cold_restore_receipt":info,
       "original_native_and_conventional_FIT_resource_measures":resources,
       "real_original_source_NATIVE_DEV_reward_and_arms":scores,
       "original_source_DEV_action_choice_disagreements":disagreements,
       "native_minus_strong_original_CS20_depletion_reward_per_step":gain,
       "native_minus_native_index_permuted_reward_per_step":inv,
       "native_minus_erased_cells_reward_per_step":erased,
       "native_minus_original_source_known_oracle":n-r(ARMS[5]),
       "native_minus_CS20_by_independent_source_replica":rep_gains,
       "preregistered_native_advance":ok})
   print("CS21_REAL_SOURCE_DECK="+str(num_decks)+" SOURCE_REWARD="+
         compact({name:round(r(name),6) for name in ARMS})+
         " ACTUAL_NATIVE_BASE_ACTION_DISAGREEMENTS="+
         str(disagreements["native_vs_CS20_baseline"]),flush=True)
  receipt["true_original_FIT_reset_episodes"]=len(DECKS)*len(REPS)*FIT_N
  receipt["true_original_DEV_reset_episodes"]=len(DECKS)*len(REPS)*len(ARMS)*DEV_N
  receipt["source_original_total_real_reset_episodes"]=(
      receipt["true_original_FIT_reset_episodes"]+receipt["true_original_DEV_reset_episodes"])
  receipt["source_original_total_real_legal_step_calls"]=sum(
    (len(REPS)*FIT_N+len(REPS)*len(ARMS)*DEV_N)*(total_cards(n)-1)
    for n in DECKS)
  require(receipt["source_original_total_real_reset_episodes"]==1792
          and receipt["source_original_total_real_legal_step_calls"]==184576,
          "EXTERNAL_REAL_SOURCE_ACTION_BUDGET_NOT_FROZEN")
  receipt["source_full_FIT_public_SHA256"]=digest(fitarchive)
  receipt["disposition"]=(
   "PUBLIC_CS21_NATIVE_LOCAL_RELEVANCE_ADVANCED_PUBLIC_ONLY"
   if all(passes) else "PUBLIC_CS21_NATIVE_LOCAL_RELEVANCE_NO_ADVANTAGE")
  receipt["scientific_first_use_accepted"]=False
  receipt["new_cognitive_architecture_advantage"]="NOT_ESTABLISHED_UNLESS_MATCHED_BENEFIT_PROSPECTIVE"
 except Exception as e:
  receipt["first_failure"]=type(e).__name__+":"+str(e)[:1100]
 finally:
  receipt["whole_python_process_CPU_ns_including_source"]=time.process_time_ns()-t0
  receipt["whole_process_peak_RSS_KiB"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
  (out/"cs21-real-original-POPGym-native-local-relevance-receipt.json").write_text(
      json.dumps(receipt,sort_keys=True,indent=2)+"\n")
  (out/"cs21-original-POPGym-shared-public-FIT-history.json").write_text(compact(fitarchive)+"\n")
 print("CS21_DISPOSITION="+receipt["disposition"],flush=True)
 return 2 if receipt["disposition"]=="PUBLIC_CS21_SOURCE_NATIVE_PROTOCOL_INVALID" else 0
if __name__=="__main__":
 raise SystemExit(main())
