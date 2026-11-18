"""WSP174 source-free public state and causal outcome boundary for CausalMBRL.

Original source: dido1998/CausalMBRL @ 2c595988b06b3d568fdde53213029e97841acb03
Original file: envs/chemistry_env_rl.py blob 58af54d7e7e30f8abe059df3d68565845a5b2c51
The caller must supply PUBLIC, list-converted state tensors from reset/step.
No simulator imports, dataset creation, protected source actions or lease.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json

SCHEMA = "yggdrasil.wsp174.chemistry-public-evidence.v1"
N_OBJECTS = 5
N_COLORS = 5
WIDTH = HEIGHT = 5
ACTION_COUNT = N_OBJECTS * N_COLORS
PUBLIC_FIELDS = frozenset({"current_state", "goal_state", "action", "next_state", "reward", "done"})
WIRE_FIELDS = frozenset({"schema", "current", "goal", "action", "next", "reward", "done"})
MAX_WIRE_BYTES = 4096


def decode_public_state(tensor: object) -> tuple[tuple[int, int, int], ...]:
    """Convert original public (25,5,5) occupancy to (x,y,color) by object."""
    if type(tensor) not in (list, tuple) or len(tensor) != ACTION_COUNT:
        raise ValueError("WSP174_STATE_CHANNEL_SHAPE")
    result: list[tuple[int, int, int]] = []
    for obj in range(N_OBJECTS):
        active: list[tuple[int, int, int]] = []
        for color in range(N_COLORS):
            channel = tensor[obj * N_COLORS + color]
            if type(channel) not in (list, tuple) or len(channel) != WIDTH:
                raise ValueError("WSP174_STATE_GRID_SHAPE")
            for x, line in enumerate(channel):
                if type(line) not in (list, tuple) or len(line) != HEIGHT:
                    raise ValueError("WSP174_STATE_GRID_SHAPE")
                for y, value in enumerate(line):
                    if type(value) is not int or value not in (0, 1):
                        raise ValueError("WSP174_STATE_BINARY")
                    if value:
                        active.append((x, y, color))
                        if len(active) > 1:
                            raise ValueError("WSP174_STATE_OBJECT_NOT_ONEHOT")
        if len(active) != 1:
            raise ValueError("WSP174_STATE_OBJECT_NOT_ONEHOT")
        result.append(active[0])
    if len({(x, y) for x, y, _ in result}) != N_OBJECTS:
        raise ValueError("WSP174_STATE_COLLISION")
    return tuple(result)


def _scene(value: object) -> tuple[tuple[int, int, int], ...]:
    if type(value) not in (list, tuple) or len(value) != N_OBJECTS:
        raise ValueError("WSP174_WIRE_SCENE")
    result = []
    for triple in value:
        if type(triple) not in (list, tuple) or len(triple) != 3:
            raise ValueError("WSP174_WIRE_SCENE")
        x, y, color = triple
        if any(type(z) is not int for z in triple):
            raise ValueError("WSP174_WIRE_SCENE")
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT and 0 <= color < N_COLORS):
            raise ValueError("WSP174_WIRE_SCENE")
        result.append((x, y, color))
    if len({(x, y) for x, y, _ in result}) != N_OBJECTS:
        raise ValueError("WSP174_WIRE_COLLISION")
    return tuple(result)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("WSP174_WIRE_DUPLICATE")
        result[key] = value
    return result


def _reject_nonfinite(_: str) -> object:
    raise ValueError("WSP174_WIRE_NONFINITE")


@dataclass(frozen=True, slots=True)
class PublicEvidence:
    current: tuple[tuple[int, int, int], ...]
    goal: tuple[tuple[int, int, int], ...]
    action: int
    next: tuple[tuple[int, int, int], ...]
    reward: float
    done: bool

    def __post_init__(self) -> None:
        current = _scene(self.current)
        goal = _scene(self.goal)
        next_state = _scene(self.next)
        if type(self.action) is not int or not 0 <= self.action < ACTION_COUNT:
            raise ValueError("WSP174_ACTION")
        if type(self.done) is not bool or self.done is not False:
            # The pinned source step() always returns done=False.
            # Any outer censoring MUST remain separately logged.
            raise ValueError("WSP174_SOURCE_DONE")
        if type(self.reward) not in (int, float):
            raise ValueError("WSP174_REWARD_TYPE")
        reward = float(self.reward)
        if reward not in tuple(k / N_OBJECTS for k in range(N_OBJECTS + 1)):
            raise ValueError("WSP174_REWARD_RANGE")
        if tuple((x, y) for x, y, _ in current) != tuple((x, y) for x, y, _ in next_state):
            raise ValueError("WSP174_MOVED_OBJECT")
        if tuple((x, y) for x, y, _ in current) != tuple((x, y) for x, y, _ in goal):
            raise ValueError("WSP174_CHANGED_TARGET_POSITIONS")
        obj, color = divmod(self.action, N_COLORS)
        if next_state[obj][2] != color:
            raise ValueError("WSP174_ACTION_EFFECT")
        expected = sum(int(a[2] == b[2]) for a, b in zip(next_state, goal)) / N_OBJECTS
        if reward != expected:
            raise ValueError("WSP174_REWARD_MISMATCH")
        object.__setattr__(self, "current", current)
        object.__setattr__(self, "goal", goal)
        object.__setattr__(self, "next", next_state)
        object.__setattr__(self, "reward", reward)

    @classmethod
    def from_public(cls, **values: object) -> "PublicEvidence":
        if set(values) != PUBLIC_FIELDS:
            # No graph/MLP/mask, future target actions, private RNG, seed,
            # lease, evaluator metadata, hidden state or info dictionary.
            raise ValueError("WSP174_PUBLIC_FIELD_SET")
        return cls(
            current=decode_public_state(values["current_state"]),
            goal=decode_public_state(values["goal_state"]),
            action=values["action"],
            next=decode_public_state(values["next_state"]),
            reward=values["reward"], done=values["done"],
        )

    def policy_input(self) -> dict[str, object]:
        """Decision-only fields; never include future outcome or secret graph."""
        return {"current": [list(x) for x in self.current],
                "goal": [list(x) for x in self.goal]}

    def learning_record(self) -> dict[str, object]:
        return {**self.policy_input(), "action": self.action,
                "next": [list(x) for x in self.next],
                "reward": self.reward, "done": self.done}

    def canonical(self) -> bytes:
        return json.dumps({"schema": SCHEMA, **self.learning_record()},
                          sort_keys=True, allow_nan=False, separators=(",", ":")).encode("ascii")

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

    @classmethod
    def restore(cls, raw: bytes, digest: str) -> "PublicEvidence":
        if type(raw) is not bytes or not (0 < len(raw) <= MAX_WIRE_BYTES):
            raise ValueError("WSP174_WIRE_SIZE")
        if (type(digest) is not str or len(digest) != 64 or
                any(c not in "0123456789abcdef" for c in digest) or
                not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), digest)):
            raise ValueError("WSP174_WIRE_HASH")
        try:
            payload = json.loads(raw.decode("ascii"),
                                 object_pairs_hook=_reject_duplicate_keys,
                                 parse_constant=_reject_nonfinite)
        except (ValueError, UnicodeError, TypeError) as exc:
            raise ValueError("WSP174_WIRE_PARSE") from exc
        if type(payload) is not dict or set(payload) != WIRE_FIELDS or payload["schema"] != SCHEMA:
            raise ValueError("WSP174_WIRE_SCHEMA")
        obj = cls(current=payload["current"], goal=payload["goal"],
                  action=payload["action"], next=payload["next"],
                  reward=payload["reward"], done=payload["done"])
        if raw != obj.canonical():
            raise ValueError("WSP174_WIRE_NONCANONICAL")
        return obj
