"""Run an actually selected C32 policy in one independently reset source world.

All source actions are executed; other policies' later states are NOT paired.
"""
from __future__ import annotations
import hashlib
import math
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c31.action_bridge import (
    source_public_navigator, source_sensor_update, decision,
)

def run_episode(family, seed, arm, model, motors, cap, cold):
    from research.mass_r7c20 import run as c20
    from research.mass_r7c22 import run as c22
    env = c20.env_make(family)
    try:
        obs, _ = env.reset(seed=seed)
        goal = c20.goal_from(obs)
        navigator = source_public_navigator(motors, family)
        rows = []
        checkpoint = None
        selected_changes = 0
        for step in range(cap):
            before = c22.public_dynamic(obs, goal)
            source_sensor_update(navigator, before)
            if arm == "r3_original":
                baseline = navigator.choose(before)
                chosen = baseline
            else:
                baseline, chosen, _ = decision(navigator, before, model)
            if baseline not in (0,1,2) or chosen not in (0,1,2):
                raise ValueError("C32_NON_SOURCE_LEGAL_SELECTED_ACTION")
            if chosen != baseline:
                if baseline not in (0,1) or chosen not in (0,1):
                    raise ValueError("C32_UNCHANGED_FORWARD_ACTION_VIOLATED")
                selected_changes += 1
            obs_next, reward, terminated, truncated, _ = env.step(chosen)
            after = c22.public_dynamic(obs_next, goal)
            if not math.isfinite(float(reward)):
                raise ValueError("C32_NONFINITE_SOURCE_REWARD")
            navigator.observe(before, chosen, after, float(reward),
                              bool(terminated), False)
            rows.append({
                "t": step, "before": before.__dict__,
                "original_r3_proposed": baseline, "executed": chosen,
                "after": after.__dict__, "reward": float(reward),
                "terminated": bool(terminated), "truncated": bool(truncated),
            })
            obs = obs_next
            if step == 2 and not (terminated or truncated):
                checkpoint = cold(navigator, model, arm, after)
            if terminated or truncated:
                break
        if not rows:
            raise ValueError("C32_EMPTY_SOURCE_EPISODE")
        if checkpoint is None:
            final_public = c22.public_dynamic(obs, goal)
            checkpoint = cold(navigator, model, arm, final_public)
        last = rows[-1]
        snapshot = navigator.snapshot()
        return {
            "family":family, "seed":seed, "arm":arm,
            "steps":len(rows), "native_real_turn_changes":selected_changes,
            "source_goal":bool(last["terminated"] and last["reward"]>0),
            "source_collision":bool(last["terminated"] and last["reward"]<0),
            "source_horizon":bool(last["truncated"]),
            "reward_sum":sum(row["reward"] for row in rows),
            "source_actual_actions":rows,
            "source_trace_sha256":hashlib.sha256(canonical(rows)).hexdigest(),
            "final_original_R3_sha256":hashlib.sha256(snapshot).hexdigest(),
            "final_original_R3_bytes":len(snapshot),
            "cold_step_three":checkpoint,
        }
    finally:
        env.close()
