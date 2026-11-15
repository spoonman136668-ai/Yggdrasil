"""ST3 frozen, in-house developmental source: hidden intervention laws.

This is a task generator, not an externally independent scientific source.
The learner interface consists ONLY of public eight-bit state, previously
observed public outcome, and current action. Hidden law and pending effects
remain inside this source; no model may be handed an instance of this class.
"""
from hashlib import sha256
import json

SCHEMA = "yggdrasil.nci04.st3.hidden-law-switchboard-source.dev.v1"
STEPS = 64


def bits(x):
    if type(x) is not int or x < 0 or x > 255:
        raise ValueError("ST3_SOURCE_INVALID_BYTE")
    return tuple((x >> i) & 1 for i in range(8))


def byte(b):
    if (type(b) not in (list, tuple) or len(b) != 8 or
            any(type(v) is not int or v not in (0, 1) for v in b)):
        raise ValueError("ST3_SOURCE_INVALID_PUBLIC_BITS")
    return sum(v << i for i, v in enumerate(b))


def rotl8(value, k):
    if type(k) is not int or not 1 <= k <= 7:
        raise ValueError("ST3_SOURCE_BAD_ROTATION")
    return ((value << k) | (value >> (8 - k))) & 255


def source_mask(law_id, actuator):
    # Source-private; no candidate/control may receive the result or law ID.
    if (type(law_id) is not int or law_id < 0 or
            type(actuator) is not int or actuator not in (0, 1, 2)):
        raise ValueError("ST3_SOURCE_BAD_HIDDEN_LAW")
    return sha256(
        ("NCI04-ST3|" + str(law_id) + "|" + str(actuator))
        .encode("utf-8")
    ).digest()[0]


def choose_blind_action(seed, tick):
    if (type(seed) is not int or seed < 0 or
            type(tick) is not int or tick < 0 or tick >= STEPS):
        raise ValueError("ST3_ACTOR_INVALID_SEED_OR_STEP")
    d = (tick + seed % 4) % 4
    return d if seed % 2 == 0 else 3 - d


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


class HiddenLawSwitchboard:
    __slots__ = ("_law", "_seed", "_state", "_pending", "_steps")

    def __init__(self, law_id, seed):
        if (type(law_id) is not int or law_id < 0 or
                type(seed) is not int or seed < 0):
            raise ValueError("ST3_SOURCE_INVALID_LAW_OR_SEED")
        self._law = law_id
        self._seed = seed
        self._state = sha256(
            ("NCI04-ST3|state|" + str(seed)).encode("utf-8")
        ).digest()[0]
        self._pending = 0
        self._steps = 0

    def public(self):
        return bits(self._state)

    def step(self, action):
        if type(action) is not int or action not in range(4):
            raise ValueError("ST3_SOURCE_BAD_ACTION")
        if self._steps >= STEPS:
            raise ValueError("ST3_SOURCE_STEP_BUDGET_EXCEEDED")
        old = self._state
        rotation = 1 + self._law % 3
        immediate = source_mask(self._law, action) if action in (0, 1) else 0
        nxt = rotl8(old, rotation) ^ immediate ^ self._pending
        self._pending = source_mask(self._law, 2) if action == 2 else 0
        self._state = nxt
        self._steps += 1
        public = bits(nxt)
        change = bits(old ^ nxt)
        return public, change

    def snapshot(self):
        # Source-only checkpoint. NEVER pass its private fields to a model.
        return _canonical({
            "schema": SCHEMA,
            "law": self._law,
            "seed": self._seed,
            "state": self._state,
            "pending": self._pending,
            "steps": self._steps,
        })

    @classmethod
    def restore(cls, payload):
        if type(payload) is not str or len(payload) > 1024:
            raise ValueError("ST3_SOURCE_BAD_CHECKPOINT_LENGTH")
        try:
            d = json.loads(payload)
            if (type(d) is not dict or
                set(d) != {"schema", "law", "seed", "state", "pending", "steps"} or
                d["schema"] != SCHEMA or
                any(type(d[k]) is not int for k in
                    ("law", "seed", "state", "pending", "steps")) or
                min(d["law"], d["seed"], d["steps"]) < 0 or
                d["state"] not in range(256) or
                d["pending"] not in range(256) or
                d["steps"] > STEPS):
                raise ValueError("ST3_SOURCE_BAD_CHECKPOINT_SHAPE")
            s = cls(d["law"], d["seed"])
            s._state = d["state"]
            s._pending = d["pending"]
            s._steps = d["steps"]
            if s.snapshot() != payload:
                raise ValueError("ST3_SOURCE_NONCANONICAL_CHECKPOINT")
            return s
        except (KeyError, TypeError, OverflowError) as exc:
            raise ValueError("ST3_SOURCE_INVALID_CHECKPOINT") from exc
