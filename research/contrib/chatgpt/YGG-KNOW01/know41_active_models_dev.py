"""KNOW41 independent mock-only candidate and strong active Bayesian comparator.

The protocol was frozen at 59d3de3be473da22471ffa66796fac6e8a1b6108.
This module has NO source-world sampler and NO native model integration.
All decisions use public c, previously selected a, and actually witnessed y.
"""
from __future__ import annotations
import json
import math
from know41_active_identifiability_dev import key, need

MAX_BYTES = 4096
HAZARDS = (1.0 / 128.0, 1.0 / 32.0, 1.0 / 8.0)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def no_duplicates(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, "DUPLICATE_KEY")
        out[k] = v
    return out


def _json(raw, allowed):
    need(type(raw) is str and len(raw) < MAX_BYTES, "COLD_BYTES")
    data = json.loads(raw, object_pairs_hook=no_duplicates)
    need(type(data) is dict and set(data) == allowed, "COLD_SCHEMA")
    need(canonical(data) == raw, "COLD_NONCANONICAL")
    return data


def _cells():
    return [[0, 0] for _ in range(16)]


def _valid_cells(cells, cap):
    return (type(cells) is list and len(cells) == 16 and
            all(type(item) is list and len(item) == 2 and
                all(type(z) is int for z in item) and
                0 <= item[1] <= item[0] <= cap for item in cells))


def _mean(cells, k):
    n, s = cells[k]
    return (s + 1.0) / (n + 2.0)


class ContradictionMemory:
    """Bounded two-bank active-memory candidate: local surprise gates B writes.

    First 64 witnessed events build protected A. Later events update a transient
    Bayesian regime belief; only sufficiently contradicted A evidence can enter B.
    A remains immutable; checkpoints preserve both banks and transient posterior.
    This is a proposed learner to FALSIFY, not a demonstrated improvement.
    """
    kind = "KNOW41_CONTRADICTION_CANDIDATE_V1"

    def __init__(self, hazard=1.0 / 32.0):
        need(type(hazard) is float and hazard in HAZARDS, "CAND_HAZARD")
        self.hazard = hazard
        self.a = _cells()
        self.b = _cells()
        self.pa = 0.97
        self.received = 0
        self.pending = None
        self.b_writes = 0

    def prob(self, c, action):
        k = key(c, action)
        if self.received < 64:
            return _mean(self.a, k)
        prior = self.pa * (1 - self.hazard) + (1 - self.pa) * self.hazard
        return prior * _mean(self.a, k) + (1 - prior) * _mean(self.b, k)

    def choose(self, t, c):
        need(type(t) is int and t == self.received and self.pending is None,
             "CAND_ORDER")
        key(c, 0)
        # Fixed, source-independent active coverage; no hidden truth is queried.
        p0, p1 = self.prob(c, 0), self.prob(c, 1)
        a = 1 if (t // 8) % 4 == 0 else int(p1 - .05 > p0)
        self.pending = [t, c, a]
        return a

    def observe(self, t, c, action, y):
        need(type(y) is int and y in (0, 1)
             and self.pending == [t, c, action], "CAND_UNWITNESSED")
        k = key(c, action)
        if self.received < 64:
            if self.a[k][0] < 12:
                self.a[k][0] += 1
                self.a[k][1] += y
        else:
            prior = self.pa * (1 - self.hazard) + (1 - self.pa) * self.hazard
            ap, bp = _mean(self.a, k), _mean(self.b, k)
            la, lb = (ap if y else 1-ap), (bp if y else 1-bp)
            den = prior * la + (1-prior) * lb
            need(den > 0, "CAND_POSTERIOR")
            self.pa = prior * la / den
            # Only actual surprise relative to A can unlock writes into B.
            if self.pa <= .2 and lb >= la and self.b[k][0] < 12:
                self.b[k][0] += 1
                self.b[k][1] += y
                self.b_writes += 1
        self.received += 1
        self.pending = None

    def checkpoint(self):
        return canonical(dict(kind=self.kind, hazard=self.hazard, a=self.a,
                              b=self.b, pa=self.pa, received=self.received,
                              b_writes=self.b_writes, pending=self.pending))

    @classmethod
    def cold(cls, raw):
        d = _json(raw, {"kind", "hazard", "a", "b", "pa",
                        "received", "b_writes", "pending"})
        need(d["kind"] == cls.kind and type(d["hazard"]) is float and
             d["hazard"] in HAZARDS and _valid_cells(d["a"], 12) and
             _valid_cells(d["b"], 12) and type(d["pa"]) is float and
             math.isfinite(d["pa"]) and 0 <= d["pa"] <= 1 and
             type(d["received"]) is int and 0 <= d["received"] <= 256 and
             type(d["b_writes"]) is int and 0 <= d["b_writes"] <= 192 and
             d["pending"] is None and
             sum(x[0] for x in d["a"]) <= 64 and
             sum(x[0] for x in d["b"]) == d["b_writes"],
             "CAND_COLD_STATE")
        result = cls(d["hazard"])
        result.a, result.b, result.pa = d["a"], d["b"], d["pa"]
        result.received, result.b_writes = d["received"], d["b_writes"]
        need(result.checkpoint() == raw, "CAND_COLD_REPLAY")
        return result


def _h_q(c, action, hypothesis):
    """Explicit four-family hypothesis class for the conventional comparator.

    These *proposed* structural hypotheses are supplied to this control
    irrespective of the actual hidden law, never an evaluator oracle label.
    Stronger prior information than the learned candidate; disclosed in scores.
    """
    key(c, action)
    need(type(hypothesis) is int and hypothesis in range(4), "BAYES_HYP")
    graph = hypothesis // 2
    theta = hypothesis % 2
    if action == 0:
        return .35
    c0, c1, c2 = c & 1, (c >> 1) & 1, (c >> 2) & 1
    m1 = c0 ^ theta
    return (.15 + .4*m1) if graph == 0 else (
        .15 + .2 * (m1 + (c1 ^ c2 ^ theta)))


def _entropy(p):
    need(0 < p < 1, "BAYES_ENTROPY")
    return -p * math.log(p) - (1-p) * math.log(1-p)


class ActiveBayesian:
    """Conventional 4-hypothesis active Bayes filter; fit-only tunable hazard.

    Action selection maximizes expected immediate net reward plus a fixed
    information-gain multiplier, not private actual-world counterfactuals.
    """
    kind = "KNOW41_ACTIVE_BAYES_CONTROL_V1"

    def __init__(self, hazard=1.0/32.0, bonus=1.0):
        need(type(hazard) is float and hazard in HAZARDS and
             type(bonus) is float and bonus in (0.0, 0.5, 1.0, 2.0),
             "BAYES_HYPER")
        self.hazard = hazard
        self.bonus = bonus
        self.weights = [0.25] * 4
        self.received = 0
        self.pending = None

    def _prior(self):
        return [(1-self.hazard)*w+self.hazard/4 for w in self.weights]

    def prob(self, c, action):
        prior = self._prior()
        return sum(w * _h_q(c, action, h) for h, w in enumerate(prior))

    def _information(self, c, action):
        prior = self._prior()
        qs = [_h_q(c, action, i) for i in range(4)]
        q = sum(w * qi for w, qi in zip(prior, qs))
        return _entropy(q) - sum(w * _entropy(qi)
                                 for w, qi in zip(prior, qs))

    def choose(self, t, c):
        need(type(t) is int and t == self.received and self.pending is None,
             "BAYES_ORDER")
        key(c, 0)
        v0 = self.prob(c, 0) + self.bonus * self._information(c, 0)
        v1 = self.prob(c, 1) - .05 + self.bonus * self._information(c, 1)
        a = int(v1 > v0)
        self.pending = [t, c, a]
        return a

    def observe(self, t, c, action, y):
        need(type(y) is int and y in (0, 1)
             and self.pending == [t, c, action], "BAYES_UNWITNESSED")
        prior = self._prior()
        weights = [p * (q if y else 1-q)
                   for h, p in enumerate(prior)
                   for q in [_h_q(c, action, h)]]
        total = sum(weights)
        need(total > 0 and math.isfinite(total), "BAYES_NORMALIZATION")
        self.weights = [w/total for w in weights]
        self.received += 1
        self.pending = None

    def checkpoint(self):
        return canonical(dict(kind=self.kind, hazard=self.hazard, bonus=self.bonus,
                              weights=self.weights, received=self.received,
                              pending=self.pending))

    @classmethod
    def cold(cls, raw):
        d = _json(raw, {"kind", "hazard", "bonus", "weights", "received", "pending"})
        need(d["kind"] == cls.kind and type(d["hazard"]) is float and
             d["hazard"] in HAZARDS and type(d["bonus"]) is float and
             d["bonus"] in (0.0, .5, 1.0, 2.0) and
             type(d["weights"]) is list and len(d["weights"]) == 4 and
             all(type(w) is float and math.isfinite(w) and 0 <= w <= 1
                 for w in d["weights"]) and
             abs(sum(d["weights"]) - 1) < 1e-12 and
             type(d["received"]) is int and 0 <= d["received"] <= 256
             and d["pending"] is None, "BAYES_COLD_STATE")
        out = cls(d["hazard"], d["bonus"])
        out.weights, out.received = d["weights"], d["received"]
        need(out.checkpoint() == raw, "BAYES_COLD_REPLAY")
        return out
