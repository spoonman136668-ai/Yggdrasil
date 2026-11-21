"""NUM05: opt-in, research-only, source-blind numerical causal memory.

One witnessed numeric observation, one of FIVE public actions, one actual
numeric successor observation and scalar reward. No Metahighway actor,
original source signature, CKAD binary adapter, controller, or model merge.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "yggdrasil.num05.public-numeric-consequence.v1"
SOURCE_TAG = "num05.synthetic-public-dev.v1"
MAX_ROWS = 512
OBS_DIMS = 2
ACTIONS = 5
BINS = 4
HEADS = 3


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def public_state(value):
    if (type(value) not in (tuple, list) or len(value) != 2
            or any(type(x) not in (int, float) or not math.isfinite(x)
                   or abs(x) > 10.0 for x in value)):
        raise ValueError("NUM05_PUBLIC_NUMERIC_STATE_REQUIRED")
    return tuple(float(v) for v in value)


def public_action(value):
    if type(value) is not int or not 0 <= value < ACTIONS:
        raise ValueError("NUM05_EXACT_FIVE_ACTIONS")
    return value


def region(value):
    x, y = public_state(value)
    return int(x >= 0) + 2 * int(y >= 0)


def _cell(observation, action):
    return str(region(observation)) + ":" + str(public_action(action))


def public_row(identifier, observation, action, successor, reward,
               terminated=False, truncated=False, *, source_tag=SOURCE_TAG):
    if (type(identifier) is not str or len(identifier) != 64
            or any(c not in "0123456789abcdef" for c in identifier)):
        raise ValueError("NUM05_SOURCE_EVENT_ID")
    if source_tag != SOURCE_TAG:
        raise ValueError("NUM05_UNAUTHORIZED_SOURCE_TAG")
    before = public_state(observation)
    after = public_state(successor)
    action = public_action(action)
    if (type(reward) not in (int, float) or not math.isfinite(reward)
            or abs(reward) > 10):
        raise ValueError("NUM05_PUBLIC_REWARD")
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("NUM05_TERMINAL_CLOCK")
    return {
        "id": identifier, "source_tag": SOURCE_TAG,
        "observation": list(before), "action": action,
        "successor": list(after), "reward": float(reward),
        "terminated": terminated, "truncated": truncated,
    }


def target(row):
    before, after = row["observation"], row["successor"]
    return [after[0] - before[0], after[1] - before[1], row["reward"]]


def error(pred, actual):
    return sum((a - b) ** 2 for a, b in zip(pred, actual, strict=True)) / HEADS


class Bank:
    """Five-action, four-region learned public three-output causal table."""
    def __init__(self):
        self.cells = {}

    def count(self, observation, action):
        return self.cells.get(_cell(observation, action), [0, [0.0]*HEADS])[0]

    def predict(self, observation, action):
        n, sums = self.cells.get(_cell(observation, action), [0, [0.0]*HEADS])
        return [z / (n + 1) for z in sums]

    def observe(self, row):
        key = _cell(row["observation"], row["action"])
        n, sums = self.cells.get(key, [0, [0.0]*HEADS])
        z = target(row)
        self.cells[key] = [n + 1, [sums[i] + z[i] for i in range(HEADS)]]

    def snapshot(self):
        return {key: [n, v[:]] for key, (n, v) in sorted(self.cells.items())}

    def signature(self):
        return digest(canonical(self.snapshot()))


class NumericRegimeMemory:
    """One persistent source-free numerical learner with archived regime recall.

    Predict BEFORE observe. A mode switch uses only preceding observed public
    action-consequence errors. Buffered high-error events are not assigned to
    old memory before novelty is qualified.
    """
    def __init__(self, *, single_bank=False):
        if type(single_bank) is not bool:
            raise ValueError("NUM05_ABLATION_TYPE")
        self.banks = [Bank()]
        self.active = 0
        self.pending = []
        self.rows = []
        self.seen = set()
        self.single_bank = single_bank
        self.mode_switches = []

    def forecast(self, observation, action):
        public_state(observation)
        public_action(action)
        return self.banks[self.active].predict(observation, action)

    def _flush(self, bank):
        for event in self.pending:
            self.banks[bank].observe(event)
        self.pending.clear()

    def observe(self, row):
        if (type(row) is not dict or set(row) != {
                "id", "source_tag", "observation", "action", "successor",
                "reward", "terminated", "truncated"}):
            raise ValueError("NUM05_ROW_SCHEMA")
        exact = public_row(
            row["id"], row["observation"], row["action"], row["successor"],
            row["reward"], row["terminated"], row["truncated"],
            source_tag=row["source_tag"])
        if exact != row or canonical(exact) != canonical(row):
            raise ValueError("NUM05_NONCANONICAL_ROW")
        if row["id"] in self.seen:
            raise ValueError("NUM05_DUPLICATE_OR_REORDERED_ID")
        if len(self.rows) >= MAX_ROWS:
            raise ValueError("NUM05_EVIDENCE_CAPACITY")
        current = self.banks[self.active]
        actual = target(row)
        prediction = current.predict(row["observation"], row["action"])
        current_loss = error(prediction, actual)
        if self.single_bank:
            current.observe(row)
        elif len(self.banks) == 1:
            anomaly = (len(self.rows) >= 100
                       and current.count(row["observation"], row["action"]) >= 3
                       and current_loss > 0.15)
            if anomaly:
                self.pending.append(row)
                if len(self.pending) == 3:
                    self.banks.append(Bank())
                    self.active = 1
                    self._flush(1)
                    self.mode_switches.append([len(self.rows) + 1, 1])
            else:
                self._flush(0)
                current.observe(row)
        else:
            other_idx = 1 - self.active
            other = self.banks[other_idx]
            comparable = (current.count(row["observation"], row["action"]) >= 3
                          and other.count(row["observation"], row["action"]) >= 3)
            better_other = (
                comparable
                and (current_loss - error(other.predict(row["observation"], row["action"]),
                                          actual)) > 0.08
            )
            if better_other:
                self.pending.append(row)
                if len(self.pending) == 3:
                    self.active = other_idx
                    self._flush(other_idx)
                    self.mode_switches.append([len(self.rows) + 1, other_idx])
            else:
                self._flush(self.active)
                current.observe(row)
        self.rows.append(row)
        self.seen.add(row["id"])
        return prediction

    def checkpoint(self):
        data = {
            "schema": SCHEMA,
            "source_owner_authenticated": False,
            "native_admission": False,
            "scientific_pass": False,
            "single_bank": self.single_bank,
            "active": self.active,
            "banks": [bank.snapshot() for bank in self.banks],
            "pending": self.pending,
            "mode_switches": self.mode_switches,
            "rows": self.rows,
        }
        raw = canonical(data)
        if len(raw) > 300000:
            raise ValueError("NUM05_CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, sha256):
        if (type(raw) is not bytes or type(sha256) is not str
                or digest(raw) != sha256 or len(raw) > 300000):
            raise ValueError("NUM05_CHECKPOINT_SHA")
        try:
            data = json.loads(raw)
            if (type(data) is not dict or data["schema"] != SCHEMA
                    or data["source_owner_authenticated"] is not False
                    or data["native_admission"] is not False
                    or data["scientific_pass"] is not False
                    or canonical(data) != raw):
                raise ValueError("NUM05_CHECKPOINT_FORMAT")
            restored = cls(single_bank=data["single_bank"])
            for row in data["rows"]:
                restored.observe(row)
            if restored.checkpoint() != raw:
                raise ValueError("NUM05_CHECKPOINT_REPLAY_MISMATCH")
        except (KeyError, TypeError, OverflowError, RecursionError) as exc:
            raise ValueError("NUM05_CHECKPOINT_FORMAT") from exc
        return restored

    def info(self):
        return {
            "source_owner_authenticated": False,
            "native_admission": False,
            "scientific_pass": False,
            "rows": len(self.rows),
            "bank_count": len(self.banks),
            "active": self.active,
            "old_bank_sha256": self.banks[0].signature(),
            "mode_switches": self.mode_switches[:],
            "pending": len(self.pending),
        }
