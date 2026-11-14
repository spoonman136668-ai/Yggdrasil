"""Fixture-only WSP99 simulator: never produces original public/reserved worlds."""
from __future__ import annotations
import hashlib

VISIBLE = 6
HIDDEN = 2
ACTIONS = 4
EPISODE_LIMIT = 4
GATES = ("AND", "OR", "XOR", "XNOR", "NAND", "NOR")


def rank(fixture: int, stream: str, index: int) -> int:
    return int.from_bytes(hashlib.sha256(
        f"WSP99|v1|FIXTURE|{fixture}|{stream}|{index}".encode("ascii")
    ).digest(), "big")


def bits(code: int):
    if type(code) is not int or not 0 <= code < 64:
        raise ValueError("invalid visible state integer")
    return tuple((code >> k) & 1 for k in range(VISIBLE))


def valid_state(value):
    if not isinstance(value, (tuple, list)) or len(value) != VISIBLE or any(
        type(x) is not int or x not in (0, 1) for x in value
    ):
        raise ValueError("six binary visible bits required")
    return tuple(value)


def pair(seed: int):
    a = seed % VISIBLE
    b = (a + 1 + (seed // VISIBLE) % (VISIBLE - 1)) % VISIBLE
    return a, b


def gate(which: str, a: int, b: int) -> int:
    if which == "AND": return a & b
    if which == "OR": return a | b
    if which == "XOR": return a ^ b
    if which == "XNOR": return 1 ^ a ^ b
    if which == "NAND": return 1 ^ (a & b)
    if which == "NOR": return 1 ^ (a | b)
    raise ValueError("unknown gate")


class FixtureWorld:
    """Learner-facing operations: reset and step. Other fields are oracle-only."""

    def __init__(self, fixture_id: int, *, _auditor_no_latches: bool = False):
        if type(fixture_id) is not int or not 0 <= fixture_id < 8:
            raise ValueError("only fixtures 0..7 are eligible")
        if type(_auditor_no_latches) is not bool:
            raise ValueError("invalid ablation flag")
        self.fixture_id = fixture_id
        self._auditor_no_latches = _auditor_no_latches
        self._clauses = []
        for i in range(VISIBLE):
            seed = rank(fixture_id, "PROGRAM", i)
            a, b = pair(seed)
            flips = (seed // 97) % 4
            law = GATES[(seed // 389) % len(GATES)]
            self._clauses.append((a, b, flips & 1, flips >> 1, law))
        first = rank(fixture_id, "TRIGGERS", 0) % ACTIONS
        second = (first + 1 + rank(fixture_id, "TRIGGERS", 1) % (ACTIONS - 1)) % ACTIONS
        self._triggers = (first, second)
        self._conditions = []
        for j in range(HIDDEN):
            seed = rank(fixture_id, "LATCH", j)
            self._conditions.append((*pair(seed), (seed // 17) % 2))
        self.reset((0,) * VISIBLE)

    @classmethod
    def original_world(cls, *_args, **_kwargs):
        raise PermissionError("original WSP99 public and reserved worlds are not admitted")

    def reset(self, visible):
        self._visible = valid_state(visible)
        self._hidden = (0, 0)
        self._steps = 0
        return self._visible

    def step(self, action: int):
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("action must be 0..3")
        if self._steps >= EPISODE_LIMIT:
            raise ValueError("episode action budget exceeded")
        x, h = self._visible, self._hidden
        new_visible = []
        for i, (a, b, fa, fb, law) in enumerate(self._clauses):
            y = gate(law, x[a] ^ fa, x[b] ^ fb)
            if i < 4 and not self._auditor_no_latches:
                y ^= h[i % HIDDEN]
            new_visible.append(y)
        new_hidden = list(h)
        if not self._auditor_no_latches:
            for j, (a, b, flip) in enumerate(self._conditions):
                if action == self._triggers[j] and (x[a] ^ x[b] ^ flip):
                    new_hidden[j] ^= 1
        self._visible = tuple(new_visible)
        self._hidden = tuple(new_hidden)
        self._steps += 1
        return {"observation": self._visible, "reward": self._visible[0] & self._visible[1]}


def auditor_delayed_witnesses(fixture_id: int, *, no_latches: bool = False):
    """Evaluator-only fixture check. Never import this into a candidate policy."""
    reference = FixtureWorld(fixture_id)
    neutral = next(i for i in range(ACTIONS) if i not in reference._triggers)
    witnesses = []
    for latch, trigger in enumerate(reference._triggers):
        for initial in range(64):
            a = FixtureWorld(fixture_id, _auditor_no_latches=no_latches)
            b = FixtureWorld(fixture_id, _auditor_no_latches=no_latches)
            a.reset(bits(initial))
            b.reset(bits(initial))
            if a.step(trigger) != b.step(neutral):
                raise AssertionError("intervention affected immediate output")
            if a.step(neutral)["observation"] != b.step(neutral)["observation"]:
                witnesses.append((latch, initial, trigger, neutral))
                break
    return tuple(witnesses)
