"""Source-free JEPA2-05 horizon-three forecast on a frozen historical checkpoint.

Contributor-only diagnostic, never an Amalgam checkpoint converter. It reads
previously trained JEPA weights and current Amalgam public history; it cannot
observe, learn, generate worlds, dispatch a runner, or promote a model.
"""
from __future__ import annotations

import hashlib
import json
import re

import numpy as np

SCHEMA = "yggdrasil.jepa2-04.future-state-native-cumulative.v1"
HORIZON, HISTORY, DIM, WIDTH, LATENT = 3, 4, 37, 16, 8
MAX_CHECKPOINT_BYTES = 2 * 1024 * 1024
FIELDS = ("future_enc", "future_bias", "future_dec", "future_dec_bias",
          "teacher_enc", "teacher_bias", "pred_enc", "pred_bias",
          "pred_latent", "pred_latent_bias", "readout", "readout_bias")


def _check(condition, label):
    if not condition:
        raise ValueError("JEPA_REENTRY_" + label)


def _bit(x):
    _check(type(x) is int and x in (0, 1), "PUBLIC_BIT")
    return x


def _public(views, *, current=False):
    _check(type(views) in (tuple, list) and len(views) == 2 and
           all(type(v) in (tuple, list) and len(v) == 2 for v in views),
           "PUBLIC_VIEWS")
    a, b, c, d = (_bit(x) for v in views for x in v)
    if current:
        # Amalgam's new-witness admission contract; reject, never filter or
        # modify a source sequence to make incompatible examples pass.
        _check(a == c, "COORDINATE_INCOMPATIBLE")
    return a, b, d


def _features(views, plans, ledger):
    now = _public(views, current=True)
    _check(type(plans) in (tuple, list) and len(plans) == HORIZON and
           type(ledger) in (tuple, list), "HORIZON_INPUT")
    actions = []
    for pair in plans:
        _check(type(pair) in (tuple, list) and len(pair) == 2,
               "ANNOUNCED_ACTIONS")
        actions.extend(_bit(v) for v in pair)
    values = [2 * bit - 1 for bit in now + tuple(actions)]
    recent = list(ledger[-HISTORY:])
    for i in range(HISTORY):
        if i >= len(recent):
            values.extend([0.] * 7)
            continue
        item = recent[-i - 1]
        _check(type(item) is tuple and len(item) == 6, "SOURCE_HISTORY")
        _, old_views, first, next_state, second, reward = item
        u, v, w = _public(old_views)
        values.extend((2 * _bit(v0) - 1) / (i + 1)
                      for v0 in (u, v, w, first, next_state, second, reward))
    _check(len(values) == DIM, "FEATURE_DIM")
    return np.asarray(values, dtype=np.float64)


class FrozenHorizonReadout:
    """Isolated, read-only direct numeric readout from original trained heads."""

    def __init__(self, blob, sha256):
        _check(type(blob) is bytes and 0 < len(blob) <= MAX_CHECKPOINT_BYTES and
               type(sha256) is str and re.fullmatch(r"[a-f0-9]{64}", sha256)
               and hashlib.sha256(blob).hexdigest() == sha256,
               "CHECKPOINT_PIN")
        try:
            data = json.loads(blob)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("JEPA_REENTRY_CHECKPOINT_JSON") from exc
        _check(type(data) is dict and set(data) == {
            "schema", "native_sha256", "native_ascii", "sensory", "reward"} and
            data["schema"] == SCHEMA, "CHECKPOINT_SCHEMA")
        native = data["native_ascii"]
        _check(type(native) is str and type(data["native_sha256"]) is str and
               hashlib.sha256(native.encode("ascii")).hexdigest() ==
               data["native_sha256"], "PARENT_CUSTODY")
        self._weights = {}
        for kind, n in (("sensory", 9), ("reward", 3)):
            head = data[kind]
            _check(type(head) is dict and
                   set(head) == set(FIELDS) | {"kind", "steps", "windows"} and
                   head["kind"] == ("sensors" if kind == "sensory" else "reward") and
                   type(head["windows"]) is int and 0 <= head["windows"] < 5000 and
                   type(head["steps"]) is int and
                   head["steps"] == 2 * head["windows"],
                   "TRAINED_HEAD_CONTRACT")
            shapes = ((n, LATENT), (LATENT,), (LATENT, n), (n,),
                      (n, LATENT), (LATENT,), (DIM, WIDTH), (WIDTH,),
                      (WIDTH, LATENT), (LATENT,), (LATENT, n), (n,))
            weights = {}
            for field, shape in zip(FIELDS, shapes):
                a = np.asarray(head[field], dtype=np.float64)
                _check(a.shape == shape and np.isfinite(a).all() and
                       (np.abs(a) <= 20).all(), "NONFINITE_OR_BAD_SHAPE")
                a.setflags(write=False)
                weights[field] = a
            self._weights[kind] = weights
        self.sha256 = sha256

    def forecast(self, views, announced_plans, witnessed_ledger):
        """Predict from PUBLIC features only; never consumes unobserved results."""
        x = _features(views, announced_plans, witnessed_ledger)
        outputs = []
        for kind in ("sensory", "reward"):
            w = self._weights[kind]
            hidden = np.tanh(x @ w["pred_enc"] + w["pred_bias"])
            z = hidden @ w["pred_latent"] + w["pred_latent_bias"]
            logit = z @ w["readout"] + w["readout_bias"]
            p = 1 / (1 + np.exp(-np.clip(logit, -50, 50)))
            _check(np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all(),
                   "PREDICTION")
            outputs.append(p)
        sensors, reward = outputs
        return tuple(float(v) for i in range(HORIZON)
                     for v in (sensors[3 * i + 1], reward[i]))

    def forecast_amalgam(self, model, views, announced_plans):
        """Read a real Amalgam episode ledger; assert no checkpoint mutation."""
        from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
        _check(isinstance(model, NativeCausalAmalgam), "CANONICAL_MODEL_REQUIRED")
        before = model.checkpoint()
        ledger = tuple(model.native._episode_reader()._ledger)
        result = self.forecast(views, announced_plans, ledger)
        _check(model.checkpoint() == before, "CANONICAL_MODEL_MUTATED")
        return result
