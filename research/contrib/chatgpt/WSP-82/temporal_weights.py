"""WSP82 generic temporal-feature numerical weight programming.

No private source, evaluator, seeded physics, WSP81 finite 31-mechanism
library or gradient training. A fixed *generic* public history feature bank
is searched for exact parsimonious XOR effects from continuous charged public
actions. Active output weights are explicitly compiled and cold restorable.

This is bounded feature selection, NOT unrestricted representation invention.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
from math import isfinite
import json

STATES = frozenset(product((0, 1), repeat=6))
ACTIONS = range(6)
SCHEMA = "wsp82.numeric-temporal-feature-editor.v1"
MAX_SNAPSHOT_CHARS = 60000

# Frozen generic Boolean predicate alphabet, not the source rule/offset.
FEATURES = (
    (("zero", -1, -1), ("one", -1, -1))
    + tuple(("action", a, -1) for a in ACTIONS)
    + tuple(("prior", a, -1) for a in ACTIONS)
    + tuple(("second_prior", a, -1) for a in ACTIONS)
    + (("prior_equal", -1, -1),)
    + tuple(("action_prior", a, b) for a in ACTIONS for b in ACTIONS)
    + tuple(("action_second_prior", a, b) for a in ACTIONS for b in ACTIONS)
    + tuple(("prior_pair", a, b) for a in ACTIONS for b in ACTIONS)
    + tuple(("prior_equal_action", a, -1) for a in ACTIONS)
)
COST = {
    "zero": 0, "one": 1, "action": 1, "prior": 1,
    "second_prior": 1, "prior_equal": 2,
    "action_prior": 3, "action_second_prior": 3, "prior_pair": 3,
    "prior_equal_action": 4,
}
assert len(FEATURES) == 135


def canonical(value):
    return json.dumps(value, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _valid(s, a, history):
    return (type(s) is tuple and s in STATES and
            type(a) is int and a in ACTIONS and
            type(history) in (tuple, list) and
            all(type(x) is int and x in ACTIONS for x in history))


def _relu(x):
    return max(0.0, x)


def _numeric_features(action, history):
    """Fixed ReLU Boolean gate bank; no source/learned-rule lookups."""
    a = [float(action == i) for i in ACTIONS]
    prev = [float(bool(history) and history[-1] == i) for i in ACTIONS]
    prev2 = [float(len(history) >= 2 and history[-2] == i) for i in ACTIONS]
    equal = sum(_relu(prev[i] + prev2[i] - 1.0) for i in ACTIONS)
    return (
        [0.0, 1.0] + a + prev + prev2 + [equal]
        + [_relu(a[i] + prev[j] - 1.0) for i in ACTIONS for j in ACTIONS]
        + [_relu(a[i] + prev2[j] - 1.0) for i in ACTIONS for j in ACTIONS]
        + [_relu(prev[i] + prev2[j] - 1.0) for i in ACTIONS for j in ACTIONS]
        + [_relu(equal + a[i] - 1.0) for i in ACTIONS]
    )


class PaidTemporalFeatureEditor:
    def __init__(self):
        self.current = (0,) * 6
        self.charges = 0
        self._rows = []
        self._history = []
        self._compiled = None

    def charge(self, before, action, after, action_cost=1):
        if (self._rows is None or self._history is None
                or not _valid(before, action, tuple(self._history))
                or type(after) is not tuple or after not in STATES
                or type(action_cost) is not int or action_cost != 1
                or before != self.current or self.charges >= 384
                or self._rows is None):
            raise ValueError("unpaid, invalid, noncontinuous or overbudget history")
        self._rows.append((before, action, after, tuple(self._history)))
        self._history.append(action)
        self.current = after
        self.charges += 1
        self._compiled = None

    def compile(self):
        if self._rows is None or self.charges != 384:
            raise ValueError("only compile after exactly 384 paid public actions")
        signatures = [0] * len(FEATURES)
        targets = [0] * 6
        for index, (before, action, after, history) in enumerate(self._rows):
            gates = _numeric_features(action, history)
            for j, v in enumerate(gates):
                if v >= 0.5:
                    signatures[j] |= 1 << index
            for bit in range(6):
                residual = before[bit] ^ after[bit] ^ int(action == bit)
                if residual:
                    targets[bit] |= 1 << index
        solutions = []
        for target in targets:
            matches = [j for j, sig in enumerate(signatures) if sig == target]
            if not matches:
                # No causal feature covers this bit. Abstain instead of
                # retrofitting outcomes with an invented rule.
                solutions.append([])
                continue
            least = min(COST[FEATURES[j][0]] for j in matches)
            matches = [j for j in matches if COST[FEATURES[j][0]] == least]
            solutions.append(matches)
        if any(not picks for picks in solutions):
            # Report a capacity failure; a new structural mechanism cannot
            # be silently invented after outcome freeze.
            raise ValueError("generic temporal feature bank cannot fit paid history")
        matrices = []
        for choices in solutions:
            models = []
            for picked in choices:
                row = [0.0] * len(FEATURES)
                row[picked] = 1.0
                models.append(row)
            matrices.append(models)
        self._compiled = {
            "schema": SCHEMA,
            "charges": self.charges,
            "feature_count": len(FEATURES),
            "weights": matrices,
        }
        return {
            "paid_actions": self.charges,
            "numeric_feature_gates": len(FEATURES),
            "active_output_weight_rows": sum(len(m) for m in matrices),
            "nonconstant_temporal_weight_selected": any(
                any(j >= 2 + 6 + 6 + 6 for j in picks) for picks in solutions),
            "unresolved_minimum_complexity_solutions": [
                len(picks) for picks in solutions],
        }

    def predict(self, state, action, history=()):
        if not _valid(state, action, history) or self._compiled is None:
            raise ValueError("invalid or uncompiled numeric temporal query")
        gates = _numeric_features(action, history)
        result = []
        for bit, choices in enumerate(self._compiled["weights"]):
            outcomes = set()
            for row in choices:
                effect = sum(w * v for w, v in zip(row, gates))
                if not isfinite(effect) or effect not in (0.0, 1.0):
                    raise ArithmeticError("non-Boolean ReLU readout")
                next_bit = float(state[bit]) + float(action == bit) + effect
                outcomes.add(int(next_bit) % 2)
            if len(outcomes) != 1:
                return None
            result.append(next(iter(outcomes)))
        return tuple(result)

    def snapshot(self):
        if self._compiled is None:
            raise ValueError("model not compiled")
        obj = self._compiled
        checksum = sha256(canonical(obj).encode("ascii")).hexdigest()
        encoded = canonical({"payload": obj, "sha256": checksum})
        if len(encoded) > MAX_SNAPSHOT_CHARS:
            raise ValueError("numerical payload exceeded bound")
        return encoded

    @classmethod
    def restore(cls, encoded):
        if type(encoded) is not str or len(encoded) > MAX_SNAPSHOT_CHARS:
            raise ValueError("invalid numeric snapshot")
        try:
            envelope = json.loads(encoded)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("snapshot envelope invalid")
            payload = envelope["payload"]
            if (type(payload) is not dict or set(payload) !=
                    {"schema", "charges", "feature_count", "weights"}
                    or payload["schema"] != SCHEMA
                    or payload["charges"] != 384
                    or payload["feature_count"] != len(FEATURES)
                    or type(payload["weights"]) is not list
                    or len(payload["weights"]) != 6):
                raise ValueError("invalid cold-model schema")
            for selections in payload["weights"]:
                if (type(selections) is not list or not selections
                        or len(selections) > len(FEATURES)):
                    raise ValueError("missing confidence weight choices")
                for row in selections:
                    if (type(row) is not list or len(row) != len(FEATURES)
                            or any(type(w) not in (int, float) or w not in (0, 1)
                                   for w in row) or sum(row) != 1):
                        raise ValueError("invalid numerical feature weights")
            if sha256(canonical(payload).encode("ascii")).hexdigest() != envelope["sha256"]:
                raise ValueError("tampered snapshot")
            model = cls()
            model._rows = None
            model._history = None
            model.current = None
            model.charges = 384
            model._compiled = payload
            if model.snapshot() != encoded:
                raise ValueError("noncanonical cold snapshot")
            return model
        except (TypeError, ValueError, KeyError, OverflowError) as exc:
            raise ValueError("corrupted frozen numeric weights") from exc
