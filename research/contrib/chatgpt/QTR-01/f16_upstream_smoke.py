#!/usr/bin/env python3
"""QTR F16: PUBLIC DEVELOPMENT smoke of exact pinned causal-worlds control adapter.

This is evaluator-side runtime/transport qualification, NOT a learner sandbox,
unseen-world experiment, recipient weight edit, scientific first-use, or transplant.
Only published built-in development worlds are used.
"""
import argparse
import json
import subprocess
from pathlib import Path

from f14_boundary import reset_frame, step_frame

UPSTREAM_SHA = "51f1431515e310dec72e3f4b6db378df46f832ea"
UPSTREAM_TREE = "c1bf53ecf03ae326b69c0321f4412d81f3122894"


def _identity(upstream):
    commit = subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True
    ).strip()
    tree = subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD^{tree}"], text=True
    ).strip()
    if (commit, tree) != (UPSTREAM_SHA, UPSTREAM_TREE):
        raise ValueError("F16_UPSTREAM_IDENTITY_MISMATCH")
    return commit, tree


def _step(world, seed, level):
    import numpy as np
    from causal_worlds.gym import ControlEnv
    from causal_worlds import worlds

    env = ControlEnv(worlds.get(world), horizon=2)
    try:
        first = env.reset(seed=seed)
        assert isinstance(first[1], dict) and "regime" in first[1]
        reset_wire = reset_frame(first)
        reset_public = json.loads(reset_wire)
        assert set(reset_public) == {"observation", "done"}
        assert reset_public["done"] is False
        assert len(reset_public["observation"]) == env.observation_space.shape[0]
        assert "regime" not in reset_wire

        action = np.full(env.action_space.shape, level, dtype=np.float64)
        raw = env.step(action)
        assert isinstance(raw[4], dict)
        assert {"regime", "optimal_reward", "regret"}.issubset(raw[4])
        step_wire = step_frame(raw)
        published = json.loads(step_wire)
        assert set(published) == {"observation", "reward", "done"}
        assert published["done"] is False
        assert len(published["observation"]) == env.observation_space.shape[0]
        for private in ("regime", "optimal_reward", "regret", "answer_key",
                        "_spec", "graph", "optimal_policy"):
            assert private not in step_wire
        return reset_wire, step_wire, published["reward"]
    finally:
        env.close()


def run(upstream):
    _identity(Path(upstream).resolve())

    import causal_worlds
    from causal_worlds import worlds
    from causal_worlds.control import NonlinearControlError
    from causal_worlds.gym import ControlEnv

    result = {}
    for name in ("coffee", "ecommerce"):
        results = [_step(name, 1701, value) for value in (0.0, 1.25, -1.25)]
        assert len({r[0] for r in results}) == 1, "F16_NONDETERMINISTIC_RESET"
        assert len({r[2] for r in results}) >= 2, "F16_NO_ACTION_CONSEQUENCE"
        assert _step(name, 1701, 0.0) == results[0], "F16_NONDETERMINISTIC_REPLAY"
        result[name] = {
            "action_levels": [0.0, 1.25, -1.25],
            "reward_by_action": [r[2] for r in results],
            "replay_deterministic": True,
            "private_info_redacted": True,
        }

    try:
        ControlEnv(worlds.get("braking"))
    except NonlinearControlError:
        nonlinear_rejected = True
    else:
        raise AssertionError("F16_NONLINEAR_WORLD_IMPROPERLY_ADMITTED")

    return {
        "schema": "yggdrasil.qtr.f16.pinned-public-dev-smoke.v1",
        "source_commit": UPSTREAM_SHA,
        "source_tree": UPSTREAM_TREE,
        "published_development_worlds_only": True,
        "native_model_or_train_run": False,
        "protected_science_consumed": False,
        "learner_process_isolation_qualified": False,
        "nonlinear_control_rejected": nonlinear_rejected,
        "worlds": result,
        "classification": "ENGINEERING_UPSTREAM_RUNTIME_DEV_ONLY",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    options = parser.parse_args()
    print(json.dumps(run(options.upstream_root), sort_keys=True, indent=2))
