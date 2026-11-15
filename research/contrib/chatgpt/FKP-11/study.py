"""FKP-11: source-blind public Memory Gym action/observation sufficiency study.

All model state comes from source-native public image observations and genuine
chosen actions/outcomes. Never access original environment internals or info.
This is an exploratory source-information diagnostic, NOT science/AGI proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import time

os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"

UPSTREAM="a94f2b60d1769ea44df3226561488768e1dff9f4"
BLOBS={
 "LICENSE":"71f0e4887c38776d7ed25bdbbd1c9f5a9156d9c5",
 "setup.py":"fca17dd1d52d5c14839e20568a6d850bfeb30044",
 "memory_gym/__init__.py":"1e0da856e084fd4a6c8a409c41182d10be7d5c13",
 "memory_gym/mortar_mayhem.py":"5217196b9b4f1dfa9e67675c0ac1dbffe4b9d9a9",
 "memory_gym/mystery_path.py":"2f80721f8dd33f4f438e07c42fa65b920fd301ed",
}
TASKS=("MortarMayhem-v0","MysteryPath-v0")
SEEDS=tuple(range(971000,971008))
ARMS=("curiosity","balanced","random")
N_ACT=9
MAX_STEPS=64
WARMUP=9
PROTOCOL=("FKP11-MEMORYGYM-V1|upstream=a94f2b60d1769ea44df3226561488768e1dff9f4|"
 "tasks=MortarMayhem-v0,MysteryPath-v0|dev=971000..971007|maxsteps=64|"
 "arms=curiosity,balanced,random|public_observation_only|warmup=9|"
 "source-still-unchanged|no-protected-first-use")
PROTOCOL_SHA256="c97dff4aa1b80b7fe8c0438a3960712224924d9475b85892f5718a1bd4c3c83e"
assert hashlib.sha256(PROTOCOL.encode()).hexdigest()==PROTOCOL_SHA256


def source_custody(root:Path)->dict:
    if not root.is_dir() or not (root/".git").exists():
        raise ValueError("FKP11_UPSTREAM_SOURCE_MISSING")
    def git(*args):
        return subprocess.run(("git","-C",str(root),*args),
            check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            encoding="utf-8").stdout.strip()
    if git("rev-parse","HEAD")!=UPSTREAM:
        raise ValueError("FKP11_UPSTREAM_SHA_MISMATCH")
    for path,blob in BLOBS.items():
        if git("rev-parse","HEAD:"+path)!=blob:
            raise ValueError("FKP11_UPSTREAM_BLOB_MISMATCH:"+path)
    if git("status","--porcelain","--untracked-files=all"):
        raise ValueError("FKP11_UPSTREAM_DIRTY")
    return {"exact_git_sha":UPSTREAM,"verified_original_blobs":len(BLOBS),
            "license":"MIT","worktree_clean":True}


def observed_state(observation)->tuple[bytes,bytes,tuple[int,...]]:
    """Derive public 8x8 quantized image, not env ground truth or position."""
    import numpy as np
    pixels=np.asarray(observation)
    if pixels.dtype.hasobject or pixels.ndim not in (2,3) or pixels.size==0:
        raise ValueError("FKP11_PUBLIC_OBSERVATION_INVALID")
    pixels=np.ascontiguousarray(pixels)
    shape=tuple(int(x) for x in pixels.shape)
    h,w=shape[:2]
    ys=np.linspace(0,h-1,8,dtype=np.intp)
    xs=np.linspace(0,w-1,8,dtype=np.intp)
    reduced=pixels[np.ix_(ys,xs)]
    if reduced.ndim==3:
        gray=reduced.astype(np.float32).mean(axis=2)
    else:gray=reduced.astype(np.float32)
    # Deliberately quantize to 8 bins to avoid treating pixel flicker as
    # evidence of distinct causal world states. No hidden game-state labels.
    feature=np.clip(gray.astype(np.int16)//32,0,7).astype(np.uint8).tobytes()
    if len(feature)!=64:raise AssertionError("FKP11_FEATURE_DIMENSION_DRIFT")
    full=hashlib.sha256(pixels.tobytes(order="C")).digest()
    return feature,full,shape


class PublicAssociationMemory:
    """Bounded source-observation/action consequence counts, no text tokens."""
    def __init__(self,seed:int):
        self.seed=seed
        self.state_action_count=Counter()
        self.global_action_count=Counter()
        self.transition_count=Counter()
        self.repeat_pairs=0
        self.repeated_pair_conflicts=0
        self.last_effect={}
    def choose(self,feature:bytes,step:int)->int:
        if type(feature) is not bytes or len(feature)!=64:
            raise ValueError("FKP11_BAD_PUBLIC_FEATURE")
        if step<WARMUP:
            return (step+self.seed%N_ACT)%N_ACT
        state=hashlib.sha256(feature).digest()[:8]
        # Equal action budget: choices depend only on prior public observations
        # and consequences, plus a frozen deterministic action tie-break.
        return min(range(N_ACT),key=lambda a:(
            self.state_action_count[(state,a)],
            self.global_action_count[a],
            (a-self.seed%N_ACT)%N_ACT))
    def update(self,before:bytes,action:int,after:bytes)->None:
        if type(before) is not bytes or type(after) is not bytes or len(before)!=64 or len(after)!=64:
            raise ValueError("FKP11_PUBLIC_TRANSITION_INVALID")
        if type(action) is not int or not 0<=action<N_ACT:
            raise ValueError("FKP11_ACTION_INVALID")
        key=(hashlib.sha256(before).digest()[:8],action)
        after_hash=hashlib.sha256(after).digest()[:8]
        if self.state_action_count[key]:
            self.repeat_pairs+=1
            if self.last_effect[key]!=after_hash:self.repeated_pair_conflicts+=1
        self.state_action_count[key]+=1
        self.global_action_count[action]+=1
        self.transition_count[(key,after_hash)]+=1
        self.last_effect[key]=after_hash
    def summary(self)->dict:
        return {"distinct_observed_state_action_pairs":len(self.state_action_count),
                "repeated_state_action_pairs":self.repeat_pairs,
                "conflicting_repeated_state_action_outcomes":self.repeated_pair_conflicts,
                "distinct_action_conditioned_transitions":len(self.transition_count),
                "memory_entries":len(self.transition_count),
                "global_action_counts":[self.global_action_count[a] for a in range(N_ACT)]}


def episode(task:str,seed:int,arm:str)->dict:
    if task not in TASKS or seed not in SEEDS or arm not in ARMS:
        raise PermissionError("FKP11_UNFROZEN_TASK_SEED_OR_POLICY")
    import gymnasium as gym
    import memory_gym # noqa: F401 - original upstream registers real Gym environments
    import numpy as np
    start=time.perf_counter()
    env=gym.make(task,render_mode=None)
    memory=PublicAssociationMemory(seed)
    reward_sum=0.0
    reward_events=0
    state_signatures=set()
    full_signatures=set()
    trace=hashlib.sha256()
    warmup_hash=hashlib.sha256()
    shape0=None
    rng=random.Random(seed^0xFA117)
    steps=0;terminated=False
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP11_ORIGINAL_ACTION_SPACE_DRIFT")
        raw,_ignored_info=env.reset(seed=seed)
        feature,full,shape=observed_state(raw)
        shape0=shape
        trace.update(full);warmup_hash.update(full)
        state_signatures.add(feature)
        full_signatures.add(full)
        for step in range(MAX_STEPS):
            if step<WARMUP:
                action=memory.choose(feature,step)
            elif arm=="curiosity":
                action=memory.choose(feature,step)
            elif arm=="balanced":
                action=(step+seed%N_ACT)%N_ACT
            else:
                action=rng.randrange(N_ACT)
            native=np.asarray([action//3,action%3],dtype=np.int64)
            assert env.action_space.contains(native)
            raw,reward,done,trunc,_ignored_info=env.step(native)
            if not math.isfinite(float(reward)):
                raise ValueError("FKP11_NONFINITE_REAL_REWARD")
            nxt,full_nxt,shape_now=observed_state(raw)
            if shape_now!=shape0:
                raise ValueError("FKP11_SOURCE_IMAGE_SHAPE_DRIFT")
            encoded=bytes((action,))+struct.pack("<d??",float(reward),bool(done),bool(trunc))+full_nxt
            trace.update(encoded)
            if step<WARMUP:warmup_hash.update(encoded)
            memory.update(feature,action,nxt)
            state_signatures.add(nxt);full_signatures.add(full_nxt)
            feature=nxt
            reward_sum+=float(reward)
            reward_events+=int(float(reward)!=0.0)
            steps=step+1
            if done or trunc:
                terminated=True
                break
    finally:
        env.close()
    if steps<1:raise AssertionError("FKP11_NO_NATIVE_SOURCE_STEPS")
    return {"task":task,"seed":seed,"arm":arm,"true_env_steps":steps,
            "actual_reward_sum":round(reward_sum,9),
            "nonzero_reward_events":reward_events,"terminated":terminated,
            "public_image_shape":list(shape0),
            "unique_quantized_observations":len(state_signatures),
            "unique_full_frames":len(full_signatures),
            "quantized_novelty_per_step":len(state_signatures)/steps,
            "warmup_public_trace_sha256":warmup_hash.hexdigest(),
            "whole_public_trace_sha256":trace.hexdigest(),
            "original_observed_source":True,
            "model":memory.summary(),
            "wall_seconds_dev":round(time.perf_counter()-start,6)}


def paired_ci(values:list[float])->list[float]:
    rng=random.Random(9090);n=len(values)
    draws=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
    return [draws[249],draws[9749]]


def study(root:Path)->dict:
    custody=source_custody(root)
    sys.path.insert(0,str(root))
    sys.dont_write_bytecode=True
    start=time.perf_counter();cpu=time.process_time()
    rows=[episode(task,seed,arm)
          for task in TASKS for seed in SEEDS for arm in ARMS]
    if len(rows)!=48:raise AssertionError("FKP11_MISSING_ARM_OR_SEED")
    paired={}
    for task in TASKS:
        for seed in SEEDS:
            rr=[r for r in rows if r["task"]==task and r["seed"]==seed]
            if len(rr)!=3 or len({r["warmup_public_trace_sha256"] for r in rr})!=1:
                raise AssertionError("FKP11_WARMUP_MISMATCH_ACROSS_ARMS")
        table={(r["seed"],r["arm"]):r for r in rows if r["task"]==task}
        summary={}
        for arm in ARMS:
            data=[table[(seed,arm)] for seed in SEEDS]
            summary[arm]={
              "actual_source_steps":sum(x["true_env_steps"] for x in data),
              "true_reward_events":sum(x["nonzero_reward_events"] for x in data),
              "true_reward_total":round(sum(x["actual_reward_sum"] for x in data),7),
              "mean_unique_quantized_observations":sum(x["unique_quantized_observations"] for x in data)/len(data),
              "mean_unique_quantized_per_step":sum(x["quantized_novelty_per_step"] for x in data)/len(data),
              "mean_distinct_state_action_pairs":sum(x["model"]["distinct_observed_state_action_pairs"] for x in data)/len(data),
              "sum_repeated_state_action_conflicts":sum(x["model"]["conflicting_repeated_state_action_outcomes"] for x in data),
              "terminal_episodes":sum(x["terminated"] for x in data),
            }
        for other in ("balanced","random"):
            deltas=[table[(seed,"curiosity")]["quantized_novelty_per_step"]-table[(seed,other)]["quantized_novelty_per_step"]
                    for seed in SEEDS]
            summary["curiosity_minus_"+other]={
                "mean_novelty_rate_gain":sum(deltas)/len(deltas),
                "paired_bootstrap_ci95":paired_ci(deltas)}
        paired[task]=summary
    positive=all(
        paired[task]["curiosity"]["mean_unique_quantized_per_step"]>=
        1.10*max(paired[task][b]["mean_unique_quantized_per_step"] for b in ("balanced","random"))
        and all(paired[task]["curiosity_minus_"+b]["paired_bootstrap_ci95"][0]>0 for b in ("balanced","random"))
        and paired[task]["curiosity"]["true_reward_total"]>=max(paired[task][b]["true_reward_total"] for b in ("balanced","random"))
        for task in TASKS)
    reward_sparse=any(sum(paired[task][arm]["true_reward_events"] for arm in ARMS)==0 for task in TASKS)
    digest_rows=[{k:r[k] for k in ("task","seed","arm","true_env_steps","actual_reward_sum",
          "nonzero_reward_events","unique_quantized_observations","warmup_public_trace_sha256",
          "whole_public_trace_sha256")} for r in rows]
    packed=json.dumps(digest_rows,sort_keys=True,separators=(",",":"))
    status=("DEV_PUBLIC_INFORMATION_SIGNAL_ONLY" if positive and not reward_sparse
            else "SOURCE_REWARD_SIGNAL_INSUFFICIENT" if reward_sparse
            else "DEV_NO_GO_CURIOSITY_POLICY")
    return {
        "schema":"fkp11.memorygym-public-action-feedback-dev.v1",
        "classification":status,
        "independent_scientific_pass":False,
        "accepted_native_model_changed":False,
        "protected_first_use":False,
        "source":custody,
        "tasks":list(TASKS),
        "arms":list(ARMS),
        "source_episode_count":len(rows),
        "per_episode_source_action_cap":MAX_STEPS,
        "source_steps":sum(r["true_env_steps"] for r in rows),
        "true_public_reward_events":sum(r["nonzero_reward_events"] for r in rows),
        "original_public_trace_sha256":hashlib.sha256(packed.encode()).hexdigest(),
        "original_source_reward_sparse":reward_sparse,
        "curiosity_positive_source_signal":positive,
        "by_task":paired,"rows":rows,
        "total_wall_seconds_dev":round(time.perf_counter()-start,6),
        "total_cpu_seconds_dev":round(time.process_time()-cpu,6),
        "strong_trained_recurrent_control":"NOT_PERFORMED",
        "whole_process_cost_parity":"NOT_PERFORMED",
        "cold_retention_under_interference":"NOT_PERFORMED"
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-dev",action="store_true")
    ap.add_argument("--upstream-root",type=Path)
    ap.add_argument("--primary",action="store_true")
    args=ap.parse_args()
    if args.primary or not args.public_dev or args.upstream_root is None:
        ap.error("FKP11 PROTECTED SCIENCE DISARMED; exact public source required")
    print(json.dumps(study(args.upstream_root.resolve()),sort_keys=True))
