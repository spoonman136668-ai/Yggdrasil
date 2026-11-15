"""FKP-10 original-source Memory Gym mechanical admission, NOT learned science.

Reads only public reset/step observation, reward, termination, and selected actions.
Never invokes protected/DEV/TRANSFER cohorts or evaluates native Yggdrasil models.
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
import subprocess

# Mandatory before importing Pygame / memory_gym; no interactive display or audio.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

SOURCE_SHA = "a94f2b60d1769ea44df3226561488768e1dff9f4"
SOURCE_BLOBS = {
    "LICENSE": "71f0e4887c38776d7ed25bdbbd1c9f5a9156d9c5",
    "setup.py": "fca17dd1d52d5c14839e20568a6d850bfeb30044",
    "memory_gym/__init__.py": "1e0da856e084fd4a6c8a409c41182d10be7d5c13",
    "memory_gym/mortar_mayhem.py": "5217196b9b4f1dfa9e67675c0ac1dbffe4b9d9a9",
    "memory_gym/mystery_path.py": "2f80721f8dd33f4f438e07c42fa65b920fd301ed",
}
TASKS = ("MortarMayhem-v0", "MysteryPath-v0")
SEEDS = (970100, 970101, 970102, 970103)
MAX_STEPS = 32
MIN_STEPS = 8


def git_text(root: Path, *args: str) -> str:
    run = subprocess.run(["git", "-C", str(root), *args], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    return run.stdout.strip()


def source_custody(root: Path) -> dict:
    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError("FKP10_UPSTREAM_GIT_CHECKOUT_REQUIRED")
    head = git_text(root, "rev-parse", "HEAD")
    if head != SOURCE_SHA:
        raise ValueError("FKP10_UPSTREAM_SHA_MISMATCH")
    for path, blob in SOURCE_BLOBS.items():
        if git_text(root, "rev-parse", f"HEAD:{path}") != blob:
            raise ValueError(f"FKP10_UPSTREAM_BLOB_MISMATCH:{path}")
    if git_text(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("FKP10_UPSTREAM_WORKTREE_DIRTY")
    return {"source_sha":head, "pinned_blobs":len(SOURCE_BLOBS), "upstream_clean":True}


def frame(hasher, observation) -> tuple[str, tuple[int, ...]]:
    import numpy as np
    arr = np.asarray(observation)
    if arr.size == 0 or not arr.flags.c_contiguous:
        arr = np.ascontiguousarray(arr)
    if arr.size == 0 or arr.dtype.hasobject or arr.ndim < 1:
        raise ValueError("FKP10_PUBLIC_OBSERVATION_INVALID")
    raw = arr.tobytes(order="C")
    # Collision-safe framed serialization (field lengths, shape, dtype).
    dtype = arr.dtype.str.encode("ascii")
    shape = tuple(int(x) for x in arr.shape)
    hasher.update(struct.pack("<I", len(dtype)) + dtype)
    hasher.update(struct.pack("<I", len(shape)))
    for dim in shape:
        hasher.update(struct.pack("<Q", dim))
    hasher.update(struct.pack("<Q", len(raw)))
    hasher.update(raw)
    return arr.dtype.name, shape


def episode(task: str, seed: int) -> dict:
    if task not in TASKS or seed not in SEEDS:
        raise ValueError("FKP10_NO_UNREGISTERED_WORLD")
    import gymnasium as gym
    import memory_gym   # noqa: F401 - register original external environments
    import numpy as np

    env = gym.make(task, render_mode=None)
    digest = hashlib.sha256()
    try:
        space = env.action_space
        if not isinstance(space, gym.spaces.MultiDiscrete) or tuple(int(x) for x in space.nvec) != (3,3):
            raise ValueError("FKP10_ORIGINAL_ACTION_SPACE_DRIFT")
        obs, _info = env.reset(seed=seed)
        dtype,shape = frame(digest,obs)
        if not shape or any(x <= 0 for x in shape):
            raise ValueError("FKP10_PUBLIC_RESET_SHAPE_INVALID")
        rng = random.Random(seed ^ 91009)
        rewards = []
        steps = 0
        terminal = False
        for i in range(MAX_STEPS):
            action = np.asarray([rng.randrange(3),rng.randrange(3)],dtype=np.int64)
            assert env.action_space.contains(action)
            digest.update(bytes((int(action[0]),int(action[1]))))
            obs, reward, terminated, truncated, _info = env.step(action)
            if not math.isfinite(float(reward)):
                raise ValueError("FKP10_PUBLIC_REWARD_NONFINITE")
            observed_dtype, observed_shape = frame(digest,obs)
            if (observed_dtype,observed_shape)!=(dtype,shape):
                raise ValueError("FKP10_SOURCE_OBSERVATION_SHAPE_DRIFT")
            digest.update(struct.pack("<d??",float(reward),bool(terminated),bool(truncated)))
            rewards.append(float(reward))
            steps = i+1
            if terminated or truncated:
                terminal=True
                break
        return {"task":task,"seed":seed,"actual_source_steps":steps,
                "terminated":terminal,"public_observation_shape":list(shape),
                "public_observation_dtype":dtype,"reward_sum":sum(rewards),
                "nonzero_reward_count":sum(r!=0 for r in rewards),
                "trace_sha256":digest.hexdigest()}
    finally:
        env.close()


def admission(root: Path) -> dict:
    custody = source_custody(root)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    rows = [episode(task,seed) for task in TASKS for seed in SEEDS]
    if len(rows)!=8 or any(not MIN_STEPS <= r["actual_source_steps"]<=MAX_STEPS for r in rows):
        classification="SOURCE_NO_GO_EPISODE_TOO_SHORT"
    else:
        classification="SOURCE_MECHANICAL_LOCAL_PASS"
    # Output contains NO raw source visuals, private ground truth, or hidden labels.
    packed=json.dumps([{k:r[k] for k in sorted(r)} for r in rows],sort_keys=True,separators=(",",":"))
    return {"schema":"yggdrasil.fkp10.memorygym-source-admission.v1",
            "classification":classification, "independent_scientific_pass":False,
            "native_model_changed":False,"science_first_use":False,
            "source":custody,"tasks":list(TASKS),"episodes":len(rows),
            "actual_native_source_steps":sum(r["actual_source_steps"] for r in rows),
            "public_reward_events":sum(r["nonzero_reward_count"] for r in rows),
            "all_rows_sha256":hashlib.sha256(packed.encode("utf-8")).hexdigest(),"rows":rows}


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mechanical",action="store_true")
    ap.add_argument("--upstream-root",type=Path)
    ap.add_argument("--primary",action="store_true")
    args=ap.parse_args()
    if args.primary or not args.mechanical or args.upstream_root is None:
        ap.error("FKP10 SCIENTIFIC FIRST_USE DISARMED; pinned mechanical upstream required")
    print(json.dumps(admission(args.upstream_root.resolve()),sort_keys=True))
