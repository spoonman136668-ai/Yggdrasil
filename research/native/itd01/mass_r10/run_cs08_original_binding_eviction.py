#!/usr/bin/env python3
"""CS08: real source-bound K4 eviction experiment, reward-fit policy menu.

All states come from original source public observations/reward and own actions.
Original POPGym ConcentrationHard source is not modified or replaced.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import resource
import subprocess
import time
from pathlib import Path

from run_cs07_concentration_associations import (
    PublicCardMemory, public_board, check, canon, sha, CARDS, FACE_DOWN, MAX_STEPS
)

FIRST="faac43a908fcf7836fddc5b4d6cf73aa556abad5"
UPSTREAM="410d5aa626dae8024f498354d8781a0d1870c399"
BLOBS={
    "popgym/envs/concentration.py":"8f0d2d316c1ae63a7965ce1c56295a9aa403bbb9",
    "popgym/core/deck.py":"12bcabfa9a96fd1261809ef0a446c74d3f3bfa86",
    "popgym/core/env.py":"26a20ba3531730b76e135f48e8fc25bb6b620984",
    "pyproject.toml":"20bd0e278a519452d66c57f2fbbff58fdcdce5c8"
}
REPS=(0,1,2)
FIT_POLICIES=("fifo","lru","novelty","frequent","rank_support")
ARMS=("fit_reward_selected_k4","conventional_k4_fifo","conventional_k4_lru",
      "conventional_k4_rank_support","conventional_full_k52_lru")
N={"FIT":16,"VALID":8,"DEV":32}
K=4
MIN_BINDING_FRACTION=.75

def source_identity(root):
    def git(*args):
        p=subprocess.run(["git",*args],cwd=root,text=True,capture_output=True,timeout=25)
        return p.returncode,p.stdout.strip()
    rc,head=git("rev-parse","HEAD")
    check(rc==0 and head==UPSTREAM,"ORIGINAL_GIT_HEAD_DRIFT")
    for path,h in sorted(BLOBS.items()):
        rc,actual=git("hash-object","--",path)
        check(rc==0 and actual==h,"ORIGINAL_GIT_BLOB_DRIFT:"+path)
    rc,_=git("diff","--exit-code","--","popgym","pyproject.toml")
    check(rc==0,"ORIGINAL_UPSTREAM_DIFF")
    return {"sha":UPSTREAM,"git_blobs":BLOBS}

def role_seed(role,r,i):
    return {"FIT":1170000,"VALID":1180000,"DEV":1190000}[role]+r*1000+i

class MemoryWithEviction(PublicCardMemory):
    """CS07 common source-free matcher, varying ONLY public cache priority.

    Publicly observed rank occurrence counters and seen-position bitmask are
    held in every arm, including FIFO/LRU and full-cache comparator.
    These are additional common states beyond K remembered associations.
    """
    def __init__(self,capacity,mode):
        check(capacity in (K,52),"FROZEN_CAPACITY_UNSUPPORTED")
        check(mode in FIT_POLICIES,"FROZEN_EVICTION_FAMILY_UNSUPPORTED")
        super().__init__(capacity)
        self.mode=mode
        self.rank_seen=[0]*FACE_DOWN
        self.index_seen=set()
        self.insert_at={}
        self.last_access={}
        self.total_evictions=0
        self.first_eviction_step=None
        self.total_access_hits=0
        self.eviction_stream=hashlib.sha256()
        self.max_extra_rank_counter_bytes=FACE_DOWN*2
    def _prune(self):
        for metadata in (self.insert_at,self.last_access):
            for index in list(metadata):
                if index not in self.cache:
                    del metadata[index]
    def _priority(self,index):
        rank=self.cache[index]
        other_count=sum(v==rank for k,v in self.cache.items() if k!=index)
        if self.mode=="fifo": score=float(self.insert_at[index])
        elif self.mode=="lru": score=float(self.last_access[index])
        elif self.mode=="novelty":score=-float(self.rank_seen[rank])
        elif self.mode=="frequent":score=float(self.rank_seen[rank])
        elif self.mode=="rank_support":score=1000.*other_count+self.last_access[index]
        else:raise RuntimeError("UNKNOWN_EVICTION_MODE")
        return (score,self.insert_at[index],index)
    def remember(self,index,value):
        check(0<=index<CARDS and 0<=value<FACE_DOWN,
              "SOURCE_PUBLIC_ASSOCIATION_OUT_OF_DOMAIN")
        # The 52-bit public observed location mask and 13 rank counters are
        # common to ALL modes and do not preserve discarded location->rank.
        if index not in self.index_seen:
            self.index_seen.add(index)
            self.rank_seen[value]+=1
        self._prune()
        if index in self.matched:return
        if index in self.cache:
            del self.cache[index]
            self.insert_at.pop(index,None)
            self.last_access.pop(index,None)
        elif len(self.cache)>=self.capacity:
            victim=min(self.cache,key=self._priority)
            data={"t":self.decisions,"mode":self.mode,"victim":victim,
                  "public_rank":self.cache[victim],"priority":self._priority(victim),
                  "new_index":index,"new_public_rank":value}
            self.eviction_stream.update((canon(data)+"\n").encode())
            self.total_evictions+=1
            if self.first_eviction_step is None:self.first_eviction_step=self.decisions
            del self.cache[victim]
            self.insert_at.pop(victim,None)
            self.last_access.pop(victim,None)
        self.cache[index]=value
        self.insert_at[index]=self.decisions
        self.last_access[index]=self.decisions
        self.peak_cache=max(self.peak_cache,len(self.cache))
        self.public_association_insertions+=1
        check(len(self.cache)<=self.capacity,"ACTUAL_BOUND_K_VIOLATION")
    def choose(self,board,reward,step):
        a=super().choose(board,reward,step)
        if a in self.cache:
            self.total_access_hits+=1
            self.last_access[a]=self.decisions
        self._prune()
        return a
    def audit(self):
        self._prune()
        common=super().status()
        return {**common,
                "mode":self.mode,"actual_evictions":self.total_evictions,
                "first_eviction_public_decision":self.first_eviction_step,
                "public_cache_access_hits":self.total_access_hits,
                "eviction_events_sha256":self.eviction_stream.hexdigest(),
                "common_public_rank_frequency":self.rank_seen,
                "common_public_seen_locations_count":len(self.index_seen),
                "current_insert_timestamps":sorted(self.insert_at.items()),
                "current_last_access_timestamps":sorted(self.last_access.items())}

def play_original(Source,reset_seed,capacity,mode):
    env=Source()
    agent=MemoryWithEviction(capacity,mode)
    try:
        initial,_unused_reset_info=env.reset(seed=reset_seed)
        board=public_board(initial)
        check(set(board)=={FACE_DOWN},"RESET_PUBLIC_BOARD_NOT_HIDDEN")
        reward=0.;total=0.;success=0;steps=0
        transcript=hashlib.sha256()
        ended=truncated=False
        for step in range(MAX_STEPS):
            action=agent.choose(board,reward,step)
            obs,reward,ended,truncated,_unused_step_info=env.step(action)
            board=public_board(obs)
            check(0<=action<CARDS and -1<=float(reward)<=1,"SOURCE_ACTION_REWARD_ILLEGAL")
            total+=float(reward);success+=int(reward>0);steps+=1
            public_event={"t":step,"action":action,"board":board,"reward":float(reward)}
            transcript.update((canon(public_event)+"\n").encode())
            if ended or truncated:break
        check(0<steps<=MAX_STEPS and (ended or truncated),
              "SOURCE_ORIGINAL_GAME_NEVER_ENDED")
        return {"seed":reset_seed,"capacity":capacity,"eviction_rule":mode,
                "original_steps":steps,"native_terminal":bool(ended),
                "native_truncated":bool(truncated),
                "original_total_reward":total,"source_matched_pairs":success,
                "original_public_transcript_sha256":transcript.hexdigest(),
                "cache":agent.audit()}
    finally:
        env.close()

def evaluate(Source,role,r,models):
    results={}
    n=N[role]
    for name,(capacity,rule) in models.items():
        start=time.process_time_ns()
        rows=[play_original(Source,role_seed(role,r,i),capacity,rule)
              for i in range(n)]
        evictions=[a["cache"]["actual_evictions"] for a in rows]
        peaks=[a["cache"]["peak_cache_entries"] for a in rows]
        rewards=[a["original_total_reward"] for a in rows]
        results[name]={
            "episodes":n,
            "mean_original_episode_reward":sum(rewards)/n,
            "original_episode_reward_sum":sum(rewards),
            "native_original_source_actions":sum(a["original_steps"] for a in rows),
            "source_pair_matches":sum(a["source_matched_pairs"] for a in rows),
            "actual_evictions_total":sum(evictions),
            "episodes_with_actual_evictions":sum(x>0 for x in evictions),
            "actual_evictions_per_episode":evictions,
            "observed_peak_cache_occupancy":max(peaks),
            "public_context_plus_cache_state_max_bytes":
                max(len(canon(a["cache"]).encode()) for a in rows),
            "public_experience_sha256":sha(rows),
            "fit_selected_heuristic":rule,
            "fixed_capacity_K":capacity,
            "CPU_ns_including_original_source":time.process_time_ns()-start}
    return results

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--upstream",required=True)
    arg.add_argument("--out",required=True)
    args=arg.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs08.original-source-binding-k4-eviction.v1",
      "first_frozen_prereg":FIRST,"source_role":"PUBLIC_DEVELOPMENT_ONLY",
      "tested_original_concentration_source":True,
      "all_K4_arms_get_same_memory_budget":True,
      "FIT_trajectory_information_matched":False,
      "capacity_binding_required_for_all_dev_K4":True,
      "common_extra_public_rank_histogram_and_seen_position_bits":True,
      "model_structure_and_heuristic_menu_handcrafted":True,
      "native_yggdrasil_wingless_learner_executed":False,
      "independent_sealed_unfamiliar_first_use":False,
      "controller_science_admission_observed":False,
      "complete_CPU_RSS_resource_parity":False,
      "disposition":"PUBLIC_CS08_INVALID_OR_LEAK","replicas":[]}
    preserved={"schema":"mass.cs08.frozen_fit_reward_menu.v1","replicas":[]}
    try:
        root=Path(args.upstream).resolve()
        receipt["source"]=source_identity(root)
        from popgym.envs.concentration import ConcentrationHard
        import inspect
        check(Path(inspect.getfile(ConcentrationHard)).resolve() ==
              root/"popgym"/"envs"/"concentration.py","NOT_UNMODIFIED_ORIGINAL_SOURCE_CLASS")
        consumed=set()
        for r in REPS:
            fit=evaluate(ConcentrationHard,"FIT",r,{mode:(K,mode) for mode in FIT_POLICIES})
            selected=max(FIT_POLICIES,key=lambda rule:(fit[rule]["original_episode_reward_sum"],
                                                      -FIT_POLICIES.index(rule)))
            candidate={ARMS[0]:(K,selected),
                       ARMS[1]:(K,"fifo"),
                       ARMS[2]:(K,"lru"),
                       ARMS[3]:(K,"rank_support"),
                       ARMS[4]:(52,"lru")}
            valid=evaluate(ConcentrationHard,"VALID",r,candidate)
            dev=evaluate(ConcentrationHard,"DEV",r,candidate)
            for role,n in N.items():
                for i in range(n):
                    s=role_seed(role,r,i)
                    check(s not in consumed,"ORIGINAL_SOURCE_ROLE_COLLISION")
                    consumed.add(s)
            k4_names=ARMS[:4]
            binding=all(
                dev[name]["episodes_with_actual_evictions"]>=24 and
                dev[name]["observed_peak_cache_occupancy"]==K
                for name in k4_names)
            binding=binding and dev[ARMS[4]]["observed_peak_cache_occupancy"]>=6
            reward=lambda name:dev[name]["mean_original_episode_reward"]
            advantage=(binding and
                reward(ARMS[0])-reward(ARMS[1])>=.05 and
                reward(ARMS[0])-reward(ARMS[2])>=.05 and
                reward(ARMS[0])-reward(ARMS[3])>=.03)
            fit_summary={name:{
                 "episode_count":fit[name]["episodes"],
                 "total_real_reward":fit[name]["original_episode_reward_sum"],
                 "real_original_actions":fit[name]["native_original_source_actions"],
                 "real_evictions":fit[name]["actual_evictions_total"],
                 "real_public_traces_sha256":fit[name]["public_experience_sha256"]}
                 for name in FIT_POLICIES}
            preserved["replicas"].append({"replica":r,"FIT_reward_selection":fit_summary,
                                         "selected_K4_eviction_heuristic":selected})
            item={"replica":r,"selected_FIT_heuristic":selected,
                  "FIT_original_episodes_per_heuristic":N["FIT"],
                  "FIT_original_summary":fit_summary,
                  "VALID":valid,"DEV":dev,
                  "binding_memory_verified":binding,
                  "K4_candidate_minus_FIFO_original_reward":
                    reward(ARMS[0])-reward(ARMS[1]),
                  "K4_candidate_minus_LRU_original_reward":
                    reward(ARMS[0])-reward(ARMS[2]),
                  "K4_candidate_minus_equal_capacity_rank_support":
                    reward(ARMS[0])-reward(ARMS[3]),
                  "K4_candidate_minus_full_memory":
                    reward(ARMS[0])-reward(ARMS[4]),
                  "fit_selected_eviction_improvement_criterion":advantage,
                  "process_inclusive_maxrss_kib_not_per_model":
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            receipt["replicas"].append(item)
            print("CS08_REPLICA="+str(r)+" SELECTED="+selected+" DEV="+canon({
                name:{"mean_reward":dev[name]["mean_original_episode_reward"],
                      "real_evictions":dev[name]["actual_evictions_total"]}
                for name in ARMS}),flush=True)
        check(len(consumed)==3*sum(N.values()),"UNIQUE_SOURCE_SEED_COUNT_INVALID")
        receipt["original_real_games"]=3*(5*16+5*(8+32))
        receipt["original_real_card_flip_actions"]=sum(
          sum(a["real_original_actions"] for a in rep["FIT_original_summary"].values())+
          sum(d["native_original_source_actions"] for d in rep["VALID"].values())+
          sum(d["native_original_source_actions"] for d in rep["DEV"].values())
          for rep in receipt["replicas"])
        check(receipt["original_real_games"]==840 and
              0<receipt["original_real_card_flip_actions"]<=840*MAX_STEPS,
              "FROZEN_SOURCE_BUDGET_MISMATCH")
        receipt["raw_fit_receipts_sha256"]=sha(preserved)
        if not all(v["binding_memory_verified"] for v in receipt["replicas"]):
            receipt["disposition"]="PUBLIC_CS08_INSUFFICIENT_ACTUAL_MEMORY_PRESSURE"
        elif all(v["fit_selected_eviction_improvement_criterion"] for v in receipt["replicas"]):
            receipt["disposition"]="PUBLIC_CS08_BINDING_MEMORY_FITTED_EVICTION_GAIN_PUBLIC_ONLY"
        else:
            receipt["disposition"]="PUBLIC_CS08_BINDING_MEMORY_NO_LEARNED_EVICTION_ADVANTAGE"
        receipt["new_native_cognition_or_true_independent_transfer"]="NOT_ESTABLISHED"
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:650]
    finally:
        (out/"cs08-public-fit-eviction-menu.json").write_text(canon(preserved)+"\n")
        (out/"cs08-source-original-receipt.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS08_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS08_INVALID_OR_LEAK" else 0
if __name__=="__main__":raise SystemExit(main())
