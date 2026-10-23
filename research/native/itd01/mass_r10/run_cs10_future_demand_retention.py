#!/usr/bin/env python3
"""CS10: original POPGym public FIT-learned future reappearance eviction.

This code NEVER accesses POPGym private deck, get_state, state, card oracle
or returned info. Training labels inspect only later ORIGINAL PUBLIC FIT
action->card observations. The 6-feature basis and K4 cache are handcrafted.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
import math
from pathlib import Path
import random
import resource
import time

from run_cs08_original_binding_eviction import (
    MemoryWithEviction, source_identity, CARDS, FACE_DOWN, MAX_STEPS,
    check, public_board, canon, sha
)

FIRST="a0a7839ba3ab29bdfee1ae16bb8c04265582e075"
K=4
REPS=(0,1,2)
N={"FIT":24,"VALID":16,"DEV":48}
CANDIDATE="FIT_learned_logistic_future_demand_K4"
TABLE="FIT_trained_tabular_future_demand_K4"
SHUFFLED="FIT_logistic_shuffled_labels_K4"
FREQUENT="strong_fixed_frequent_K4"
FIFO="fixed_FIFO_K4"
LRU="fixed_LRU_K4"
FULL="full_conventional_K52_LRU"
ARMS=(CANDIDATE,TABLE,SHUFFLED,FREQUENT,FIFO,LRU,FULL)
PAIRS=((CANDIDATE,FREQUENT),(CANDIDATE,TABLE),(CANDIDATE,SHUFFLED),
       (FREQUENT,FIFO),(FREQUENT,LRU))
ETA=.08
L2=.002
PASSES=8
BOOT_N=3000
FUTURE_HORIZON=24

def public_seed(role,rep,i):
    return {"FIT":1250000,"VALID":1260000,"DEV":1270000}[role]+1000*rep+i

def public_features(mem,index):
    # All six features depend ONLY on current public cache/recorded earlier flips.
    rank=mem.cache[index]
    last_age=max(0,min(MAX_STEPS,mem.decisions-mem.last_access[index]))
    insert_age=max(0,min(MAX_STEPS,mem.decisions-mem.insert_at[index]))
    support=sum(v==rank for j,v in mem.cache.items() if j!=index)
    return [1.0, min(mem.rank_seen[rank],4)/4.0,
            1.0-last_age/MAX_STEPS,
            insert_age/MAX_STEPS,
            min(support,4)/4.0,
            min(mem.decisions,MAX_STEPS)/MAX_STEPS]

class LearnedLogistic:
    def __init__(self):
        self.weights=[0.0]*6
        self.updates=0
    def fit(self,examples,shuffle_labels=False,rep=0):
        labels=[x["future_public_reappearance"] for x in examples]
        if shuffle_labels:
            rng=random.Random(246810+rep)
            rng.shuffle(labels)
        for _ in range(PASSES):
            for row,y in zip(examples,labels):
                xx=row["source_public_features"]
                p=self.predict(xx)
                for i,f in enumerate(xx):
                    self.weights[i]+=ETA*((y-p)*f-L2*self.weights[i])
                self.updates+=1
        check(self.updates==PASSES*len(examples),"LOGISTIC_FIT_UPDATE_BUDGET_INVALID")
        check(any(abs(x)>1e-8 for x in self.weights),"LOGISTIC_NOT_TRAINED")
    def predict(self,vec):
        z=sum(x*w for x,w in zip(vec,self.weights))
        z=max(-30.0,min(30.0,z))
        return 1.0/(1.0+math.exp(-z))
    def state(self):
        return {"learner":"FIT_supervised_future_public_recurrence_logistic",
                "weights":self.weights,"updates":self.updates,"eta":ETA,
                "l2":L2,"passes":PASSES}

def tabular_key(f):
    rank_seen=max(0,min(4,int(round(f[1]*4))))
    recency_age=max(0.0,min(1.0,1.0-f[2]))
    bucket=max(0,min(3,int(4*recency_age*MAX_STEPS/105)))
    support=int(f[4]>0)
    return (rank_seen,bucket,support)

class LearnedTabular:
    def __init__(self):
        self.counts={}
        self.updates=0
    def fit(self,examples):
        for e in examples:
            k=tabular_key(e["source_public_features"])
            count=self.counts.setdefault(k,[1,1])
            count[e["future_public_reappearance"]]+=1
            self.updates+=1
        check(self.updates==len(examples),"TABULAR_FIT_BUDGET")
    def predict(self,vec):
        n=self.counts.get(tabular_key(vec),[1,1])
        return n[1]/(n[0]+n[1])
    def state(self):
        return {"learner":"FIT_conventional_tabular_future_public_recurrence",
                "counts":[[list(k),v] for k,v in sorted(self.counts.items())],
                "updates":self.updates}

class PredictionCache(MemoryWithEviction):
    def __init__(self,capacity,mode,learner=None,log=False):
        check(capacity in (K,52),"ORIGINAL_MEMORY_CAPACITY_UNSUPPORTED")
        check(mode in ("frequent","fifo","lru","prediction"),
              "ORIGINAL_MODE_OUTSIDE_FROZEN_FAMILY")
        super().__init__(capacity,"frequent" if mode=="prediction" else mode)
        self.mode=mode
        self.learner=learner
        self.log=log
        self.snapshots=[]
    def _priority(self,index):
        x=public_features(self,index)
        if self.log:
            # This snapshot is taken before the cache evicts anything;
            # future labels get attached AFTER source episode ends.
            self.snapshots.append({
                "source_public_step":self.decisions,
                "cached_original_position":index,
                "cached_public_rank":self.cache[index],
                "source_public_features":x})
        if self.learner is None:
            return super()._priority(index)
        value=self.learner.predict(x)
        check(0<=value<=1 and math.isfinite(value),"LEARNED_SCORE_NOT_PROBABILITY")
        return (value,self.insert_at[index],index)

def original_episode(Source,seed_value,capacity,mode,learner=None,fit_trace=False):
    source=Source()
    mem=PredictionCache(capacity,mode,learner,fit_trace)
    observations=[]
    original_stream=hashlib.sha256()
    try:
        observed,_ignored_reset_info=source.reset(seed=seed_value)
        board=public_board(observed)
        check(set(board)=={FACE_DOWN},"ORIGINAL_PUBLIC_RESET_NOT_HIDDEN")
        reward=0.
        steps=0
        summed_reward=0.
        matches=0
        final_terminated=final_truncated=False
        for step in range(MAX_STEPS):
            a=mem.choose(board,reward,step)
            check(type(a) is int and 0<=a<CARDS,"SOURCE_CARD_ACTION_INVALID")
            obs,reward,terminated,truncated,_ignored_step_info=source.step(a)
            board=public_board(obs)
            rank=board[a]
            check(0<=rank<FACE_DOWN,"CHOSEN_CARD_NOT_PUBLICLY_REVEALED")
            reward=float(reward)
            check(-1<=reward<=1,"ORIGINAL_SOURCE_REWARD_INVALID")
            event={"step":step,"chosen_public_position":a,
                   "revealed_original_public_rank":rank,
                   "original_public_reward":reward}
            observations.append(event)
            original_stream.update((canon({"step":step,"chosen_action":a,
                                             "whole_public_board":board,
                                             "source_reward":reward})+"\n").encode())
            steps+=1
            matches+=int(reward>0)
            summed_reward+=reward
            final_terminated=bool(terminated)
            final_truncated=bool(truncated)
            if terminated or truncated:break
        check(0<steps<=MAX_STEPS and (final_terminated or final_truncated),
              "ORIGINAL_GAME_DID_NOT_END")
        state=mem.audit()
        check(state["peak_cache_entries"]<=capacity,"SOURCE_CACHE_CAP_VIOLATION")
        row={
            "source_seed":seed_value,
            "source_native_original_steps":steps,
            "source_native_original_reward":summed_reward,
            "source_matched_pairs":matches,
            "real_evictions":state["actual_evictions"],
            "peak_unmatched_assoc_cache":state["peak_cache_entries"],
            "source_end":final_terminated,
            "source_truncated":final_truncated,
            "eviction_log_sha256":state["eviction_events_sha256"],
            "public_source_actions_rewards_sha256":original_stream.hexdigest(),
            "original_source_full_policy_state_bytes":len(canon(state).encode()),
            "model_state_sha256":sha(learner.state()) if learner else None,
        }
        if fit_trace:
            rows=[]
            for entry in mem.snapshots:
                t=entry["source_public_step"]
                rank=entry["cached_public_rank"]
                idx=entry["cached_original_position"]
                label=int(any(
                    t<=e["step"]<t+FUTURE_HORIZON and
                    e["revealed_original_public_rank"]==rank and
                    e["chosen_public_position"]!=idx
                    for e in observations))
                rows.append({**entry,"future_public_reappearance":label})
            row["FIT_public_action_revelation_stream"]=observations
            row["FIT_original_cache_examples"]=rows
        return row
    finally:
        source.close()

def fit_models(examples,rep):
    log=LearnedLogistic()
    tab=LearnedTabular()
    shuffled=LearnedLogistic()
    cpu={}
    for name,model in ((CANDIDATE,log),(TABLE,tab),(SHUFFLED,shuffled)):
        start=time.process_time_ns()
        if name==SHUFFLED:model.fit(examples,True,rep)
        else:model.fit(examples)
        cpu[name]=time.process_time_ns()-start
    return {
        CANDIDATE:log,TABLE:tab,SHUFFLED:shuffled
    },{
        name:{"FIT_training_CPU_ns":cpu[name],
              "serialized_model_bytes":len(canon(model.state()).encode()),
              "FIT_model_sha256":sha(model.state()),
              "parameters":model.state()}
        for name,model in ((CANDIDATE,log),(TABLE,tab),(SHUFFLED,shuffled))
    }

def eval_role(Source,role,rep,models):
    configurations={
        CANDIDATE:(K,"prediction",models[CANDIDATE]),
        TABLE:(K,"prediction",models[TABLE]),
        SHUFFLED:(K,"prediction",models[SHUFFLED]),
        FREQUENT:(K,"frequent",None),
        FIFO:(K,"fifo",None),
        LRU:(K,"lru",None),
        FULL:(52,"lru",None)
    }
    frozen={k:sha(v.state()) for k,v in models.items()}
    output={}
    for arm,(capacity,mode,learner) in configurations.items():
        start=time.process_time_ns()
        rows=[original_episode(Source,public_seed(role,rep,i),capacity,mode,learner)
              for i in range(N[role])]
        check(len(rows)==N[role],"SOURCE_SCORE_EPISODE_COUNT")
        output[arm]={
            "capacity_unmatched_associations":capacity,
            "real_episodes":N[role],
            "source_native_action_calls":sum(x["source_native_original_steps"] for x in rows),
            "original_source_mean_reward":sum(x["source_native_original_reward"] for x in rows)/N[role],
            "original_source_total_reward":sum(x["source_native_original_reward"] for x in rows),
            "real_source_matches":sum(x["source_matched_pairs"] for x in rows),
            "episodes_with_real_evictions":sum(x["real_evictions"]>0 for x in rows),
            "real_total_evictions":sum(x["real_evictions"] for x in rows),
            "original_observed_peak_cache":max(x["peak_unmatched_assoc_cache"] for x in rows),
            "full_policy_cache_aux_state_max_serialized_bytes":
                max(x["original_source_full_policy_state_bytes"] for x in rows),
            "frozen_FIT_model_bytes":len(canon(learner.state()).encode()) if learner else 0,
            "original_source_inclusive_cpu_ns":time.process_time_ns()-start,
            "every_original_scored_seed_outcome":rows,
            "raw_scored_source_outcome_sha256":sha(rows),
        }
    check(frozen=={k:sha(v.state()) for k,v in models.items()},
          "FITTED_MODEL_CHANGED_DURING_ORIGINAL_SCORE")
    return output

def paired_bootstrap(x,y,rep,index):
    a=x["every_original_scored_seed_outcome"]
    b=y["every_original_scored_seed_outcome"]
    check(len(a)==len(b)==N["DEV"],"PAIRED_SCORE_COUNT_MISMATCH")
    deltas=[]
    for left,right in zip(a,b):
        check(left["source_seed"]==right["source_seed"],"PAIRED_SOURCE_SEED_DRIFT")
        deltas.append(left["source_native_original_reward"]-
                      right["source_native_original_reward"])
    rng=random.Random(20261023+100*rep+index)
    means=[]
    for _ in range(BOOT_N):
        means.append(sum(deltas[rng.randrange(len(deltas))]
                         for _ in range(len(deltas)))/len(deltas))
    means.sort()
    return {
        "mean_source_reward_delta":sum(deltas)/len(deltas),
        "paired_bootstrap_resamples":BOOT_N,
        "bootstrap_rng_seed":20261023+100*rep+index,
        "paired_95_lower":means[int(.025*BOOT_N)],
        "paired_95_upper":means[int(.975*BOOT_N)-1],
        "every_paired_original_source_reward_delta":deltas,
        "pair_delta_sha256":sha(deltas)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    rec={
        "schema":"mass.cs10.original_public_shared_fit_predictive_eviction.v1",
        "frozen_FIRST_prereg_sha":FIRST,
        "source_role":"PUBLIC_DEVELOPMENT_ONLY",
        "original_source_modified":False,
        "public_observation_only":True,
        "FIT_labels_are_future_legal_PUBLIC_observations_not_source_private":True,
        "FIT_models_get_IDENTICAL_experience_examples":True,
        "source_trajectories_after_FIT_are_not_identical_across_policies":True,
        "memory_structure_and_feature_design_are_handcrafted":True,
        "native_yggdrasil_or_wingless_model_tested":False,
        "complete_isolated_cpu_rss_parity_established":False,
        "new_unfamiliar_source_scientific_first_use":False,
        "controller_science_admission_observed":False,
        "disposition":"PUBLIC_CS10_INVALID_OR_SOURCE_LEAK",
        "replicas":[]}
    FIT={"schema":"mass.cs10.public-original-identical-FIT.v1","replicas":[]}
    try:
        path=Path(args.upstream).resolve()
        rec["original_external_source_verified"]=source_identity(path)
        from popgym.envs.concentration import ConcentrationHard
        check(Path(inspect.getfile(ConcentrationHard)).resolve() ==
              path/"popgym"/"envs"/"concentration.py",
              "NOT_ORIGINAL_SOURCE_CONCENTRATION")
        consumed=set()
        for rep in REPS:
            fit=[original_episode(ConcentrationHard,public_seed("FIT",rep,i),
                                  K,"frequent",fit_trace=True)
                 for i in range(N["FIT"])]
            examples=[entry for ep in fit for entry in ep["FIT_original_cache_examples"]]
            count_one=sum(e["future_public_reappearance"] for e in examples)
            check(len(examples)>=120 and 0<count_one<len(examples),
                  "PUBLIC_CS10_FIT_IDENTIFIABILITY_NO_GO")
            for role,n in N.items():
                for i in range(n):
                    s=public_seed(role,rep,i)
                    check(s not in consumed,"ROLE_SOURCE_SEED_REUSE")
                    consumed.add(s)
            models,fit_training=fit_models(examples,rep)
            valid=eval_role(ConcentrationHard,"VALID",rep,models)
            dev=eval_role(ConcentrationHard,"DEV",rep,models)
            contrasts={
                left+"_minus_"+right:paired_bootstrap(dev[left],dev[right],rep,index)
                for index,(left,right) in enumerate(PAIRS)}
            def diff(a,b):
                return contrasts[a+"_minus_"+b]
            binding=all(
                dev[a]["original_observed_peak_cache"]==K and
                dev[a]["episodes_with_real_evictions"]>=45 for a in ARMS[:-1])
            binding=binding and dev[FULL]["original_observed_peak_cache"]>=6
            superiority=(
                diff(CANDIDATE,FREQUENT)["mean_source_reward_delta"]>=.04 and
                diff(CANDIDATE,TABLE)["mean_source_reward_delta"]>=.03 and
                diff(CANDIDATE,SHUFFLED)["mean_source_reward_delta"]>=.04 and
                diff(CANDIDATE,FREQUENT)["paired_95_lower"]>0 and
                diff(CANDIDATE,TABLE)["paired_95_lower"]>0)
            FIT["replicas"].append({
                "replica":rep,
                "genuine_original_public_FIT_source_episodes":fit,
                "same_observation_training_samples":examples,
                "FIT_examples_sha256":sha(examples)})
            result={
                "replica":rep,
                "FIT_source_original_episode_count":len(fit),
                "FIT_source_original_action_calls":sum(z["source_native_original_steps"] for z in fit),
                "FIT_actual_source_capacity_evictions":sum(z["real_evictions"] for z in fit),
                "FIT_public_candidate_sample_count":len(examples),
                "FIT_public_future_reappearance_positive_count":count_one,
                "FIT_public_future_reappearance_negative_count":len(examples)-count_one,
                "FIT_same_training_examples_sha256":sha(examples),
                "learned_models_frozen_training_receipt":fit_training,
                "VALID":valid,"DEV":dev,
                "per_original_seed_paired_reward_bootstrap":contrasts,
                "actual_K4_memory_pressure_qualified":binding,
                "candidate_predeclared_strong_learned_value_gain":binding and superiority,
                "source_process_peak_RSS_kib_NOT_model_isolated":
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            rec["replicas"].append(result)
            print("CS10_REPLICA="+str(rep)+" FIT_LABELS="+str(len(examples))+
                  " DEV_ORIGINAL_MEANS="+canon({
                    k:round(v["original_source_mean_reward"],6)
                    for k,v in dev.items()}),flush=True)
        check(len(consumed)==3*sum(N.values()),"PUBLIC_ROLE_ID_DUPLICATED")
        rec["genuine_source_original_episode_instances"]=3*(24+7*(16+48))
        rec["genuine_source_original_action_calls"]=sum(
            sum(e["source_native_original_steps"] for e in fit["genuine_original_public_FIT_source_episodes"])
            for fit in FIT["replicas"])+sum(
            sum(v["source_native_action_calls"] for v in rep[role].values())
            for rep in rec["replicas"] for role in ("VALID","DEV"))
        check(rec["genuine_source_original_episode_instances"]==1416
              and 0<rec["genuine_source_original_action_calls"]<=1416*MAX_STEPS,
              "ORIGINAL_GLOBAL_SOURCE_BUDGET")
        rec["original_shared_public_FIT_sha256"]=sha(FIT)
        if not all(r["actual_K4_memory_pressure_qualified"] for r in rec["replicas"]):
            rec["disposition"]="PUBLIC_CS10_MEMORY_PRESSURE_NO_GO"
        elif all(r["candidate_predeclared_strong_learned_value_gain"] for r in rec["replicas"]):
            rec["disposition"]="PUBLIC_CS10_LEARNED_VALUE_ADVANTAGE_PUBLIC_ONLY"
        else:
            rec["disposition"]="PUBLIC_CS10_LEARNED_VALUE_NO_GAIN"
        rec["native_new_cognition_or_source_unfamiliar_transfer"]="NOT_ESTABLISHED"
    except Exception as exc:
        rec["first_failure"]=type(exc).__name__+":"+str(exc)[:850]
    finally:
        (out/"cs10-public-identical-fit-original-source.json").write_text(canon(FIT)+"\n")
        (out/"cs10-original-source-scored-per-seed-receipt.json").write_text(
            json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print("CS10_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS10_INVALID_OR_SOURCE_LEAK" else 0

if __name__=="__main__":
    raise SystemExit(main())
