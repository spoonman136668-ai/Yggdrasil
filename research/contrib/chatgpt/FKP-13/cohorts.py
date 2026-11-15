"""FKP-13 unmodified native Mystery Path source adapter.

Observations/actions/outcomes only. This is source-owner evidence from a real
simulator, not its hidden path/position/info. No FKP12 consumed cohorts reused.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import struct
import sys
import time

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"FKP-12"
sys.path.insert(0,str(PARENT))
import source as source12

TRAIN=tuple(range(973100,973148))
VALIDATE=tuple(range(973200,973216))
DEV=tuple(range(973500,973524))
TRANSFER=tuple(range(973600,973632))
CAP=512
TASK="MysteryPath-v0"
OPTIONS={"reward_fall_off":-0.05,"max_steps":CAP}
SOURCE_SHA=source12.SOURCE_SHA
POLICIES=("uniform","macro8")


def cohort(seed,dev=False):
    if type(seed) is not int:raise ValueError("FKP13_SEED_TYPE")
    if seed in TRAIN:return "TRAIN"
    if seed in VALIDATE:return "VALIDATE"
    if dev and seed in DEV:return "DEV"
    raise PermissionError("FKP13_FIRSTUSE_OR_SOURCE_FENCE")


def policy_rng(seed,policy):
    cohort(seed,dev=True)
    if policy not in POLICIES:raise ValueError("FKP13_ACTION_POLICY")
    return random.Random(seed^(0xF11A1 if policy=="uniform" else 0xF11B2))


def public_policy(rng,policy,step,macro=None):
    if policy not in POLICIES or type(step) is not int or not 0<=step<CAP:
        raise ValueError("FKP13_POLICY_STEP")
    if policy=="uniform":return (rng.randrange(3),rng.randrange(3))
    if macro is None or step%8==0:return (rng.randrange(3),rng.randrange(3))
    return macro


def custody(upstream:Path):
    return source12.source_custody(upstream)


def new_env(seed,upstream,dev=False):
    cohort(seed,dev=dev)
    import gymnasium as gym
    import memory_gym  # noqa: F401  original public source registry
    import numpy as np
    env=gym.make(TASK,render_mode=None)
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete):
            raise ValueError("FKP13_NATIVE_ACTION_TYPE")
        if tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP13_NATIVE_ACTION_SPACE")
        obs,info=env.reset(seed=seed,options=OPTIONS)
        if not (isinstance(obs,np.ndarray) and obs.dtype==np.uint8
                and obs.ndim==3 and obs.shape[2]==3):
            raise ValueError("FKP13_PUBLIC_OBS_TYPE")
        return env,obs
    except Exception:
        env.close()
        raise


def real_step(env,a):
    import numpy as np
    if type(a) is not tuple or len(a)!=2 or any(type(v) is not int or not 0<=v<3 for v in a):
        raise ValueError("FKP13_ONLY_PUBLIC_NATIVE_ACTION")
    obs,reward,done,trunc,_unused_info=env.step(np.asarray(a,dtype=np.int64))
    if not bool(np.isfinite(reward)):raise ValueError("FKP13_BAD_PUBLIC_REWARD")
    return obs,float(reward),bool(done),bool(trunc)


def source_blind_episode(seed,policy,upstream,dev=False):
    cohort(seed,dev=dev)
    env,obs=new_env(seed,upstream,dev=dev)
    import numpy as np
    rng=policy_rng(seed,policy)
    digest=hashlib.sha256()
    source12.admit.frame(digest,obs)
    records=[]
    macro=None;prev=1
    began=time.perf_counter()
    try:
        for t in range(CAP):
            a=public_policy(rng,policy,t,macro)
            macro=a
            x=source12.input_feature(obs,a,prev)
            digest.update(bytes(a))
            obs,reward,done,trunc=real_step(env,a)
            source12.admit.frame(digest,obs)
            digest.update(struct.pack("<d??",reward,done,trunc))
            y=source12.label(reward)
            records.append((x,y))
            prev=y
            if done or trunc:break
        if not records:raise RuntimeError("FKP13_NO_SOURCE_ACTION")
        return {
            "seed":seed,"policy":policy,
            "x":np.stack([x for x,y in records]).astype(np.float32),
            "y":np.asarray([y for x,y in records],dtype=np.int64),
            "steps":len(records),
            "source_sha256":digest.hexdigest(),
            "wall_seconds":time.perf_counter()-began}
    finally:env.close()


def collect(seeds,upstream):
    if type(seeds) is not tuple or seeds not in (TRAIN,VALIDATE):
        raise PermissionError("FKP13_TRAIN_VALIDATION_ONLY")
    return [source_blind_episode(s,policy,upstream)
            for s in seeds for policy in POLICIES]


def source_blind_dev_receipt(upstream):
    # Replay consumed DEV only after the original owner's live score.
    result=[]
    for s in DEV:
        for pol in POLICIES:
            x=source_blind_episode(s,pol,upstream,dev=True)
            result.append((s,pol,x["source_sha256"],x["steps"]))
    return result
