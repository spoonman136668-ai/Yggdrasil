"""WSP-101 observationally equivalent DEV world pairs.

Only fixture contexts 0..7 exist. All original FIT/TRANSFER/NOVEL/RESERVED
identities are rejected. This is task construction, not a trained learner.
"""
from __future__ import annotations

import hashlib
import json

CHANNELS = 6
ALPHABET = 4
ACTIONS = 4
STEPS = 4
PASSIVE_EPISODES = 16
DEV_CONTEXTS = tuple(range(8))


def rank(context_id: int, stream: str, index: int) -> int:
    if type(context_id) is not int or context_id not in DEV_CONTEXTS:
        raise PermissionError("only WSP101 development contexts 0..7 allowed")
    if type(index) is not int or index < 0 or not isinstance(stream, str):
        raise ValueError("invalid domain-separated hash argument")
    return int.from_bytes(hashlib.sha256(
        f"WSP101|v1|DEV|{context_id}|{stream}|{index}".encode("ascii")
    ).digest(), "big")


def digits4(integer: int):
    if type(integer) is not int or not 0 <= integer < 4096:
        raise ValueError("six base-4 digits expected")
    return tuple((integer >> (2 * i)) & 3 for i in range(CHANNELS))


def visible_tuple(visible):
    if not isinstance(visible, (tuple, list)) or len(visible) != CHANNELS:
        raise ValueError("six four-valued observations required")
    if any(type(v) is not int or not 0 <= v < ALPHABET for v in visible):
        raise ValueError("all observations must be integers 0..3")
    return tuple(visible)


def source_sha256(data):
    return hashlib.sha256(json.dumps(
        data, separators=(",", ":"), sort_keys=True, allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _operator(index, a, b):
    if index == 0:
        return (a + b) % 4
    if index == 1:
        return a ^ b
    if index == 2:
        return a if b % 2 == 0 else 3 - a
    if index == 3:
        return (a * b + b) % 4
    raise ValueError("unknown fixture operator")


class _PairOracle:
    """Evaluator-only parameters. Never pass this object to a learner."""

    def __init__(self, context_id: int, mode: int, *, no_latches=False):
        if type(context_id) is not int or context_id not in DEV_CONTEXTS:
            raise PermissionError("original world identities cannot be constructed")
        if type(mode) is not int or mode not in (0, 1):
            raise ValueError("paired world mode must be 0 or 1")
        if type(no_latches) is not bool:
            raise ValueError("invalid ablation")
        self._program = (
            rank(context_id, "FAMILY", 0) % 4,
            rank(context_id, "WIRING", 0) % 6,
            rank(context_id, "PHASE", 0) % 4,
            1 + rank(context_id, "TRIGGER", 0) % 3,
        )
        self._mode = mode
        self._no_latches = no_latches
        self.reset((0,) * CHANNELS)

    def reset(self, initial):
        self._visible = visible_tuple(initial)
        self._hidden = (0, 0)
        self._steps = 0
        return self._visible

    def step(self, action):
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("action must be an integer from 0 to 3")
        if self._steps >= STEPS:
            raise ValueError("episode action budget exceeded")
        f, w, p, trigger = self._program
        x, old_h = self._visible, self._hidden
        y = []
        for i in range(CHANNELS):
            a, b = x[(i + w) % CHANNELS], x[(i + w + 2) % CHANNELS]
            base = (_operator((f + i % 4) % 4, a, b)
                    + x[(i + 4) % CHANNELS] + p * (i % 3)) % ALPHABET
            if i < 4 and not self._no_latches:
                base = (base + old_h[i % 2]) % ALPHABET
            y.append(base)
        next_h = list(old_h)
        if not self._no_latches:
            if action == trigger:
                next_h[0] = (old_h[0] + (1 if self._mode == 0 else 2)) % ALPHABET
                if (x[0] + p) % 2 == 1:
                    next_h[1] = (old_h[1] + 1) % ALPHABET
            if action == (trigger % 3) + 1:
                next_h[1] = (old_h[1] + 1 + (x[5] % 2)) % ALPHABET
        self._visible = tuple(y)
        self._hidden = tuple(next_h)
        self._steps += 1
        return {
            "observation": self._visible,
            "reward": int((self._visible[0] + self._visible[1]) % 4 == 3),
        }


class ObservationAPI:
    """Cooperative observer-facing interface: reset() and step() only.

    This Python facade is an API discipline, NOT a malicious-reflection
    security boundary. Models must consume recorded histories, not oracle
    objects or their implementation details.
    """
    __slots__ = ("reset", "step")

    def __init__(self, oracle: _PairOracle):
        self.reset = oracle.reset
        self.step = oracle.step


def observe_world(context_id: int, mode: int):
    """Creates an observer endpoint; original worlds always fail closed."""
    return ObservationAPI(_PairOracle(context_id, mode))


def passive_source(context_id: int, mode: int):
    """A mode-unlabeled source: 16 four-step action-0 episodes.

    The caller/experiment custodian decides which endpoint to request; the
    learner only receives the returned visible/action/consequence rows.
    """
    observer = observe_world(context_id, mode)
    episodes = []
    for episode_id in range(PASSIVE_EPISODES):
        initial = digits4(rank(context_id, "PASSIVE-INIT", episode_id) % 4096)
        current = observer.reset(initial)
        rows = []
        for _ in range(STEPS):
            response = observer.step(0)
            if set(response) != {"observation", "reward"}:
                raise ValueError("unexpected oracle field")
            nxt = visible_tuple(response["observation"])
            reward = int((nxt[0] + nxt[1]) % 4 == 3)
            if type(response["reward"]) is not int or response["reward"] != reward:
                raise ValueError("invalid visible reward")
            rows.append((current, 0, nxt, reward))
            current = nxt
        episodes.append(tuple(rows))
    result = tuple(episodes)
    validate_passive_source(result)
    return result


def validate_passive_source(episodes):
    if not isinstance(episodes, (tuple, list)) or len(episodes) != PASSIVE_EPISODES:
        raise ValueError("source must have exactly 16 episodes")
    for episode in episodes:
        if not isinstance(episode, (tuple, list)) or len(episode) != STEPS:
            raise ValueError("every episode must contain exactly four steps")
        prior = None
        for row in episode:
            if not isinstance(row, (tuple, list)) or len(row) != 4:
                raise ValueError("source row must contain visible/action/next/reward")
            x, action, y, reward = row
            x, y = visible_tuple(x), visible_tuple(y)
            if action != 0 or type(action) is not int:
                raise ValueError("passive action protocol violated")
            if prior is not None and x != prior:
                raise ValueError("source trajectory not contiguous")
            if type(reward) is not int or reward != int((y[0] + y[1]) % 4 == 3):
                raise ValueError("source reward invalid")
            prior = y
    return True


def paired_passive_proof(context_id):
    """Custodian-only equality check; only the unlabeled observations hash."""
    left = passive_source(context_id, 0)
    right = passive_source(context_id, 1)
    return {
        "classification": "DEV_PASSIVE_EQUIVALENCE_ONLY",
        "source_sha256": source_sha256(left),
        "same_source": left == right,
        "episodes": len(left),
        "transitions_per_mode": len(left) * STEPS,
    }


def paired_delayed_witness(context_id, initial):
    """Evaluator-only mechanistic witness; do not import into learner."""
    initial = visible_tuple(initial)
    trigger = 1 + rank(context_id, "TRIGGER", 0) % 3
    left = _PairOracle(context_id, 0)
    right = _PairOracle(context_id, 1)
    left.reset(initial)
    right.reset(initial)
    first_left, first_right = left.step(trigger), right.step(trigger)
    second_left, second_right = left.step(0), right.step(0)
    return {
        "classification": "DEV_DELAYED_CAUSAL_WITNESS_ONLY",
        "immediate_equal": first_left == first_right,
        "delayed_visible_differs":
            second_left["observation"] != second_right["observation"],
        "first_step_observations": first_left["observation"],
        "delayed_channel_difference_count": sum(
            a != b for a, b in zip(
                second_left["observation"], second_right["observation"]
            )
        ),
    }
