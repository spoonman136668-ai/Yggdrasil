#!/usr/bin/env python3
"""CS20 real original POPGym learned card-depletion and equal-FIT conventional controls.

PUBLIC source development only. No source-private deck, model API, peek or
counterfactual reward. All learning labels are returned by genuine env.step().
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_cs19_original_popgym_rank_history import (
    original_class,TrainedRank,TrainedLogistic,SourceKnownFull
)

FIRST="7e6cce12c7ed5be036b135a7ef44123d8dee4517"
ORIGINAL="proroklab/popgym@410d5aa626dae8024f498354d8781a0d1870c399"
DECK_SIZES=(1,3)
REPS=(0,1)
FIT_N=48
DEV_N=64
ARMS=("trained_public_depletion_belief",
      "trained_no_depletion_prior",
      "trained_rank_only_Laplace",
      "trained_history_summary_logistic",
      "trained_episodic_conditional_table",
      "trained_public_K3_depletion",
      "frozen_CS19_history_logistic",
      "source_known_full_remaining_oracle")
GRID=(0.,.25,.5,.75,1.)
EPS=1e-9
def need(value,reason):
    if not value:raise RuntimeError(reason)
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def source_seed(role,deck_index,rep,i):
    return (6100000 if role=="FIT" else 6300000)+400000*deck_index+10000*rep+i
def total_cards(num_decks):return 52*num_decks
def mass(c,seen,lam):
    return [max(0.,float(c[j])-lam*seen[j]) for j in range(13)]
def higher_or_lower_from_mass(rank,weights):
    return 0 if sum(weights[rank+1:])>=sum(weights[:rank]) else 1

class LearnedDepletion:
    def __init__(self,c,learned_lambda,cap=None):
        self.c=tuple(float(v) for v in c)
        self.lam=float(learned_lambda)
        self.cap=cap
    def choose(self,rank,seen,num_decks,t):
        need(len(seen)==13 and 0<=rank<13,"SOURCE_PUBLIC_RANK_HISTORY_INVALID")
        actual=[int(v) if self.cap is None or i<self.cap else 0
                for i,v in enumerate(seen)]
        return higher_or_lower_from_mass(rank,mass(self.c,actual,self.lam))
    def state(self):
        return {"empirically_FIT_observed_public_rank_baseline":self.c,
                "public_FIT_loglikelihood_calibrated_lambda":self.lam,
                "public_episode_counter_cap":self.cap}

def fit_c_and_lambda(episodes):
    need(len(episodes)==len(REPS)*FIT_N,
         "DEPLETION_PUBLIC_ORIGINAL_FIT_COHORT_SIZE_DRIFT")
    counts=[0]*13
    events=[]
    for ep in episodes:
        stream=ep["original_source_FIT_legal_public_action_rows"]
        first=stream[0]["public_current_rank"]
        counts[first]+=1
        for row in stream:
            counts[row["actual_source_returned_next_public_rank"]]+=1
            events.append(row)
    c=[count/len(episodes) for count in counts]
    need(all(z>0 for z in c) and len(events)>0,
         "ORIGINAL_PUBLIC_FIT_RANK_DISTRIBUTION_EMPTY")
    loglike={}
    for lam in GRID:
        value=0.
        for row in events:
            hist=row["public_seen_rank_hist"]
            w=[max(EPS,c[j]-lam*hist[j]) for j in range(13)]
            true_next=row["actual_source_returned_next_public_rank"]
            value+=math.log(w[true_next]/sum(w))
        loglike[str(lam)]=value
    selected=max(GRID,key=lambda lam:(loglike[str(lam)],-lam))
    return tuple(c),float(selected),loglike

class FittedSummary:
    def __init__(self):
        self.w=[0.]*17
        self.updates=0
    @staticmethod
    def features(rank,seen,num_decks,t):
        need(sum(seen)==t+1,"PUBLIC_FIT_SUMMARY_PREACTION_HISTORY_DRIFT")
        above=sum((4*num_decks-seen[j]) for j in range(rank+1,13))
        below=sum((4*num_decks-seen[j]) for j in range(rank))
        # Source-known 4 per rank is a hard-coded feature approximation,
        # not learned here; document this engineering/source-law privilege.
        return [1.]+[float(rank==j) for j in range(13)]+[
            (above-below)/(52*num_decks),
            (t+1)/(52*num_decks),
            seen[rank]/(4*num_decks)]
    def fit(self,rows,num_decks):
        for epoch in range(12):
            for row in rows:
                y=row["original_binary_next_higher"]
                if y is None:continue
                f=self.features(row["public_current_rank"],row["public_seen_rank_hist"],
                                num_decks,row["public_time_step"])
                z=sum(w*v for w,v in zip(self.w,f))
                p=1./(1.+math.exp(-max(-25,min(25,z))))
                self.w=[w+.08*((float(y)-p)*v-.003*w)
                        for w,v in zip(self.w,f)]
                self.updates+=1
    def choose(self,rank,seen,num_decks,t):
        f=self.features(rank,seen,num_decks,t)
        return 0 if sum(w*v for w,v in zip(self.w,f))>=0. else 1
    def state(self):return {"w":self.w,"updates":self.updates,"epochs":12,
                              "source_known_per_rank_prior_in_features":True}
class LearnedEpisodic:
    BINS=(-.30,-.08,.08,.30)
    def __init__(self):
        self.obs=defaultdict(lambda:[1,1])
        self.rank=TrainedRank()
        self.rows=0
    @classmethod
    def key(cls,rank,seen,t,num_decks):
        above=sum(seen[j] for j in range(rank+1,13))
        below=sum(seen[:rank])
        v=(above-below)/(t+1)
        bucket=sum(v>b for b in cls.BINS)-2
        quartile=min(3,int(4*t/(52*num_decks)))
        return (rank,bucket,quartile)
    def fit(self,rows,num_decks):
        for row in rows:
            self.rank.learn(row)
            y=row["original_binary_next_higher"]
            if y is None:continue
            k=self.key(row["public_current_rank"],row["public_seen_rank_hist"],
                       row["public_time_step"],num_decks)
            self.obs[k][int(y)]+=1
            self.rows+=1
    def choose(self,rank,seen,num_decks,t):
        k=self.key(rank,seen,t,num_decks)
        if k not in self.obs:return self.rank.choose(rank,seen,num_decks,t)
        neg,pos=self.obs[k]
        return 0 if pos>=neg else 1
    def state(self):
        return {"bucket_counts":{str(k):v for k,v in sorted(self.obs.items())},
                "rank_fallback":self.rank.state(),
                "source_real_labeled_examples":self.rows,
                "bins":self.BINS}
def episode(cls,di,rep,i,role,num_decks,policy=None):
    seed=source_seed(role,di,rep,i)
    env=cls(num_decks=num_decks)
    t_start=time.process_time_ns()
    initial,info=env.reset(seed=seed)
    del info
    rank=int(initial)
    need(0<=rank<13 and env.action_space.n==2,
         "ORIGINAL_SOURCE_PUBLIC_RANK_INVALID")
    n=total_cards(num_decks)-1
    seen=[0]*13
    obs=[rank]
    rows=[]
    wins=miss=ties=0
    source_sum=0
    for t in range(n):
        seen[rank]+=1
        need(sum(seen)==t+1 and all(0<=z<=4*num_decks for z in seen),
             "PUBLIC_ONLY_SOURCE_HISTORY_INVALID")
        hist=tuple(seen)
        action=(t+i)%2 if policy is None else int(policy.choose(rank,hist,num_decks,t))
        need(action in (0,1) and env.action_space.contains(action),
             "SOURCE_NATIVE_ILLEGAL_ACTION")
        next_public,r,done,truncated,hidden_info=env.step(action)
        del hidden_info
        next_rank=int(next_public)
        need(0<=next_rank<13 and bool(done)==(t==n-1) and truncated is False,
             "SOURCE_NATIVE_TERMINAL_STEP_COUNT_DRIFT")
        signed=float(r)*total_cards(num_decks)
        need(min(abs(signed-x) for x in (-1,0,1))<1e-8,
             "SOURCE_NATIVE_REAL_REWARD_SCALE_OR_SIGN_INVALID")
        reward_sign=round(signed)
        label=None if reward_sign==0 else bool((action==0)==(reward_sign>0))
        # SOURCE true label is generated solely FROM original reward
        # received AFTER original action. Returned next rank may be used to
        # fit source transition likelihood only at this point.
        rows.append({
            "public_current_rank":rank,"public_seen_rank_hist":hist,
            "public_time_step":t,"original_chosen_legal_action":action,
            "real_original_source_reward_sign":reward_sign,
            "actual_source_returned_next_public_rank":next_rank,
            "original_binary_next_higher":label})
        wins+=int(reward_sign>0)
        miss+=int(reward_sign<0)
        ties+=int(reward_sign==0)
        source_sum+=reward_sign
        obs.append(next_rank)
        rank=next_rank
    need(wins+miss+ties==n and len(obs)==n+1,
         "ORIGINAL_SOURCE_TOTAL_ACTION_MISMATCH")
    return {
        "role":role,"source_seed":seed,"num_decks":num_decks,
        "real_original_source_legal_action_count":n,
        "genuine_source_signed_rewards_sum":source_sum,
        "genuine_source_correct_action_count":wins,
        "genuine_source_incorrect_action_count":miss,
        "genuine_source_tied_action_count":ties,
        "real_original_source_total_episode_reward":source_sum/total_cards(num_decks),
        "actual_public_rank_sequence_SHA256":sha(obs),
        "actual_source_legal_reward_action_rows_SHA256":sha(rows),
        "original_source_FIT_legal_public_action_rows":rows if role=="FIT" else [],
        "original_source_DEV_public_legal_reward_trace":(
            [[x["public_current_rank"],x["original_chosen_legal_action"],
              x["real_original_source_reward_sign"],x["actual_source_returned_next_public_rank"]]
             for x in rows] if role=="DEV" else []),
        "full_original_source_plus_model_CPU_ns":time.process_time_ns()-t_start,
    }
def fit_models(fit,num_decks):
    c,lam,ll=fit_c_and_lambda(fit)
    rows=[r for ep in fit for r in ep["original_source_FIT_legal_public_action_rows"]]
    base=TrainedRank()
    summary=FittedSummary()
    episodic=LearnedEpisodic()
    prior=TrainedLogistic(None)
    t=time.process_time_ns()
    for r in rows:base.learn(r)
    base_fit_cpu=time.process_time_ns()-t
    t=time.process_time_ns();summary.fit(rows,num_decks)
    summary_cpu=time.process_time_ns()-t
    t=time.process_time_ns();episodic.fit(rows,num_decks)
    episodic_cpu=time.process_time_ns()-t
    t=time.process_time_ns()
    for epoch in range(12):
        for r in rows:
            if r["original_binary_next_higher"] is not None:
                prior.fit if False else None
    # Exact CS19 baseline uses .learn_all(fit,num_decks) for frozen 12 passes.
    prior.fit_start=time.process_time_ns()
    prior.learn_all(rows,num_decks)
    prior_cpu=time.process_time_ns()-prior.fit_start
    models={
      ARMS[0]:LearnedDepletion(c,lam,None),
      ARMS[1]:LearnedDepletion(c,0.,None),
      ARMS[2]:base,
      ARMS[3]:summary,
      ARMS[4]:episodic,
      ARMS[5]:LearnedDepletion(c,lam,3),
      ARMS[6]:prior,
      ARMS[7]:SourceKnownFull()}
    met={}
    for name,m in models.items():
        saved=canon(m.state())
        met[name]={
            "source_learned_serialized_parameter_bytes":len(saved.encode()),
            "frozen_source_fit_model_sha256":sha(m.state()),
            "original_public_online_history_counter_slots":(
              0 if name in (ARMS[1],ARMS[2]) else 3 if name==ARMS[5] else 13),
            "original_source_FIT_episodes_seen":len(fit) if name!=ARMS[7] else 0,
            "original_SOURCE_FIT_training_process_CPU_ns":{
              ARMS[2]:base_fit_cpu,ARMS[3]:summary_cpu,ARMS[4]:episodic_cpu,
              ARMS[6]:prior_cpu}.get(name,"shared_rank_priors_and_lambda_fit_measured_below"),
            "full_source_FIT_legal_actions_available":len(rows) if name!=ARMS[7] else 0,
        }
    return models,met,{"source_original_PUBLIC_fit_observed_rank_counts_per_episode":c,
        "learned_depletion_lambda":lam,
        "true_original_source_FIT_next_rank_loglikelihood_candidates":ll,
        "genuine_SOURCE_FIT_legal_labeled_binary_outcomes":
            sum(r["original_binary_next_higher"] is not None for r in rows)}
def eval_models(cls,di,num_decks,models):
    initial={name:sha(model.state()) for name,model in models.items()}
    result={}
    for name,model in models.items():
        e=[episode(cls,di,rep,i,"DEV",num_decks,model)
           for rep in REPS for i in range(DEV_N)]
        mean=sum(z["genuine_source_signed_rewards_sum"] for z in e)/(len(e)*(total_cards(num_decks)-1))
        rr=[sum(z["genuine_source_signed_rewards_sum"] for z in e[rep*DEV_N:(rep+1)*DEV_N])/
            (DEV_N*(total_cards(num_decks)-1)) for rep in REPS]
        result[name]={
            "original_genuine_DEV_resets":len(e),
            "original_genuine_DEV_legal_actions":len(e)*(total_cards(num_decks)-1),
            "true_original_source_reward_per_decision":mean,
            "source_real_reward_per_decision_by_replica":rr,
            "actual_source_correct_action_rate":sum(z["genuine_source_correct_action_count"]
                for z in e)/(len(e)*(total_cards(num_decks)-1)),
            "original_public_source_DEV_episode_data":e,
            "original_source_DEV_trace_SHA256":sha(e),
            "source_plus_model_DEV_CPU_ns":sum(z["full_original_source_plus_model_CPU_ns"] for z in e)}
    need(initial=={name:sha(model.state()) for name,model in models.items()},
         "TEST_TIME_MODEL_MUTATED_ORIGINAL_FIT_PARAMETERS")
    for i in range(len(REPS)*DEV_N):
        obs={result[arm]["original_public_source_DEV_episode_data"][i]["actual_public_rank_sequence_SHA256"]
             for arm in ARMS}
        need(len(obs)==1,"SOURCE_DEV_ORIGINAL_PUBLIC_RANK_SEQUENCES_UNPAIRED")
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    root=Path(args.upstream).resolve()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rec={"schema":"mass.cs20.original_POPGym_FIT_learned_depletion.v1",
         "FIRST_frozen_prereg":FIRST,"source":ORIGINAL,
         "original_R7_native_source_unchanged":True,
         "source_private_hidden_deck_or_info_read":False,
         "trained_native_architecture":False,
         "independently_blinded_source_first_use":False,
         "original_R7_frozen_integration":"BLOCKED_UNCHANGED",
         "disposition":"PUBLIC_CS20_ORIGINAL_SOURCE_PROTOCOL_INVALID","strata":[]}
    fitarchive={"schema":"mass.cs20.original_PUBLIC_FIT_only.v1","strata":[]}
    start=time.process_time_ns()
    try:
        cls=original_class(root)
        seeds=[source_seed(role,di,rep,i) for role,n in
          (("FIT",FIT_N),("DEV",DEV_N)) for di in range(2)
          for rep in REPS for i in range(n)]
        need(len(seeds)==len(set(seeds))==2*2*(FIT_N+DEV_N),
             "SOURCE_FIT_DEV_SEED_CUSTODY_COLLISION")
        conclusions=[]
        for di,num_decks in enumerate(DECK_SIZES):
            t=time.process_time_ns()
            fit=[episode(cls,di,rep,i,"FIT",num_decks)
                 for rep in REPS for i in range(FIT_N)]
            original_fit_cpu=time.process_time_ns()-t
            need(len(fit)==len(REPS)*FIT_N and all(
                z["real_original_source_legal_action_count"]==total_cards(num_decks)-1
                for z in fit),"SOURCE_FIT_EPISODE_COUNT_OR_REWARD_DRIFT")
            fitarchive["strata"].append({
                "original_num_decks":num_decks,"genuine_original_source_FIT_episodes":fit})
            model_start=time.process_time_ns()
            models,resources,learned=fit_models(fit,num_decks)
            learned["source_FIT_training_CPU_ns_shared_candidate_and_all_alternatives"]=(
                time.process_time_ns()-model_start)
            dev=eval_models(cls,di,num_decks,models)
            score=lambda n:dev[n]["true_original_source_reward_per_decision"]
            learned_gain=score(ARMS[0])-score(ARMS[2])
            no_memory_gain=score(ARMS[0])-score(ARMS[1])
            replica_gain=[dev[ARMS[0]]["source_real_reward_per_decision_by_replica"][i]-
                          dev[ARMS[2]]["source_real_reward_per_decision_by_replica"][i]
                          for i in range(2)]
            best_learned=max(score(n) for n in (ARMS[3],ARMS[4],ARMS[6]))
            qualifies=(learned_gain>=.005 and no_memory_gain>=.005 and
                        all(x>0 for x in replica_gain) and
                        score(ARMS[0])>=score(ARMS[7])-.015 and
                        score(ARMS[0])>=best_learned-.015)
            conclusions.append(qualifies)
            rec["strata"].append({
                "num_decks":num_decks,
                "actual_original_source_FIT_resets":len(fit),
                "actual_original_source_FIT_legal_actions":
                    len(fit)*(total_cards(num_decks)-1),
                "true_SOURCE_original_FIT_public_SHA256":sha(fit),
                "actual_original_source_FIT_CPU_ns":original_fit_cpu,
                "actual_source_FIT_learned_history_representation":learned,
                "full_cost_frozen_FIT_model_resource_receipts":resources,
                "genuine_source_original_DEV_models":dev,
                "learned_depletion_minus_rank_only_real_reward_per_step":learned_gain,
                "learned_depletion_minus_same_FIT_no_depletion_reward_per_step":no_memory_gain,
                "learned_depletion_minus_rank_only_by_replica":replica_gain,
                "learned_depletion_minus_original_source_known_oracle":score(ARMS[0])-score(ARMS[7]),
                "learned_depletion_minus_best_learned_conventional":score(ARMS[0])-best_learned,
                "preregistered_original_deck_stratum_advancement":qualifies})
            print("CS20_DECK="+str(num_decks)+" ORIGINAL_REAL_REWARD="+
                  canon({name:round(score(name),6) for name in ARMS})+
                  " TRAINED_LAMBDA="+str(learned["learned_depletion_lambda"]),flush=True)
        rec["original_source_FIT_resets"]=2*len(REPS)*FIT_N
        rec["original_source_DEV_resets"]=2*len(ARMS)*len(REPS)*DEV_N
        rec["original_SOURCE_total_reset_episodes"]=rec["original_source_FIT_resets"]+rec["original_source_DEV_resets"]
        rec["original_SOURCE_real_step_action_count"]=sum(
            (len(REPS)*FIT_N+len(ARMS)*len(REPS)*DEV_N)*(total_cards(n)-1)
            for n in DECK_SIZES)
        need(rec["original_SOURCE_total_reset_episodes"]==2240 and
             rec["original_SOURCE_real_step_action_count"]==230720,
             "ORIGINAL_SOURCE_PROSPECTIVE_TOTAL_ACTIONS_INVALID")
        rec["original_SOURCE_public_SHARED_FIT_SHA256"]=sha(fitarchive)
        rec["disposition"]=(
            "PUBLIC_CS20_LEARNED_CONVENTIONAL_DEPLETION_HISTORY_ELIGIBLE_FOR_NATIVE_STUDY"
            if all(conclusions) else "PUBLIC_CS20_LEARNED_HISTORY_NO_QUALIFIED_ADVANTAGE")
        rec["native_novel_cognition_or_efficiency"]="NOT_TESTED"
        rec["independent_unfamiliar_family_first_use"]="NONE_PUBLICLY_INSPECTED_POPGYM"
    except Exception as exc:
        rec["first_failure"]=type(exc).__name__+":"+str(exc)[:1100]
    finally:
        rec["original_SOURCE_and_all_models_process_CPU_ns"]=time.process_time_ns()-start
        rec["process_inclusive_RSS_KiB_not_model_isolated"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs20-original-POPGym-learned-history-receipt.json").write_text(
            json.dumps(rec,sort_keys=True,indent=2)+"\n")
        (out/"cs20-original-POPGym-public-FIT-history.json").write_text(canon(fitarchive)+"\n")
    print("CS20_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS20_ORIGINAL_SOURCE_PROTOCOL_INVALID" else 0
if __name__=="__main__":
    raise SystemExit(main())
