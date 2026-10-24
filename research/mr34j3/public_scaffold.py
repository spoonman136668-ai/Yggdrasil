"""MR34J3C staged PUBLIC-OBSERVATION-ONLY scaffold. OFFLINE ONLY.

Source target: Farama MiniGrid@7f5853792ea7f04f75614661006d87fcf949f26d,
MiniGrid-MemoryS7-v0. Does not import source or perform resets/steps.
Not source-admitted, source-tested, accepted, or repository-frozen.

The controller sees only the observation image/direction/mission, plus its own
finite-state navigation record. It never receives the hidden correct branch.
All arms, including the public-rule control, receive identical stage events.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

LEFT, RIGHT, FORWARD = 0, 1, 2
EAST, SOUTH, WEST, NORTH = 0, 1, 2, 3
UNSEEN, EMPTY, WALL, FLOOR, KEY, BALL = 0, 1, 2, 3, 5, 6
MISSION = "go to the matching object at the end of the hallway"
VIEW_SIZE = 7

class ProtocolBlocked(RuntimeError):
    """Missing public evidence; abort rather than invent a source event."""

class Stage(str, Enum):
    SEEK_WEST = "seek_west_public_wall"
    SCAN_CUE = "scan_cue_public_front"
    SEEK_EAST = "seek_east_public_wall"
    SCAN_FORK = "scan_fork_public_upper"
    AWAIT_CHOICE = "await_arm_choice"
    COMMIT_CHOICE = "commit_choice"
    DONE = "done"


def _read_voxel(image: Any, x: int, y: int, k: int) -> int:
    if hasattr(image, "shape"):
        if tuple(image.shape) != (VIEW_SIZE, VIEW_SIZE, 3):
            raise ProtocolBlocked("PUBLIC_IMAGE_SHAPE_MISMATCH")
        element = image[x, y, k]
    else:
        if len(image) != VIEW_SIZE or any(len(column) != VIEW_SIZE for column in image):
            raise ProtocolBlocked("PUBLIC_IMAGE_SHAPE_MISMATCH")
        element = image[x][y][k]
    if int(element) != element or not 0 <= int(element) <= 255:
        raise ProtocolBlocked("PUBLIC_IMAGE_BYTE_INVALID")
    return int(element)


@dataclass(frozen=True)
class PublicView:
    """Copy of exactly the original emitted visual/heading fields.

    It contains NO env reference, positions, world-grid access or action history.
    A one-time 147-byte immutable copy prevents a caller mutating a past view.
    """
    image_bytes: bytes
    direction: int

    @classmethod
    def from_observation(cls, obs: Any) -> "PublicView":
        if not isinstance(obs, dict) or set(obs) != {"image", "direction", "mission"}:
            raise ProtocolBlocked("NONPUBLIC_OBSERVATION_FIELDS")
        if obs["mission"] != MISSION or type(obs["direction"]) is not int or obs["direction"] not in (0, 1, 2, 3):
            raise ProtocolBlocked("PUBLIC_DIRECTION_OR_MISSION_INVALID")
        image = obs["image"]
        if not hasattr(image, "shape"):
            if any(len(image[x][y]) != 3 for x in range(7) for y in range(7)):
                raise ProtocolBlocked("PUBLIC_IMAGE_SHAPE_MISMATCH")
        raw = bytes(_read_voxel(image, x, y, c) for x in range(7) for y in range(7) for c in range(3))
        return cls(raw, obs["direction"])

    def obj(self, x: int, y: int) -> int:
        if not (0 <= x < 7 and 0 <= y < 7):
            raise ProtocolBlocked("PUBLIC_IMAGE_COORDINATE_INVALID")
        return self.image_bytes[3 * (x * 7 + y)]

    def front(self) -> int:
        # In original MiniGrid, agent at (3,6) in 7x7 agent-centric image.
        return self.obj(3, 5)


@dataclass(frozen=True)
class Step:
    action: Optional[int]
    event: str = ""


def _turn(now: int, heading: int) -> Optional[int]:
    diff = (heading - now) % 4
    if diff == 0:
        return None
    return RIGHT if diff == 1 else LEFT


class PublicOnlyNavigation:
    """Fixed source-public sensor policy; no hidden agent/world coordinates.

    Uses west/east wall contact as observational landmarks. The whole
    west-wall -> cue -> east-wall -> upper-object structure is openly
    predeclared task scaffolding, not learned navigation or an oracle label.
    """
    def __init__(self, max_navigation_commands: int = 24):
        self.stage = Stage.SEEK_WEST
        self.commands = 0
        self.max_commands = max_navigation_commands
        self.cue_exposed = False
        self.fork_exposed = False
        self._branch = None
        self._choice_actions: tuple[int, ...] = ()

    def _emit(self, action: int, event: str = "") -> Step:
        if action not in (LEFT, RIGHT, FORWARD):
            raise ProtocolBlocked("ILLEGAL_SHARED_ACTION")
        self.commands += 1
        if self.commands > self.max_commands:
            raise ProtocolBlocked("SHARED_SCAFFOLD_BUDGET_EXCEEDED")
        return Step(action, event)

    def advance(self, obs: dict) -> Step:
        view = PublicView.from_observation(obs)
        if self.stage == Stage.DONE:
            raise ProtocolBlocked("ACTION_AFTER_DONE")
        if self.stage == Stage.AWAIT_CHOICE:
            raise ProtocolBlocked("FORK_NEEDS_ONE_BRANCH_CHOICE")
        if self.stage == Stage.COMMIT_CHOICE:
            if not self._choice_actions:
                self.stage = Stage.DONE
                return Step(None, "COMMIT_ACTIONS_EXHAUSTED")
            action, *rest = self._choice_actions
            self._choice_actions = tuple(rest)
            return self._emit(action)

        if self.stage == Stage.SEEK_WEST:
            turn = _turn(view.direction, WEST)
            if turn is not None:
                return self._emit(turn)
            if view.front() == WALL:
                self.stage = Stage.SCAN_CUE
            elif view.front() in (EMPTY, FLOOR):
                return self._emit(FORWARD)
            else:
                raise ProtocolBlocked("WEST_FRONT_UNSUPPORTED_PUBLIC_OBJECT")

        if self.stage == Stage.SCAN_CUE:
            turn = _turn(view.direction, NORTH)
            if turn is not None:
                return self._emit(turn)
            if view.front() not in (KEY, BALL):
                raise ProtocolBlocked("STARTING_CUE_NOT_PUBLICLY_EXPOSED")
            self.cue_exposed = True
            self.stage = Stage.SEEK_EAST
            turn = _turn(view.direction, EAST)
            assert turn is not None
            return self._emit(turn, "PUBLIC_CUE_EXPOSURE")

        if self.stage == Stage.SEEK_EAST:
            turn = _turn(view.direction, EAST)
            if turn is not None:
                return self._emit(turn)
            if view.front() == WALL:
                self.stage = Stage.SCAN_FORK
            elif view.front() in (EMPTY, FLOOR):
                return self._emit(FORWARD)
            else:
                raise ProtocolBlocked("EAST_FRONT_UNSUPPORTED_PUBLIC_OBJECT")

        if self.stage == Stage.SCAN_FORK:
            turn = _turn(view.direction, NORTH)
            if turn is not None:
                return self._emit(turn)
            # Two cells ahead is a public fork-side key/ball in original S7.
            # It is NOT the hidden correct branch. No cue memory in controller.
            if view.obj(3, 4) not in (KEY, BALL):
                raise ProtocolBlocked("FORK_OBJECT_NOT_PUBLICLY_EXPOSED")
            self.fork_exposed = True
            self.stage = Stage.AWAIT_CHOICE
            return Step(None, "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")

        raise ProtocolBlocked("SHARED_NAVIGATION_STATE_UNHANDLED")

    def commit(self, choice: str) -> Step:
        if self.stage != Stage.AWAIT_CHOICE:
            raise ProtocolBlocked("CHOOSE_OUTSIDE_FORK")
        if choice not in ("north", "south"):
            raise ProtocolBlocked("INVALID_BRANCH_CHOICE")
        if not (self.cue_exposed and self.fork_exposed):
            raise ProtocolBlocked("UNVERIFIED_PUBLIC_EXPOSURE")
        self._branch = choice  # chosen by arm, never by shared controller
        # Facing north at fork: one original forward reaches north terminal;
        # otherwise turn twice to south and then forward to south terminal.
        self._choice_actions = (FORWARD,) if choice == "north" else (RIGHT, RIGHT, FORWARD)
        self.stage = Stage.COMMIT_CHOICE
        return Step(None, "BRANCH_CHOICE_ACCEPTED")


def public_rule_choice(cue_view: PublicView, fork_view: PublicView) -> str:
    """Training-free strong comparator using the SAME public exposure views."""
    if cue_view.direction != NORTH or fork_view.direction != NORTH:
        raise ProtocolBlocked("PUBLIC_RULE_VIEW_ORIENTATION_INVALID")
    cue, fork = cue_view.front(), fork_view.obj(3, 4)
    if cue not in (KEY, BALL) or fork not in (KEY, BALL):
        raise ProtocolBlocked("PUBLIC_RULE_MISSING_EXPOSURE")
    return "north" if cue == fork else "south"
