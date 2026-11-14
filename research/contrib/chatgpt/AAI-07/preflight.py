"""AAI-07 external MiniGrid memory environment mechanical preflight.

Reserved seeds only; no learner fit, scientific scoring, or hidden-state inspection.
External benchmark source MUST be git checked out at the exact commit.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import gymnasium as gym
import minigrid
import numpy as np

EXTERNAL_SHA = "64e1eaec904bc35e7de041167274e2c0dfe541d2"
SOURCE_BLOB = "660b0a1b769948034c87bb421759c2b9a4f24548"
PRECHECK_SEEDS = tuple(range(970000, 970008))
ENVIRONMENTS = ("MiniGrid-MemoryS11-v0", "MiniGrid-MemoryS13Random-v0")
TEST_ACTIONS = (2, 0, 2, 1, 2, 2, 0, 2)


def inspect_observation(obs):
    # Explicitly exclude language/mission and all privileged simulator internals.
    assert isinstance(obs, dict)
    assert {"image", "direction", "mission"}.issubset(obs)
    pixels = np.asarray(obs["image"])
    assert pixels.shape == (7, 7, 3), pixels.shape
    assert np.issubdtype(pixels.dtype, np.integer)
    direction = int(obs["direction"])
    assert 0 <= direction < 4
    assert np.min(pixels) >= 0
    return direction, pixels.astype(np.uint8).tobytes()


def rollout(env_name, seed):
    digest = hashlib.sha256()
    env = gym.make(env_name, render_mode=None)
    try:
        assert env.action_space.n == 7, env.action_space
        obs, info = env.reset(seed=seed)
        assert isinstance(info, dict)
        direction, image = inspect_observation(obs)
        digest.update(image)
        digest.update(bytes((direction,)))
        steps, total_reward = 0, 0.0
        for action in TEST_ACTIONS:
            assert env.action_space.contains(action)
            obs, reward, terminated, truncated, info = env.step(action)
            assert isinstance(info, dict)
            assert isinstance(terminated, (bool, np.bool_))
            assert isinstance(truncated, (bool, np.bool_))
            assert -1.0 <= float(reward) <= 1.0
            total_reward += float(reward)
            steps += 1
            direction, image = inspect_observation(obs)
            digest.update(image)
            digest.update(bytes((direction, action, int(terminated), int(truncated))))
            if terminated or truncated:
                break
        return {
            "seed": seed, "steps": steps,
            "total_reward": round(total_reward, 9),
            "obs_trace_sha256": digest.hexdigest(),
        }
    finally:
        env.close()


def run():
    root_string = os.environ.get("AAI07_EXTERNAL_ROOT")
    assert root_string, "AAI07_EXTERNAL_ROOT must identify pinned external source"
    root = Path(root_string).resolve(strict=True)
    source_file = (root / "minigrid" / "envs" / "memory.py").resolve(strict=True)
    assert source_file.is_relative_to(root)
    assert minigrid.__version__ == "3.2.0", minigrid.__version__
    imported = Path(minigrid.__file__).resolve(strict=True)
    assert imported.is_relative_to(root), (imported, root)
    # Code blob identity is separately validated by git rev-parse in workflow.
    source_digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
    results = {}
    for name in ENVIRONMENTS:
        records = []
        for seed in PRECHECK_SEEDS:
            first = rollout(name, seed)
            second = rollout(name, seed)
            assert first == second, (name, seed, first, second)
            records.append(first)
        results[name] = records
    return {
        "schema": "yggdrasil.contrib.aai07.external-preflight.v1",
        "scope": "mechanical-only; 16 reserved seed/environment cases",
        "benchmark": "Farama-Foundation/Minigrid",
        "external_commit": EXTERNAL_SHA,
        "external_memory_source_git_blob": SOURCE_BLOB,
        "external_memory_source_sha256": source_digest,
        "package_version": minigrid.__version__,
        "environments": list(ENVIRONMENTS),
        "reserved_seed_count": len(PRECHECK_SEEDS),
        "reproducible_same_seed": True,
        "no_mission_text_consumed": True,
        "no_hidden_simulator_state_consumed": True,
        "scientific_first_use": False,
        "native_model_integration": "NONE",
        "trace_receipt_sha256": hashlib.sha256(json.dumps(
            results, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
