#!/usr/bin/env python3
"""CS19 original POPGym HigherLower: changing public deck-history usefulness.

Exactly original external reset/step rewards, never hidden source deck/state,
matched FIT episodes, trained conventional predictors and published-law oracles.
No native learner is trained until this source-information screen qualifies.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import importlib
import inspect
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time
import types

FIRST="5e26fcde4cf91754a21228405f4e6f4521d39624"
SOURCE_REPO="proroklab/popgym"
SOURCE_SHA="410d5aa626dae8024f498354d8781a0d1870c399"
BLOBS={
 "popgym/envs/higher_lower.py":"3047f7fab47a0e6403a0985033d73492bc6850e0",
 "popgym/core/deck.py":"12bcabfa9a96fd1261809ef0a446c74d3f3bfa86",
 "popgym/core/env.py":"26a20ba3531730b76e135f48e8fc25bb6b620984",
 "popgym/core/observability.py":"72b5266f79a74b49140f603b859d59d19122b33c",
}
DECK_SIZES=(1,3)
REPS=(0,1)
FIT_PER_REP=64
DEV_PER_REP=96
K=3
ARMS=("trained_rank_only_Laplace","trained_public_history_logistic",
      "trained_public_K3_hist_logistic","source_known_full_remaining_oracle",
      "source_known_memoryless_rank_prior")
EPOCHS=12
LR=.08
L2=.003
def need(t,msg):
    if not t:raise RuntimeError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def original_gitblob(path):
    r=subprocess.run(["git","hash-object","--",str(path)],capture_output=True,text=True,timeout=20)
    need(r.returncode==0,"ORIGINAL_SOURCE_GIT_BLOB_UNAVAILABLE")
    return r.stdout.strip()
def original_class(root):
    for p,h in BLOBS.items():
        need(original_gitblob(root/p)==h,"ORIGINAL_EXTERNAL_POPGYM_SOURCE_ID_DRIFT:"+p)
    for name,relative in (("popgym","popgym"),("popgym.envs","popgym/envs"),
                          ("popgym.core","popgym/core")):
        m=types.ModuleType(name);m.__path__=[str(root/relative)]
        m.__package__=name;sys.modules[name]=m
    for n in list(sys.modules):
        if n.startswith("popgym.") and n not in ("popgym.envs","popgym.core"):
            sys.modules.pop(n)
    module=importlib.import_module("popgym.envs.higher_lower")
    cls=module.HigherLower
    need(Path(inspect.getfile(cls)).resolve()==(root/"popgym/envs/higher_lower.py").resolve(),
         "ORIGINAL_HIGHERLOWER_IMPORT_WRONG_SOURCE")
    return cls
def source_seed(role,di,rep,i):
    return (5100000 if role=="FIT" else 5300000)+500000*di+10000*rep+i
def rank_bit_features(rank,seen,deck_count,t,k):
    need(len(seen)==13 and sum(seen)==t+1 and 0<=rank<13,
         "PUBLIC_HISTORY_FOR_FITTED_FEATURE_INVALID")
    # Hand-specified bounded public rank-history feature extractor, not
    # a discovered relevance gate. The first K ranks may retain counts.
    retained=[seen[j] if k is None or j<k else 0 for j in range(13)]
    per_rank=4*deck_count
    above=sum(per_rank-retained[j] for j in range(rank+1,13))
    below=sum(per_rank-retained[j] for j in range(rank))
    x=[1.]+[float(rank==j) for j in range(13)]
    x.extend([above/(52*deck_count),below/(52*deck_count),
              float(t+1)/(52*deck_count)])
    need(len(x)==17,"FROZEN_LOGISTIC_FEATURE_DIMENSION_DRIFT")
    return x
class TrainedRank:
    def __init__(self):self.counts=[[1,1] for _ in range(13)];self.fit_rows=0
    def learn(self,row):
        if row["original_binary_next_higher"] is not None:
            self.counts[row["public_current_rank"]][int(row["original_binary_next_higher"])]+=1
            self.fit_rows+=1
    def choose(self,rank,seen,num_decks,t):
        low,high=self.counts[rank]
        return 0 if high>=low else 1
    def state(self):return {"counts":self.counts,"fit_non_ties":self.fit_rows}
class TrainedLogistic:
    def __init__(self,k):
        self.k=k;self.weights=[0.]*17;self.updates=0
    def feature(self,row,deck_size):
        return rank_bit_features(row["public_current_rank"],row["public_seen_rank_hist"],
                                 deck_size,row["public_time_step"],self.k)
    def learn_all(self,fit,deck_size):
        for epoch in range(EPOCHS):
            for row in fit:
                y=row["original_binary_next_higher"]
                if y is None:continue
                f=self.feature(row,deck_size)
                z=sum(w*v for w,v in zip(self.weights,f))
                p=1./(1.+math.exp(-max(-25.,min(25.,z))))
                d=float(y)-p
                self.weights=[w+LR*(d*v-L2*w) for w,v in zip(self.weights,f)]
                self.updates+=1
    def choose(self,rank,seen,num_decks,t):
        f=rank_bit_features(rank,seen,num_decks,t,self.k)
        z=sum(w*v for w,v in zip(self.weights,f))
        return 0 if z>=0 else 1
    def state(self):return {"weights":self.weights,"history_cap":self.k,
                             "epochs":EPOCHS,"fit_updates":self.updates}
class SourceKnownFull:
    def choose(self,rank,seen,num_decks,t):
        higher=sum(4*num_decks-seen[j] for j in range(rank+1,13))
        lower=sum(4*num_decks-seen[j] for j in range(rank))
        need(higher>=0 and lower>=0,"SOURCE_PUBLISHED_ORACLE_IMPOSSIBLE_PUBLIC_HISTORY")
        return 0 if higher>=lower else 1
    def state(self):return {"kind":"ORIGINAL_PUBLISHED_LAW_FULL_PUBLIC_SEEN_HIST_ORACLE"}
class SourceKnownPrior:
    def choose(self,rank,seen,num_decks,t):
        higher=4*num_decks*(12-rank)
        lower=4*num_decks*rank
        return 0 if higher>=lower else 1
    def state(self):return {"kind":"ORIGINAL_PUBLISHED_LAW_NO_PRIOR_HISTORY"}
def trained_models(fit,num_decks):
    models={ARMS[0]:TrainedRank(),ARMS[1]:TrainedLogistic(None),
            ARMS[2]:TrainedLogistic(K),ARMS[3]:SourceKnownFull(),
            ARMS[4]:SourceKnownPrior()}
    resources={}
    for name,model in models.items():
        start=time.process_time_ns()
        if isinstance(model,TrainedRank):
            for row in fit:model.learn(row)
        elif isinstance(model,TrainedLogistic):
            model.learn_all(fit,num_decks)
        fit_cpu=time.process_time_ns()-start
        resources[name]={
          "original_source_FIT_episodes_seen":len(fit)//(52*num_decks-1) if name in ARMS[:3] else 0,
          "source_legal_labeled_non_tie_FIT_actions":
               sum(row["original_binary_next_higher"] is not None for row in fit)
               if name in ARMS[:3] else 0,
          "learner_persistent_source_FIT_state_bytes":len(canonical(model.state()).encode()),
          "source_FIT_training_cpu_ns":fit_cpu,
          "source_free_trained_model_SHA256":sha(model.state()),
          "full_running_public_rank_hist_counter_slots":13 if name in (ARMS[1],ARMS[3]) else
                   (K if name==ARMS[2] else 0),
          "learned_model":name in ARMS[:3],
        }
    return models,resources

def episode(cls,di,rep,i,role,num_decks,policy=None):
    start=time.process_time_ns()
    seed=source_seed(role,di,rep,i)
    env=cls(num_decks=num_decks)
    obs,ignore=env.reset(seed=seed)
    del ignore
    rank=int(obs)
    need(0<=rank<13 and env.action_space.n==2,
         "ORIGINAL_SOURCE_PUBLIC_RANK_AND_ACTION_INVALID")
    steps=52*num_decks-1
    seen=[0]*13
    public_observations=[rank]
    public_steps=[]
    signed_reward_sum=0.
    wins=misses=ties=0
    source_fitted_rows=[]
    for t in range(steps):
        seen[rank]+=1
        need(sum(seen)==t+1 and all(0<=c<=4*num_decks for c in seen),
             "ORIGINAL_PUBLIC_HISTORY_COUNTER_DRIFT")
        before=tuple(seen)
        if policy is None:action=(t+i)%2
        else:action=int(policy.choose(rank,before,num_decks,t))
        need(action in (0,1) and env.action_space.contains(action),
             "NONLEGAL_ORIGINAL_HIGHER_LOWER_ACTION")
        next_obs,reward,term,trunc,hidden_info=env.step(action)
        del hidden_info
        next_rank=int(next_obs)
        need(0<=next_rank<13 and trunc is False and
             bool(term)==(t==steps-1),
             "ORIGINAL_SOURCE_TERMINAL_PUBLIC_RANK_DRIFT")
        reward=float(reward)
        scale=reward*52*num_decks
        need(min(abs(scale-v) for v in (-1.,0.,1.))<1e-8,
             "ORIGINAL_NATIVE_SIGNED_REWARD_SCALE_DRIFT")
        sgn=round(scale)
        high=None if sgn==0 else bool((action==0)==(sgn>0))
        signed_reward_sum+=sgn
        wins+=int(sgn>0);misses+=int(sgn<0);ties+=int(sgn==0)
        source_fitted_rows.append({
           "public_current_rank":rank,"public_seen_rank_hist":before,
           "public_time_step":t,"real_chosen_source_action":action,
           "actual_original_native_source_signed_reward":int(sgn),
           "original_binary_next_higher":high})
        public_steps.append({"current_public_rank":rank,"public_time_step":t,
                             "legal_source_action":action,"original_reward_sign":sgn,
                             "returned_public_next_rank":next_rank,
                             "source_terminated":bool(term)})
        rank=next_rank
        public_observations.append(rank)
    need(wins+misses+ties==steps and len(public_observations)==steps+1,
         "ORIGINAL_SOURCE_EPISODE_BUDGET_DRIFT")
    data={"role":role,"external_original_seed":seed,"num_decks":num_decks,
          "original_source_legal_actions":steps,
          "actual_original_source_wins":wins,
          "actual_original_source_misses":misses,
          "actual_original_source_ties":ties,
          "original_native_reward_sum_normalized_sign":signed_reward_sum,
          "original_native_reward_sum_episode":signed_reward_sum/(52*num_decks),
          "native_public_observation_stream_SHA256":sha(public_observations),
          "original_source_step_action_reward_SHA256":sha(public_steps),
          "source_public_step_trace":public_steps,
          "original_real_source_plus_policy_CPU_ns":time.process_time_ns()-start}
    return data,source_fitted_rows

def evaluate(cls,di,num_decks,models):
    paired_roles={}
    for arm in ARMS:
        outcomes=[episode(cls,di,rep,i,"DEV",num_decks,models[arm])[0]
                  for rep in REPS for i in range(DEV_PER_REP)]
        perrep=[]
        for rep in REPS:
            zz=outcomes[rep*DEV_PER_REP:(rep+1)*DEV_PER_REP]
            perrep.append(sum(x["original_native_reward_sum_normalized_sign"] for x in zz)
                          /(len(zz)*(52*num_decks-1)))
        paired_roles[arm]={
           "actual_original_source_DEV_episode_count":len(outcomes),
           "original_source_DEV_real_legal_actions":sum(z["original_source_legal_actions"] for z in outcomes),
           "original_source_normalized_reward_per_decision":
              sum(z["original_native_reward_sum_normalized_sign"] for z in outcomes)
               /(len(outcomes)*(52*num_decks-1)),
           "paired_original_DEV_reward_per_decision_by_replica":perrep,
           "original_source_real_correct_action_rate":
              sum(z["actual_original_source_wins"] for z in outcomes)/
              (len(outcomes)*(52*num_decks-1)),
           "source_original_real_episode_rewards":outcomes,
           "source_original_public_episode_SHA256":sha(outcomes),
           "model_and_original_source_DEV_CPU_ns":sum(z["original_real_source_plus_policy_CPU_ns"]
                                                        for z in outcomes)}
    for k in range(len(paired_roles[ARMS[0]]["source_original_real_episode_rewards"])):
        original={paired_roles[arm]["source_original_real_episode_rewards"][k]["native_public_observation_stream_SHA256"]
                  for arm in ARMS}
        need(len(original)==1,"ORIGINAL_SOURCE_PUBLIC_RANK_SEQUENCE_NOT_PAIRED")
    full=paired_roles[ARMS[3]]["source_original_real_episode_rewards"]
    prior=paired_roles[ARMS[4]]["source_original_real_episode_rewards"]
    changed=0
    better=0
    for a,b in zip(full,prior):
        for x,y in zip(a["source_public_step_trace"],b["source_public_step_trace"]):
            if x["legal_source_action"]!=y["legal_source_action"]:
                changed+=1
                better+=x["original_reward_sign"]-y["original_reward_sign"]
    return paired_roles,{"oracle_vs_prior_source_real_action_disagreements":changed,
                         "oracle_vs_prior_signed_native_reward_advantage_sum":better}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True);ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs19.original_popgym_dynamic_rank_information.v1",
             "first_only_prereg_commit":FIRST,
             "original_external_source":SOURCE_REPO+"@"+SOURCE_SHA,
             "original_SOURCE_ranks_not_hidden_deck_or_info":True,
             "native_memory_model_trained":False,
             "original_R7_historical_failure_preserved":True,
             "independent_scientific_first_use":False,
             "disposition":"PUBLIC_CS19_ORIGINAL_SOURCE_PROTOCOL_INVALID",
             "strata":[]}
    shared={"schema":"mass.cs19.shared_real_original_source_FIT.v1","strata":[]}
    t0=time.process_time_ns()
    try:
        cls=original_class(Path(args.upstream).resolve())
        all_seeds=[source_seed(role,di,rep,i) for role,n in
            (("FIT",FIT_PER_REP),("DEV",DEV_PER_REP))
            for di in range(2) for rep in REPS for i in range(n)]
        need(len(all_seeds)==len(set(all_seeds))==2*2*(FIT_PER_REP+DEV_PER_REP),
             "FROZEN_ORIGINAL_SOURCE_ROLE_SEED_COLLISION")
        gate=[]
        for di,decksize in enumerate(DECK_SIZES):
            start=time.process_time_ns()
            episodes_and_rows=[episode(cls,di,rep,i,"FIT",decksize)
                               for rep in REPS for i in range(FIT_PER_REP)]
            fit_ep=[x for x,rows in episodes_and_rows]
            fit=[item for x,rows in episodes_and_rows for item in rows]
            need(len(fit_ep)==128 and len(fit)==128*(52*decksize-1),
                 "SHARED_SOURCE_FIT_ACTION_COUNT_DRIFT")
            shared["strata"].append({"num_decks":decksize,
                                     "original_source_SHARED_FIT_episodes":fit_ep,
                                     "original_source_FIT_public_observed_labeled_action_rows":fit})
            original_fit_cpu=time.process_time_ns()-start
            models,model_meta=trained_models(fit,decksize)
            model_state={n:sha(m.state()) for n,m in models.items()}
            scores,paired=evaluate(cls,di,decksize,models)
            need(model_state=={n:sha(m.state()) for n,m in models.items()},
                 "ORIGINAL_SOURCE_DEV_UPDATED_TRAINED_MODEL")
            mean=lambda a:scores[a]["original_source_normalized_reward_per_decision"]
            oracle_gain=mean(ARMS[3])-mean(ARMS[4])
            fitted_gain=mean(ARMS[1])-mean(ARMS[0])
            perrep=[scores[ARMS[1]]["paired_original_DEV_reward_per_decision_by_replica"][rep]-
                    scores[ARMS[0]]["paired_original_DEV_reward_per_decision_by_replica"][rep]
                    for rep in REPS]
            qualified=(paired["oracle_vs_prior_source_real_action_disagreements"]>=100 and
                       oracle_gain>=.005 and fitted_gain>=.005 and
                       all(z>0 for z in perrep))
            gate.append({"oracle":oracle_gain,"fitted":fitted_gain,
                         "qualified":qualified,"oracle_signal":(
                           paired["oracle_vs_prior_source_real_action_disagreements"]>=100 and
                           oracle_gain>=.005)})
            receipt["strata"].append({
                "original_num_decks":decksize,"original_source_FIT_real_episodes":128,
                "original_source_FIT_real_legal_actions":len(fit),
                "original_source_FIT_process_CPU_ns":original_fit_cpu,
                "original_source_shared_FIT_trace_SHA256":sha(fit_ep),
                "conventional_fitted_model_costs_and_state":model_meta,
                "original_source_real_DEV_by_policy":scores,
                "original_SOURCE_oracle_history_signal":paired,
                "source_oracle_minus_prior_normalized_reward_per_decision":oracle_gain,
                "trained_history_minus_trained_rank_only_normalized_reward_per_decision":fitted_gain,
                "trained_public_history_gain_by_replica":perrep,
                "prospective_per_level_strong_source_and_fit_eligibility":qualified,
            })
            print("CS19_ORIGINAL_POPGYM_DECK="+str(decksize)+" REWARD="+
                  canonical({n:round(mean(n),6) for n in ARMS})+
                  " ORACLE_CHANGED_ACTIONS="+str(paired["oracle_vs_prior_source_real_action_disagreements"]),
                  flush=True)
        receipt["original_external_SOURCE_FIT_resets"]=256
        receipt["original_external_SOURCE_DEV_resets"]=1920
        receipt["total_original_SOURCE_reset_episodes"]=2176
        receipt["total_original_SOURCE_legal_step_calls"]=sum(
            (2*FIT_PER_REP+2*DEV_PER_REP*len(ARMS))*(52*num_decks-1)
            for num_decks in DECK_SIZES)
        need(receipt["total_original_SOURCE_legal_step_calls"]==224128,
             "FROZEN_224128_ORIGINAL_SOURCE_LEGAL_ACTION_COUNT_INVALID")
        receipt["original_public_shared_FIT_transcript_SHA256"]=sha(shared)
        receipt["disposition"]=(
            "PUBLIC_CS19_DYNAMIC_HISTORY_SIGNAL_ELIGIBLE_FOR_NATIVE_LEARNER"
            if all(x["qualified"] for x in gate) else
            "PUBLIC_CS19_ORACLE_HISTORY_USEFUL_BUT_LEARNING_NOT_YET_QUALIFIED"
            if all(x["oracle_signal"] for x in gate) else
            "PUBLIC_CS19_NO_MATERIAL_ACTIONABLE_PUBLIC_RELEVANCE_GAIN")
        receipt["novel_native_learning_law_supported"]=False
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:1000]
    finally:
        receipt["all_source_and_policy_process_CPU_ns"]=time.process_time_ns()-t0
        receipt["process_inclusive_RSS_KiB"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs19-real-original-POPGym-dynamic-source-receipt.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        (out/"cs19-original-public-FIT-source.json").write_text(canonical(shared)+"\n")
    print("CS19_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS19_ORIGINAL_SOURCE_PROTOCOL_INVALID" else 0
if __name__=="__main__":raise SystemExit(main())
