"""FKP-12 source adapter: true public Mystery Path action consequences only.

Never use env.unwrapped, render debug, info content, source-private layout or
protected science. Public image -> fixed pooled numeric features, no tokens.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import random
import struct
import sys
import time

os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-10"))
import admit

SOURCE_SHA="a94f2b60d1769ea44df3226561488768e1dff9f4"
TASK="MysteryPath-v0"
TRAIN=tuple(range(971300,971316))
VALIDATION=tuple(range(971400,971404))
DEV=tuple(range(971500,971508))
RESERVED_TRANSFER=tuple(range(971600,971608))
POLICIES=("uniform","macro8")
FEATURE_DIM=204
CAP_STEPS=256
NEGATIVE_REWARD=-0.05


def permitted(seed:int,allow_dev:bool=False)->str:
    if type(seed) is not int:raise ValueError("FKP12_SEED_TYPE")
    if seed in TRAIN:return "TRAIN"
    if seed in VALIDATION:return "VALIDATE"
    if seed in DEV and allow_dev:return "DEV"
    raise PermissionError("FKP12_SOURCE_COHORT_FENCE")


def action(seed:int,policy:str,step:int)->tuple[int,int]:
    permitted(seed,allow_dev=True)
    if policy not in POLICIES or type(step) is not int or not 0<=step<CAP_STEPS:
        raise ValueError("FKP12_UNREGISTERED_ACTION")
    if policy=="uniform":
        rng=random.Random(seed^0xF11A1)
        for _ in range(step):
            rng.randrange(3);rng.randrange(3)
        return rng.randrange(3),rng.randrange(3)
    rng=random.Random(seed^0xF11B2)
    for _ in range(step//8):
        rng.randrange(3);rng.randrange(3)
    return rng.randrange(3),rng.randrange(3)


def pooled_public_rgb(obs):
    import numpy as np
    z=np.asarray(obs)
    if z.ndim!=3 or z.shape[2]!=3 or z.dtype!=np.uint8 or min(z.shape[:2])<8:
        raise ValueError("FKP12_PUBLIC_IMAGE_REQUIRED")
    h,w=z.shape[:2]
    out=np.empty((8,8,3),dtype=np.float32)
    for i in range(8):
        top=i*h//8;bottom=(i+1)*h//8
        for j in range(8):
            left=j*w//8;right=(j+1)*w//8
            out[i,j,:]=z[top:bottom,left:right,:].mean(axis=(0,1),dtype=np.float64)
    return (out.reshape(192)/np.float32(255)).astype(np.float32)


def input_feature(obs,control:tuple[int,int],previous_label:int):
    import numpy as np
    if type(control) is not tuple or len(control)!=2 or any(type(v)!=int or not 0<=v<3 for v in control):
        raise ValueError("FKP12_PUBLIC_ACTION_REQUIRED")
    if type(previous_label) is not int or previous_label not in (0,1,2):
        raise ValueError("FKP12_PUBLIC_PREVIOUS_FEEDBACK")
    feat=np.zeros(FEATURE_DIM,dtype=np.float32)
    feat[:192]=pooled_public_rgb(obs)
    feat[192+control[0]*3+control[1]]=1
    feat[201+previous_label]=1
    return feat


def label(reward:float)->int:
    if not isinstance(reward,(float,int)) or reward!=reward:
        raise ValueError("FKP12_UNSAFE_REWARD")
    if reward<0:return 0
    if reward>0:return 2
    return 1


def source_custody(upstream:Path)->dict:
    return admit.source_custody(upstream)


def episode(seed:int,policy:str,allow_dev:bool=False):
    """Collect only actual action/observation/feedback and pre-reward features."""
    permitted(seed,allow_dev=allow_dev)
    if policy not in POLICIES:raise ValueError("FKP12_POLICY_FENCE")
    import numpy as np
    import gymnasium as gym
    import memory_gym  # noqa: F401; original exact source registration
    started=time.perf_counter()
    env=gym.make(TASK,render_mode=None)
    source_digest=hashlib.sha256()
    try:
        obs,_info=env.reset(seed=seed,options={"reward_fall_off":NEGATIVE_REWARD})
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP12_SOURCE_ACTION_SPACE_DRIFT")
        admit.frame(source_digest,obs)
        xs=[];ys=[];previous=1
        for step in range(CAP_STEPS):
            a=action(seed,policy,step)
            xs.append(input_feature(obs,a,previous))
            source_digest.update(bytes(a))
            obs,reward,terminated,truncated,_info=env.step(np.asarray(a,dtype=np.int64))
            current=label(float(reward))
            ys.append(current)
            admit.frame(source_digest,obs)
            source_digest.update(struct.pack("<d??",float(reward),bool(terminated),bool(truncated)))
            previous=current
            if terminated or truncated:break
        x=np.asarray(xs,dtype=np.float32)
        y=np.asarray(ys,dtype=np.int64)
        if x.ndim!=2 or x.shape[1]!=FEATURE_DIM or len(y)!=len(x):
            raise AssertionError("FKP12_SOURCE_FEATURE_IDENTITY")
        return {"seed":seed,"policy":policy,"x":x,"y":y,
                "source_receipt_sha256":source_digest.hexdigest(),
                "actions":len(y),"positives":int(np.sum(y==2)),
                "negatives":int(np.sum(y==0)),
                "wall_seconds":time.perf_counter()-started}
    finally:env.close()


def collect(seeds:tuple[int,...],*,allow_dev:bool=False):
    if type(seeds) is not tuple or any(permitted(s,allow_dev=allow_dev) not in ("TRAIN","VALIDATE","DEV") for s in seeds):
        raise PermissionError("FKP12_DATASET_COHORT_FENCE")
    if len(set(seeds))!=len(seeds):raise ValueError("FKP12_DUPLICATE_SEED")
    if allow_dev and seeds!=DEV:raise PermissionError("FKP12_ORIGINAL_DEV_EXACT_SET_ONLY")
    if not allow_dev and seeds not in (TRAIN,VALIDATION):
        raise PermissionError("FKP12_ONLY_FROZEN_TRAIN_OR_VALIDATION")
    return [episode(seed,policy,allow_dev=allow_dev) for seed in seeds for policy in POLICIES]
