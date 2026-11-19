"""Opt-in, tokenless native Yggdrasil multi-horizon future-state JEPA (dev only).

The existing NativeTemporalMultiLearner (native cumulative memory + FOUR prior
learned specialists) is retained/continued unchanged. Two new independent
trainable heads predict a THREE-STEP sequence of PUBLIC future sensory states
(9 bits) or intervention consequences (3 bits). Each has its own trainable
future encoder+decoder, EMA stop-gradient teacher and action-conditioned
predictor. Delayed learning happens only after future action consequences
have been OBSERVED. Never use hidden regime tags or simulator latents.

This is a new nonlinear learned future-state objective, not binary-label JEPA,
but NOT Meta's pretrained video V-JEPA 2 and NOT independent science.
"""
from __future__ import annotations
import hashlib
import json
from math import cos, sin
import numpy as np
from yggdrasil.native_context_basis import canonical, digest, require
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner

HORIZON = 3
HISTORY = 4
WIDTH = 16
LATENT = 8
DIM = 3 + 2 * HORIZON + 7 * HISTORY
MOMENTUM = 0.98
LR_FUTURE, LR_PRED, LR_READOUT, LR_DIRECT = 0.03, 0.03, 0.04, 0.08
UPDATES = 2
SCHEMA = "yggdrasil.jepa2-04.future-state-native-cumulative.v1"


def _bit(x):
    require(type(x) is int and x in (0, 1), "JEPA4_PUBLIC_BIT")
    return x


def public_observed(views):
    require(type(views) in (tuple, list) and len(views) == 2
            and all(type(v) in (tuple, list) and len(v) == 2 for v in views),
            "JEPA4_PUBLIC_VIEWS")
    a, b, c = _bit(views[0][0]), _bit(views[0][1]), _bit(views[1][1])
    # Prior CKAD37 paired public views may be different projections;
    # do NOT impose a synthetic-source-only overlapping-view constraint
    # on genuine previously witnessed Yggdrasil native experiences.
    _bit(views[1][0])
    return a, b, c


def observed_features(views, plans, ledger, *, no_history=False, no_actions=False):
    current = public_observed(views)
    require(type(plans) in (tuple, list) and len(plans) == HORIZON
            and type(ledger) in (tuple, list), "JEPA4_INPUT_ARITY")
    actions = []
    for pair in plans:
        require(type(pair) in (tuple, list) and len(pair) == 2,
                "JEPA4_PLANNED_ACTION_PAIR")
        actions.extend(_bit(x) for x in pair)
    result = [2 * b - 1 for b in current]
    result.extend([0] * 6 if no_actions else [2 * b - 1 for b in actions])
    recent = list(ledger[-HISTORY:])
    for i in range(HISTORY):
        if no_history or i >= len(recent):
            result.extend([0.] * 7)
        else:
            item = recent[-i-1]
            require(type(item) is tuple and len(item) == 6, "JEPA4_OLD_SOURCE_ITEM")
            _, prior_views, x1, next_state, x2, reward = item
            u, v, w = public_observed(prior_views)
            result.extend([(2 * _bit(x) - 1) / (i + 1)
                           for x in (u, v, w, x1, next_state, x2, reward)])
    require(len(result) == DIM, "JEPA4_FEATURE_DIM")
    return np.asarray(result, dtype=np.float64)


def targets(window):
    require(type(window) in (tuple, list) and len(window) == HORIZON,
            "JEPA4_OBSERVED_HORIZON")
    sensors, rewards = [], []
    for row in window:
        require(type(row) is dict and set(row) >= {"post", "row"},
                "JEPA4_PUBLIC_TARGET_FIELDS")
        post = row["post"]
        require(type(post) in (tuple, list) and len(post) == 3,
                "JEPA4_PUBLIC_POST")
        sensors.extend(_bit(z) for z in post)
        rewards.append(_bit(row["row"]["y"]))
        require(_bit(row["row"]["s2"]) == _bit(post[1]),
                "JEPA4_NATIVE_OUTCOME_CUSTODY")
    return (np.asarray(sensors, dtype=np.float64),
            np.asarray(rewards, dtype=np.float64))


def primary_probabilities(predicted_sensors, predicted_reward):
    sens = np.asarray(predicted_sensors, dtype=np.float64)
    rew = np.asarray(predicted_reward, dtype=np.float64)
    require(sens.shape == (9,) and rew.shape == (3,), "JEPA4_PRIMARY_HEAD")
    return np.asarray([v for i in range(3)
                       for v in (sens[3*i+1], rew[i])], dtype=np.float64)


def primary_truth(window):
    sens, rew = targets(window)
    return primary_probabilities(sens, rew)


def _sigmoid(x):
    # Bound numerical exponential without hiding nonfinite gradients.
    x = np.asarray(x, dtype=np.float64)
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def _init(shape, salt, scale=0.095):
    return np.asarray([scale * sin((i + 2) * (salt + 3) * 0.713)
                       + scale / 3 * cos((i + 1) * (salt + 11) * 0.411)
                       for i in range(int(np.prod(shape)))],
                      dtype=np.float64).reshape(shape)


class FutureStateHead:
    """Noncollapsed learned future encoder/decoder + EMA teacher + predictor.

    Online future encoder must reconstruct actual PUBLIC future observations;
    predictor is regressed toward a stop-gradient EMA future representation,
    and its latent readout predicts those observed sensor/reward bits.
    """
    def __init__(self, kind):
        require(kind in ("sensors", "reward"), "JEPA4_HEAD_KIND")
        self.kind = kind
        self.n = 9 if kind == "sensors" else 3
        salt = 19 if kind == "sensors" else 31
        self.future_enc = _init((self.n, LATENT), salt)
        self.future_bias = np.zeros(LATENT)
        self.future_dec = _init((LATENT, self.n), salt + 7)
        self.future_dec_bias = np.zeros(self.n)
        self.teacher_enc = self.future_enc.copy()
        self.teacher_bias = self.future_bias.copy()
        self.pred_enc = _init((DIM, WIDTH), salt + 13)
        self.pred_bias = np.zeros(WIDTH)
        self.pred_latent = _init((WIDTH, LATENT), salt + 17)
        self.pred_latent_bias = np.zeros(LATENT)
        self.readout = _init((LATENT, self.n), salt + 23)
        self.readout_bias = np.zeros(self.n)
        self.steps = 0
        self.windows = 0

    def predict(self, x):
        require(np.asarray(x).shape == (DIM,), "JEPA4_PREDICT_FEATURES")
        h = np.tanh(x @ self.pred_enc + self.pred_bias)
        latent = h @ self.pred_latent + self.pred_latent_bias
        p = _sigmoid(latent @ self.readout + self.readout_bias)
        require(bool(np.isfinite(p).all()), "JEPA4_FINITE_PREDICTION")
        return p

    def target_embedding(self, target):
        return np.tanh(target @ self.teacher_enc + self.teacher_bias)

    def learn(self, x, observed):
        y = np.asarray(observed, dtype=np.float64)
        require(y.shape == (self.n,) and bool(np.isin(y, [0, 1]).all()),
                "JEPA4_VERIFIED_FUTURE_TARGET")
        for _ in range(UPDATES):
            # STOP GRADIENT through the slowly adapting target encoder.
            target = self.target_embedding(y)
            # Online future representation learns to preserve all public bits.
            encoded = np.tanh(y @ self.future_enc + self.future_bias)
            reconstruct = _sigmoid(encoded @ self.future_dec + self.future_dec_bias)
            rec_err = reconstruct - y
            d_dec = np.outer(encoded, rec_err)
            d_dec_b = rec_err.copy()
            d_enc = (rec_err @ self.future_dec.T) * (1 - encoded ** 2)
            d_fenc = np.outer(y, d_enc)
            d_fb = d_enc.copy()
            # Action-conditioned nonlinear predictive latent, plus supervised
            # observation decoder, with an independently trained stopgrad EMA.
            h = np.tanh(x @ self.pred_enc + self.pred_bias)
            z = h @ self.pred_latent + self.pred_latent_bias
            pred = _sigmoid(z @ self.readout + self.readout_bias)
            out_err = pred - y
            d_read = np.outer(z, out_err)
            d_read_b = out_err.copy()
            d_z = out_err @ self.readout.T + 0.25 * (z - target)
            d_lat = np.outer(h, d_z)
            d_lat_b = d_z.copy()
            d_h = (d_z @ self.pred_latent.T) * (1 - h ** 2)
            d_pen = np.outer(x, d_h)
            d_pen_b = d_h.copy()
            clip = lambda v: np.clip(v, -5, 5)
            self.future_enc -= LR_FUTURE * clip(d_fenc) / self.n
            self.future_bias -= LR_FUTURE * clip(d_fb) / self.n
            self.future_dec -= LR_FUTURE * clip(d_dec) / self.n
            self.future_dec_bias -= LR_FUTURE * clip(d_dec_b) / self.n
            self.pred_enc -= LR_PRED * clip(d_pen) / self.n
            self.pred_bias -= LR_PRED * clip(d_pen_b) / self.n
            self.pred_latent -= LR_PRED * clip(d_lat) / self.n
            self.pred_latent_bias -= LR_PRED * clip(d_lat_b) / self.n
            self.readout -= LR_READOUT * clip(d_read) / self.n
            self.readout_bias -= LR_READOUT * clip(d_read_b) / self.n
            self.teacher_enc = MOMENTUM * self.teacher_enc + (1-MOMENTUM) * self.future_enc
            self.teacher_bias = MOMENTUM * self.teacher_bias + (1-MOMENTUM) * self.future_bias
            self.steps += 1
        self.windows += 1
        self.validate()
        return self

    def variance(self, future_observations):
        embeddings = np.asarray([
            self.target_embedding(np.asarray(y, dtype=np.float64))
            for y in future_observations
        ])
        require(embeddings.ndim == 2 and embeddings.shape[1] == LATENT
                and embeddings.shape[0] >= 16, "JEPA4_VARIANCE_SAMPLE")
        return float(np.mean(np.var(embeddings, axis=0)))

    @staticmethod
    def _fields():
        return ("future_enc", "future_bias", "future_dec", "future_dec_bias",
                "teacher_enc", "teacher_bias", "pred_enc", "pred_bias",
                "pred_latent", "pred_latent_bias", "readout", "readout_bias")

    def validate(self):
        shapes = ((self.n, LATENT), (LATENT,), (LATENT, self.n), (self.n,),
                  (self.n, LATENT), (LATENT,), (DIM, WIDTH), (WIDTH,),
                  (WIDTH, LATENT), (LATENT,), (LATENT, self.n), (self.n,))
        for field, shape in zip(self._fields(), shapes):
            a = getattr(self, field)
            require(type(a) is np.ndarray and a.shape == shape
                    and bool(np.isfinite(a).all()) and bool((np.abs(a) <= 20).all()),
                    "JEPA4_WEIGHTS_VALID_" + field)
        require(type(self.windows) is int and type(self.steps) is int
                and self.windows * UPDATES == self.steps and
                0 <= self.windows < 5000, "JEPA4_UPDATE_COUNTS")

    def checkpoint(self):
        self.validate()
        return {"kind": self.kind, "steps": self.steps, "windows": self.windows,
                **{field: getattr(self, field).tolist()
                   for field in self._fields()}}

    @classmethod
    def restore(cls, data):
        require(type(data) is dict and set(data) ==
                {"kind", "steps", "windows", *cls._fields()},
                "JEPA4_HEAD_CHECKPOINT_KEYS")
        out = cls(data["kind"])
        out.steps, out.windows = data["steps"], data["windows"]
        for field in cls._fields():
            setattr(out, field, np.asarray(data[field], dtype=np.float64))
        out.validate()
        return out


class DirectLogistic:
    """Fully fitted same-information public-action conventional baseline."""
    def __init__(self):
        self.w = np.zeros((DIM, 12), dtype=np.float64)
        self.b = np.zeros(12, dtype=np.float64)
        self.steps = 0

    def predict(self, x):
        return _sigmoid(x @ self.w + self.b)

    def learn(self, x, y):
        require(np.asarray(y).shape == (12,), "JEPA4_DIRECT_TARGET")
        for _ in range(UPDATES):
            err = self.predict(x) - y
            self.w -= LR_DIRECT * np.outer(x, err) / 12
            self.b -= LR_DIRECT * err / 12
            self.steps += 1


class NativeFutureStateLearner:
    """An optional SIX-specialist+native cumulative model, never accepted main."""
    def __init__(self, original, sensory=None, reward=None):
        require(isinstance(original, NativeTemporalMultiLearner),
                "JEPA4_ORIGINAL_NATIVE_MODEL")
        self.original = original
        self.sensory = sensory if sensory is not None else FutureStateHead("sensors")
        self.reward = reward if reward is not None else FutureStateHead("reward")

    def forecast(self, views, actions, prior):
        x = observed_features(views, actions, prior)
        return (self.sensory.predict(x), self.reward.predict(x))

    def learn_window(self, x, window):
        s, r = targets(window)
        self.sensory.learn(x, s)
        self.reward.learn(x, r)

    def observe_native(self, identifier, views, row):
        self.original = self.original.observe(
            identifier, views, row)

    def checkpoint(self):
        prior = self.original.checkpoint()
        return canonical({
            "schema": SCHEMA, "native_sha256": digest(prior),
            "native_ascii": prior.decode("ascii"),
            "sensory": self.sensory.checkpoint(),
            "reward": self.reward.checkpoint(),
        })

    @classmethod
    def restore(cls, blob, expected_sha):
        require(type(blob) is bytes and digest(blob) == expected_sha,
                "JEPA4_CHECKPOINT_PIN")
        try:
            d = json.loads(blob.decode("ascii"))
            require(set(d) == {"schema", "native_sha256", "native_ascii",
                              "sensory", "reward"}
                    and d["schema"] == SCHEMA and canonical(d) == blob,
                    "JEPA4_CHECKPOINT_SCHEMA")
            original = NativeTemporalMultiLearner.restore(
                d["native_ascii"].encode("ascii"), d["native_sha256"])
            return cls(original, FutureStateHead.restore(d["sensory"]),
                       FutureStateHead.restore(d["reward"]))
        except (TypeError, ValueError, KeyError, OverflowError, UnicodeError,
                AttributeError) as exc:
            raise ValueError("YGG_JEPA2_04_CHECKPOINT_REJECTED") from exc

