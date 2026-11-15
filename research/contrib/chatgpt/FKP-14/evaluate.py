"""FKP-14 original public-source branching-action HEADROOM ONLY.

Every contrasted action physically executes in the unchanged original Memory Gym
environment after resetting and replaying EXACTLY the same source-public prefix.
No hidden path state, private source info, debug rendering, model fitting,
scientific first use, or native Yggdrasil weight changes.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
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
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-10"))
import admit

SOURCE_SEEDS=tuple(range(974000,974032))
ANCHORS=(0,16,32,64)
HORIZONS=(8,16)
ACTIONS=tuple((x,y) for x in range(3) for y in range(3))
MAX_FUTURE=16
REWARD_OPTIONS={"reward_fall_off":-0.05,"max_steps":512}
TASK="MysteryPath-v0"


@lru_cache(maxsize=32)
def public_prefix(seed:int)->tuple[tuple[int,int],...]:
    if seed not in SOURCE_SEEDS:
        raise ValueError("FKP14_UNREGISTERED_WORLD")
    rng=random.Random(seed^0xF14A0)
    out=[]
    for _ in range(max(ANCHORS)//8):
        action=(rng.randrange(3),rng.randrange(3))
        out.extend([action]*8)
    assert len(out)==max(ANCHORS)
    return tuple(out)


def fixed_random_control(seed:int,anchor:int)->int:
    if seed not in SOURCE_SEEDS or anchor not in ANCHORS:
        raise ValueError("FKP14_UNKNOWN_SOURCE_OR_ANCHOR")
    return random.Random(seed^(anchor<<12)^0xF14B4).randrange(len(ACTIONS))


def digest_public(obs,hasher):
    import numpy as np
    arr=np.asarray(obs)
    if arr.dtype!=np.uint8 or arr.ndim!=3 or arr.shape[-1]!=3 or arr.size==0:
        raise ValueError("FKP14_INVALID_REAL_PUBLIC_RGB")
    hasher.update(struct.pack("<III",*arr.shape))
    hasher.update(arr.tobytes(order="C"))
    return arr.shape


def episode(seed:int,anchor:int,action:tuple[int,int]|None,horizon:int)->dict:
    if seed not in SOURCE_SEEDS or anchor not in ANCHORS or horizon not in (0,*HORIZONS):
        raise ValueError("FKP14_SOURCE_SCOPE")
    if (horizon==0)!=(action is None) or (action is not None and action not in ACTIONS):
        raise ValueError("FKP14_MACRO_SCOPE")
    import gymnasium as gym
    import memory_gym  # register real original upstream package
    import numpy as np

    env=gym.make(TASK,render_mode=None)
    prefix_hasher=hashlib.sha256()
    branch_hasher=hashlib.sha256()
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP14_ORIGINAL_ACTION_SPACE_DRIFT")
        observation,_info=env.reset(seed=seed,options=dict(REWARD_OPTIONS))
        original_shape=digest_public(observation,prefix_hasher)
        prefix_steps=0
        for a,b in public_prefix(seed)[:anchor]:
            public_action=np.asarray((a,b),dtype=np.int64)
            if not env.action_space.contains(public_action):
                raise ValueError("FKP14_ILLEGAL_PREFIX_ACTION")
            prefix_hasher.update(bytes((a,b)))
            observation,reward,terminated,truncated,_info=env.step(public_action)
            digest_public(observation,prefix_hasher)
            prefix_hasher.update(struct.pack("<d??",float(reward),bool(terminated),bool(truncated)))
            prefix_steps+=1
            if terminated or truncated:
                return {"seed":seed,"anchor":anchor,"valid":False,"prefix_steps":prefix_steps,
                        "prefix_sha256":prefix_hasher.hexdigest(),"terminal_prefix":True}
        if prefix_steps!=anchor:
            raise AssertionError("FKP14_PREFIX_STEPS_DRIFT")
        common={"seed":seed,"anchor":anchor,"prefix_steps":prefix_steps,
                "prefix_sha256":prefix_hasher.hexdigest(),"terminal_prefix":False,
                "original_public_shape":list(original_shape),"valid":True}
        if horizon==0:
            return common
        rewards=[]
        positives=0
        negatives=0
        goals=0
        terminated=False
        for _ in range(horizon):
            a,b=action
            public_action=np.asarray((a,b),dtype=np.int64)
            branch_hasher.update(bytes((a,b)))
            observation,reward,done,truncated,_info=env.step(public_action)
            digest_public(observation,branch_hasher)
            branch_hasher.update(struct.pack("<d??",float(reward),bool(done),bool(truncated)))
            reward=float(reward)
            if not math.isfinite(reward):
                raise ValueError("FKP14_NONFINITE_ORIGINAL_REWARD")
            rewards.append(reward)
            positives+=int(reward>0)
            negatives+=int(reward<0)
            goals+=int(reward>=1.0 and done)
            if done or truncated:
                terminated=True
                break
        return {**common,"macro":list(action),"horizon":horizon,
                "future_source_actions":len(rewards),
                "future_actual_return":round(sum(rewards),8),
                "positive_events":positives,"negative_events":negatives,
                "terminal_goal_events":goals,"ended_early":terminated,
                "branch_sha256":branch_hasher.hexdigest()}
    finally:
        env.close()


def summarize_anchor(seed,anchor,reference,horizon,rows):
    if len(rows)!=len(ACTIONS) or any(not x["valid"] for x in rows):
        raise ValueError("FKP14_MISSING_REAL_BRANCH")
    if any(x["prefix_sha256"]!=reference["prefix_sha256"] for x in rows):
        raise AssertionError("FKP14_DIFFERENT_PRE_ACTION_HISTORY")
    scores=[x["future_actual_return"] for x in rows]
    best=max(scores)
    worst=min(scores)
    random_idx=fixed_random_control(seed,anchor)
    best_pos=any(x["positive_events"]>0 for x in rows)
    return {
      "seed":seed,"anchor":anchor,"horizon":horizon,
      "source_replay_same_prefix":True,"distinct_branches":len(rows),
      "return_spread":round(best-worst,8),
      "return_contrast_ge_005":best-worst>=0.05-1e-9,
      "best_future_return":best,"worst_future_return":worst,
      "random_control_index":random_idx,
      "random_control_return":scores[random_idx],
      "oracle_minus_random_return":round(best-scores[random_idx],8),
      "any_positive_event":best_pos,
      "any_positive_return":any(x["future_actual_return"]>0 for x in rows),
      "any_terminal_goal":any(x["terminal_goal_events"]>0 for x in rows),
      "source_branch_action_counts":[x["future_source_actions"] for x in rows],
      "branch_receipts":[x["branch_sha256"] for x in rows]
    }


def run(upstream:Path)->dict:
    start=time.perf_counter()
    cpu=time.process_time()
    source=admit.source_custody(upstream)
    sys.path.insert(0,str(upstream))
    references={}
    anchor_results=[]
    skipped=[]
    charged=0
    reset_count=0
    for seed in SOURCE_SEEDS:
        for anchor in ANCHORS:
            ref=episode(seed,anchor,None,0)
            charged+=ref["prefix_steps"]
            reset_count+=1
            references[(seed,anchor)]=ref
            if not ref["valid"]:
                skipped.append({"seed":seed,"anchor":anchor,"reason":"PREFIX_TERMINAL"})
                continue
            for horizon in HORIZONS:
                branches=[]
                for action in ACTIONS:
                    row=episode(seed,anchor,action,horizon)
                    reset_count+=1
                    charged+=row["prefix_steps"]+row.get("future_source_actions",0)
                    if not row["valid"]:
                        raise AssertionError("FKP14_SOURCE_PREFIX_INTERMITTENT_TERMINAL")
                    branches.append(row)
                anchor_results.append(summarize_anchor(seed,anchor,ref,horizon,branches))
    valid={h:[r for r in anchor_results if r["horizon"]==h] for h in HORIZONS}
    n16=len(valid[16])
    fraction_16=(sum(r["return_contrast_ge_005"] for r in valid[16])/n16 if n16 else 0)
    positive_fraction=(sum(r["any_positive_return"] for r in valid[16])/n16 if n16 else 0)
    mean_oracle_adv=(sum(r["oracle_minus_random_return"] for r in valid[16])/n16 if n16 else 0)
    cross_os_receipt=hashlib.sha256(json.dumps(
        {"source_sha":source["source_sha"],"skipped":skipped,"rows":anchor_results},
        separators=(",",":"),sort_keys=True).encode("utf-8")).hexdigest()
    requirements={
       "source_public_replay_exact_all":True,
       "valid_at_least_96_of_128":n16>=96,
       "horizon16_true_return_contrasts_ge20percent":fraction_16>=.20,
       "horizon16_positive_return_ge10percent":positive_fraction>=.10,
       "privileged_oracle_vs_frozen_random_macro_ge_010":mean_oracle_adv>=.10-1e-12
    }
    # One OS can establish LOCAL source headroom; cross-platform independent
    # certificate must compare the same SHA256 and require full CI PASS.
    local_pass=all(requirements.values())
    result={
       "schema":"yggdrasil.fkp14.actual-intervention-identifiability.v1",
       "status":"SOURCE_ACTION_LOCAL_HEADROOM_PASS" if local_pass else "SOURCE_ACTION_HEADROOM_NO_GO",
       "scientific_pass":False,"native_model_modified":False,
       "new_public_dev_cohort_consumed":True,"protected_firstuse":False,
       "model_trained":False,
       "upstream":source,"registered_worlds":len(SOURCE_SEEDS),
       "reference_anchors":len(SOURCE_SEEDS)*len(ANCHORS),
       "valid_anchors":n16,"skipped_anchors":skipped,
       "actual_env_step_actions":charged,
       "physical_env_resets":reset_count,
       "macro_horizons":list(HORIZONS),"macro_choices_per_anchor":len(ACTIONS),
       "horizon8_contrast_fraction":(sum(r["return_contrast_ge_005"] for r in valid[8])/len(valid[8]) if valid[8] else 0),
       "horizon16_contrast_fraction":fraction_16,
       "horizon16_positive_return_fraction":positive_fraction,
       "horizon16_oracle_minus_random_mean":mean_oracle_adv,
       "horizon16_any_terminal_goal_anchors":sum(r["any_terminal_goal"] for r in valid[16]),
       "prespecified_requirements":requirements,
       "source_receipt_sha256":cross_os_receipt,
       "whole_process_wall_seconds":round(time.perf_counter()-start,6),
       "whole_process_cpu_seconds":round(time.process_time()-cpu,6),
       "per_anchor":anchor_results
    }
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-dev",action="store_true")
    ap.add_argument("--protected",action="store_true")
    ap.add_argument("--upstream-root",type=Path)
    a=ap.parse_args()
    if not a.public_dev or a.protected or not a.upstream_root:
        ap.error("FKP14 ONLY FROZEN NEW PUBLIC DEV SOURCE; SCIENTIFIC FIRST_USE DISARMED")
    print(json.dumps(run(a.upstream_root.resolve()),sort_keys=True))
