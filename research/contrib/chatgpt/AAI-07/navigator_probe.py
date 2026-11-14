"""AAI-07 observation-only navigation control, reserved mechanical seeds.
This is a hand-built benchmark probe, NOT an associative learner or primary science.
"""
from __future__ import annotations
import hashlib
import json

import gymnasium as gym
import numpy as np

from minigrid.core.constants import OBJECT_TO_IDX

WALL = OBJECT_TO_IDX["wall"]
CUES = {OBJECT_TO_IDX["key"], OBJECT_TO_IDX["ball"]}
EXTERNAL_TASKS = ("MiniGrid-MemoryS11-v0", "MiniGrid-MemoryS13Random-v0")
MECHANICAL_SEEDS = tuple(range(970000, 970008))
MAX_TOTAL_STEPS = 120


def in_front(obs, distance=1):
    """Use only the published 7x7 agent-centric integer observation."""
    image = np.asarray(obs["image"])
    assert image.shape == (7, 7, 3)
    assert distance in (1, 2)
    return int(image[3, 6-distance, 0])


def reset_step(env, obs, action, trace):
    obs, reward, terminated, truncated, info = env.step(action)
    trace.append(int(action))
    if len(trace) > MAX_TOTAL_STEPS:
        raise RuntimeError("Navigation exceeded public action budget")
    return obs, float(reward), bool(terminated or truncated)


def run(env_name, seed, remember=True):
    env = gym.make(env_name, render_mode=None)
    actions = []
    try:
        obs, _ = env.reset(seed=seed)
        # Start heading east per public MemoryEnv. Face west and return
        # to the entrance; detect walls solely through public image.
        for action in (1,1):
            obs,_,done = reset_step(env,obs,action,actions)
            assert not done
        for _ in range(24):
            if in_front(obs)==WALL:
                break
            obs,_,done = reset_step(env,obs,2,actions)
            assert not done
        else:
            raise AssertionError("No visible entrance boundary")
        # West -> north, inspect initial cue directly ahead.
        obs,_,done = reset_step(env,obs,1,actions)
        assert not done
        cue=in_front(obs)
        assert cue in CUES, ("missing entrance cue",cue)
        if not remember:
            cue = None
        # North -> east, traverse hallway until front wall at decision junction.
        obs,_,done = reset_step(env,obs,1,actions)
        assert not done
        for _ in range(24):
            if in_front(obs)==WALL:
                break
            obs,_,done = reset_step(env,obs,2,actions)
            assert not done
        else:
            raise AssertionError("No visible junction boundary")
        # East -> north; inspect top branch object two cells ahead.
        obs,_,done = reset_step(env,obs,0,actions)
        assert not done
        upper=in_front(obs,distance=2)
        assert upper in CUES, ("missing upper target",upper)
        choose_top=(cue is not None and cue==upper) if remember else True
        if not choose_top:
            for action in (1,1):
                obs,_,done=reset_step(env,obs,action,actions)
                assert not done
        obs,reward,done=reset_step(env,obs,2,actions)
        assert done, "Decision action must terminate this canonical memory task"
        return {"seed":seed,"remember":bool(remember),
                "success":reward>0,"reward":round(reward,8),
                "step_count":len(actions),"terminal":done,
                "action_trace":actions}
    finally:
        env.close()


def mechanical():
    result={}
    for env in EXTERNAL_TASKS:
        records=[]
        for seed in MECHANICAL_SEEDS:
            first=run(env,seed,True)
            second=run(env,seed,True)
            assert first==second, (env,seed)
            baseline=run(env,seed,False)
            records.append({"seed":seed,"memory_success":first["success"],
                            "reactive_success":baseline["success"],
                            "memory_steps":first["step_count"],
                            "reactive_steps":baseline["step_count"]})
        result[env]={"n":len(records),
                     "memory_success":sum(r["memory_success"] for r in records),
                     "reactive_success":sum(r["reactive_success"] for r in records),
                     "records":records}
    return {"schema":"aai07.observation_only_navigator_mechanical.v1",
            "first_use":False,"privileged_grid_access":False,
            "preprogrammed_matching_rule":True,
            "result":result,
            "receipt_sha256":hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()}


if __name__=="__main__":
    print(json.dumps(mechanical(),sort_keys=True,indent=2))
