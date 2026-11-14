"""AAI-10A frozen non-token operator association research learners.

All methods see only PUBLIC (x, mediators, goal, reward, action count) rows.
No model receives a hidden law name or formula. Scientific first-use disabled.
Model/controls compare equal evidence and use the SAME action planner.
"""
from __future__ import annotations

from itertools import combinations
import json
import math
from pathlib import Path
import sys

# Reuse the exact admitted AAI-10P benchmark; never copy/modify its laws.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'AAI-10P'))
from benchmark import ACTIONS, COST, require_bits

OPS = ("xor", "and", "or")
GRAMMAR = tuple((op, i, j) for op in OPS for i, j in combinations(range(3), 2))
assert len(GRAMMAR) == 9
P_OK = 0.90
P_ERR = 0.10
LOG_MARGIN = math.log(4)
MAX_SLOT_ROWS = 96


def canonical(state):
    return json.dumps(state, separators=(",", ":"), sort_keys=True, allow_nan=False)


def visible(row):
    """Reject extra keys, hidden-label access and malformed observations."""
    if type(row) is not dict or set(row) != {
        "x", "mediators", "goal", "reward", "actions_taken"
    }:
        raise ValueError("model input must be exactly public initial/step state")
    x = require_bits(row["x"], 3)
    m = require_bits(row["mediators"], 2)
    require_bits(row["goal"], 2)
    if type(row["actions_taken"]) is not int or row["actions_taken"] not in (0, 1, 2):
        raise ValueError("bad action count")
    if type(row["reward"]) not in (int, float) or not math.isfinite(row["reward"]):
        raise ValueError("invalid public reward")
    return (x, m)


def pattern(hypothesis, x):
    op, i, j = hypothesis
    a, b = x[i], x[j]
    if op == "xor":
        return a ^ b
    if op == "and":
        return a & b
    if op == "or":
        return a | b
    raise ValueError("unrecognized operator")


def grammar_posterior(samples, output, bias=None):
    """Public-evidence Bernoulli-likelihood posterior on same shared grammar."""
    bias = bias or {"xor": 1.0, "and": 1.0, "or": 1.0}
    logs = [math.log(bias[h[0]]) for h in GRAMMAR]
    for x, m in samples:
        for idx, hypothesis in enumerate(GRAMMAR):
            logs[idx] += math.log(P_OK if pattern(hypothesis, x) == m[output] else P_ERR)
    peak = max(logs)
    scaled = [math.exp(v - peak) for v in logs]
    mass = sum(scaled)
    return [q / mass for q in scaled]


def grammar_predict(samples, x, bias=None):
    return tuple(
        round(sum(weight * pattern(h, x) for weight, h in
            zip(grammar_posterior(samples, output, bias), GRAMMAR)), 12)
        for output in (0, 1)
    )


def sample_log_probability(samples, batch, bias=None):
    """Only candidate-public-event probabilities, never law oracle probabilities."""
    loss = 0.0
    for x, m in batch:
        pred = grammar_predict(samples, x, bias)
        for out in range(2):
            p = min(1 - 1e-6, max(1e-6, pred[out]))
            loss += math.log(p if m[out] else 1.0 - p)
    return loss


def expected_reward(probs, goal, n):
    return sum(p if g else 1.0 - p for p, g in zip(probs, goal)) - COST * n


def do_x(x, action):
    i, b = action
    out = list(x)
    out[i] = b
    return tuple(out)


def plan(model, row, steps=2):
    """Single fair deterministic planning method for EVERY learner.

    Select an optional STOP or the first action of an exhaustive two-step
    action pair using predicted mediator outcomes. First intervention's PUBLIC
    consequence may be learned; replan for the second action.
    """
    x, _ = visible(row)
    goal = tuple(row["goal"])
    spent = row["actions_taken"]
    steps = min(steps, 2 - spent)
    if steps < 1:
        return None
    current = expected_reward(model.predict(x), goal, spent)
    best = (current, -1, -1)  # score, negative first index, negative second
    choice = None
    for i, first in enumerate(ACTIONS):
        x1 = do_x(x, first)
        v1 = expected_reward(model.predict(x1), goal, spent + 1)
        candidate = (v1, -i, 0)
        if candidate > best:
            best, choice = candidate, first
        if steps > 1:
            for j, second in enumerate(ACTIONS):
                x2 = do_x(x1, second)
                v2 = expected_reward(model.predict(x2), goal, spent + 2)
                candidate = (v2, -i, -j)
                if candidate > best:
                    best, choice = candidate, first
    return choice


class Learner:
    label = "base"
    def learn(self, row):
        raise NotImplementedError
    def predict(self, x):
        raise NotImplementedError
    def state(self):
        raise NotImplementedError
    def choose(self, row):
        return plan(self, row)


class GrammarWindow(Learner):
    label = "symbolic_window"
    def __init__(self, limit=None):
        self.limit = limit
        self.samples = []
    def learn(self, row):
        self.samples.append(visible(row))
        if self.limit is not None:
            self.samples = self.samples[-self.limit:]
    def predict(self, x):
        return grammar_predict(self.samples, require_bits(x, 3))
    def state(self):
        return {"type": "grammar", "limit": self.limit,
                "samples": [[list(x), list(m)] for x, m in self.samples]}


class Tabular(Learner):
    label = "tabular"
    def __init__(self, limit=None):
        self.limit = limit
        self.samples = []
    def learn(self, row):
        self.samples.append(visible(row))
        if self.limit is not None:
            self.samples = self.samples[-self.limit:]
    def predict(self, x):
        x = require_bits(x, 3)
        matching = [m for xi, m in self.samples if xi == x]
        return tuple((1 + sum(m[o] for m in matching)) / (2 + len(matching))
                     for o in (0, 1))
    def state(self):
        return {"type": "tabular", "limit": self.limit,
                "samples": [[list(x), list(m)] for x, m in self.samples]}


def features(x):
    x0, x1, x2 = require_bits(x, 3)
    return (1., float(x0), float(x1), float(x2),
            float(x0*x1), float(x0*x2), float(x1*x2),
            float(x0*x1*x2))


class LogisticInteractions(Learner):
    """Conventional 1200-epoch full-batch logistic, all binary monomials."""
    label = "logistic_interactions"
    def __init__(self):
        self.samples = []
        self.weights = None
    def learn(self, row):
        self.samples.append(visible(row))
        self.weights = None
    def _fit(self):
        if self.weights is not None:
            return
        weights = [[0.] * 8 for _ in range(2)]
        n = len(self.samples)
        if n:
            rows = [(features(x), m) for x, m in self.samples]
            for _ in range(1200):
                gradients = [[0.] * 8 for _ in range(2)]
                for feats, m in rows:
                    for o in (0, 1):
                        z = sum(v * w for v, w in zip(feats, weights[o]))
                        z = max(-35., min(35., z))
                        err = 1. / (1. + math.exp(-z)) - m[o]
                        for j in range(8):
                            gradients[o][j] += err * feats[j]
                for o in (0, 1):
                    for j in range(8):
                        w = weights[o][j]
                        # Fixed precision prevents cross-OS libm drift in
                        # 1200-epoch conventional-control checkpoints.
                        weights[o][j] = round(w - 0.20 * (gradients[o][j] / n +
                                            (0.01 * w if j else 0.)), 12)
        self.weights = weights
    def predict(self, x):
        self._fit()
        feats = features(x)
        return tuple(round(1. / (1. + math.exp(-max(-35., min(35., sum(
            a*b for a, b in zip(row, feats)))))), 12) for row in self.weights)
    def state(self):
        self._fit()
        return {"type": "logistic", "samples": [[list(x), list(m)]
                                              for x, m in self.samples],
                "weights": self.weights, "epochs": 1200}


class ProtectedOperatorBank(Learner):
    """Frozen three-slot public-evidence bank, two-observation switch gate."""
    label = "candidate"
    def __init__(self, max_slots=3, reuse=True):
        if max_slots not in (1, 2, 3):
            raise ValueError("approved capacities are 1, 2 and 3")
        self.max_slots = max_slots
        self.reuse = bool(reuse) and max_slots > 1
        self.slots = [{"id": 0, "samples": []}]
        self.active_id = 0
        self.next_id = 1
        self.scratch = []
        self.retrievals = 0

    def active(self):
        return next(s for s in self.slots if s["id"] == self.active_id)

    def _prior(self, slot):
        if not self.reuse:
            return None
        # Operator reuse comes ONLY from previously experienced PUBLIC evidence.
        # Never consults a hidden law identity or simulator equations.
        result = {op: 1. for op in OPS}
        for other in self.slots:
            if other["id"] == slot["id"] or len(other["samples"]) < 4:
                continue
            for output in (0, 1):
                post = grammar_posterior(other["samples"], output)
                best = max(range(len(GRAMMAR)), key=lambda i: post[i])
                result[GRAMMAR[best][0]] = 2.
        return result

    def _likelihood(self, slot, batch):
        return sample_log_probability(slot["samples"], batch, self._prior(slot))

    def learn(self, row):
        sample = visible(row)
        self.scratch.append(sample)
        if len(self.scratch) != 2:
            return
        batch = tuple(self.scratch)
        active = self.active()
        score = self._likelihood(active, batch)
        others = [slot for slot in self.slots if slot["id"] != self.active_id]
        switched = False
        if others:
            target = max(others, key=lambda slot: self._likelihood(slot, batch))
            if self._likelihood(target, batch) >= score + LOG_MARGIN:
                self.active_id = target["id"]
                self.retrievals += 1
                active = target
                switched = True
        # Never create a novel slot in the same batch as a successful recall.
        if not switched and len(self.slots) < self.max_slots:
            current_score = self._likelihood(active, batch)
            uniform_score = 4 * math.log(0.5)
            if uniform_score >= current_score + LOG_MARGIN:
                active = {"id": self.next_id, "samples": []}
                self.next_id += 1
                self.slots.append(active)
                self.active_id = active["id"]
        active["samples"].extend(batch)
        active["samples"] = active["samples"][-MAX_SLOT_ROWS:]
        self.scratch.clear()

    def predict(self, x):
        slot = self.active()
        return grammar_predict(slot["samples"], require_bits(x, 3), self._prior(slot))
    def state(self):
        return {"type": "bank", "max_slots": self.max_slots, "reuse": self.reuse,
                "slots": [{"id": s["id"],
                           "samples": [[list(x), list(m)] for x, m in s["samples"]]}
                          for s in self.slots],
                "active_id": self.active_id, "next_id": self.next_id,
                "scratch": [[list(x), list(m)] for x, m in self.scratch],
                "retrievals": self.retrievals}


class ConventionalSegmentBank(ProtectedOperatorBank):
    """Two-slot conventional hazard-cost change-point comparator, no reuse."""
    label = "symbolic_bank"
    def __init__(self):
        super().__init__(2, False)
    def learn(self, row):
        # No retained grammar-operator prior. Use hazard 1/12 threshold ln(11).
        # Separate two active-state segments only (max 2 slots).
        sample = visible(row)
        self.scratch.append(sample)
        if len(self.scratch) < 2:
            return
        batch = tuple(self.scratch)
        a = self.active()
        score = self._likelihood(a, batch)
        options = [s for s in self.slots if s["id"] != self.active_id]
        if options:
            old = max(options, key=lambda s: self._likelihood(s, batch))
            if self._likelihood(old, batch) >= score + math.log(11):
                self.active_id = old["id"]
                self.retrievals += 1
                a = old
        if (len(self.slots) < 2 and
            4*math.log(0.5) >= self._likelihood(a, batch) + math.log(11)):
            a = {"id": self.next_id, "samples": []}
            self.next_id += 1
            self.slots.append(a)
            self.active_id = a["id"]
        a["samples"].extend(batch)
        a["samples"] = a["samples"][-MAX_SLOT_ROWS:]
        self.scratch.clear()
    def state(self):
        result = super().state()
        result["type"] = "segment_bank"
        result["hazard"] = 1/12
        return result


class Reactive(Learner):
    label = "reactive"
    def learn(self, row):
        visible(row)
    def predict(self, x):
        require_bits(x, 3)
        return (0.5, 0.5)
    def state(self):
        return {"type": "reactive"}


NAMES = ("candidate", "symbolic_all", "symbolic_recent8",
         "symbolic_recent16", "tabular_recent16", "tabular_all",
         "logistic_interactions", "symbolic_bank", "reactive", "one_slot")
MATCHED = tuple(n for n in NAMES if n not in ("candidate", "one_slot", "reactive"))


def create(name):
    constructors = {
        "candidate": lambda: ProtectedOperatorBank(3, True),
        "symbolic_all": lambda: GrammarWindow(),
        "symbolic_recent8": lambda: GrammarWindow(8),
        "symbolic_recent16": lambda: GrammarWindow(16),
        "tabular_recent16": lambda: Tabular(16),
        "tabular_all": lambda: Tabular(),
        "logistic_interactions": LogisticInteractions,
        "symbolic_bank": ConventionalSegmentBank,
        "reactive": Reactive,
        "one_slot": lambda: ProtectedOperatorBank(1, False),
    }
    if name not in constructors:
        raise ValueError("unregistered learner")
    return constructors[name]()


def checkpoint(models):
    return {name: canonical(model.state()) for name, model in models.items()}


def cold_restore(saved):
    result = {}
    for name, state in saved.items():
        model = create(name)
        s = json.loads(state)
        if canonical(s) != state:
            raise ValueError("checkpoint not canonical")
        if s["type"] in ("grammar", "tabular"):
            model.samples = [(require_bits(x, 3), require_bits(m, 2))
                             for x, m in s["samples"]]
            if model.limit != s["limit"]:
                raise ValueError("window mismatch")
        elif s["type"] == "logistic":
            model.samples = [(require_bits(x, 3), require_bits(m, 2))
                             for x, m in s["samples"]]
            model.weights = s["weights"]
            if s["epochs"] != 1200 or len(model.weights) != 2:
                raise ValueError("bad logistic checkpoint")
        elif s["type"] in ("bank", "segment_bank"):
            model.slots = [
                {"id": slot["id"],
                 "samples": [(require_bits(x, 3), require_bits(m, 2))
                             for x, m in slot["samples"]]}
                for slot in s["slots"]
            ]
            model.max_slots = s["max_slots"]
            model.reuse = s["reuse"]
            model.active_id = s["active_id"]
            model.next_id = s["next_id"]
            model.scratch = [(require_bits(x, 3), require_bits(m, 2))
                             for x, m in s["scratch"]]
            model.retrievals = s["retrievals"]
            if len(model.slots) > model.max_slots or len(model.scratch) > 1:
                raise ValueError("bad bank checkpoint")
        elif s["type"] != "reactive":
            raise ValueError("unknown checkpoint kind")
        if canonical(model.state()) != state:
            raise ValueError("checkpoint restoration changed bytes")
        result[name] = model
    return result
