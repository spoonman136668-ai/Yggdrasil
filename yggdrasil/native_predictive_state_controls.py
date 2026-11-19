"""CAP04 conventional matched-information controls. Fixture-only until source first-use.

All forecasting is prequential. Terminal reward may depend on the actually
witnessed current s2, but not on future rewards, latent labels or phase.
"""
from __future__ import annotations

import json
import math
import hashlib
import numpy as np
from yggdrasil.native_context_basis import canonical, digest, pin
from yggdrasil.native_paired_causal_contrast import state, arm

SCHEMA = "yggdrasil.cap04.matched-history-controls.v1"
ARMS = ("full_history_exact_state_action_Beta", "history_order1_Beta",
        "history_order2_Beta", "Bayesian_context_tree_mixture",
        "regularized_linear_history", "random_history_split_sham")
STAGES = ("transition", "residual")
MAX_RECORDS = 2048
SHRINK = 4.0
RIDGE_L2 = 8.0
TREE_PRIOR = (1.0, 0.5, 0.25)


def require(condition, reason):
    if not condition:
        raise ValueError("CAP04_CONTROL_" + reason)


def bit(v):
    require(type(v) is int and v in (0, 1), "BIT")
    return v


def context(views, legacy=False):
    if not legacy:
        return state(views)
    require(type(views) is tuple and len(views) == 2 and
            all(type(v) is tuple and len(v) == 2 for v in views) and
            all(type(b) is int and b in (0, 1) for v in views for b in v),
            "LEGACY_VIEWS")
    return (views[0][0], views[0][1], views[1][1])


def signature(record):
    return (record[2], record[5], record[4])


class MatchedHistoryControls:
    """Independently fitted Beta, order-Markov, context tree, ridge, and sham.

    Shared observed ledger supplies identical source information. Each arm has
    its own independently updated state and the count/tree/ridge predictions
    are independently fit, rather than relabeled versions of one forecast.
    """
    def __init__(self):
        self._events = []
        self._seen = set()
        self._counts = {stage: [{} for _ in range(4)] for stage in STAGES}
        self._tree_log = {stage: [math.log(p) for p in TREE_PRIOR] for stage in STAGES}
        self._ridge_inverse = {stage: None for stage in STAGES}
        self._ridge_rhs = {stage: None for stage in STAGES}

    @property
    def count(self):
        return len(self._events)

    def _history(self, order):
        if self.count < order:
            return None
        return tuple(signature(e) for e in self._events[-order:])

    def _key(self, stage, st, chosen, s2, order):
        root = (st, chosen) if stage == "transition" else (st, chosen, s2)
        if order == 0:
            return root
        if order == 3:  # negative: fixed source-ID-hashed random split
            previous_id = self._events[-1][0] if self.count else "none"
            salt = ("cap04-random-history-sham-v1/" + previous_id).encode("ascii")
            cell = hashlib.sha256(salt).digest()[0] & 7
            return root + ((cell,),)
        history = self._history(order)
        return root + ((history if history is not None else ("none",)),)

    def _beta(self, stage, st, chosen, s2, order):
        root = self._key(stage, st, chosen, s2, 0)
        y0, n0 = self._counts[stage][0].get(root, (0, 0))
        pooled = (y0 + 1.0) / (n0 + 2.0)
        if order == 0:
            return pooled
        key = self._key(stage, st, chosen, s2, order)
        yi, ni = self._counts[stage][order].get(key, (0, 0))
        return (yi + SHRINK * pooled) / (ni + SHRINK)

    def _vector(self, stage, st, chosen, s2):
        a, b = chosen
        p = self._events[-1] if self.count else None
        q = self._events[-2] if self.count >= 2 else None
        # Explicit missingness is available to every fitted arm.
        pa, pb = p[2] if p else (0, 0)
        pu, pv, pw = p[5] if p else (0, 0, 0)
        py = p[4] if p else 0
        qa, qb = q[2] if q else (0, 0)
        qu, qv, qw = q[5] if q else (0, 0, 0)
        qy = q[4] if q else 0
        u, v, w = st
        s = s2 if stage == "residual" else 0
        arr = (1, u, v, w, a, b, s, a*b, u*a, v*a, w*a,
               u*b, v*b, w*b, s*a, s*b,
               pa, pb, pu, pv, pw, py, qa, qb, qu, qv, qw, qy,
               int(p is not None), int(q is not None),
               a*pa, b*pb, s*py, pa*pu, pb*pv, py*pa,
               pa*qa, pb*qb, py*qy)
        return np.asarray(arr, dtype=np.float64)

    def _linear(self, stage, st, chosen, s2):
        vec = self._vector(stage, st, chosen, s2)
        inverse = self._ridge_inverse[stage]
        if inverse is None:
            return 0.5
        p = float(vec @ (inverse @ self._ridge_rhs[stage]))
        return max(0.01, min(0.99, p))

    def _forecast_direct(self, st, chosen, stage, s2):
        p0 = self._beta(stage, st, chosen, s2, 0)
        p1 = self._beta(stage, st, chosen, s2, 1)
        p2 = self._beta(stage, st, chosen, s2, 2)
        # Fixed complexity prior with evidence updated before each observation.
        logits = self._tree_log[stage]
        shift = max(logits)
        weights = [math.exp(x - shift) for x in logits]
        tree = sum(w*p for w, p in zip(weights, (p0, p1, p2))) / sum(weights)
        return (p0, p1, p2, tree, self._linear(stage, st, chosen, s2),
                self._beta(stage, st, chosen, s2, 3))

    def forecast(self, views, chosen, stage, witnessed_s2=None):
        st = context(views)
        pair = arm(chosen)
        require(stage in STAGES, "STAGE")
        if stage == "transition":
            require(witnessed_s2 is None, "FUTURE_SENSOR")
            s2 = None
        else:
            s2 = bit(witnessed_s2)
        # Strong conventional stage-2 comparator learns DIRECT y|witnessed-s2;
        # unlike the candidate's residual XOR, it need not impose that form.
        return dict(zip(ARMS, self._forecast_direct(st, pair, stage, s2)))

    def observe(self, identifier, views, chosen, s2, reward, post, *, legacy=False):
        require(pin(identifier), "SOURCE_ID")
        st = context(views, legacy=legacy)
        pair = arm(chosen)
        s2 = bit(s2)
        reward = bit(reward)
        require(type(post) is tuple and len(post) == 3 and
                all(type(x) is int and x in (0, 1) for x in post) and
                post[1] == s2, "POST")
        require(identifier not in self._seen, "DUPLICATE")
        require(self.count < MAX_RECORDS, "MAX_RECORDS")
        targets = {"transition": s2, "residual": reward}
        for stage, y in targets.items():
            sensor = None if stage == "transition" else s2
            probs = self._forecast_direct(st, pair, stage, sensor)
            for order in range(3):
                p = max(1e-12, min(1 - 1e-12, probs[order]))
                self._tree_log[stage][order] += math.log(p if y else 1 - p)
            for order in range(4):
                key = self._key(stage, st, pair, sensor, order)
                yes, n = self._counts[stage][order].get(key, (0, 0))
                self._counts[stage][order][key] = (yes + y, n + 1)
            x = self._vector(stage, st, pair, sensor)
            inv = self._ridge_inverse[stage]
            if inv is None:
                inv = np.eye(len(x), dtype=np.float64) / RIDGE_L2
                self._ridge_inverse[stage] = inv
                self._ridge_rhs[stage] = np.zeros(len(x), dtype=np.float64)
            vx = inv @ x
            inv -= np.outer(vx, vx) / (1.0 + float(x @ vx))
            self._ridge_rhs[stage] += y * x
        self._events.append((identifier, st, pair, s2, reward, post))
        self._seen.add(identifier)
        return self

    @classmethod
    def from_native_events(cls, native_events):
        model = cls()
        for ident, views, a, s2, b, reward, post in native_events:
            model.observe(ident, views, (a, b), s2, reward, post, legacy=True)
        return model

    def checkpoint(self):
        return canonical({"schema": SCHEMA, "events": self._events})

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and pin(expected_sha) and
                digest(raw) == expected_sha, "COLD_HASH")
        try:
            doc = json.loads(raw.decode("ascii"))
            require(type(doc) is dict and set(doc) == {"schema", "events"} and
                    doc["schema"] == SCHEMA and type(doc["events"]) is list and
                    canonical(doc) == raw, "COLD_SCHEMA")
            obj = cls()
            for ident, st, chosen, s2, reward, post in doc["events"]:
                views = ((st[0], st[1]), (st[1], st[2]))
                obj.observe(ident, views, tuple(chosen), s2, reward, tuple(post))
            require(obj.checkpoint() == raw, "COLD_REPLAY")
            return obj
        except (ValueError, TypeError, KeyError, IndexError, UnicodeError,
                ArithmeticError, OverflowError) as exc:
            raise ValueError("YGG_CAP04_CONTROL_COLD_REJECTED") from exc
