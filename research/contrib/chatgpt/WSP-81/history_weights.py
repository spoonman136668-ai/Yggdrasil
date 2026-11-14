"""WSP81 paid-history-conditioned numerical latent dynamics; source-blind.

A finite PREDEFINED 31-member model class, NOT unrestricted mechanism
discovery or AGI. Only charged, continuous public action-consequence rows
inform feature selection. Model weights and mode-register weights are
compiled to numbers; cold restore has no physics, ledger, source module,
search algorithm, or hidden evaluator labels.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
import json
import math

STATES = frozenset(product((0, 1), repeat=6))
ACTIONS = tuple(range(6))
SCHEMA = "wsp81.history-numeric.v1"
MAX_SNAPSHOT_CHARS = 60000


def _valid_state(s):
    return type(s) is tuple and s in STATES


def _valid_action(a):
    return type(a) is int and a in ACTIONS


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _relu(v):
    return max(0.0, v)


def _private_hypotheses():
    """Predeclared generator-independent two-state model family."""
    return [(None, None)] + [
        (trigger, offset) for trigger in ACTIONS for offset in range(1, 6)]


def _numerical_parameters(trigger, offset):
    mode_weights = [float(a == trigger) if trigger is not None else 0.0
                    for a in ACTIONS]
    effect_weights = [[0.0] * 6 for _ in range(6)]
    if trigger is not None:
        for action in ACTIONS:
            if action != trigger:
                effect_weights[(action + offset) % 6][action] = 1.0
    return {"mode_weights": mode_weights, "effect_weights": effect_weights}


def _predict_one(state, action, history, params):
    """Two-layer numeric ReLU transition readout with numeric mode register."""
    trigger_count = sum(params["mode_weights"][prior] for prior in history)
    # Parity is the fixed state-machine update of the learned onehot weights,
    # not a private source truth label or symbolic hypothesis solver.
    mode = int(trigger_count) & 1
    x = [float(s) for s in state] + [
        float(action == a) for a in ACTIONS] + [float(mode)]
    gates = [_relu(x[6 + a] + x[12] - 1.0) for a in ACTIONS]
    result = []
    for bit, row in enumerate(params["effect_weights"]):
        flip = x[6 + bit] + sum(w * g for w, g in zip(row, gates))
        value = x[bit] + flip - 2.0 * _relu(x[bit] + flip - 1.0)
        if not math.isfinite(value) or abs(value - round(value)) > 1e-10:
            raise ArithmeticError("non-binary numerical cold readout")
        result.append(int(round(value)))
    return tuple(result)


class PaidHistoryNumeric:
    def __init__(self):
        self.current = (0,) * 6
        self.charges = 0
        self._rows = []
        self._payload = None

    def charge(self, before, action, after, action_cost=1):
        if (not _valid_state(before) or not _valid_state(after)
                or not _valid_action(action)
                or type(action_cost) is not int or action_cost != 1
                or before != self.current or self.charges >= 384
                or self._rows is None):
            raise ValueError("unpaid, invalid, noncontinuous, or overbudget public event")
        self._rows.append((before, action, after))
        self.current = after
        self.charges += 1
        self._payload = None

    def compile(self):
        if self._rows is None or self.charges != 384:
            raise ValueError("compile only after all 384 charged observations")
        consistent = []
        for trigger, offset in _private_hypotheses():
            numeric = _numerical_parameters(trigger, offset)
            history = []
            compatible = True
            for before, action, after in self._rows:
                if _predict_one(before, action, history, numeric) != after:
                    compatible = False
                    break
                history.append(action)
            if compatible:
                consistent.append(numeric)
        if not consistent:
            raise ValueError("none of 31 predefined mechanisms explain paid history")
        self._payload = {
            "schema": SCHEMA, "charges": self.charges,
            "models": consistent,
        }
        return {"charged_actions": self.charges,
                "surviving_mechanisms": len(consistent),
                "numerical_parameters": len(consistent) * (6 + 36),
                "cold_restorable": True}

    def predict(self, state, action, history=()):
        if (not _valid_state(state) or not _valid_action(action)
                or type(history) not in (tuple, list)
                or any(not _valid_action(x) for x in history)):
            raise ValueError("invalid source-blind cold public query")
        if self._payload is None:
            raise ValueError("uncompiled model")
        results = {
            _predict_one(state, action, history, params)
            for params in self._payload["models"]
        }
        return next(iter(results)) if len(results) == 1 else None

    def snapshot(self):
        if self._payload is None:
            raise ValueError("uncompiled numeric weights")
        core = _canonical(self._payload)
        envelope = _canonical({
            "payload": self._payload,
            "sha256": sha256(core.encode("ascii")).hexdigest(),
        })
        if len(envelope) > MAX_SNAPSHOT_CHARS:
            raise ValueError("oversized snapshot")
        return envelope

    @classmethod
    def restore(cls, serialized):
        if (type(serialized) is not str or
                len(serialized) > MAX_SNAPSHOT_CHARS):
            raise ValueError("invalid frozen snapshot type/size")
        try:
            box = json.loads(serialized)
            if type(box) is not dict or set(box) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            payload = box["payload"]
            if (type(payload) is not dict or set(payload) != {
                    "schema", "charges", "models"}
                    or payload["schema"] != SCHEMA
                    or type(payload["charges"]) is not int
                    or payload["charges"] != 384
                    or type(payload["models"]) is not list
                    or not 1 <= len(payload["models"]) <= 31):
                raise ValueError("invalid numerical model provenance")
            for model in payload["models"]:
                if type(model) is not dict or set(model) != {
                        "mode_weights", "effect_weights"}:
                    raise ValueError("invalid model matrix keys")
                mw, ew = model["mode_weights"], model["effect_weights"]
                if (type(mw) is not list or len(mw) != 6
                        or type(ew) is not list or len(ew) != 6
                        or any(type(row) is not list or len(row) != 6
                               for row in ew)
                        or any(type(v) not in (int, float) or v not in (0, 1)
                               for v in mw + [v for row in ew for v in row])):
                    raise ValueError("invalid or nonfinite numeric matrices")
            if sha256(_canonical(payload).encode("ascii")).hexdigest() != box["sha256"]:
                raise ValueError("model weight checksum mismatch")
            model = cls()
            model.current = None
            model.charges = payload["charges"]
            model._rows = None
            model._payload = payload
            if model.snapshot() != serialized:
                raise ValueError("noncanonical/corrupt snapshot")
            return model
        except (TypeError, ValueError, OverflowError, KeyError) as exc:
            raise ValueError("invalid or tampered numeric snapshot") from exc
