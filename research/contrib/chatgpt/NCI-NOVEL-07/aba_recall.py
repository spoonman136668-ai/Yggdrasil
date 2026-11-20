"""NCI07 source-free engineering prototype for unsignaled same-address A/B/A.

No original-world outcomes, oracle context, phase marker, reset, or protected seeds.
The optional fixture in tests is hand-authored engineering-only, not science.
"""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import json

from protocol_guard import AuditError, canonical_public_tape


class BoundedCausalRecall:
    """Two learned empirical action-outcome slots with buffered mismatch routing.

    Slot identities are allocated by public observation order, not source labels.
    The transition detector has fixed developer settings (2 incompatible witnesses,
    each predicted likelihood < 1/4). This is an explicit mechanism sketch, not
    autonomous structural learning and not known to beat change-point controls.
    """

    MAGIC = b"NCI07A1:"
    MAX_COUNT = 4095
    MAX_SLOTS = 2

    def __init__(self):
        self.slots = [[[0, 0], [0, 0]]]
        self.active = 0
        self.pending = []
        self.transitions = 0

    @staticmethod
    def _bit(value):
        if type(value) is not int or value not in (0, 1):
            raise AuditError("NCI07_INVALID_BIT")
        return value

    def _p(self, slot, action):
        fail, success = self.slots[slot][action]
        return (success + 1) / (fail + success + 2)

    def predict(self, action, observation=0):
        self._bit(action)
        if type(observation) is not int or not 0 <= observation <= 255:
            raise AuditError("NCI07_INVALID_OBSERVATION")
        return self._p(self.active, action)

    def choose(self, observation=0):
        p0, p1 = self.predict(0, observation), self.predict(1, observation)
        return None if abs(p0 - p1) < 1e-12 else int(p1 > p0)

    def retained_predict(self, slot, action):
        self._bit(action)
        if type(slot) is not int or not 0 <= slot < len(self.slots):
            raise AuditError("NCI07_UNKNOWN_SLOT")
        return self._p(slot, action)

    def _apply(self, slot, action, outcome):
        counts = self.slots[slot][action]
        counts[1 if outcome else 0] = min(self.MAX_COUNT, counts[1 if outcome else 0] + 1)

    def observe(self, row):
        # A source label/phase/reset/counterfactual never enters the learner.
        canonical_public_tape([row])
        action, outcome = row["action"], row["outcome"]
        likelihood = self.predict(action, row["observation"])
        likelihood = likelihood if outcome else 1 - likelihood
        if likelihood < 0.25:
            self.pending.append((action, outcome))
            if len(self.pending) < 2:
                return
            # On a public contradiction, reuse a previously formed slot if it
            # already predicts the pending witnesses better; otherwise allocate.
            candidates = [i for i in range(len(self.slots)) if i != self.active]
            def score(slot):
                result = 1.0
                for a, y in self.pending:
                    p = self._p(slot, a)
                    result *= p if y else 1 - p
                return result
            current = score(self.active)
            alternative = max(candidates, key=score) if candidates else None
            if alternative is not None and score(alternative) > current:
                self.active = alternative
                self.transitions += 1
            elif alternative is None and len(self.slots) < self.MAX_SLOTS:
                self.active = len(self.slots)
                self.slots.append([[0, 0], [0, 0]])
                self.transitions += 1
            # If both slots are present, but neither beats the active one,
            # do not overwrite retained knowledge or invent a third context.
            for a, y in self.pending:
                self._apply(self.active, a, y)
            self.pending.clear()
        else:
            # Pending witnesses are attributed to the current slot only if
            # the later observation supports continuing in the same context.
            for a, y in self.pending:
                self._apply(self.active, a, y)
            self.pending.clear()
            self._apply(self.active, action, outcome)

    def snapshot(self):
        raw = json.dumps({"slots": self.slots, "active": self.active,
                          "pending": self.pending, "transitions": self.transitions},
                         sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
        return self.MAGIC + raw + b":" + sha256(self.MAGIC + raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls, data):
        if type(data) is not bytes or not data.startswith(cls.MAGIC):
            raise AuditError("NCI07_CHECKPOINT_REJECTED")
        try:
            raw, digest = data[len(cls.MAGIC):].rsplit(b":", 1)
            if sha256(cls.MAGIC + raw).hexdigest().encode("ascii") != digest:
                raise AuditError("NCI07_CHECKPOINT_DIGEST_MISMATCH")
            d = json.loads(raw)
            if set(d) != {"slots", "active", "pending", "transitions"}:
                raise ValueError()
            if type(d["slots"]) is not list or not 1 <= len(d["slots"]) <= cls.MAX_SLOTS:
                raise ValueError()
            for slot in d["slots"]:
                if (type(slot) is not list or len(slot) != 2 or
                        any(type(arm) is not list or len(arm) != 2 or
                            any(type(c) is not int or not 0 <= c <= cls.MAX_COUNT for c in arm)
                            for arm in slot)):
                    raise ValueError()
            if type(d["active"]) is not int or not 0 <= d["active"] < len(d["slots"]):
                raise ValueError()
            if type(d["transitions"]) is not int or d["transitions"] < 0:
                raise ValueError()
            if type(d["pending"]) is not list or len(d["pending"]) > 1:
                raise ValueError()
            for pair in d["pending"]:
                if type(pair) is not list or len(pair) != 2 or any(type(x) is not int or x not in (0, 1) for x in pair):
                    raise ValueError()
        except (ValueError, TypeError, UnicodeError, KeyError) as exc:
            raise AuditError("NCI07_CHECKPOINT_REJECTED") from exc
        result = cls()
        result.slots, result.active, result.pending, result.transitions = (
            d["slots"], d["active"], [tuple(x) for x in d["pending"]], d["transitions"])
        if result.snapshot() != data:
            raise AuditError("NCI07_CHECKPOINT_REJECTED")
        return result


class ExactGridSwitchBayes:
    """Independently specified 4-state Bayesian HMM with fixed emission grid.

    Emissions enumerate all pairs of (0.1, 0.9) public action success rates;
    prior is uniform and switch probability is fixed at 0.08, including the
    current state. Posterior is updated from the entire public tape recursively.
    The model is a strong *specified-grid* comparator, not fitted general-world
    unknown emissions; future science needs a fully fitted change-point model.
    """

    def __init__(self, hazard=0.08):
        if type(hazard) is not float or not 0.0 <= hazard <= 1.0:
            raise AuditError("NCI07_HAZARD_INVALID")
        self.hazard = hazard
        self.laws = ((0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9))
        self.posterior = [0.25] * 4
        self.witnesses = 0

    def _prior(self):
        return [(1.0 - self.hazard) * p + self.hazard / 4.0 for p in self.posterior]

    def predict(self, action, observation=0):
        BoundedCausalRecall._bit(action)
        if type(observation) is not int or not 0 <= observation <= 255:
            raise AuditError("NCI07_INVALID_OBSERVATION")
        prior = self._prior()
        return sum(prior[i] * self.laws[i][action] for i in range(4))

    def choose(self, observation=0):
        a,b = self.predict(0, observation), self.predict(1, observation)
        return None if abs(a-b) < 1e-12 else int(b > a)

    def observe(self, row):
        canonical_public_tape([row])
        action, outcome = row["action"], row["outcome"]
        prior = self._prior()
        terms = [prior[i] * (self.laws[i][action] if outcome else 1 - self.laws[i][action])
                 for i in range(4)]
        normalizer = sum(terms)
        if normalizer <= 0:
            raise AuditError("NCI07_BAYES_INVALID_EVIDENCE")
        self.posterior = [p / normalizer for p in terms]
        self.witnesses += 1


class WindowBetaControl:
    """Conventional recency or full-history beta-Bernoulli control."""

    def __init__(self, window=None):
        if window is not None and (type(window) is not int or window <= 0):
            raise AuditError("NCI07_WINDOW_INVALID")
        self.window = window
        self.tape = deque(maxlen=window)

    def predict(self, action, observation=0):
        BoundedCausalRecall._bit(action)
        if type(observation) is not int or not 0 <= observation <= 255:
            raise AuditError("NCI07_INVALID_OBSERVATION")
        observations = [y for a, y in self.tape if a == action]
        return (1 + sum(observations)) / (2 + len(observations))

    def choose(self, observation=0):
        a,b = self.predict(0, observation), self.predict(1, observation)
        return None if abs(a-b) < 1e-12 else int(b > a)

    def observe(self, row):
        canonical_public_tape([row])
        self.tape.append((row["action"], row["outcome"]))


class EpisodicTwoWindowControl:
    """Independent public-only episodic case matching with two fixed windows.

    Unlike BoundedCausalRecall, stores complete public cases and does not
    allocate probability-table slots. Selects whichever of first/last eight
    public cases best predicts the most recent two cases, without phase labels.
    """

    def __init__(self, window=8):
        if type(window) is not int or window < 2:
            raise AuditError("NCI07_EPISODIC_WINDOW_INVALID")
        self.window = window
        self.tape = []

    def _windows(self):
        if len(self.tape) <= self.window:
            return [self.tape]
        return [self.tape[:self.window], self.tape[-self.window:]]

    def _selected(self):
        windows = self._windows()
        if len(windows) == 1 or len(self.tape) < 2:
            return windows[-1]
        recent = self.tape[-2:]
        def score(win):
            loss = 0.0
            for a,y in recent:
                ys = [z for x,z in win if a == x]
                p = (sum(ys) + 1) / (len(ys) + 2)
                loss += (p-y)**2
            return loss
        return min(windows, key=score)

    def predict(self, action, observation=0):
        BoundedCausalRecall._bit(action)
        if type(observation) is not int or not 0 <= observation <= 255:
            raise AuditError("NCI07_INVALID_OBSERVATION")
        ys = [y for a,y in self._selected() if a == action]
        return (sum(ys)+1)/(len(ys)+2)

    def choose(self, observation=0):
        a,b = self.predict(0, observation), self.predict(1, observation)
        return None if abs(a-b) < 1e-12 else int(b > a)

    def observe(self, row):
        canonical_public_tape([row])
        self.tape.append((row["action"], row["outcome"]))
