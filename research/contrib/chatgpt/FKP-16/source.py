"""FKP-16 genuine source-only public visual histories and macro consequences.

Train/VAL/DEV source partitions immutable; DEV called only by one-shot after
dual-platform source-safe/G29/full-regression gate. No hidden env state/info.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import random
import struct
import sys
import time
import numpy as np

os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-10"))
import admit

SOURCE_SHA=admit.SOURCE_SHA
TASK="MysteryPath-v0"
OPTIONS={"reward_fall_off":-0.05,"max_steps":512}
TRAIN=tuple(range(975100,975164))
VAL=tuple(range(975200,975216))
DEV=tuple(range(976500,976532))
TRANSFER=tuple(range(976600,976664))
ANCHORS=(0,16,32,64)
HORIZON=16
ACTIONS=tuple((a,b) for a in range(3) for b in range(3))
MAX_ACTIONS=358400
DIM=204


def gate(seed:int,allow_dev:bool=False):
    if type(seed) is not int:raise ValueError("FKP15_BAD_SEED")
    if seed in TRAIN:return "TRAIN"
    if seed in VAL:return "VALIDATION"
    if seed in DEV and allow_dev:return "DEVELOPMENT"
    raise PermissionError("FKP15_COHORT_BOUNDARY")


def prefix(seed:int,anchor:int):
    gate(seed,allow_dev=True)
    if anchor not in ANCHORS:raise ValueError("FKP15_ANCHOR_FENCE")
    r=random.Random(seed^0xF15A0)
    actions=[]
    for _ in range(max(ANCHORS)//8):
        x=(r.randrange(3),r.randrange(3))
        actions.extend([x]*8)
    return tuple(actions[:anchor])


def public_feature(obs,previous_action,previous_sign):
    a=np.asarray(obs)
    if a.ndim!=3 or a.shape[-1]!=3 or a.dtype!=np.uint8 or min(a.shape[:2])<8:
        raise ValueError("FKP15_INVALID_PUBLIC_RGB")
    if previous_action is not None and (previous_action not in ACTIONS):
        raise ValueError("FKP15_BAD_PUBLIC_PRIOR_ACTION")
    if previous_sign not in (0,1,2):raise ValueError("FKP15_BAD_PREVIOUS_REWARD")
    h,w=a.shape[:2]
    f=np.zeros(DIM,dtype=np.float32)
    for i in range(8):
        for j in range(8):
            f[3*(i*8+j):3*(i*8+j)+3]=a[i*h//8:(i+1)*h//8,
                                           j*w//8:(j+1)*w//8,:].mean(
                                               axis=(0,1),dtype=np.float64)/255.0
    if previous_action is not None:
        f[192+previous_action[0]*3+previous_action[1]]=1
    f[201+previous_sign]=1
    return f


def outcome_sign(reward):
    if not np.isfinite(reward):raise ValueError("FKP15_NONFINITE_SOURCE_REWARD")
    return 0 if reward<0 else 2 if reward>0 else 1


def public_digest(h,obs):
    frame=np.asarray(obs)
    if frame.dtype!=np.uint8 or frame.ndim!=3 or frame.shape[2]!=3:
        raise ValueError("FKP15_RGB_DIGEST")
    h.update(struct.pack("<III",*frame.shape))
    h.update(frame.tobytes(order="C"))


def real_prefix(seed:int,anchor:int,allow_dev=False):
    gate(seed,allow_dev=allow_dev)
    """Only public returned RGB+actions+rewards; no simulator private fields."""
    import gymnasium as gym
    import memory_gym  # noqa: F401 source-original native registration
    env=gym.make(TASK,render_mode=None)
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP15_NATIVE_ACTION_DRIFT")
        obs,_unused_info=env.reset(seed=seed,options=dict(OPTIONS))
        digest=hashlib.sha256()
        public_digest(digest,obs)
        history=[public_feature(obs,None,1)]
        steps=0
        for action in prefix(seed,anchor):
            digest.update(bytes(action))
            obs,r,done,trunc,_unused_info=env.step(np.asarray(action,dtype=np.int64))
            r=float(r)
            public_digest(digest,obs)
            digest.update(struct.pack("<d??",r,bool(done),bool(trunc)))
            history.append(public_feature(obs,action,outcome_sign(r)))
            steps+=1
            if done or trunc:
                env.close()
                return {"valid":False,"seed":seed,"anchor":anchor,"source_steps":steps,
                        "prefix_sha256":digest.hexdigest(),"reason":"PUBLIC_PREFIX_TERMINATED"}
        sequence=np.stack(history).astype(np.float32)
        context=sequence[-min(8,len(sequence)):].mean(axis=0,dtype=np.float64).astype(np.float32)
        return {"valid":True,"seed":seed,"anchor":anchor,"source_steps":steps,
                "prefix_sha256":digest.hexdigest(),
                "sequence":sequence,"context":context,"env":env}
    except Exception:
        env.close()
        raise


def replay_branch(seed:int,anchor:int,action_index:int,allow_dev=False):
    gate(seed,allow_dev=allow_dev)
    if type(action_index) is not int or not 0<=action_index<9:
        raise ValueError("FKP15_ACTION_INDEX")
    pre=real_prefix(seed,anchor,allow_dev=allow_dev)
    if not pre["valid"]:
        return pre
    env=pre.pop("env")
    digest=hashlib.sha256()
    rewards=[]
    goal=0
    try:
        action=ACTIONS[action_index]
        for t in range(HORIZON):
            digest.update(bytes(action))
            obs,r,done,trunc,_unused_info=env.step(np.asarray(action,dtype=np.int64))
            r=float(r)
            public_digest(digest,obs)
            digest.update(struct.pack("<d??",r,bool(done),bool(trunc)))
            rewards.append(r)
            goal+=int(r>=1. and done)
            if done or trunc:break
        return {**pre,
                "action_index":action_index,"branch_sha256":digest.hexdigest(),
                "future_source_steps":len(rewards),
                "reward_return":round(sum(rewards),8),
                "positive_return":int(sum(rewards)>0),
                "positive_events":int(sum(r>0 for r in rewards)),
                "negative_events":int(sum(r<0 for r in rewards)),
                "goals":goal}
    finally:
        env.close()


def collect_one(seed:int,anchor:int,allow_dev=False):
    gate(seed,allow_dev=allow_dev)
    ref=real_prefix(seed,anchor,allow_dev=allow_dev)
    if not ref["valid"]:return {"valid":False,"seed":seed,"anchor":anchor,"source_steps":ref["source_steps"]}
    env=ref.pop("env")
    env.close()
    branches=[replay_branch(seed,anchor,k,allow_dev=allow_dev) for k in range(9)]
    for r in branches:
        if not r["valid"] or r["prefix_sha256"]!=ref["prefix_sha256"] or not np.array_equal(r["context"],ref["context"]) or not np.array_equal(r["sequence"],ref["sequence"]):
            raise AssertionError("FKP15_ALTERNATIVE_DIFFERENT_PUBLIC_HISTORY")
    return {"valid":True,"seed":seed,"anchor":anchor,
            "sequence":ref["sequence"],"context":ref["context"],
            "prefix_sha256":ref["prefix_sha256"],
            "returns":np.asarray([r["reward_return"] for r in branches],dtype=np.float64),
            "goal_by_action":[r["goals"] for r in branches],
            "positive_by_action":[r["positive_events"] for r in branches],
            "physical_steps":ref["source_steps"]+sum(r["source_steps"]+r["future_source_steps"] for r in branches),
            "physical_resets":10,
            "branches_sha256":[r["branch_sha256"] for r in branches]}


def collect(seeds:tuple[int,...],allow_dev=False):
    if type(seeds) is not tuple or (not allow_dev and seeds not in (TRAIN,VAL)) or (allow_dev and seeds!=DEV):
        raise PermissionError("FKP15_FROZEN_SPLIT_ONLY")
    out=[]
    for seed in seeds:
        for anchor in ANCHORS:
            out.append(collect_one(seed,anchor,allow_dev=allow_dev))
    return out


def cohort_digest(rows):
    h=hashlib.sha256()
    for r in rows:
        h.update(struct.pack("<II?",r["seed"],r["anchor"],r["valid"]))
        if r["valid"]:
            h.update(r["prefix_sha256"].encode("ascii"))
            h.update(r["context"].astype("<f4").tobytes())
            h.update(r["sequence"].astype("<f4").tobytes())
            h.update(r["returns"].astype("<f8").tobytes())
            for digest in r["branches_sha256"]:h.update(digest.encode("ascii"))
    return h.hexdigest()
