"""WSP80 fixed-capacity numerical ReLU controls from genuinely charged rows.

Source-blind WSP79-equivalent degree<=3 and always-degree4 alternatives.
All sparse search is TRAINING ONLY. Cold restored inference uses exclusively
numeric ReLU matrices and numeric confidence detectors, never a solver, raw
ledger, source generator or private evaluator labels.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math

from controls import paid_rows
from independent_symbolic import _ACTIONS, _HIGH, _LOW, _STATES, _solve

SCHEMA = "wsp80.fixed-numerical-sparse-control.v1"
MAX_SNAPSHOT_BYTES = 1100000
MODES = {"fixed_degree3": _LOW, "always_degree4": _HIGH}


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _relu(value):
    return max(0.0, value)


def _input(state, action):
    if (type(state) is not tuple or state not in _STATES
            or type(action) is not int or action not in _ACTIONS):
        raise ValueError("invalid public query")
    return [float(x) for x in state] + [float(a == action) for a in _ACTIONS]


def _confidence_detector(state, action):
    weights = [float(1 if b else -1) for b in state]
    weights += [float(a == action) for a in _ACTIONS]
    return weights, float(sum(1 for b in state if not b) - 6)


class FixedSparseNumeric:
    def __init__(self, mode="fixed_degree3"):
        if mode not in MODES:
            raise ValueError("unknown frozen numeric baseline")
        self.mode = mode
        self.paid_actions = 0
        self._payload = None
        self._training_summary = None

    def fit(self, experiences):
        if self._payload is not None:
            raise ValueError("numerical baseline already compiled")
        rows = paid_rows(experiences, allowed_lengths=(144, 384))
        groups = [dict() for _ in _ACTIONS]
        for before, action, after in rows:
            prior = groups[action].get(before)
            if prior is not None and prior != after:
                raise ValueError("contradictory paid public observation")
            groups[action][before] = after
        terms = MODES[self.mode]
        width = len(terms)
        features = []
        for action in _ACTIONS:
            for term in terms:
                weights = [float(i in term) for i in range(6)]
                weights += [float(a == action) for a in _ACTIONS]
                features.append((weights, float(-len(term))))
        numeric_effects = [[0.0] * (6 * width) for _ in range(6)]
        survivors = []
        for action in _ACTIONS:
            compatible = _solve(tuple(sorted(groups[action].items())), terms)
            survivors.append(compatible)
            for bit, options in enumerate(compatible):
                if not options:
                    continue
                first = options[0]
                for j in range(width):
                    if first & (1 << j):
                        numeric_effects[bit][action * width + j] = 1.0
        conf = []
        for state in sorted(_STATES):
            for action in _ACTIONS:
                current = survivors[action]
                if not all(current):
                    continue
                mask = sum(1 << j for j, term in enumerate(terms)
                           if all(state[k] for k in term))
                if all(all(((c & mask).bit_count() & 1) ==
                           ((options[0] & mask).bit_count() & 1)
                           for c in options[1:]) for options in current):
                    conf.append(_confidence_detector(state, action))
        self.paid_actions = len(rows)
        self._payload = {
            "schema": SCHEMA, "mode": self.mode,
            "paid_actions": len(rows),
            "hidden_w": [w for w, b in features],
            "hidden_b": [b for w, b in features],
            "effect_w": numeric_effects,
            "confidence_w": [w for w, b in conf],
            "confidence_b": [b for w, b in conf],
        }
        n = len(features)
        self._training_summary = {
            "mode": self.mode,
            "charged_actions": len(rows),
            "numerical_relu_features": n,
            "numeric_parameters": 13 * n + 6 * n + 13 * len(conf),
            "numerically_confident_public_queries": len(conf),
            "incompatible_action_outputs": sum(
                not opts for action in survivors for opts in action),
            "gradient_steps": 0,
        }
        return dict(self._training_summary)

    def predict(self, state, action, force=False):
        x = _input(state, action)
        if type(force) is not bool or self._payload is None:
            raise ValueError("uncompiled or invalid numeric readout")
        p = self._payload
        hidden = [_relu(sum(w * v for w, v in zip(row, x)) + bias)
                  for row, bias in zip(p["hidden_w"], p["hidden_b"])]
        result = []
        for bit, head in enumerate(p["effect_w"]):
            count = sum(w * v for w, v in zip(head, hidden))
            parity = count + sum((-2.0 if j % 2 else 2.0) *
                                 _relu(count - j) for j in (1, 2, 3))
            number = x[bit] + parity - 2.0 * _relu(x[bit] + parity - 1.0)
            if not math.isfinite(number) or abs(number - round(number)) > 1e-7:
                raise ArithmeticError("nonbinary numerical prediction")
            result.append(int(round(number)))
        if force:
            return tuple(result)
        confidence = sum(_relu(sum(w * v for w, v in zip(row, x)) + bias)
                         for row, bias in zip(p["confidence_w"], p["confidence_b"]))
        if (not math.isfinite(confidence) or
                abs(confidence - round(confidence)) > 1e-7 or
                confidence > 1 + 1e-7):
            raise ArithmeticError("invalid numerical confidence")
        return tuple(result) if confidence > 0.5 else None

    def snapshot(self):
        if self._payload is None:
            raise ValueError("uncompiled numerical control")
        encoded = _canonical(self._payload)
        packed = _canonical({
            "payload": self._payload,
            "sha256": sha256(encoded.encode("ascii")).hexdigest(),
        })
        if len(packed) > MAX_SNAPSHOT_BYTES:
            raise ValueError("oversized numerical control")
        return packed

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid numerical snapshot")
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("invalid numerical envelope")
            p = envelope["payload"]
            needed = {"schema", "mode", "paid_actions", "hidden_w", "hidden_b",
                      "effect_w", "confidence_w", "confidence_b"}
            if (type(p) is not dict or set(p) != needed or
                    p["schema"] != SCHEMA or p["mode"] not in MODES or
                    type(p["paid_actions"]) is not int or
                    p["paid_actions"] not in (144, 384)):
                raise ValueError("invalid numeric schema or provenance")
            n = 6 * len(MODES[p["mode"]])
            def row_is_finite(rows, expected, cols):
                return type(rows) is list and len(rows) == expected and all(
                    type(row) is list and len(row) == cols and all(
                        type(item) in (int, float) and math.isfinite(item)
                        for item in row) for row in rows)
            def vector_is_finite(values, expected):
                return (type(values) is list and len(values) == expected
                        and all(type(x) in (int, float) and math.isfinite(x)
                                for x in values))
            c = len(p["confidence_w"]) if type(p["confidence_w"]) is list else -1
            if not (row_is_finite(p["hidden_w"], n, 12) and
                    vector_is_finite(p["hidden_b"], n) and
                    row_is_finite(p["effect_w"], 6, n) and 0 <= c <= 384 and
                    row_is_finite(p["confidence_w"], c, 12) and
                    vector_is_finite(p["confidence_b"], c)):
                raise ValueError("invalid numerical matrix shape or values")
            if sha256(_canonical(p).encode("ascii")).hexdigest() != envelope["sha256"]:
                raise ValueError("numerical checksum mismatch")
            model = cls(p["mode"])
            model.paid_actions = p["paid_actions"]
            model._payload = p
            if model.snapshot() != raw:
                raise ValueError("noncanonical numerical snapshot")
            return model
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError("invalid/tampered numerical snapshot") from exc
