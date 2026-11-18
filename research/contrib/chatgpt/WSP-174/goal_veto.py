"""WSP-176: unbeatable fifth-step goal-reward no-learning control for source's public goal.

No environment calls, hidden DAG, MLP, reward oracle or candidate model.
This is a deterministic conventional baseline and a source-law veto, not
native causal learning. The goal is explicitly public in original reset().
"""
from __future__ import annotations

from public_boundary import N_OBJECTS, N_COLORS, _scene


def goal_action(public_goal: object, step_index: int) -> int:
    """Set object step_index to its public goal color, in increasing index order."""
    if type(step_index) is not int or not 0 <= step_index < N_OBJECTS:
        raise ValueError("WSP176_STEP_RANGE")
    goal = _scene(public_goal)
    return step_index * N_COLORS + goal[step_index][2]


def plan(public_goal: object) -> tuple[int, ...]:
    """Five public actions; no access to source structure or consequences."""
    goal = _scene(public_goal)
    return tuple(i * N_COLORS + goal[i][2] for i in range(N_OBJECTS))
