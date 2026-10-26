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


def public_key_ball_cells(observation):
    """List all visible Key/Ball cells in a 7x7 public observation.

    The output is a candidate inventory only. It does not assign semantic roles
    such as "start cue" or "upper branch"; those roles must be preregistered and
    validated using public event geometry. Occluded cells are not inferred.
    """
    if type(observation) is not dict or type(observation.get("image")) not in (list, tuple):
        raise ValueError("PUBLIC_IMAGE_REQUIRED")
    image = observation["image"]
    if len(image) != 7:
        raise ValueError("PUBLIC_IMAGE_SHAPE_INVALID")
    found = []
    for x, column in enumerate(image):
        if type(column) not in (list, tuple) or len(column) != 7:
            raise ValueError("PUBLIC_IMAGE_SHAPE_INVALID")
        for y, cell in enumerate(column):
            if type(cell) not in (list, tuple) or len(cell) != 3:
                raise ValueError("PUBLIC_CELL_ENCODING_INVALID")
            object_index = cell[0]
            if type(object_index) is int and object_index in (5, 6):
                found.append({
                    "coordinate": [x, y],
                    "object": "key" if object_index == 5 else "ball",
                })
    return found


def rotate_left_cell_coordinate(x, y, *, width=7, height=7):
    """Map a cell through the pinned Grid.rotate_left coordinate transform.

    Source rule: destination (x', y') = (y, height - 1 - x).
    This is pure arithmetic; it does not import or execute MiniGrid.
    """
    if type(x) is not int or type(y) is not int:
        raise ValueError("GRID_COORDINATE_INVALID")
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise ValueError("GRID_DIMENSION_INVALID")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError("GRID_COORDINATE_INVALID")
    return (y, height - 1 - x)


def east_facing_public_view_coordinate(global_x, global_y, agent_x, agent_y, *, view_size=7):
    """Map a global cell into the public 7x7 view for an east-facing agent.

    The pinned MiniGrid pipeline slices from (agent_x, agent_y-view_size//2),
    then rotates the slice left once for direction 0. This source-derived,
    pure coordinate calculation does not instantiate or query the environment.
    """
    values = (global_x, global_y, agent_x, agent_y, view_size)
    if any(type(value) is not int for value in values):
        raise ValueError("GLOBAL_VIEW_COORDINATE_INVALID")
    if view_size != 7 or view_size <= 0:
        raise ValueError("WITNESS_VIEW_SIZE_MISMATCH")
    local_x = global_x - agent_x
    local_y = global_y - (agent_y - view_size // 2)
    if not (0 <= local_x < view_size and 0 <= local_y < view_size):
        raise ValueError("GLOBAL_CELL_OUTSIDE_PUBLIC_VIEW")
    return rotate_left_cell_coordinate(local_x, local_y, width=view_size, height=view_size)
