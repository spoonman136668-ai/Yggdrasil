"""Research-only public event log for numerical, single-step causal environments.

No source actor, sampler, learner, prediction, training, or CKAD admission.
SHA-256 custody detects accidental mutation, NOT source-owner authentication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

SCHEMA = "yggdrasil.research.numeric-public-episode.p0.v1"
CHECKPOINT_SCHEMA = "yggdrasil.research.numeric-public-checkpoint.p0.v1"
PUBLIC_KEYS = frozenset(("source_sha256", "identifier", "step", "before", "action",
                         "after", "reward", "terminated", "truncated"))
CHECKPOINT_KEYS = frozenset(("schema", "source_sha256", "shape", "steps"))
EVENT_KEYS = frozenset(("identifier", "step", "before", "action", "after",
                       "reward", "terminated", "truncated"))
MAX_EVENTS = 2048   # independent RESEARCH buffer, not a native capacity extension
MAX_DIMENSION = 128


def _pin(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _check(condition, tag):
    if not condition:
        raise ValueError("NUMERIC_P0_" + tag)


def _finite_float(value):
    return type(value) is float and math.isfinite(value)


def _vector(value, shape):
    _check(type(value) is tuple and len(value) == shape, "PUBLIC_VECTOR_SHAPE")
    _check(all(_finite_float(x) for x in value), "PUBLIC_VECTOR_TYPE")
    return value


def _encoded_float(x):
    # Preserves exact binary64, including negative zero and subnormal values.
    return x.hex()


def _decoded_float(value):
    _check(type(value) is str, "CHECKPOINT_FLOAT_TYPE")
    try:
        x = float.fromhex(value)
    except (ValueError, OverflowError):
        raise ValueError("NUMERIC_P0_CHECKPOINT_FLOAT") from None
    _check(_finite_float(x) and x.hex() == value, "CHECKPOINT_FLOAT_CANONICAL")
    return x


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class PublicStep:
    identifier: str
    step: int
    before: tuple[float, ...]
    action: int
    after: tuple[float, ...]
    reward: float
    terminated: bool
    truncated: bool

    @staticmethod
    def parse(packet, source, shape, expected_step):
        _check(type(packet) is dict and frozenset(packet) == PUBLIC_KEYS, "EXACT_PUBLIC_FIELDS")
        _check(_pin(packet["source_sha256"]) and packet["source_sha256"] == source,
               "SOURCE_PIN_MISMATCH")
        _check(_pin(packet["identifier"]), "IDENTIFIER_PIN")
        _check(type(packet["step"]) is int and packet["step"] == expected_step,
               "CHRONOLOGICAL_STEP")
        _check(type(packet["action"]) is int and 0 <= packet["action"] < 5,
               "FIVE_ACTION_IDENTITY")
        _vector(packet["before"], shape)
        _vector(packet["after"], shape)
        _check(_finite_float(packet["reward"]), "SCALAR_REWARD")
        _check(type(packet["terminated"]) is bool and type(packet["truncated"]) is bool,
               "TERMINAL_FLAGS")
        return PublicStep(packet["identifier"], packet["step"], packet["before"],
                          packet["action"], packet["after"], packet["reward"],
                          packet["terminated"], packet["truncated"])

    def checkpoint_row(self):
        return {"identifier": self.identifier, "step": self.step,
                "before": [_encoded_float(x) for x in self.before],
                "action": self.action,
                "after": [_encoded_float(x) for x in self.after],
                "reward": _encoded_float(self.reward),
                "terminated": self.terminated, "truncated": self.truncated}


@dataclass(frozen=True, slots=True)
class NumericPublicEpisodeLog:
    source_sha256: str
    shape: int
    steps: tuple[PublicStep, ...] = ()

    def __post_init__(self):
        _check(_pin(self.source_sha256), "SOURCE_PIN")
        _check(type(self.shape) is int and 1 <= self.shape <= MAX_DIMENSION,
               "SHAPE_BOUNDS")
        _check(type(self.steps) is tuple and len(self.steps) <= MAX_EVENTS,
               "STEP_CAPACITY")
        # Only append/restore should create nonempty logs; reject caller-forged tuples.
        if self.steps:
            seen = set()
            for i, event in enumerate(self.steps):
                _check(type(event) is PublicStep and event.step == i, "UNTRUSTED_HISTORY")
                _check(event.identifier not in seen and _pin(event.identifier), "REPLAYED_IDENTIFIER")
                seen.add(event.identifier)
                _vector(event.before, self.shape)
                _vector(event.after, self.shape)
                _check(type(event.action) is int and 0 <= event.action < 5 and
                       _finite_float(event.reward) and
                       type(event.terminated) is bool and type(event.truncated) is bool,
                       "UNTRUSTED_EVENT")
                _check(i == len(self.steps) - 1 or not (event.terminated or event.truncated),
                       "AFTER_TERMINAL")

    def append(self, public_packet):
        _check(len(self.steps) < MAX_EVENTS, "STEP_CAPACITY")
        _check(not self.steps or not (self.steps[-1].terminated or self.steps[-1].truncated),
               "AFTER_TERMINAL")
        event = PublicStep.parse(public_packet, self.source_sha256, self.shape,
                                 len(self.steps))
        _check(all(p.identifier != event.identifier for p in self.steps),
               "REPLAYED_IDENTIFIER")
        return NumericPublicEpisodeLog(self.source_sha256, self.shape, self.steps + (event,))

    def checkpoint(self):
        return _canonical({"schema": CHECKPOINT_SCHEMA, "source_sha256": self.source_sha256,
                           "shape": self.shape,
                           "steps": [event.checkpoint_row() for event in self.steps]})

    @classmethod
    def restore(cls, raw, expected_sha256):
        _check(type(raw) is bytes and _pin(expected_sha256), "CHECKPOINT_TYPE")
        _check(_sha(raw) == expected_sha256, "CHECKPOINT_DIGEST")
        try:
            doc = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ValueError("NUMERIC_P0_CHECKPOINT_JSON") from None
        _check(type(doc) is dict and frozenset(doc) == CHECKPOINT_KEYS and
               doc["schema"] == CHECKPOINT_SCHEMA, "CHECKPOINT_SCHEMA")
        _check(type(doc["steps"]) is list and len(doc["steps"]) <= MAX_EVENTS,
               "CHECKPOINT_STEPS")
        obj = cls(doc["source_sha256"], doc["shape"])
        for row in doc["steps"]:
            _check(type(row) is dict and frozenset(row) == EVENT_KEYS,
                   "CHECKPOINT_PUBLIC_FIELDS")
            event = dict(row)
            event["source_sha256"] = obj.source_sha256
            _check(type(event["before"]) is list and type(event["after"]) is list,
                   "CHECKPOINT_VECTOR_SHAPE")
            event["before"] = tuple(_decoded_float(x) for x in event["before"])
            event["after"] = tuple(_decoded_float(x) for x in event["after"])
            event["reward"] = _decoded_float(event["reward"])
            obj = obj.append(event)
        _check(obj.checkpoint() == raw, "CHECKPOINT_CANONICAL")
        return obj

    def proof_of_scope(self):
        return {"schema": SCHEMA, "public_steps": len(self.steps),
                "numeric_shape": self.shape, "action_cardinality": 5,
                "source_pin_claimed_not_owner_authenticated": True,
                "source_owner_authenticated": False, "native_admission": False,
                "original_world_first_use": False, "scientific_gain_verified": False,
                "can_act": False, "can_train": False, "can_deploy": False,
                "ckad_two_stage_synthesized": False}

    def require_native_abi(self):
        raise ValueError("NUMERIC_P0_NOT_NATIVE_ABI")
