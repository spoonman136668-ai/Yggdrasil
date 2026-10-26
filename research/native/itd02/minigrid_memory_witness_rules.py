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


def public_object_at(observation, coordinate):
    """Classify one object from a recorded public image cell [x, y, channel].

    MiniGrid encodes object identity in channel 0: key=5, ball=6. Coordinates
    must be frozen in advance and supplied by a public-only evaluator. This
    function does not attest that the chosen cell semantically is the cue or
    upper branch; it only decodes the recorded public bytes.
    """
    if type(observation) is not dict or type(observation.get("image")) not in (list, tuple):
        raise ValueError("PUBLIC_IMAGE_REQUIRED")
    if type(coordinate) not in (list, tuple) or len(coordinate) != 2:
        raise ValueError("PUBLIC_CELL_COORDINATE_INVALID")
    x, y = coordinate
    if type(x) is not int or type(y) is not int or not (0 <= x < 7 and 0 <= y < 7):
        raise ValueError("PUBLIC_CELL_COORDINATE_INVALID")
    image = observation["image"]
    try:
        cell = image[x][y]
        object_index = cell[0]
    except (IndexError, TypeError) as exc:
        raise ValueError("PUBLIC_CELL_ENCODING_INVALID") from exc
    if type(object_index) is not int or object_index not in (5, 6):
        raise ValueError("PUBLIC_CELL_NOT_KEY_OR_BALL")
    return "key" if object_index == 5 else "ball"
