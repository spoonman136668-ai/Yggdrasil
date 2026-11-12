"""WSP52 negative-control learners; no segmentation or model semantics.

Only learner-facing Observation objects can be observed. A whole-stream
memorizer cannot compose unseen instructions. An erased learner learns nothing.
"""
from __future__ import annotations

from hashlib import sha256
import json


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _validate(acoustic_bits, before, after=None):
    if not isinstance(acoustic_bits, str) or not acoustic_bits or not set(acoustic_bits) <= {"0", "1"}:
        raise ValueError("acoustic stream must be nonempty binary")
    for state in (before, after):
        if state is None:
            continue
        if not isinstance(state, tuple) or len(state) != 8 or any(
            type(x) is not int or x not in (0, 1, 2, 3) for x in state
        ):
            raise ValueError("physical state must contain eight positions in 0..3")


class WholeStreamTable:
    """Exact observed (before, full acoustic stream) -> after only."""

    def __init__(self):
        self._facts: dict[tuple[tuple[int, ...], str], tuple[int, ...] | None] = {}
        self._conflicts = set()
        self.action_experiences = 0

    def observe(self, observation):
        # Only the five fields supplied by the public Observation contract.
        before = observation.before
        bits = observation.acoustic_bits
        after = observation.after
        _validate(bits, before, after)
        if type(observation.action_cost) is not int or observation.action_cost != 1:
            raise ValueError("unexpected action cost")
        if type(observation.reset_cost) is not int or observation.reset_cost != 0:
            raise ValueError("unexpected reset cost")
        key = (before, bits)
        self.action_experiences += observation.action_cost
        if key in self._conflicts:
            return
        if key in self._facts and self._facts[key] != after:
            self._conflicts.add(key)
            self._facts[key] = None  # evidence contradiction => abstain
        else:
            self._facts[key] = after

    def predict(self, before: tuple[int, ...], acoustic_bits: str) -> tuple[int, ...] | None:
        _validate(acoustic_bits, before)
        return self._facts.get((before, acoustic_bits))

    def capacity_bits(self) -> int:
        # Conservative serialized upper bound, not a memory or FLOP parity claim.
        return len(self.snapshot().encode("ascii")) * 8

    def snapshot(self) -> str:
        rows = []
        for (before, bits), after in sorted(self._facts.items()):
            rows.append([list(before), bits, None if after is None else list(after)])
        data = {"schema": "wsp52.whole-stream-table.v1",
                "experiences": self.action_experiences, "rows": rows,
                "conflicts": [[list(before), bits] for before, bits in sorted(self._conflicts)]}
        payload = _canonical(data)
        return _canonical({"payload": data, "sha256": sha256(payload.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, blob: str) -> "WholeStreamTable":
        if not isinstance(blob, str):
            raise ValueError("invalid snapshot")
        try:
            envelope = json.loads(blob)
            if set(envelope) != {"payload", "sha256"}:
                raise ValueError("unknown snapshot envelope")
            payload = envelope["payload"]
            if sha256(_canonical(payload).encode("ascii")).hexdigest() != envelope["sha256"]:
                raise ValueError("tampered snapshot")
            if payload["schema"] != "wsp52.whole-stream-table.v1" or set(payload) != {"schema", "experiences", "rows", "conflicts"}:
                raise ValueError("invalid snapshot schema")
            obj = cls()
            if type(payload["experiences"]) is not int or payload["experiences"] < 0:
                raise ValueError("invalid evidence count")
            for before_list, bits, after_list in payload["rows"]:
                before = tuple(before_list)
                after = None if after_list is None else tuple(after_list)
                _validate(bits, before, after)
                key = (before, bits)
                if key in obj._facts:
                    raise ValueError("duplicated snapshot key")
                obj._facts[key] = after
            for before_list, bits in payload["conflicts"]:
                key = (tuple(before_list), bits)
                _validate(bits, key[0])
                if key not in obj._facts or obj._facts[key] is not None:
                    raise ValueError("unrecognized snapshot contradiction")
                obj._conflicts.add(key)
            if any(v is None and k not in obj._conflicts for k, v in obj._facts.items()):
                raise ValueError("unrecorded contradictory fact")
            obj.action_experiences = payload["experiences"]
            if obj.snapshot() != blob:
                raise ValueError("noncanonical snapshot")
            return obj
        except (TypeError, KeyError, IndexError, json.JSONDecodeError, UnicodeEncodeError) as exc:
            raise ValueError("invalid snapshot") from exc


class ErasedControl:
    """Zero-knowledge control. Always abstains regardless of experience."""
    def __init__(self):
        self.action_experiences = 0

    def observe(self, observation):
        if observation.action_cost != 1 or observation.reset_cost != 0:
            raise ValueError("unexpected source cost")
        self.action_experiences += observation.action_cost

    def predict(self, before, acoustic_bits):
        _validate(acoustic_bits, before)
        return None

    def capacity_bits(self):
        return 0
