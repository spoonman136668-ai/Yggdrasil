"""FCR03 source-free, stage-separated affine-law archive. Research only.

Forecasts depend only on previously witnessed public bits. No phase IDs,
source actions, native learner mutation, or scientific checkpoint promotion.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque

SCHEMA = "yggdrasil.fcr03.stage-law-recall.dev.v1"
CONFIDENCE_LOW = 1 / 16
CONFIDENCE_HIGH = 15 / 16
INITIAL_SUPPORT = 12
WINDOW = 8
ALARM_ERRORS = 4
COOLDOWN = 8
MAX_ARCHIVE = 3
MAX_EPISODES = 368


def require(condition, code):
    if not condition:
        raise ValueError("FCR03_" + code)


def bit(value):
    require(type(value) is int and value in (0, 1), "BIT")
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def laws(n):
    return tuple((mask, bias) for mask in range(1 << n) for bias in (0, 1))


def evaluate(law, features):
    mask, bias = law
    packed = sum(bit(value) << index for index, value in enumerate(features))
    return ((packed & mask).bit_count() & 1) ^ bias


def best_law(history, n):
    require(len(history) > 0, "FIT_EMPTY")
    return min(laws(n), key=lambda law: (
        sum(evaluate(law, x) != y for x, y in history),
        law[0].bit_count(), law[0], law[1],
    ))


class Stage:
    """Up to three frozen law candidates plus one active law, per outcome head."""

    def __init__(self, n):
        require(n in (2, 4), "HEAD_DIMENSIONS")
        self.n = n
        self.history = []
        self.current = None
        self.archive = []
        self.switch_index = 0
        self.active_since = 0
        self.switches = 0
        self.recalls = 0
        self.new_laws = 0
        self.alarms = 0

    def predict(self, features):
        require(type(features) is tuple and len(features) == self.n,
                "FEATURES")
        for v in features:
            bit(v)
        if self.current is None:
            return 0.5
        return CONFIDENCE_HIGH if evaluate(self.current, features) else CONFIDENCE_LOW

    def observe(self, features, outcome):
        self.predict(features)  # validate before mutation
        y = bit(outcome)
        self.history.append((features, y))
        size = len(self.history)
        require(size <= MAX_EPISODES, "EPISODE_CAP")
        if self.current is None:
            if size == INITIAL_SUPPORT:
                self.current = best_law(self.history, self.n)
                self.switch_index = size
                self.new_laws += 1
            return
        if size - self.switch_index < COOLDOWN:
            return
        recent = self.history[-WINDOW:]
        active_errors = sum(evaluate(self.current, x) != t for x, t in recent)
        if active_errors < ALARM_ERRORS:
            return
        self.alarms += 1
        proposal = best_law(recent, self.n)
        choices = self.archive + [proposal]
        def score(law):
            return sum(evaluate(law, x) != t for x, t in recent)
        # Stored archived laws win ties against fresh fits, never phase-ID lookup.
        selected = min(choices, key=lambda law: (score(law),
                              0 if law in self.archive else 1,
                              self.archive.index(law) if law in self.archive else 99,
                              law[0], law[1]))
        if selected == self.current or score(selected) + 2 > active_errors:
            return
        former = self.current
        if size - self.active_since >= INITIAL_SUPPORT and former not in self.archive:
            self.archive.append(former)
        self.archive = self.archive[-MAX_ARCHIVE:]
        if selected in self.archive:
            self.archive.remove(selected)
            self.recalls += 1
        else:
            self.new_laws += 1
        self.current = selected
        self.switch_index = size
        self.active_since = size
        self.switches += 1

    def summary(self):
        return {"dimensions": self.n,
                "current": list(self.current) if self.current is not None else None,
                "archive": [list(x) for x in self.archive],
                "switch_index": self.switch_index,
                "active_since": self.active_since,
                "switches": self.switches,
                "recalls": self.recalls,
                "new_laws": self.new_laws,
                "alarms": self.alarms,
                "history_hash": digest(canonical(self.history))}


class StagewiseRecall:
    def __init__(self):
        self.transition = Stage(2)
        self.reward = Stage(4)
        self.ledger = []
        self.ids = set()

    def transition_forecast(self, context, x1):
        return self.transition.predict((context, x1))

    def reward_forecast(self, context, x1, s2, x2):
        return self.reward.predict((context, x1, s2, x2))

    def admit_fixture(self, identifier, context, x1, s2, x2, y):
        require(type(identifier) is str and len(identifier) == 64
                and set(identifier) <= set("0123456789abcdef"), "WITNESS_ID")
        values = tuple(bit(v) for v in (context, x1, s2, x2, y))
        require(identifier not in self.ids, "DUPLICATE_OR_CONFLICT")
        require(len(self.ledger) < MAX_EPISODES, "EPISODE_CAP")
        # External native source admission is NOT established by fixture acceptance.
        self.transition.observe(values[:2], values[2])
        self.reward.observe(values[:4], values[4])
        self.ledger.append((identifier, *values))
        self.ids.add(identifier)

    def checkpoint(self, source_sha):
        require(type(source_sha) is str and len(source_sha) == 40
                and set(source_sha) <= set("0123456789abcdef"), "SOURCE_SHA")
        return canonical({"schema": SCHEMA, "source_sha": source_sha,
                          "event_count": len(self.ledger),
                          "ledger_sha256": digest(canonical(self.ledger)),
                          "transition": self.transition.summary(),
                          "reward": self.reward.summary(),
                          "source_free_dev": True,
                          "scientific_pass": False,
                          "accepted_native": False})

    @classmethod
    def restore(cls, evidence, raw, expected_sha256, source_sha):
        require(type(raw) is bytes and digest(raw) == expected_sha256,
                "CHECKPOINT_PIN")
        def no_duplicates(pairs):
            seen = {}
            for k, v in pairs:
                require(k not in seen, "DUPLICATE_JSON_KEY")
                seen[k] = v
            return seen
        try:
            value = json.loads(raw.decode("ascii"), object_pairs_hook=no_duplicates)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("FCR03_CHECKPOINT_JSON") from exc
        require(type(value) is dict and value.get("schema") == SCHEMA and
                value.get("source_sha") == source_sha and
                value.get("source_free_dev") is True and
                value.get("scientific_pass") is False and
                value.get("accepted_native") is False and
                canonical(value) == raw, "CHECKPOINT_SCHEMA")
        require(type(evidence) is list and len(evidence) == value.get("event_count")
                and digest(canonical(evidence)) == value.get("ledger_sha256"),
                "EVIDENCE_DRIFT")
        candidate = cls()
        for event in evidence:
            require(type(event) in (tuple, list) and len(event) == 6,
                    "LEDGER_ROW")
            candidate.admit_fixture(*event)
        require(candidate.checkpoint(source_sha) == raw, "REPLAY_PARITY")
        return candidate
