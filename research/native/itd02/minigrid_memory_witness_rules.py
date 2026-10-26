"""Frozen source-derived rule for the pinned MiniGrid MemoryS7 witness.

Inputs must be classifications extracted from public observation images by the
independent public-only evaluator. This module never imports or queries MiniGrid.
The returned action is a predicted branch-entry action under the pinned source
rule; it is not an execution receipt or proof the classifications are correct.
"""
SCHEMA = "ygg.itd02.minigrid_memory.public_cue_rule.v1"
LEFT = 0
RIGHT = 1
FORWARD = 2
OBJECTS = frozenset({"key", "ball"})


def expected_branch_action(public_start_cue, public_upper_end_object, *, agent_direction):
    """Return the source-law branch turn from public cue/order classifications.

    For the pinned source: success is at the branch containing the same object
    class as the start cue. When the agent faces east at the junction, LEFT
    enters the upper/north branch and RIGHT enters the lower/south branch.
    """
    if public_start_cue not in OBJECTS or public_upper_end_object not in OBJECTS:
        raise ValueError("PUBLIC_OBJECT_CLASS_INVALID")
    if type(agent_direction) is not int or agent_direction != 0:
        raise ValueError("WITNESS_POSE_NOT_EAST_FACING")
    return LEFT if public_start_cue == public_upper_end_object else RIGHT
