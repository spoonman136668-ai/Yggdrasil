"""C27 source-only three-way front observation, strict source-event boundary.

No original environment import, creation, reset, step, hidden map, or source seeds.
This is a testable visibility contract and hand-designed demonstrator, NOT a
native causal learner or a scientific observation of unfamiliar-world learning.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from research.native.itd02.r1.native_policy import PublicGrid, features as validate_original_public

CLEAR = "CLEAR"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"
FRONTS = frozenset((CLEAR, BLOCKED, UNKNOWN))
SCHEMA = "itd02.c27.present-missing-public-front.v1"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


@dataclass(frozen=True)
class PublicView:
    x: int
    y: int
    goal_x: int
    goal_y: int
    direction: int
    front: str

    def __post_init__(self):
        if any(type(v) is not int or not (0 <= v <= 31) for v in (
              self.x, self.y, self.goal_x, self.goal_y)):
            raise ValueError("INVALID_PUBLIC_COORD")
        if type(self.direction) is not int or self.direction not in range(4):
            raise ValueError("INVALID_PUBLIC_DIRECTION")
        if type(self.front) is not str or self.front not in FRONTS:
            raise ValueError("INVALID_FRONT_PRESENCE_TOKEN")

    def edge(self) -> str:
        return ",".join(map(str, (self.x, self.y, self.direction)))

    def location(self) -> tuple[int, ...]:
        return (self.x, self.y, self.goal_x, self.goal_y, self.direction)

    def payload(self) -> dict:
        return {"x": self.x, "y": self.y, "goal_x": self.goal_x,
                "goal_y": self.goal_y, "direction": self.direction, "front": self.front}


def _view(raw: object) -> PublicView:
    if type(raw) is not PublicView:
        raise ValueError("EXPECTED_EXACT_PUBLIC_VIEW_NO_EXTRA_METADATA")
    return raw


def from_source(source_public: PublicGrid, reveal: bool) -> PublicView:
    """Evaluator-only conversion; policy NEVER receives source_public.

    UNKNOWN contains no encoded source front boolean, not an imputed FALSE.
    """
    if type(source_public) is not PublicGrid or type(reveal) is not bool:
        raise ValueError("ORIGINAL_PUBLIC_SOURCE_OR_VISIBILITY_INVALID")
    validate_original_public(source_public)
    return PublicView(source_public.x, source_public.y,
                      source_public.goal_x, source_public.goal_y,
                      source_public.direction,
                      (BLOCKED if source_public.front_blocked else CLEAR)
                      if reveal else UNKNOWN)


def to_original(view: PublicView) -> PublicGrid:
    """Explicitly deny feeding unknown into old R1/R2/R3 bool-only features."""
    view = _view(view)
    if view.front == UNKNOWN:
        raise ValueError("UNKNOWN_CANNOT_DOWNCAST_TO_PUBLICGRID_BOOL")
    return PublicGrid(view.x, view.y, view.goal_x, view.goal_y,
                      view.direction, view.front == BLOCKED)


class VisibilityEvidenceDemonstrator:
    """A source-only, deliberately hand-coded baseline with bounded public memory.

    It exists to certify actual missingness handling and action receipt custody;
    it is NOT a trained native value-of-information/cellular controller.
    """
    def __init__(self):
        self.evidence: dict[str, str] = {}
        self.action_counts = {"0": 0, "1": 0, "2": 0}
        self.steps = 0
        self.reward_total = 0.0
        self.last_return: tuple[int, ...] | None = None
        self.ended = False

    def choose(self, current: PublicView) -> int:
        current = _view(current)
        # Current source-observed front is authoritative; UNKNOWN must consult
        # only prior LEGAL observations, or take a conservative turn.
        status = current.front
        if status == UNKNOWN:
            status = self.evidence.get(current.edge(), UNKNOWN)
        return 2 if status == CLEAR else 0

    def observe_return(self, before: PublicView, action: int,
                       after: PublicView, reward: float,
                       terminal: bool, truncated: bool):
        before, after = _view(before), _view(after)
        if self.ended:
            raise ValueError("EPISODE_ALREADY_ENDED")
        if type(action) is not int or action not in (0, 1, 2):
            raise ValueError("INVALID_SELECTED_ACTION")
        if type(reward) not in (float, int) or not math.isfinite(reward):
            raise ValueError("INVALID_RETURNED_SOURCE_REWARD")
        if type(terminal) is not bool or type(truncated) is not bool:
            raise ValueError("INVALID_DONE_OR_TRUNCATED_FLAG")
        if (before.goal_x, before.goal_y) != (after.goal_x, after.goal_y):
            raise ValueError("SOURCE_GOAL_DRIFT")
        if self.last_return is not None and before.location() != self.last_return:
            raise ValueError("MISSING_OR_UNLINKED_SELECTED_ACTION_RETURN")
        if action in (0, 1):
            turn = (-1 if action == 0 else 1)
            if ((before.x, before.y) != (after.x, after.y) or
                after.direction != (before.direction + turn) % 4):
                raise ValueError("NOT_A_LEGAL_SOURCE_TURN_EFFECT")
        else:
            if (before.direction != after.direction or
                abs(after.x - before.x) + abs(after.y - before.y) > 1):
                raise ValueError("NOT_A_LEGAL_SOURCE_FORWARD_EFFECT")
        if self.steps >= 10000:
            raise ValueError("EPISODE_ACTION_BUDGET")
        # All validation occurs before mutation. No observation recorded from
        # an explicitly UNKNOWN reading (neither a false-clear nor a false-block).
        for view in (before, after):
            if view.front != UNKNOWN:
                if len(self.evidence) >= 4096 and view.edge() not in self.evidence:
                    raise ValueError("MEMORY_LIMIT")
        for view in (before, after):
            if view.front != UNKNOWN:
                self.evidence[view.edge()] = view.front
        self.action_counts[str(action)] += 1
        self.steps += 1
        self.reward_total += float(reward)
        self.last_return = after.location()
        self.ended = bool(terminal or truncated)

    def snapshot(self) -> bytes:
        obj = {"schema": SCHEMA, "evidence": self.evidence,
               "action_counts": self.action_counts, "steps": self.steps,
               "reward_total": self.reward_total,
               "last_return": list(self.last_return) if self.last_return else None,
               "ended": self.ended}
        result = canonical({"data": obj, "sha256": hashlib.sha256(canonical(obj)).hexdigest()})
        if len(result) > 262144:
            raise ValueError("CHECKPOINT_TOO_LARGE")
        return result

    @classmethod
    def restore(cls, checkpoint: bytes) -> "VisibilityEvidenceDemonstrator":
        if type(checkpoint) is not bytes or not 0 < len(checkpoint) <= 262144:
            raise ValueError("INVALID_CHECKPOINT_TYPE_OR_SIZE")
        try:
            wire = json.loads(checkpoint)
            if type(wire) is not dict or set(wire) != {"data", "sha256"}:
                raise ValueError("INVALID_CHECKPOINT_ENVELOPE")
            raw = wire["data"]
            if (type(raw) is not dict or
                set(raw) != {"schema", "evidence", "action_counts", "steps",
                             "reward_total", "last_return", "ended"} or
                raw["schema"] != SCHEMA or
                hashlib.sha256(canonical(raw)).hexdigest() != wire["sha256"]):
                raise ValueError("UNAUTHENTICATED_CHECKPOINT")
            if (type(raw["steps"]) is not int or not 0 <= raw["steps"] <= 10000 or
                type(raw["ended"]) is not bool or
                type(raw["reward_total"]) not in (float, int) or
                not math.isfinite(raw["reward_total"])):
                raise ValueError("CORRUPT_CHECKPOINT_COUNTERS")
            if (type(raw["action_counts"]) is not dict or
                set(raw["action_counts"]) != {"0", "1", "2"} or
                any(type(k) is not int or k < 0 for k in raw["action_counts"].values()) or
                sum(raw["action_counts"].values()) != raw["steps"]):
                raise ValueError("CORRUPT_SELECTED_ACTION_RECEIPTS")
            ev = raw["evidence"]
            if (type(ev) is not dict or len(ev) > 4096 or
                any(type(k) is not str or type(v) is not str or
                    v not in (CLEAR, BLOCKED) or
                    len(k.split(",")) != 3 or
                    any(not e.isdecimal() or int(e) > 31 for e in k.split(","))
                    for k, v in ev.items())):
                raise ValueError("CORRUPT_PUBLIC_EVIDENCE")
            lr = raw["last_return"]
            if lr is not None and (type(lr) is not list or len(lr) != 5 or
                any(type(v) is not int or not 0 <= v <= 31 for v in lr) or
                lr[4] > 3):
                raise ValueError("CORRUPT_RETURN_POSITION")
            if (raw["steps"] == 0) != (lr is None):
                raise ValueError("CORRUPT_RECEIPT_HISTORY")
            model = cls()
            model.evidence = ev
            model.action_counts = raw["action_counts"]
            model.steps = raw["steps"]
            model.reward_total = float(raw["reward_total"])
            model.last_return = tuple(lr) if lr is not None else None
            model.ended = raw["ended"]
            return model
        except (KeyError, TypeError, OverflowError, AttributeError) as exc:
            raise ValueError("MALFORMED_CHECKPOINT") from exc
