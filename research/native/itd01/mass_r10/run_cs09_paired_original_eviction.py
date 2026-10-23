#!/usr/bin/env python3
"""CS09 prospective source-native paired seeded eviction replication.

Uses original POPGym ConcentrationHard reset/step only. Inherits CS08
hand-coded original public matcher and bounded cache, does not modify source.
Actual per-seed original rewards and eviction observables retained.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from run_cs08_original_binding_eviction import (
    MemoryWithEviction, source_identity, CARDS, FACE_DOWN, MAX_STEPS,
    check, public_board, canon, sha
)

FIRST="effc828b9fba5e2b5015f5e933ae9713d4b2dac6"
UPSTREAM="410d5aa626dae8024f498354d8781a0d1870c399"
N={"FIT":20,"VALID":12,"DEV":48}
REPS=(0,1,2)
K4=4
MENU=("frequent","hybrid_025","hybrid_100","hybrid_400","novelty","rank_support")
SELECT="FIT_selected_K4"
FREQ="strong_fixed_frequent_K4"
FIFO="fixed_FIFO_K4"
LRU="fixed_LRU_K4"
RANK="fixed_rank_support_K4"
FULL="full_conventional_K52"
ARMS=(SELECT,FREQ,FIFO,LRU,RANK,FULL)
COMPARE=(
 ("fixed_freq_minus_FIFO",FREQ,FIFO),
 ("fixed_freq_minus_LRU",FREQ,LRU),
 ("selected_minus_strong_freq",SELECT,FREQ),
 ("selected_minus_FIFO",SELECT,FIFO),
 ("selected_minus_LRU",SELECT,LRU),
 ("selected_minus_rank_support",SELECT,RANK),
)
BOOT_N=5000

def seed(role,rep,i):
    return {"FIT":1200000,"VALID":1210000,"DEV":1220000}[role]+1000*rep+i

class ProspectiveMemory(MemoryWithEviction):
    """K4 source-public cache; FIT-selected extra numerical factor only."""
    def __init__(self,capacity,mode):
        check(capacity in (4,52),"CS09_MEMORY_CAPACITY_INVALID")
        check(mode in (*MENU,"fifo","lru"),"UNKNOWN_FROZEN_EVICTION_MODE")
        super().__init__(capacity,"frequent" if mode.startswith("hybrid_") else mode)
        self.mode=mode
    def _priority(self,index):
        if not self.mode.startswith("hybrid_"):
            return super()._priority(index)
        factor={"hybrid_025":.25,"hybrid_100":1.0,"hybrid_400":4.0}[self.mode]
        public_rank=self.cache[index]
        score=(float(self.rank_seen[public_rank])
               +factor*self.last_access[index]/104.0)
        return (score,self.insert_at[index],index)

def original_episode(Source,reset_seed,capacity,mode):
    original=Source()
    memory=ProspectiveMemory(capacity,mode)
    try:
        observation,_discard_original_info=original.reset(seed=reset_seed)
        board=public_board(observation)
        check(set(board)=={FACE_DOWN},"SOURCE_ORIGINAL_RESET_UNEXPECTED")
        reward=0.0
        reward_sum=0.0
        successes=0
        steps=0
        transcript=hashlib.sha256()
        terminated=truncated=False
        for index in range(MAX_STEPS):
            action=memory.choose(board,reward,index)
            check(type(action) is int and 0<=action<CARDS,"SOURCE_ILLEGAL_ACTION")
            next_obs,reward,terminated,truncated,_drop_private_info=original.step(action)
            board=public_board(next_obs)
            reward=float(reward)
            check(-1<=reward<=1,"SOURCE_REWARD_RANGE_DRIFT")
            event={"step":index,"original_public_board":board,
                   "action":action,"original_reward":reward}
            transcript.update((canon(event)+"\n").encode())
            reward_sum+=reward
            successes+=int(reward>0)
            steps+=1
            if terminated or truncated:break
        check(0<steps<=MAX_STEPS and (terminated or truncated),
              "ORIGINAL_ENV_TERMINATION_OR_BUDGET")
        state=memory.audit()
        check(state["capacity"]==capacity and
              state["peak_cache_entries"]<=capacity,
              "ORIGINAL_SOURCE_ACTUAL_CAPACITY_INVALID")
        return {
            "seed":reset_seed,
            "reward_sum":reward_sum,
            "successful_matched_pairs":successes,
            "source_legal_steps":steps,
            "actual_eviction_count":state["actual_evictions"],
            "observed_peak_association_entries":state["peak_cache_entries"],
            "original_terminated":bool(terminated),
            "original_truncated":bool(truncated),
            "eviction_events_sha256":state["eviction_events_sha256"],
            "public_action_board_reward_trace_sha256":transcript.hexdigest(),
            "complete_serialized_state_bytes":len(canon(state).encode()),
            "final_state_sha256":sha(state),
        }
    finally:
        original.close()

def execute_policy(Source,role,rep,mode,capacity):
    start=time.process_time_ns()
    rows=[original_episode(Source,seed(role,rep,i),capacity,mode)
          for i in range(N[role])]
    check(len(rows)==N[role],"ORIGINAL_ROLE_EPISODE_MISSING")
    actions=sum(x["source_legal_steps"] for x in rows)
    check(0<actions<=N[role]*MAX_STEPS,"ORIGINAL_ROLE_SOURCE_ACTION_BUDGET")
    return {
        "mode":mode,"capacity":capacity,"original_episodes":len(rows),
        "original_action_calls":actions,
        "original_reward_sum":sum(x["reward_sum"] for x in rows),
        "original_reward_mean":sum(x["reward_sum"] for x in rows)/len(rows),
        "matched_pairs":sum(x["successful_matched_pairs"] for x in rows),
        "original_evictions":sum(x["actual_eviction_count"] for x in rows),
        "real_eviction_episode_count":sum(x["actual_eviction_count"]>0 for x in rows),
        "actual_maximum_cache_occupancy":max(x["observed_peak_association_entries"] for x in rows),
        "complete_serialized_state_max_bytes":max(x["complete_serialized_state_bytes"] for x in rows),
        "original_source_inclusive_cpu_ns":time.process_time_ns()-start,
        "per_seed_original_outcomes":rows,
        "per_seed_rows_sha256":sha(rows),
    }

def paired_bootstrap(a,b,rep,idx):
    ar=a["per_seed_original_outcomes"]
    br=b["per_seed_original_outcomes"]
    check(len(ar)==len(br)==N["DEV"],"PAIRED_BOOTSTRAP_SOURCE_COUNT_DRIFT")
    deltas=[]
    for left,right in zip(ar,br):
        check(left["seed"]==right["seed"],"PAIRED_SOURCE_SEED_IDENTITY_DRIFT")
        deltas.append(left["reward_sum"]-right["reward_sum"])
    rng=random.Random(20261023+100*rep+idx)
    means=[]
    for _ in range(BOOT_N):
        means.append(sum(deltas[rng.randrange(len(deltas))]
                         for _ in range(len(deltas)))/len(deltas))
    means.sort()
    return {"mean_original_episode_reward_delta":sum(deltas)/len(deltas),
            "paired_bootstrap_n":BOOT_N,
            "bootstrap_seed":20261023+100*rep+idx,
            "paired_95_percentile_lower":means[int(.025*BOOT_N)],
            "paired_95_percentile_upper":means[int(.975*BOOT_N)-1],
            "per_seed_reward_deltas":deltas,
            "per_seed_deltas_sha256":sha(deltas)}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--upstream",required=True)
    cli.add_argument("--out",required=True)
    args=cli.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    receipt={
        "schema":"mass.cs09.prospective_original_paired_eviction.v1",
        "frozen_first_prereg_git_sha":FIRST,
        "source_is_original_external_public_development":True,
        "source_owned_private_fields_used":False,
        "original_source_FIT_trajectories_identical_across_arms":False,
        "menu_is_handcrafted_not_end_to_end_learned":True,
        "all_K4_arms_include_common_auxiliary_public_state":True,
        "model_RSS_or_CPU_isolated_and_matched":False,
        "protected_source_or_independently_unfamiliar_first_use":False,
        "native_wingless_yggdrasil_learner_tested":False,
        "controller_scientific_admission_observed":False,
        "disposition":"PUBLIC_CS09_INVALID_OR_SOURCE_DRIFT",
        "replicas":[]}
    fit_records={"schema":"mass.cs09.original_source_new_FIT_per_seed.v1","replicas":[]}
    try:
        path=Path(args.upstream).resolve()
        receipt["original_source"]=source_identity(path)
        from popgym.envs.concentration import ConcentrationHard
        import inspect
        check(Path(inspect.getfile(ConcentrationHard)).resolve() ==
              path/"popgym"/"envs"/"concentration.py",
              "ORIGINAL_CONCENTRATION_CLASS_DRIFT")
        seen=set()
        for rep in REPS:
            fit={name:execute_policy(ConcentrationHard,"FIT",rep,name,K4) for name in MENU}
            winner=max(MENU,key=lambda name:(fit[name]["original_reward_sum"],
                                             -MENU.index(name)))
            models={
                SELECT:(K4,winner),FREQ:(K4,"frequent"),
                FIFO:(K4,"fifo"),LRU:(K4,"lru"),
                RANK:(K4,"rank_support"),FULL:(52,"lru")}
            val={arm:execute_policy(ConcentrationHard,"VALID",rep,mode,capacity)
                 for arm,(capacity,mode) in models.items()}
            dev={arm:execute_policy(ConcentrationHard,"DEV",rep,mode,capacity)
                 for arm,(capacity,mode) in models.items()}
            for role,count in N.items():
                for i in range(count):
                    s=seed(role,rep,i)
                    check(s not in seen,"PUBLIC_SOURCE_ROLE_OVERLAP")
                    seen.add(s)
            binding=(all(dev[a]["real_eviction_episode_count"]>=45 and
                         dev[a]["actual_maximum_cache_occupancy"]==4 for a in ARMS[:5])
                     and dev[FULL]["actual_maximum_cache_occupancy"]>=6)
            contrasts={name:paired_bootstrap(dev[a],dev[b],rep,i)
                       for i,(name,a,b) in enumerate(COMPARE)}
            gain_vs_control=(
                contrasts["selected_minus_strong_freq"]["mean_original_episode_reward_delta"]>=.04
                and contrasts["selected_minus_strong_freq"]["paired_95_percentile_lower"]>0
                and contrasts["selected_minus_FIFO"]["mean_original_episode_reward_delta"]>=.04
                and contrasts["selected_minus_LRU"]["mean_original_episode_reward_delta"]>=.04
                and contrasts["selected_minus_rank_support"]["mean_original_episode_reward_delta"]>=.03
            )
            freq_rep=all(
                contrasts[name]["mean_original_episode_reward_delta"]>=.05
                and contrasts[name]["paired_95_percentile_lower"]>0
                for name in ("fixed_freq_minus_FIFO","fixed_freq_minus_LRU"))
            fit_records["replicas"].append({
                "replica":rep,"all_FIT_menu_public_original_episodes":fit,
                "selected_heuristic":winner})
            result={
                "replica":rep,"FIT_selection":winner,
                "actual_original_FIT_games":sum(z["original_episodes"] for z in fit.values()),
                "FIT_model_selection_scores":{n:z["original_reward_sum"] for n,z in fit.items()},
                "VALID":val,"DEV":dev,
                "paired_original_reward_contrasts":contrasts,
                "actual_K4_binding_verified":binding,
                "CS08_fixed_frequency_heuristic_prospectively_replicated":binding and freq_rep,
                "new_fitted_selector_vs_strong_conventional_positive":binding and gain_vs_control,
                "process_inclusive_maxrss_kib_not_isolated_model":
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            receipt["replicas"].append(result)
            print("CS09_REPLICA="+str(rep)+" SELECTED="+winner+" DEV="+canon({
                n:{"r":round(z["original_reward_mean"],6),
                   "e":z["real_eviction_episode_count"]}
                for n,z in dev.items()}),flush=True)
        check(len(seen)==3*sum(N.values()),"SOURCE_UNIQUE_SPLIT_IDS_INVALID")
        receipt["original_source_games"]=3*(6*20+6*12+6*48)
        receipt["original_source_legal_actions"]=sum(
            sum(z["original_action_calls"] for z in fit["all_FIT_menu_public_original_episodes"].values())
            for fit in fit_records["replicas"])+sum(
            sum(z["original_action_calls"] for z in r[role].values())
            for r in receipt["replicas"] for role in ("VALID","DEV"))
        check(receipt["original_source_games"]==1440 and
              0<receipt["original_source_legal_actions"]<=1440*MAX_STEPS,
              "TOTAL_SOURCE_BUDGET_INVALID")
        receipt["new_original_FIT_transcripts_sha256"]=sha(fit_records)
        receipt["CS08_fixed_frequency_advantage_replication_all_replicas"]=all(
            x["CS08_fixed_frequency_heuristic_prospectively_replicated"] for x in receipt["replicas"])
        if not all(x["actual_K4_binding_verified"] for x in receipt["replicas"]):
            receipt["disposition"]="PUBLIC_CS09_INSUFFICIENT_ACTUAL_BINDING"
        elif all(x["new_fitted_selector_vs_strong_conventional_positive"] for x in receipt["replicas"]):
            receipt["disposition"]="PUBLIC_CS09_FITTED_HEURISTIC_ADVANTAGE_PUBLIC_ONLY"
        else:
            receipt["disposition"]="PUBLIC_CS09_NO_GAIN_VS_STRONG_FREQUENT"
        receipt["new_native_learned_memory_or_transfer_advantage"]="NOT_ESTABLISHED"
    except Exception as err:
        receipt["first_failure"]=type(err).__name__+":"+str(err)[:850]
    finally:
        (out/"cs09-original-public-FIT-per-seed.json").write_text(canon(fit_records)+"\n")
        (out/"cs09-original-paired-all-outcomes.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS09_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS09_INVALID_OR_SOURCE_DRIFT" else 0
if __name__=="__main__":
    raise SystemExit(main())
