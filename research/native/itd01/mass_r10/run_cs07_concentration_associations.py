#!/usr/bin/env python3
"""CS07: public-only original POPGym Concentration learned memory capacity.

Original source reset/step with source-native public board, last OWN actions
and feedback only. Cached observed position->rank pair values are learned
online, with K chosen on original source FIT rewards. Navigation heuristic and
memory format remain handcrafted conventional controls, NOT native cognition.
"""
from __future__ import annotations
import argparse
from collections import OrderedDict,defaultdict
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

FIRST="47e739e2872cdaed1908dab4c8f33553ec5ed913"
UPSTREAM="410d5aa626dae8024f498354d8781a0d1870c399"
BLOBS={
 "popgym/envs/concentration.py":"8f0d2d316c1ae63a7965ce1c56295a9aa403bbb9",
 "popgym/core/deck.py":"12bcabfa9a96fd1261809ef0a446c74d3f3bfa86",
 "popgym/core/env.py":"26a20ba3531730b76e135f48e8fc25bb6b620984",
 "pyproject.toml":"20bd0e278a519452d66c57f2fbbff58fdcdce5c8"}
REPS=(0,1,2)
CAPS=(0,4,16,52)
ROLE_COUNTS={"FIT":12,"VALID":8,"DEV":24}
ARMS=("fit_reward_selected_K","full_conventional_associative_K52",
      "bounded_conventional_associative_K4","zero_unmatched_cache_K0",
      "selected_K_erased_at_decision_53")
CARDS=52
FACE_DOWN=13
MAX_STEPS=104

def check(v,msg):
    if not v:raise RuntimeError(msg)
def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()
def seed(role,r,i):
    return {"FIT":1140000,"VALID":1150000,"DEV":1160000}[role]+1000*r+i

def original_source(root):
    def call(args):
        p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=25)
        return p.returncode,p.stdout.strip()
    rc,head=call(["git","rev-parse","HEAD"])
    check(rc==0 and head==UPSTREAM,"UPSTREAM_GIT_SHA_DRIFT")
    for path,h in sorted(BLOBS.items()):
        rc,got=call(["git","hash-object","--",path])
        check(rc==0 and got==h,"UPSTREAM_GIT_BLOB_DRIFT:"+path)
    rc,_=call(["git","diff","--exit-code","--","popgym","pyproject.toml"])
    check(rc==0,"UPSTREAM_SOURCE_MODIFIED")
    return {"original_git_sha":UPSTREAM,"source_blobs":BLOBS}

def public_board(obs):
    import numpy as np
    a=np.asarray(obs)
    check(a.shape==(CARDS,) and np.issubdtype(a.dtype,np.integer),
          "ORIGINAL_PUBLIC_BOARD_SHAPE")
    b=[int(z) for z in a]
    check(all(0<=x<=FACE_DOWN for x in b),"ORIGINAL_CARD_VALUE_INVALID")
    return b

class PublicCardMemory:
    """Source-free selectable cached associations; no original hidden state."""
    def __init__(self,capacity,erase=False):
        check(capacity in CAPS,"MEMORY_CAPACITY_DRIFT")
        self.capacity=capacity
        self.erase=erase
        self.cache=OrderedDict()
        self.matched=set()
        self.first=None
        self.last_action=None
        self.last_first=None
        self.previous_was_second=False
        self.erased=False
        self.decisions=0
        self.peak_cache=0
        self.public_association_insertions=0
        self.decisions_from_remembered_pair=0
        self._last_feedback=None
    def remember(self,index,value):
        check(0<=index<CARDS and 0<=value<FACE_DOWN,
              "PUBLIC_ASSOCIATION_INVALID")
        if self.capacity==0 or index in self.matched:
            return
        if index in self.cache:
            del self.cache[index]
        self.cache[index]=value
        if len(self.cache)>self.capacity:
            self.cache.popitem(last=False)
        check(len(self.cache)<=self.capacity,"CACHE_BUDGET_EXCEEDED")
        self.peak_cache=max(self.peak_cache,len(self.cache))
        self.public_association_insertions+=1
    def choose(self,board,reward,step):
        """The model receives only public board, original reward, own past action."""
        board=public_board(board)
        check(self.decisions==step,"ACTION_CLOCK_DRIFT")
        if self.last_action is not None:
            seen=board[self.last_action]
            check(seen!=FACE_DOWN,"LAST_CHOSEN_CARD_NOT_PUBLIC")
            if self.previous_was_second:
                check(self.last_first is not None,"SECOND_CARD_HISTORY_MISSING")
                first_value=board[self.last_first]
                check(first_value!=FACE_DOWN,"FIRST_CARD_NOT_VISIBLE_AT_SECOND_FEEDBACK")
                if reward>0:
                    self.matched.update((self.last_first,self.last_action))
                    self.cache.pop(self.last_first,None)
                    self.cache.pop(self.last_action,None)
                else:
                    self.remember(self.last_first,first_value)
                    self.remember(self.last_action,seen)
                self.last_first=None
            else:
                check(self.first==self.last_action,"FIRST_CARD_PHASE_MISMATCH")
                self.remember(self.last_action,seen)
        if self.erase and step==52:
            self.cache.clear()
            self.erased=True
        check(len(self.matched)%2==0,"MATCHED_CARD_PARITY_INVALID")
        eligible=[i for i in range(CARDS) if i not in self.matched]
        check(eligible,"ALL_CARDS_ALREADY_MATCHED")
        if self.first is not None:
            # The first flipped card remains visible in the current public board.
            first=self.first
            value=board[first]
            check(value!=FACE_DOWN,"ACTIVE_FIRST_CARD_NOT_PUBLICLY_VISIBLE")
            matching=[i for i,v in self.cache.items()
                      if i!=first and i in eligible and v==value]
            if matching:
                choice=min(matching)
                self.decisions_from_remembered_pair+=1
            else:
                choice=self._explore(eligible,forbidden={first})
            self.last_first=first
            self.first=None
            self.previous_was_second=True
        else:
            by_rank=defaultdict(list)
            for i,v in self.cache.items():
                if i in eligible:by_rank[v].append(i)
            pair_options=[min(indices) for indices in by_rank.values()
                          if len(indices)>=2]
            if pair_options:
                choice=min(pair_options)
                self.decisions_from_remembered_pair+=1
            else:
                choice=self._explore(eligible,forbidden=set())
            self.first=choice
            self.previous_was_second=False
        check(type(choice) is int and choice in eligible,
              "ILLEGAL_MATCHED_OR_INDEX_ACTION")
        self.last_action=choice
        self.decisions+=1
        return choice
    def _explore(self,eligible,forbidden):
        choices=[i for i in eligible if i not in forbidden]
        check(bool(choices),"NO_SOURCE_PUBLIC_LEGAL_UNMATCHED_CARD")
        unseen=[i for i in choices if i not in self.cache]
        if unseen:choices=unseen
        start=(self.decisions*7)%CARDS
        return min(choices,key=lambda i:((i-start)%CARDS,i))
    def status(self):
        return {"capacity":self.capacity,"erased":self.erased,
                "peak_cache_entries":self.peak_cache,
                "public_association_insertions":self.public_association_insertions,
                "pair_memory_decisions":self.decisions_from_remembered_pair,
                "final_cache_items":[[k,v] for k,v in self.cache.items()],
                "observed_matched_indices":sorted(self.matched)}

def source_episode(Source,reset_seed,capacity,erase=False,include_actions=False):
    env=Source()
    policy=PublicCardMemory(capacity,erase)
    try:
        obs,_drop_priv_info=env.reset(seed=reset_seed)
        board=public_board(obs)
        check(set(board)=={FACE_DOWN},"ORIGINAL_SOURCE_RESET_NOT_ALL_HIDDEN")
        rewards=0.;matched_pairs=0;steps=0;actions=[]
        last_reward=0.
        final_end=final_trunc=False
        for t in range(MAX_STEPS):
            a=policy.choose(board,last_reward,t)
            nxt,r,ended,trunc,_drop_private_info=env.step(a)
            board=public_board(nxt)
            r=float(r)
            check(-1.0<=r<=1.0,"UNBOUNDED_ORIGINAL_REWARD")
            steps+=1;rewards+=r
            matched_pairs+=int(r>0)
            if include_actions:
                actions.append({"t":t,"own_card_index_action":a,
                                "original_observation_board":board,
                                "original_reward":r})
            final_end=bool(ended);final_trunc=bool(trunc)
            last_reward=r
            if ended or trunc:break
        check(0<steps<=MAX_STEPS,"ORIGINAL_ACTION_BUDGET_INVALID")
        check(final_end or final_trunc,
              "SOURCE_NEITHER_TERMINATED_NOR_TRUNCATED_ON_MAX_STEPS")
        return {
            "seed":reset_seed,"memory_K":capacity,"memory_erasure":erase,
            "source_legal_actions":steps,"original_source_reward_sum":rewards,
            "successful_original_source_matched_pairs":matched_pairs,
            "source_terminated":final_end,"source_truncated":final_trunc,
            "public_memory_status":policy.status(),
            "public_action_transcript_sha256":sha(actions) if include_actions else None,
            "full_public_actions":actions if include_actions else None}
    finally:
        env.close()

def run_role(Source,role,r,capacities):
    n=ROLE_COUNTS[role]
    output={}
    for name,(k,erasure) in capacities.items():
        cpu_start=time.process_time_ns()
        episodes=[]
        for i in range(n):
            row=source_episode(Source,seed(role,r,i),k,erasure)
            episodes.append(row)
        output[name]={
            "episodes":n,
            "original_reward_sum":sum(x["original_source_reward_sum"] for x in episodes),
            "original_reward_mean":sum(x["original_source_reward_sum"] for x in episodes)/n,
            "matched_pairs_total":sum(x["successful_original_source_matched_pairs"] for x in episodes),
            "original_source_actions":sum(x["source_legal_actions"] for x in episodes),
            "peak_stored_associations":max(x["public_memory_status"]["peak_cache_entries"] for x in episodes),
            "public_experiences_sha256":sha(episodes),
            "process_cpu_ns_including_original_source":time.process_time_ns()-cpu_start,
            "model_serialized_stored_assoc_max_bytes":
                max(len(canon(x["public_memory_status"]).encode()) for x in episodes)}
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rec={"schema":"mass.cs07.original_concentration_public_association_budget.v1",
        "FIRST_frozen_prereg_sha":FIRST,
        "source_role":"PUBLIC_DEVELOPMENT_ONLY",
        "native_nontransformer_cognition_model_tested":False,
        "memory_architecture_handcrafted":True,
        "capacity_FIT_learned_from_original_source_reward":True,
        "strong_conventional_full_episodic_memory_also_evaluated":True,
        "arms_have_equal_FIT_experience_histories":False,
        "source_private_deck_or_full_hidden_state_exposed":False,
        "independently_sealed_unfamiliar_source_used":False,
        "protected_first_use_consumed":False,
        "CKB_controller_science_admission_observed":False,
        "full_regression_or_resource_parity_qualified":False,
        "disposition":"PUBLIC_CS07_INVALID_OR_LEAK",
        "replicas":[]}
    raw={"schema":"mass.cs07.original_source_FIT_capacity_selection.v1","replicas":[]}
    try:
        root=Path(args.upstream).resolve()
        rec["source_identity"]=original_source(root)
        from popgym.envs.concentration import ConcentrationHard
        import inspect
        check(Path(inspect.getfile(ConcentrationHard)).resolve() ==
              root/"popgym"/"envs"/"concentration.py",
              "NOT_ORIGINAL_SOURCE_CONCENTRATION_HARD")
        seen=set()
        for r in REPS:
            fit_records={}
            scores={}
            for k in CAPS:
                per=[]
                t0=time.process_time_ns()
                for i in range(ROLE_COUNTS["FIT"]):
                    ss=seed("FIT",r,i)
                    per.append(source_episode(ConcentrationHard,ss,k))
                scores[k]=sum(x["original_source_reward_sum"] for x in per)
                fit_records[str(k)]={
                    "source_original_episodes":len(per),
                    "source_original_actions":sum(x["source_legal_actions"] for x in per),
                    "original_reward_sum":scores[k],
                    "original_successful_pairs":sum(x["successful_original_source_matched_pairs"] for x in per),
                    "public_FIT_trace_sha256":sha(per),
                    "FIT_process_cpu_ns_including_original_source":time.process_time_ns()-t0}
            selected=max(CAPS,key=lambda k:(scores[k],-k))
            for role,n in ROLE_COUNTS.items():
                for i in range(n):
                    ss=seed(role,r,i)
                    check(ss not in seen,"SOURCE_ROLE_OR_REPLICA_SEED_COLLISION")
                    seen.add(ss)
            models={ARMS[0]:(selected,False),ARMS[1]:(52,False),
                    ARMS[2]:(4,False),ARMS[3]:(0,False),
                    ARMS[4]:(selected,True)}
            raw["replicas"].append({"replica":r,"selected_fit_memory_capacity":selected,
                                    "candidate_capacities_FIT":fit_records})
            valid=run_role(ConcentrationHard,"VALID",r,models)
            dev=run_role(ConcentrationHard,"DEV",r,models)
            get=lambda k:dev[k]["original_reward_mean"]
            selective=(selected in (4,16)
                       and get(ARMS[0])>=get(ARMS[1])-.05
                       and get(ARMS[0])>=get(ARMS[3])+.10
                       and get(ARMS[0])>=get(ARMS[4])+.05)
            rec["replicas"].append({
                "replica":r,
                "FIT_selection_capacities":list(CAPS),
                "selected_reward_fitted_K":selected,
                "FIT_original_rewards_by_capacity":{str(k):v for k,v in scores.items()},
                "FIT_original_candidate_episodes_per_K":ROLE_COUNTS["FIT"],
                "VALID":valid,"DEV":dev,
                "candidate_minus_full_conventional_mean_original_reward":get(ARMS[0])-get(ARMS[1]),
                "candidate_minus_zero_cache_mean_original_reward":get(ARMS[0])-get(ARMS[3]),
                "candidate_minus_mid_episode_erasure_mean_original_reward":get(ARMS[0])-get(ARMS[4]),
                "prospective_selective_memory_criterion_passed":selective,
                "process_inclusive_peak_rss_kib_not_model_isolated":
                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
            print("CS07_REPLICA="+str(r)+" selected_K="+str(selected)+" dev_original_reward="+
                  canon({k:round(dev[k]["original_reward_mean"],5) for k in ARMS}),flush=True)
        check(len(seen)==3*(12+8+24),"SEED_ROLE_IDENTITY_DRIFT")
        rec["expected_original_source_episodes"]=624
        rec["actual_original_source_episodes"]=3*(4*12+5*(8+24))
        rec["original_source_public_steps"]=sum(
            sum(z["source_original_actions"] for z in x["candidate_capacities_FIT"].values())
            for x in raw["replicas"])+sum(
                sum(y["original_source_actions"] for y in rep[role].values())
                for rep in rec["replicas"] for role in ("VALID","DEV"))
        check(rec["actual_original_source_episodes"]==624 and
              rec["original_source_public_steps"]<=624*MAX_STEPS,
              "TOTAL_ORIGINAL_SOURCE_BUDGET_DRIFT")
        rec["complete_public_fit_capacity_receipts_sha256"]=sha(raw)
        rec["disposition"]=(
            "PUBLIC_CS07_REWARD_SELECTED_SELECTIVE_MEMORY_SUPPORTED"
            if all(x["prospective_selective_memory_criterion_passed"] for x in rec["replicas"])
            else "PUBLIC_CS07_NO_VERIFIED_SELECTIVE_MEMORY_GAIN")
        rec["novel_architecture_or_genuine_unfamiliar_transfer_advantage"]="NOT_ESTABLISHED"
    except Exception as e:
        rec["first_failure"]=type(e).__name__+":"+str(e)[:750]
    finally:
        (out/"cs07-original-public-FIT-receipt.json").write_text(canon(raw)+"\n")
        (out/"cs07-original-source-receipt.json").write_text(
            json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print("CS07_DISPOSITION="+rec["disposition"],flush=True)
    return 2 if rec["disposition"]=="PUBLIC_CS07_INVALID_OR_LEAK" else 0
if __name__=="__main__":raise SystemExit(main())
