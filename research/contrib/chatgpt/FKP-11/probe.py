"""FKP-11 public Memory Gym feedback headroom, not a trained learner.

Exactly 32 NEW public DEV trajectories: two original upstream tasks, 4 seeds,
two source-blind public action policies and two upstream public reward modes.
Unmodified transitions/observations are compared by paired trace SHA256.
No protected first-use, private labels, debug/hidden env or model training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys
import time

os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"

HERE=Path(__file__).resolve().parent
FKP10=HERE.parent/"FKP-10"
sys.path.insert(0,str(FKP10))
import admit

TASKS=("MortarMayhem-v0","MysteryPath-v0")
SEEDS=(971100,971101,971102,971103)
POLICIES=("random","macro8")
MODES=("original","public_failure_feedback")
MAX_STEPS=256
REWARD_FAILURE=-0.05


def reward_options(task: str,mode: str) -> dict|None:
    if task not in TASKS or mode not in MODES:
        raise ValueError("FKP11_UNREGISTERED_TASK_OR_MODE")
    if mode=="original":return None
    if task=="MortarMayhem-v0":
        return {"reward_command_failure":REWARD_FAILURE}
    return {"reward_fall_off":REWARD_FAILURE}


def choose_action(seed:int,policy:str,step:int)->tuple[int,int]:
    if type(seed) is not int or seed not in SEEDS or policy not in POLICIES:
        raise ValueError("FKP11_UNREGISTERED_SOURCE_COHORT")
    if type(step) is not int or not 0<=step<MAX_STEPS:
        raise ValueError("FKP11_ACTION_OUTSIDE_BUDGET")
    if policy=="random":
        # Recompute from the same fixed seed/step, so paired modes MUST agree.
        rng=random.Random(seed^0xF11A1)
        for _ in range(step):
            rng.randrange(3);rng.randrange(3)
        return rng.randrange(3),rng.randrange(3)
    rng=random.Random(seed^0xF11B2)
    for _ in range(step//8):
        rng.randrange(3);rng.randrange(3)
    return rng.randrange(3),rng.randrange(3)


def episode(task:str,seed:int,policy:str,mode:str)->dict:
    if task not in TASKS or seed not in SEEDS or policy not in POLICIES or mode not in MODES:
        raise ValueError("FKP11_SOURCE_BOUNDARY")
    import gymnasium as gym
    import memory_gym  # noqa: F401; original source registration
    import numpy as np
    started=time.perf_counter()
    env=gym.make(task,render_mode=None)
    trace=hashlib.sha256()
    reward_digest=hashlib.sha256()
    n_obs=set()
    rewards=[]
    terminal=False
    try:
        space=env.action_space
        if (not isinstance(space,gym.spaces.MultiDiscrete)
            or tuple(int(x) for x in space.nvec)!=(3,3)):
            raise ValueError("FKP11_ACTION_SPACE_DRIFT")
        obs,_info=env.reset(seed=seed,options=reward_options(task,mode))
        dtype,shape=admit.frame(trace,obs)
        n_obs.add(hashlib.sha256(np.asarray(obs).tobytes(order="C")).digest())
        for step in range(MAX_STEPS):
            a,b=choose_action(seed,policy,step)
            action=np.asarray((a,b),dtype=np.int64)
            if not env.action_space.contains(action):
                raise ValueError("FKP11_ACTION_INVALID")
            trace.update(bytes((a,b)))
            obs,rew,done,trunc,_info=env.step(action)
            if not math.isfinite(float(rew)):
                raise ValueError("FKP11_NONFINITE_ORIGINAL_REWARD")
            dtype_next,shape_next=admit.frame(trace,obs)
            if (dtype_next,shape_next)!=(dtype,shape):
                raise ValueError("FKP11_OBSERVATION_SHAPE_DRIFT")
            n_obs.add(hashlib.sha256(np.asarray(obs).tobytes(order="C")).digest())
            trace.update(bytes((bool(done),bool(trunc))))
            reward_digest.update(struct.pack("<d",float(rew)))
            rewards.append(float(rew))
            if done or trunc:
                terminal=True
                break
        return {"task":task,"seed":seed,"policy":policy,"mode":mode,
            "actions":len(rewards),"terminated":terminal,
            "trace_observation_actions_sha256":trace.hexdigest(),
            "native_reward_sha256":reward_digest.hexdigest(),
            "observation_shape":list(shape),"observation_dtype":dtype,
            "distinct_observation_frames":len(n_obs),
            "rewards_positive":sum(r>0 for r in rewards),
            "rewards_negative":sum(r<0 for r in rewards),
            "rewards_nonzero":sum(r!=0 for r in rewards),
            "rewards_nonzero_first32":sum(r!=0 for r in rewards[:32]),
            "reward_sum":round(sum(rewards),8),
            "wall_seconds":round(time.perf_counter()-started,6)}
    finally:
        env.close()


def run(root:Path)->dict:
    began=time.perf_counter()
    source=admit.source_custody(root)
    sys.path.insert(0,str(root))
    pairs=[];rows=[]
    paired_identity=True
    for task in TASKS:
        for seed in SEEDS:
            for policy in POLICIES:
                original=episode(task,seed,policy,"original")
                feedback=episode(task,seed,policy,"public_failure_feedback")
                rows.extend((original,feedback))
                identical=(original["actions"]==feedback["actions"]
                    and original["terminated"]==feedback["terminated"]
                    and original["trace_observation_actions_sha256"]==
                        feedback["trace_observation_actions_sha256"])
                paired_identity &= identical
                pairs.append({"task":task,"seed":seed,"policy":policy,"dynamics_same":identical,
                    "original_nonzero":original["rewards_nonzero"],
                    "feedback_nonzero":feedback["rewards_nonzero"],
                    "added_nonzero":feedback["rewards_nonzero"]-original["rewards_nonzero"]})
    metrics={}
    headroom={}
    for task in TASKS:
        x=[r for r in rows if r["task"]==task]
        a=[r for r in x if r["mode"]=="original"]
        b=[r for r in x if r["mode"]=="public_failure_feedback"]
        paired=[p for p in pairs if p["task"]==task]
        added=sum(p["added_nonzero"] for p in paired)
        with_feedback=sum(p["feedback_nonzero"]>=2 for p in paired)
        novel=max(r["distinct_observation_frames"] for r in x)
        metrics[task]={
            "original_reward_events":sum(r["rewards_nonzero"] for r in a),
            "original_positive_events":sum(r["rewards_positive"] for r in a),
            "feedback_reward_events":sum(r["rewards_nonzero"] for r in b),
            "feedback_positive_events":sum(r["rewards_positive"] for r in b),
            "feedback_negative_events":sum(r["rewards_negative"] for r in b),
            "additional_reward_events":added,
            "feedback_episodes_ge2":with_feedback,
            "distinct_observation_frames_at_least":novel,
            "original_paid_source_steps":sum(r["actions"] for r in a),
            "feedback_paid_source_steps":sum(r["actions"] for r in b),
            "nonzero_first32_original":sum(r["rewards_nonzero_first32"] for r in a),
        }
        headroom[task]=(added>=16 and with_feedback>=4 and novel>=2)
    digest=hashlib.sha256()
    for row in rows:
        for field in ("task","seed","policy","mode","actions","terminated",
                      "trace_observation_actions_sha256","native_reward_sha256",
                      "rewards_positive","rewards_negative","rewards_nonzero"):
            val=str(row[field]).encode("utf-8")
            digest.update(len(val).to_bytes(4,"little")+val)
    classification=("SOURCE_HEADROOM_PASS" if paired_identity and all(headroom.values())
                    else "SOURCE_PAIR_DRIFT" if not paired_identity
                    else "SOURCE_MIXED_FEEDBACK_INSUFFICIENT")
    return {
        "schema":"yggdrasil.fkp11.memorygym-feedback-headroom.v1",
        "original_development_consumed":True,
        "protected_science_used":False,
        "learner_trained":False,
        "native_yggdrasil_modified":False,
        "science_pass":False,
        "source":source,
        "episodes":len(rows),
        "actual_source_actions":sum(r["actions"] for r in rows),
        "all_reward_pairs_identical_dynamics":paired_identity,
        "headroom_per_task":headroom,
        "classification":classification,
        "metrics":metrics,
        "source_receipt_sha256":digest.hexdigest(),
        "wall_seconds_total":round(time.perf_counter()-began,6),
        "rows":rows,
        "pairs":pairs,
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--public-dev",action="store_true")
    p.add_argument("--upstream-root",type=Path)
    p.add_argument("--protected",action="store_true")
    args=p.parse_args()
    if args.protected or not args.public_dev or args.upstream_root is None:
        p.error("FKP11_ONLY_FROZEN_PUBLIC_SOURCE_DEV_AND_NO_PROTECTED_FIRST_USE")
    print(json.dumps(run(args.upstream_root.resolve()),sort_keys=True))
