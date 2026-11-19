"""Source-bound, opt-in JEPA-style specialists ON the native Yggdrasil episodic learner.

No transformers, token prediction, hidden simulator states, source actors, external
model weights, new controller, or accepted-model promotion. Two independent
action-conditioned trainable encoders/predictors update ONLY after the existing
native learner has accepted a witnessed public action/outcome episode.

This is a development candidate, not Meta's pretrained video V-JEPA 2.
"""
from __future__ import annotations

import json
from math import cos, exp, isfinite, sin, tanh

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_episode_experience import NativeEpisodeExperience, MAX_EPISODES as NATIVE_MAX_EPISODES

SCHEMA = "yggdrasil.ckad.native-multilearner-jepa2.v1"
HIDDEN, LATENT = 8, 2
LR, STEPS, CLIP = 0.045, 3, 5.0
NATIVE_WEIGHT, JEPA_WEIGHT = 0.75, 0.25
MAX_BYTES = 1024 * 1024
MAX_EPISODES = NATIVE_MAX_EPISODES


def _bit(v):
    require(type(v) is int and v in (0, 1), "JEPA2_PUBLIC_BIT")
    return v


def _views(views):
    require(type(views) is tuple and len(views) == 2, "JEPA2_VIEWS")
    for view in views:
        require(type(view) is tuple and len(view) == 2, "JEPA2_VIEW_SHAPE")
        for value in view:
            _bit(value)
    return views


def _features(view, extras):
    return tuple(2 * _bit(v) - 1 for v in (*view, *extras))


def _sigmoid(x):
    return 1 / (1 + exp(-x)) if x >= 0 else exp(x) / (1 + exp(x))


def _clip(v):
    return min(CLIP, max(-CLIP, v))


class ActionLatentSpecialist:
    """An independent learned, public-view-conditioned latent world predictor."""

    def __init__(self, kind):
        require(kind in ("transition", "reward"), "JEPA2_KIND")
        self.kind = kind
        size = 3 if kind == "transition" else 5
        salt = 3 if kind == "transition" else 7
        self.encoder = [
            [0.075 * sin((j + 1) * (i + 2) * (salt + 1)) for i in range(size)]
            for j in range(HIDDEN)
        ]
        self.encoder_bias = [0.0] * HIDDEN
        self.predictor = [
            [0.075 * cos((k + 1) * (j + 2) * (salt + 3)) for j in range(HIDDEN)]
            for k in range(LATENT)
        ]
        self.predictor_bias = [0.0] * LATENT
        self.steps = 0

    def _input(self, views, extras):
        _views(views)
        need = 1 if self.kind == "transition" else 3
        require(type(extras) is tuple and len(extras) == need, "JEPA2_ACTIONS")
        return tuple(_features(v, extras) for v in views)

    def _forward(self, x):
        hidden = [tanh(sum(w * v for w, v in zip(row, x)) + self.encoder_bias[j])
                  for j, row in enumerate(self.encoder)]
        out = [sum(w * v for w, v in zip(row, hidden)) + self.predictor_bias[k]
               for k, row in enumerate(self.predictor)]
        return hidden, out

    def probability(self, views, *extras):
        xs = self._input(views, tuple(extras))
        score = sum(self._forward(x)[1][0] - self._forward(x)[1][1] for x in xs) / 2
        p = _sigmoid(2 * score)
        require(isfinite(p) and 0 <= p <= 1, "JEPA2_PROBABILITY")
        return p

    def observe(self, views, extras, label):
        """Update three times using both public projections and stop-gradient target."""
        xs = self._input(views, extras)
        y = _bit(label)
        target = (1.0, -1.0) if y else (-1.0, 1.0)
        d = len(xs[0])
        for _ in range(STEPS):
            ge = [[0.0] * d for _ in range(HIDDEN)]
            geb = [0.0] * HIDDEN
            gp = [[0.0] * HIDDEN for _ in range(LATENT)]
            gpb = [0.0] * LATENT
            for x in xs:
                h, out = self._forward(x)
                error = (out[0] - target[0], out[1] - target[1])
                for k in range(LATENT):
                    gpb[k] += error[k]
                    for j in range(HIDDEN):
                        gp[k][j] += error[k] * h[j]
                for j in range(HIDDEN):
                    back = sum(error[k] * self.predictor[k][j]
                               for k in range(LATENT)) * (1 - h[j] * h[j])
                    geb[j] += back
                    for i in range(d):
                        ge[j][i] += back * x[i]
            rate = LR / len(xs)
            for j in range(HIDDEN):
                self.encoder_bias[j] -= rate * _clip(geb[j])
                for i in range(d):
                    self.encoder[j][i] -= rate * _clip(ge[j][i])
            for k in range(LATENT):
                self.predictor_bias[k] -= rate * _clip(gpb[k])
                for j in range(HIDDEN):
                    self.predictor[k][j] -= rate * _clip(gp[k][j])
            self.steps += 1
        self._validate()
        return self

    def _validate(self):
        d = 3 if self.kind == "transition" else 5
        require(len(self.encoder) == HIDDEN
                and all(type(row) is list and len(row) == d for row in self.encoder)
                and len(self.predictor) == LATENT
                and all(type(row) is list and len(row) == HIDDEN for row in self.predictor)
                and len(self.encoder_bias) == HIDDEN
                and len(self.predictor_bias) == LATENT
                and type(self.steps) is int and 0 <= self.steps <= MAX_EPISODES * STEPS,
                "JEPA2_MODEL_SHAPE")
        values = [v for row in self.encoder + self.predictor for v in row]
        values += self.encoder_bias + self.predictor_bias
        require(all(type(v) is float and isfinite(v) and abs(v) <= 20 for v in values),
                "JEPA2_MODEL_NUMERIC")

    def as_data(self):
        self._validate()
        return {"kind": self.kind, "encoder": self.encoder, "encoder_bias": self.encoder_bias,
                "predictor": self.predictor, "predictor_bias": self.predictor_bias,
                "steps": self.steps}

    @classmethod
    def from_data(cls, d, expected):
        require(type(d) is dict and set(d) == {
            "kind", "encoder", "encoder_bias", "predictor", "predictor_bias", "steps"
        } and d["kind"] == expected, "JEPA2_MODEL_KEYS")
        obj = cls(expected)
        obj.encoder = d["encoder"]
        obj.encoder_bias = d["encoder_bias"]
        obj.predictor = d["predictor"]
        obj.predictor_bias = d["predictor_bias"]
        obj.steps = d["steps"]
        obj._validate()
        return obj

    def clone(self):
        return self.from_data(json.loads(json.dumps(self.as_data())), self.kind)


class NativeMultiLearner:
    """One versioned bundle: original NativeEpisodeExperience plus TWO learners.

    No accepted native model is replaced. Training uses public views/consequences,
    and original native checkpoints are embedded and cryptographically rechecked.
    """

    def __init__(self, native=None, transition=None, reward=None):
        self.native = native if native is not None else NativeEpisodeExperience(repair=True)
        self.transition = transition if transition is not None else ActionLatentSpecialist("transition")
        self.reward = reward if reward is not None else ActionLatentSpecialist("reward")

    def begin_stream(self):
        return NativeMultiLearner(self.native.begin_stream(),
                                  self.transition.clone(), self.reward.clone())

    def predict(self, views, first, next_state, second, *, stream):
        _views(views)
        require(type(stream) is bool, "JEPA2_STREAM_MODE")
        first, next_state, second = _bit(first), _bit(next_state), _bit(second)
        native_p = (self.native.context_forecast(views[0], first) if stream
                    else self.native.forecast(views[0], first))
        native_q = (self.native.context_forecast(views[0], first, next_state, second) if stream
                    else self.native.forecast(views[0], first, next_state, second))
        native = (float(native_p), float(native_q))
        jepa = (self.transition.probability(views, first),
                self.reward.probability(views, first, next_state, second))
        mixed = tuple(NATIVE_WEIGHT * a + JEPA_WEIGHT * b for a, b in zip(native, jepa))
        return {"native": native, "jepa": jepa, "mixed": mixed}

    def observe(self, identifier, views, row):
        _views(views)
        require(type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"},
                "JEPA2_PUBLIC_ROW")
        for name in row:
            _bit(row[name])
        next_native = self.native.observe(identifier, views, row)
        if next_native is self.native:
            return self
        t, r = self.transition.clone(), self.reward.clone()
        t.observe(views, (row["x1"],), row["s2"])
        r.observe(views, (row["x1"], row["s2"], row["x2"]), row["y"])
        return NativeMultiLearner(next_native, t, r)

    def checkpoint(self):
        raw_native = self.native.checkpoint()
        data = {"schema": SCHEMA, "native_sha256": digest(raw_native),
                "native_ascii": raw_native.decode("ascii"),
                "transition": self.transition.as_data(),
                "reward": self.reward.as_data()}
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "JEPA2_CHECKPOINT_SIZE")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and pin(expected_sha256)
                and digest(raw) == expected_sha256, "JEPA2_CHECKPOINT_PIN")
        try:
            d = json.loads(raw.decode("ascii"))
            require(type(d) is dict and set(d) == {
                "schema", "native_sha256", "native_ascii", "transition", "reward"
            } and d["schema"] == SCHEMA and canonical(d) == raw,
                "JEPA2_CHECKPOINT_CONTRACT")
            native_raw = d["native_ascii"].encode("ascii")
            native = NativeEpisodeExperience.restore(native_raw, d["native_sha256"])
            t = ActionLatentSpecialist.from_data(d["transition"], "transition")
            r = ActionLatentSpecialist.from_data(d["reward"], "reward")
            count = native.info()["count"]
            require(t.steps == STEPS * count and r.steps == STEPS * count,
                    "JEPA2_STEPS_SOURCE_PARITY")
            # Treat persisted neural weights as evidence-derived, not trusted
            # metadata. Rebuild from the native immutable public source ledger.
            reference_t, reference_r = (ActionLatentSpecialist("transition"),
                                        ActionLatentSpecialist("reward"))
            for _, views, first, next_state, second, outcome in native._ledger:
                reference_t.observe(views, (first,), next_state)
                reference_r.observe(views, (first, next_state, second), outcome)
            require(canonical(reference_t.as_data()) == canonical(t.as_data())
                    and canonical(reference_r.as_data()) == canonical(r.as_data()),
                    "JEPA2_LEARNED_WEIGHTS_SOURCE_PARITY")
            obj = cls(native, t, r)
            require(obj.checkpoint() == raw, "JEPA2_CHECKPOINT_REPLAY")
            return obj
        except (TypeError, KeyError, AttributeError, ValueError, UnicodeError,
                RecursionError, OverflowError) as exc:
            raise ValueError("YGG_JEPA2_CHECKPOINT_REJECTED") from exc

