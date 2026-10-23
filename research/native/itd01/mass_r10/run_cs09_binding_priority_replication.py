#!/usr/bin/env python3
"""Mass CS09: truly binding K4 eviction, disjoint seeds and paired raw evidence.

Original POPGym ConcentrationHard.reset/step only, no private state. The
feature family, online matcher, and rank counters are hand-engineered.
FIT learns only the priority weights (finite preregistered source-reward menu).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import resource
import subprocess
import time
from pathlib import Path

from run_cs08_original_binding_eviction import (
    MemoryWithEviction, FIT_POLICIES, BLOBS, UPSTREAM,
)
from run_cs07_concentration_associations import (
    check, public_board, CARDS, FACE_DOWN, MAX_STEPS, canon, sha,
)

FIRST="906e71ebbf0f74b890501d31feb941be014a8aed"
K=4
REPS=(0,1,2)
N={"FIT":12,"VALID":8,"DEV":40}
FREQ_WEIGHTS=(-2.0,-1.0,0.0,1.0)
RECENCY_WEIGHTS=(0.0,1.0,4.0)
WEIGHTS=tuple((f,t,0.0) for f in FREQ_WEIGHTS for t in RECENCY_WEIGHTS)
TRAIN_CONVENTIONAL=("fifo","lru","rank_support")
ARMS=("learned_linear_k4","frozen_frequent_k4","fifo_k4","lru_k4",
      "rank_support_k4","fit_selected_conventional_k4","full_k52")
PAIR_CONTRASTS=(("frozen_frequent_k4","fifo_k4"),("frozen_frequent_k4","lru_k4"),
                ("learned_linear_k4","fifo_k4"),
                ("learned_linear_k4","frozen_frequent_k4"),
                ("learned_linear_k4","fit_selected_conventional_k4"))

def frozen_source(root):
    def git(*args):
        z=subprocess.run(["git",*args],cwd=root,text=True,capture_output=True,timeout=25)
        return z.returncode,z.stdout.strip()
    r,head=git("rev-parse","HEAD")
    check(r==0 and head==UPSTREAM,"SOURCE_COMMIT_DRIFT")
    for path,expected in sorted(BLOBS.items()):
        r,h=git("hash-object","--",path)
        check(r==0 and h==expected,"ORIGINAL_SOURCE_BLOB_DRIFT:"+path)
    r,_=git("diff","--exit-code","--","popgym","pyproject.toml")
    check(r==0,"UNMODIFIED_ORIGINAL_SOURCE_DIFF")
    return {"original_git_commit":UPSTREAM,"upstream_git_blobs":BLOBS}

def role_seed(role,r,i):
    return {"FIT":1200000,"VALID":1210000,"DEV":1220000}[role]+1000*r+i

class RecordedEviction(MemoryWithEviction):
    """Same CS08 source-free matcher; record actual public victim decisions."""
    def __init__(self,capacity,mode):
        super().__init__(capacity,mode)
        self.eviction_events=[]
        self.peak_accounted_serial_state_bytes=0
    def remember(self,index,value):
        if index not in self.cache and index not in self.matched and len(self.cache)>=self.capacity:
            victim=min(self.cache,key=self._priority)
            self.eviction_events.append({
                "decision":self.decisions,
                "victim_position":victim,
                "victim_public_rank":self.cache[victim],
                "victim_priority":list(self._priority(victim)),
                "incoming_position":index,
                "incoming_public_rank":value})
        super().remember(index,value)
    def state_for_budget(self):
        """All action-relevant state, INCLUDING aux counters/seen positions."""
        self._prune()
        return {
            "association_capacity":self.capacity,
            "association_items":[[i,v] for i,v in sorted(self.cache.items())],
            "original_public_matched_indices":sorted(self.matched),
            "public_seen_positions_bitmap_as_indices":sorted(self.index_seen),
            "all_thirteen_public_rank_frequency_counters":self.rank_seen,
            "association_insert_times":sorted(self.insert_at.items()),
            "association_last_access_times":sorted(self.last_access.items()),
            "partial_pair_index":self.first,
            "last_own_card_action":self.last_action,
            "last_first_card_action":self.last_first,
            "previous_was_second":self.previous_was_second,
            "decision_clock":self.decisions,
            "matching_action_phase_memory_calls":self.decisions_from_remembered_pair,
        }
    def choose(self,board,reward,step):
        result=super().choose(board,reward,step)
        # Fully charge matched positions, public rank counters and own actions.
        self.peak_accounted_serial_state_bytes=max(
            self.peak_accounted_serial_state_bytes,
            len(canon(self.state_for_budget()).encode()))
        return result

class LearnedWeightedEviction(RecordedEviction):
    """One FIT-selected real-valued vector; no hidden source semantics."""
    def __init__(self,weights):
        super().__init__(K,"frequent")
        check(len(weights)==3 and weights in WEIGHTS,
              "LEARNED_VECTOR_OUTSIDE_PROSPECTIVE_MENU")
        self.weights=weights
    def _priority(self,index):
        rank=self.cache[index]
        f,rec,pair=self.weights
        duplicates=sum(v==rank for i,v in self.cache.items() if i!=index)
        score=(f*self.rank_seen[rank]/4.0 +
               rec*(self.last_access[index]-self.decisions)/104.0 +
               pair*duplicates)
        return (score,self.insert_at[index],index)
    def state_for_budget(self):
        x=super().state_for_budget()
        x["frozen_reward_FIT_learned_weight_vector"]=list(self.weights)
        return x

def source_episode(Source,original_seed,policy_kind,policy_value):
    source=Source()
    policy=(LearnedWeightedEviction(policy_value) if policy_kind=="linear"
            else RecordedEviction(policy_value,policy_kind))
    try:
        initial,_drop_source_info=source.reset(seed=original_seed)
        board=public_board(initial)
        check(set(board)=={FACE_DOWN},"ORIGINAL_SOURCE_INITIAL_PUBLIC_BOARD_CHANGED")
        prev_reward=0.0
        rewards=0.0;pair_matches=0
        transcript=hashlib.sha256()
        completed=truncated=False
        actions=0
        for t in range(MAX_STEPS):
            action=policy.choose(board,prev_reward,t)
            next_obs,reward,ended,trunc,_discard_private_info=source.step(action)
            board=public_board(next_obs)
            check(type(action) is int and 0<=action<CARDS,
                  "ILLEGAL_ORIGINAL_PUBLIC_CARD_FLIP")
            prev_reward=float(reward)
            check(-1.0<=prev_reward<=1.0,"INVALID_ORIGINAL_SOURCE_REWARD")
            actions+=1
            rewards+=prev_reward
            pair_matches+=int(prev_reward>0)
            event={"step":t,"own_action":action,"public_card_board":board,
                   "native_source_reward":prev_reward}
            transcript.update((canon(event)+"\n").encode())
            completed=bool(ended);truncated=bool(trunc)
            if completed or truncated:break
        check(0<actions<=MAX_STEPS and (completed or truncated),
              "ORIGINAL_SOURCE_GAME_NOT_TERMINATED")
        audited=policy.audit()
        check(len(policy.eviction_events)==audited["actual_evictions"],
              "SOURCE_PUBLIC_EVICTION_LOG_COUNT_MISMATCH")
        check(audited["peak_cache_entries"]<=policy.capacity,
              "SOURCE_CACHE_BUDGET_EXCEEDED")
        return {
          "original_reset_seed":original_seed,
          "policy_kind":policy_kind,
          "source_original_episode_reward":rewards,
          "source_matched_pairs":pair_matches,
          "source_original_action_calls":actions,
          "terminated":completed,"truncated":truncated,
          "actual_peak_association_cache":audited["peak_cache_entries"],
          "real_source_public_evictions":audited["actual_evictions"],
          "public_eviction_events":policy.eviction_events,
          "public_original_action_trace_sha256":transcript.hexdigest(),
          "all_auxiliary_and_cache_action_state_max_serialized_bytes":
             policy.peak_accounted_serial_state_bytes,
          "final_action_relevant_public_state_sha256":sha(policy.state_for_budget())
        }
    finally:
        source.close()

def source_batch(Source,role,rep,kind,value):
    start=time.process_time_ns()
    results=[source_episode(Source,role_seed(role,rep,i),kind,value)
             for i in range(N[role])]
    check(len(results)==N[role],"SOURCE_EPISODES_CHANGED")
    return {
      "episode_count":len(results),
      "mean_original_reward":sum(z["source_original_episode_reward"] for z in results)/len(results),
      "total_original_source_rewards":sum(z["source_original_episode_reward"] for z in results),
      "original_action_calls":sum(z["source_original_action_calls"] for z in results),
      "total_real_evictions":sum(z["real_source_public_evictions"] for z in results),
      "episodes_with_real_evictions":sum(z["real_source_public_evictions"]>0 for z in results),
      "actual_peak_cache_occupancy":max(z["actual_peak_association_cache"] for z in results),
      "mean_original_matches":sum(z["source_matched_pairs"] for z in results)/len(results),
      "peak_all_auxiliary_state_bytes":max(z["all_auxiliary_and_cache_action_state_max_serialized_bytes"] for z in results),
      "process_CPU_ns_original_source_included":time.process_time_ns()-start,
      "complete_original_public_episode_sha256":sha(results),
      "per_episode_original_source_evidence":results
    }

def percentile_bootstrap(differences,seed_value):
    """10000 deterministic paired resamples with replacement, no tuning."""
    rng=random.Random(seed_value)
    n=len(differences)
    obs=sum(differences)/n
    samples=[]
    for _ in range(10000):
        samples.append(sum(differences[rng.randrange(n)] for j in range(n))/n)
    samples.sort()
    return {"mean_original_reward_difference":obs,
            "confidence_interval_95_percentile":[samples[250],samples[9749]],
            "paired_original_dev_episodes":n,
            "bootstrap_resamples":10000,
            "rng_seed":seed_value}

def differences(replica,name_a,name_b):
    a=replica["DEV"][name_a]["per_episode_original_source_evidence"]
    b=replica["DEV"][name_b]["per_episode_original_source_evidence"]
    check(len(a)==len(b)==N["DEV"],"PAIRED_SEED_ROLE_LENGTH_DRIFT")
    check(all(x["original_reset_seed"]==y["original_reset_seed"] for x,y in zip(a,b)),
          "ORIGINAL_PAIRED_SEED_MISMATCH")
    return [x["source_original_episode_reward"]-y["source_original_episode_reward"]
            for x,y in zip(a,b)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    evidence={"schema":"mass.cs09.public_original_popgym_genuinely_binding_k4.v1",
              "first_frozen_protocol_commit":FIRST,
              "source_role":"PUBLIC_DEVELOPMENT_ONLY",
              "original_external_source_SHA":UPSTREAM,
              "original_env_private_state_never_read":True,
              "FIT_episodes_not_equal_behavior_trajectories":True,
              "model_priority_family_and_matcher_handcrafted":True,
              "all_auxiliary_state_counted_not_just_K4_associations":True,
              "computation_training_budgets_not_matched":True,
              "isolated_per_model_CPU_RSS_qualified":False,
              "native_yggdrasil_or_wingless_model_run":False,
              "independently_unfamiliar_protected_first_use":False,
              "controller_science_admission_observed":False,
              "disposition":"PUBLIC_CS09_INVALID_OR_EVIDENCE_MISSING",
              "replicas":[]}
    fit_archive={"schema":"mass.cs09.complete_true_source_fit_by_policy.v1","replicas":[]}
    try:
        root=Path(a.upstream).resolve()
        evidence["original_source_git_identity"]=frozen_source(root)
        from popgym.envs.concentration import ConcentrationHard
        import inspect
        check(Path(inspect.getfile(ConcentrationHard)).resolve()==root/"popgym"/"envs"/"concentration.py",
              "NOT_SOURCE_OWNED_CONCENTRATION_CLASS")
        unique_seeds=set()
        for r in REPS:
            train_linear={}
            for index,weights in enumerate(WEIGHTS):
                train_linear[str(index)]={
                    "weights":list(weights),
                    "original":source_batch(ConcentrationHard,"FIT",r,"linear",weights)}
            train_conventional={mode:source_batch(ConcentrationHard,"FIT",r,mode,K)
                                for mode in TRAIN_CONVENTIONAL}
            winner_index=max(range(len(WEIGHTS)),
                key=lambda i:(train_linear[str(i)]["original"]["total_original_source_rewards"],-i))
            best_weight=WEIGHTS[winner_index]
            winner_conv=max(TRAIN_CONVENTIONAL,
                key=lambda name:(train_conventional[name]["total_original_source_rewards"],
                                 -TRAIN_CONVENTIONAL.index(name)))
            models={
                ARMS[0]:("linear",best_weight),
                ARMS[1]:("frequent",K),
                ARMS[2]:("fifo",K),
                ARMS[3]:("lru",K),
                ARMS[4]:("rank_support",K),
                ARMS[5]:(winner_conv,K),
                ARMS[6]:("lru",52)}
            valid={name:source_batch(ConcentrationHard,"VALID",r,*v) for name,v in models.items()}
            dev={name:source_batch(ConcentrationHard,"DEV",r,*v) for name,v in models.items()}
            for role,size in N.items():
                for i in range(size):
                    key=role_seed(role,r,i)
                    check(key not in unique_seeds,"SOURCE_ROLE_REPLICA_OVERLAP")
                    unique_seeds.add(key)
            rep={"replica":r,
                 "FIT_reward_selected_weight_vector":list(best_weight),
                 "FIT_selected_weight_menu_index":winner_index,
                 "FIT_selected_conventional_heuristic":winner_conv,
                 "FIT_linear_reward_candidates":{
                     key:{"weights":z["weights"],
                          "original_reward_total":z["original"]["total_original_source_rewards"],
                          "actual_original_episodes":z["original"]["episode_count"],
                          "original_action_calls":z["original"]["original_action_calls"],
                          "FIT_episode_trace_sha256":z["original"]["complete_original_public_episode_sha256"]}
                     for key,z in train_linear.items()},
                 "FIT_conventional_reward_candidates":{
                     key:{"original_reward_total":val["total_original_source_rewards"],
                          "actual_original_episodes":val["episode_count"],
                          "original_action_calls":val["original_action_calls"],
                          "FIT_episode_trace_sha256":val["complete_original_public_episode_sha256"]}
                     for key,val in train_conventional.items()},
                 "VALID":valid,"DEV":dev,
                 "process_inclusive_maxrss_KiB_not_model_isolated":
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            rep["original_development_paired_bootstraps"]={
                a+"__minus__"+b:percentile_bootstrap(differences(rep,a,b),
                    20261023+r*100+j)
                for j,(a,b) in enumerate(PAIR_CONTRASTS)}
            k4=ARMS[:6]
            rep["all_K4_real_binding"]=all(
                dev[name]["episodes_with_real_evictions"]>=30 and
                dev[name]["actual_peak_cache_occupancy"]==4
                for name in k4) and dev[ARMS[6]]["actual_peak_cache_occupancy"]>=6
            reward=lambda name:dev[name]["mean_original_reward"]
            rep["frozen_frequency_vs_fifo"]=reward(ARMS[1])-reward(ARMS[2])
            rep["frozen_frequency_vs_lru"]=reward(ARMS[1])-reward(ARMS[3])
            rep["FIT_linear_vs_frozen_frequency"]=reward(ARMS[0])-reward(ARMS[1])
            rep["FIT_linear_vs_fitted_conventional"]=reward(ARMS[0])-reward(ARMS[5])
            evidence["replicas"].append(rep)
            fit_archive["replicas"].append({"replica":r,
                 "all_linear_source_FIT_episodes":train_linear,
                 "all_conventional_source_FIT_episodes":train_conventional})
            print("CS09_REPLICA="+str(r)+" FIT_VECTOR="+canon(list(best_weight))+
                  " FIT_CONVENTIONAL="+winner_conv+" DEV="+canon({
                name:round(dev[name]["mean_original_reward"],6) for name in ARMS}),flush=True)
        check(len(unique_seeds)==3*(12+8+40),"TOTAL_SOURCE_SEEDS_DRIFT")
        total_episodes=3*(12*(len(WEIGHTS)+len(TRAIN_CONVENTIONAL))+7*(8+40))
        evidence["total_genuine_original_source_episodes"]=total_episodes
        check(total_episodes==1548,"PREREG_REAL_SOURCE_EPISODE_COUNT_DRIFT")
        evidence["original_source_real_card_flips"]=sum(
           sum(val["original"]["original_action_calls"]
               for val in rr["all_linear_source_FIT_episodes"].values())+
           sum(val["original_action_calls"]
               for val in rr["all_conventional_source_FIT_episodes"].values())
           for rr in fit_archive["replicas"])+sum(
               sum(d["original_action_calls"] for d in rep[role].values())
               for rep in evidence["replicas"] for role in ("VALID","DEV"))
        check(0<evidence["original_source_real_card_flips"]<=1548*MAX_STEPS,
              "SOURCE_ORIGINAL_ACTION_BUDGET_EXCEEDED")
        # pool all 120 paired DEV resets as predeclared; no random permutation tuning.
        pooled={}
        for j,(name_a,name_b) in enumerate(PAIR_CONTRASTS):
            all_d=[v for rr in evidence["replicas"] for v in differences(rr,name_a,name_b)]
            pooled[name_a+"__minus__"+name_b]=percentile_bootstrap(all_d,20261026+j)
        evidence["pooled_original_source_paired_bootstrap"]=pooled
        ci_positive=lambda a,b:pooled[a+"__minus__"+b]["confidence_interval_95_percentile"][0]>0
        frequency_replication=(all(x["all_K4_real_binding"] and
                                   x["frozen_frequency_vs_fifo"]>=.05 and
                                   x["frozen_frequency_vs_lru"]>=.05
                                   for x in evidence["replicas"]) and
                                   ci_positive(ARMS[1],ARMS[2]) and
                                   ci_positive(ARMS[1],ARMS[3]))
        linear_gain=(all(x["all_K4_real_binding"] and
                         x["FIT_linear_vs_frozen_frequency"]>=.03 and
                         x["FIT_linear_vs_fitted_conventional"]>=.03 and
                         x["FIT_reward_selected_weight_vector"][0]!=0 and
                         x["FIT_reward_selected_weight_vector"][1]!=0
                         for x in evidence["replicas"]) and
                         ci_positive(ARMS[0],ARMS[1]) and
                         ci_positive(ARMS[0],ARMS[5]))
        evidence["frozen_CS08_frequency_replication"]=frequency_replication
        evidence["new_FIT_linear_stronger_control_improvement"]=linear_gain
        evidence["disposition"]=("PUBLIC_CS09_BINDING_FREQUENCY_REPLICATION_PASS"
                                if frequency_replication else "PUBLIC_CS09_REPLICATION_NO_GAIN")
        evidence["FIT_linear_priority_disposition"]=(
            "PUBLIC_CS09_FITTED_LINEAR_PRIORITY_ADVANTAGE" if linear_gain
            else "LINEAR_LEARNING_ADVANTAGE_NOT_ESTABLISHED")
        evidence["FIT_complete_evidence_sha256"]=sha(fit_archive)
        evidence["not_scientific_transfer_or_architecture_novelty"]=True
    except Exception as ex:
        evidence["first_failure"]=type(ex).__name__+":"+str(ex)[:900]
    finally:
        (out/"cs09-original-source-fit-per-episode.json").write_text(
            canon(fit_archive)+"\n")
        (out/"cs09-original-source-episode-level-receipt.json").write_text(
            json.dumps(evidence,indent=2,sort_keys=True)+"\n")
    print("CS09_DISPOSITION="+evidence["disposition"],flush=True)
    return 2 if evidence["disposition"]=="PUBLIC_CS09_INVALID_OR_EVIDENCE_MISSING" else 0

if __name__=="__main__":
    raise SystemExit(main())
