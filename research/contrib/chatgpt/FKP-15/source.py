"""FKP15 actual 16-step macro action return source. No hidden state or proxy rewards.

Source uses unmodified external Memory Gym at pinned public git SHA and its
explicit publicly configurable reward_fall_off=-0.05; NOT official default.
"""
from __future__ import annotations
import hashlib
import math
import os
from pathlib import Path
import random
import struct
import sys
os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
sys.dont_write_bytecode=True

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-12"))
import source as fkp12_source

TRAIN=tuple(range(975100,975148))
VALIDATION=tuple(range(975200,975216))
DEV=tuple(range(975500,975524))
TRANSFER=tuple(range(975600,975632))
ANCHORS=(0,16,32,64)
ACTIONS=tuple((a,b) for a in range(3) for b in range(3))
HORIZON=16
OPTIONS={"reward_fall_off":-0.05,"max_steps":512}
MAX_ACTIONS=245760
SOURCE_SHA="a94f2b60d1769ea44df3226561488768e1dff9f4"


def cohort(seed:int,*,allow_dev:bool=False)->str:
    if type(seed) is not int:raise ValueError("FKP15_SOURCE_SEED_TYPE")
    if seed in TRAIN:return "train"
    if seed in VALIDATION:return "validation"
    if allow_dev and seed in DEV:return "development"
    raise PermissionError("FKP15_PROTECTED_OR_UNREGISTERED_SOURCE")


def prefix_actions(seed:int)->tuple[tuple[int,int],...]:
    cohort(seed,allow_dev=True)
    rng=random.Random(seed^0xF15A0)
    result=[]
    for _ in range(max(ANCHORS)//8):
        action=(rng.randrange(3),rng.randrange(3))
        result.extend([action]*8)
    return tuple(result)


def sample_public_image(obs)->np.ndarray:
    return fkp12_source.pooled_public_rgb(obs)


def feature_pair(older:np.ndarray,now:np.ndarray,action_index:int)->np.ndarray:
    if (older.shape!=(192,) or now.shape!=(192,) or
        type(action_index) is not int or not 0<=action_index<9):
        raise ValueError("FKP15_INVALID_PUBLIC_INPUT")
    row=np.zeros(393,dtype=np.float32)
    row[:192]=older;row[192:384]=now;row[384+action_index]=1
    return row


def _frame_hash(frame,stream):
    image=np.asarray(frame)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3:
        raise ValueError("FKP15_NATIVE_RGB_DRIFT")
    stream.update(struct.pack("<III",*image.shape))
    stream.update(image.tobytes(order="C"))


def source_branch(seed:int,anchor:int,chosen:int|None,upstream:Path,*,allow_dev:bool=False)->dict:
    cohort(seed,allow_dev=allow_dev)
    if anchor not in ANCHORS or (chosen is not None and (type(chosen) is not int or not 0<=chosen<9)):
        raise ValueError("FKP15_BAD_PUBLIC_BRANCH")
    if str(upstream) not in sys.path:sys.path.insert(0,str(upstream))
    import gymnasium as gym
    import memory_gym # noqa: F401 (registers original source environments)
    env=gym.make("MysteryPath-v0",render_mode=None)
    hasher=hashlib.sha256()
    history={}
    steps=0
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP15_NATIVE_ACTION_SPACE_DRIFT")
        frame,_ignored=env.reset(seed=seed,options=dict(OPTIONS))
        _frame_hash(frame,hasher)
        history[0]=sample_public_image(frame)
        done=False
        for step,action in enumerate(prefix_actions(seed)[:anchor],1):
            if not env.action_space.contains(np.asarray(action,dtype=np.int64)):
                raise ValueError("FKP15_ILLEGAL_PUBLIC_PREFIX")
            hasher.update(bytes(action))
            frame,r,terminated,truncated,_ignored=env.step(np.asarray(action,dtype=np.int64))
            if not math.isfinite(float(r)):
                raise ValueError("FKP15_NONFINITE_SOURCE_PREFIX_REWARD")
            _frame_hash(frame,hasher)
            hasher.update(struct.pack("<d??",float(r),bool(terminated),bool(truncated)))
            steps+=1
            if step%8==0:history[step]=sample_public_image(frame)
            if terminated or truncated:
                done=True
                break
        if done:
            return {"valid":False,"seed":seed,"anchor":anchor,"prefix_steps":steps,
                    "prefix_sha256":hasher.hexdigest()}
        if steps!=anchor:
            raise AssertionError("FKP15_PUBLIC_PREFIX_MISMATCH")
        old=history[0] if anchor==0 else history[anchor-8]
        now=history[anchor]
        public_prefix=hasher.hexdigest()
        if chosen is None:
            return {"valid":True,"seed":seed,"anchor":anchor,
                    "prefix_sha256":public_prefix,"prefix_steps":steps,
                    "last_two_images":[old.tolist(),now.tolist()]}
        row=feature_pair(old,now,chosen)
        ret=0.0;reward_pos=0;reward_neg=0;goals=0;future=0
        act=ACTIONS[chosen]
        branch=hashlib.sha256()
        for _ in range(HORIZON):
            branch.update(bytes(act))
            frame,r,terminated,truncated,_ignored=env.step(np.asarray(act,dtype=np.int64))
            _frame_hash(frame,branch)
            branch.update(struct.pack("<d??",float(r),bool(terminated),bool(truncated)))
            if not math.isfinite(float(r)):raise ValueError("FKP15_NONFINITE_PUBLIC_RETURN")
            ret+=float(r)
            reward_pos+=int(float(r)>0)
            reward_neg+=int(float(r)<0)
            goals+=int(float(r)>=1 and bool(terminated))
            future+=1
            if terminated or truncated:break
        return {"valid":True,"seed":seed,"anchor":anchor,
            "action":chosen,"prefix_sha256":public_prefix,
            "prefix_steps":steps,"future_steps":future,
            "real_return":float(round(ret,8)),
            "positive_events":reward_pos,"negative_events":reward_neg,
            "true_goals":goals,"branch_sha256":branch.hexdigest(),
            "x":row}
    finally:env.close()


def collect_all_branches(seeds:tuple[int,...],upstream:Path)->tuple[list[dict],dict]:
    if seeds not in (TRAIN,VALIDATION):
        raise PermissionError("FKP15_TRAIN_VAL_ONLY")
    receipts=[]
    actions=0;prefixes=0
    custody=fkp12_source.source_custody(upstream)
    assert custody["source_sha"]==SOURCE_SHA
    for seed in seeds:
        for anchor in ANCHORS:
            row_prefix=source_branch(seed,anchor,None,upstream)
            actions+=row_prefix["prefix_steps"]
            prefixes+=1
            if not row_prefix["valid"]:
                raise ValueError("FKP15_EARLY_PREFIX_TERMINATION")
            for a in range(9):
                r=source_branch(seed,anchor,a,upstream)
                actions+=r["prefix_steps"]+r["future_steps"]
                if not r["valid"] or r["prefix_sha256"]!=row_prefix["prefix_sha256"]:
                    raise ValueError("FKP15_DIFFERENT_REAL_PUBLIC_PREFIX")
                receipts.append(r)
    digest=hashlib.sha256()
    for r in receipts:
        digest.update(struct.pack("<IIId",r["seed"],r["anchor"],r["action"],r["real_return"]))
        digest.update(bytes.fromhex(r["prefix_sha256"]))
        digest.update(bytes.fromhex(r["branch_sha256"]))
    return receipts,{"source_receipt_sha256":digest.hexdigest(),
                    "actions":actions,"physical_resets":prefixes+len(receipts),
                    "branch_count":len(receipts),"world_count":len(seeds),
                    "upstream_original_sha":SOURCE_SHA}
