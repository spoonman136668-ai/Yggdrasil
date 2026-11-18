"""Yggdrasil native, cumulative, temporal-history JEPA-style learning (development).

This is NOT Meta's pretrained V-JEPA2. Public action-consequence records only,
a frozen stop-gradient binary teacher, two independently trainable latent
specialists, and the existing source-authenticated NativeMultiLearner.
In particular, old native evidence AND two earlier learned experts are retained
and continue updating; no model or history gets restarted when worlds change.
"""
from __future__ import annotations

import json
from math import cos, exp, isfinite, sin, tanh

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_jepa2_multilearner import (
    NativeMultiLearner, _bit, _views,
)

SCHEMA = "yggdrasil.ckad.native-temporal-multilearner.v1"
HISTORY, HIDDEN, LATENT = 8, 8, 2
LR, STEPS, CLIP = 0.06, 3, 5.0
BASE_BLEND, TEMPORAL_BLEND = 0.90, 0.10
MAX_BYTES = 1048576
MAX_EPISODES = 1000


def _sigmoid(x):
    return 1 / (1 + exp(-x)) if x >= 0 else exp(x) / (1 + exp(x))


def _clip(x):
    return min(CLIP, max(-CLIP, x))


def _features(views, extras, ledger, kind):
    _views(views)
    need = 1 if kind == "transition" else 3
    require(type(extras) is tuple and len(extras) == need, "JEPA3_ACTION_ARITY")
    for i in extras:
        _bit(i)
    require(type(ledger) in (tuple, list), "JEPA3_LEDGER_TYPE")
    # Exactly the last eight VERIFIED, previously witnessed actions/outcomes.
    # Causal context and nuisance view bits are projected separately; all
    # windows are computed strictly from previous original-native episodes.
    features = []
    for view in views:
        x = [2 * _bit(v) - 1 for v in (*view, *extras)]
        past = list(ledger[-HISTORY:])
        for age in range(HISTORY):
            if age < len(past):
                event = past[-age-1]
                require(type(event) is tuple and len(event) == 6,
                        "JEPA3_SOURCE_EVENT_CONTRACT")
                _, pv, px1, ps2, px2, py = event
                _views(pv)
                # Relative alignment to CURRENT public stable context and
                # action choice; no private regime or source identifier enters.
                scale = 1.0 / (age + 1)
                x.extend([
                    scale * (1 if pv[0][0] == view[0] else -1),
                    scale * (1 if px1 == extras[0] else -1),
                    scale * (2 * _bit(ps2) - 1),
                    scale * (2 * _bit(px2) - 1),
                    scale * (2 * _bit(py) - 1),
                ])
            else:
                x.extend((0., 0., 0., 0., 0.))
        features.append(tuple(x))
    return tuple(features)


class TemporalLatentSpecialist:
    """Two public projections -> learned history/action-conditioned latent."""

    def __init__(self, kind):
        require(kind in ("transition", "reward"), "JEPA3_KIND")
        self.kind = kind
        self.dimension = 2 + (1 if kind == "transition" else 3) + 5*HISTORY
        salt = 13 if kind == "transition" else 17
        self.encoder = [
            [0.055 * sin((j + 2)*(i + 1)*(salt + 1)) for i in range(self.dimension)]
            for j in range(HIDDEN)
        ]
        self.encoder_bias = [0.0] * HIDDEN
        self.predictor = [
            [0.055 * cos((k + 2)*(j + 1)*(salt + 2)) for j in range(HIDDEN)]
            for k in range(LATENT)
        ]
        self.predictor_bias = [0.0] * LATENT
        self.steps = 0

    def _forward(self, x):
        h = [tanh(sum(w * v for w, v in zip(row, x)) + self.encoder_bias[j])
             for j, row in enumerate(self.encoder)]
        y = [sum(w*v for w,v in zip(row,h)) + self.predictor_bias[k]
             for k,row in enumerate(self.predictor)]
        return h, y

    def probability(self, views, extras, prior_source):
        xs = _features(views, extras, prior_source, self.kind)
        p = sum((self._forward(x)[1][0] - self._forward(x)[1][1])
                for x in xs) / len(xs)
        prob = _sigmoid(2*p)
        require(isfinite(prob) and 0 <= prob <= 1, "JEPA3_PREDICTION")
        return prob

    def observe(self, views, extras, prior_source, label):
        xs = _features(views, extras, prior_source, self.kind)
        label = _bit(label)
        teacher = (1., -1.) if label else (-1., 1.)
        d = self.dimension
        for _ in range(STEPS):
            ge = [[0.0] * d for _ in range(HIDDEN)]
            geb = [0.0] * HIDDEN
            gp = [[0.0] * HIDDEN for _ in range(LATENT)]
            gpb = [0.0] * LATENT
            for x in xs:
                h, out = self._forward(x)
                e = (out[0] - teacher[0], out[1] - teacher[1])
                for k in range(LATENT):
                    gpb[k] += e[k]
                    for j in range(HIDDEN):
                        gp[k][j] += e[k] * h[j]
                for j in range(HIDDEN):
                    dh = sum(e[k]*self.predictor[k][j] for k in range(LATENT))
                    dh *= 1 - h[j]*h[j]
                    geb[j] += dh
                    for i in range(d):
                        ge[j][i] += dh*x[i]
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
        require(len(self.encoder) == HIDDEN and
                all(type(row) is list and len(row) == self.dimension
                    for row in self.encoder) and
                len(self.encoder_bias) == HIDDEN and
                len(self.predictor) == LATENT and
                all(type(row) is list and len(row) == HIDDEN
                    for row in self.predictor) and
                len(self.predictor_bias) == LATENT and
                type(self.steps) is int and 0 <= self.steps <= MAX_EPISODES*STEPS,
                "JEPA3_PARAMETER_SHAPE")
        vals = [x for row in (self.encoder + self.predictor) for x in row]
        vals += self.encoder_bias + self.predictor_bias
        require(all(type(x) is float and isfinite(x) and abs(x) <= 20
                    for x in vals), "JEPA3_PARAMETER_NUMERIC")

    def data(self):
        self._validate()
        return {"kind": self.kind, "encoder": self.encoder,
                "encoder_bias": self.encoder_bias, "predictor": self.predictor,
                "predictor_bias": self.predictor_bias, "steps": self.steps}

    @classmethod
    def from_data(cls, d, kind):
        require(type(d) is dict and set(d) == {
            "kind", "encoder", "encoder_bias", "predictor",
            "predictor_bias", "steps"
        } and d["kind"] == kind, "JEPA3_RESTORED_KEYS")
        obj = cls(kind)
        obj.encoder, obj.encoder_bias = d["encoder"], d["encoder_bias"]
        obj.predictor, obj.predictor_bias = d["predictor"], d["predictor_bias"]
        obj.steps = d["steps"]
        obj._validate()
        return obj

    def clone(self):
        return self.from_data(json.loads(json.dumps(self.data())), self.kind)


def _fit_history(ledger, *, mispair=False):
    t, r = TemporalLatentSpecialist("transition"), TemporalLatentSpecialist("reward")
    for i, (_, views, first, next_state, second, reward) in enumerate(ledger):
        prior = ledger[:i]
        label_t, label_r = ((ledger[i-1][3], ledger[i-1][5])
                            if mispair and i else (next_state, reward))
        t.observe(views, (first,), prior, label_t)
        r.observe(views, (first, next_state, second), prior, label_r)
    return t, r


class NativeTemporalMultiLearner:
    """One cumulative native experience model, four independently trained heads.

    Two original JEPA2-02 experts and original NativeEpisodeExperience remain
    untouched on bootstrap, then keep updating together with 2 new temporal
    specialists on each new authenticated witnessed event.
    """

    def __init__(self, base, transition, reward, source_count):
        require(isinstance(base, NativeMultiLearner), "JEPA3_BASE")
        require(isinstance(transition, TemporalLatentSpecialist) and
                isinstance(reward, TemporalLatentSpecialist), "JEPA3_TEMPORAL_TYPES")
        self.base, self.transition, self.reward = base, transition, reward
        self.source_count = source_count

    @classmethod
    def bootstrap(cls, base_raw, expected_sha):
        base = NativeMultiLearner.restore(base_raw, expected_sha)
        pinned = base.checkpoint()
        t,r = _fit_history(base.native._ledger)
        require(base.checkpoint() == pinned, "JEPA3_OLD_MODEL_RESTART")
        return cls(base,t,r,len(base.native._ledger))

    def predict(self, views, first, next_state, second):
        prior = self.base.native._ledger
        original = self.base.predict(views, first, next_state, second, stream=True)
        temporal = (self.transition.probability(views, (first,), prior),
                    self.reward.probability(
                        views, (first,next_state,second), prior))
        native = original["native"]
        blend = tuple(BASE_BLEND*a + TEMPORAL_BLEND*b
                      for a,b in zip(native,temporal))
        return {"native":native,"one_step":original["jepa"],
                "temporal":temporal,"blend":blend}

    def observe(self, identifier, views, row):
        prior = self.base.native._ledger
        updated = self.base.observe(identifier,views,row)
        if updated is self.base:
            return self
        t,r = self.transition.clone(), self.reward.clone()
        t.observe(views,(row["x1"],),prior,row["s2"])
        r.observe(views,(row["x1"],row["s2"],row["x2"]),prior,row["y"])
        return NativeTemporalMultiLearner(updated,t,r,self.source_count)

    def checkpoint(self):
        old = self.base.checkpoint()
        d = {"schema":SCHEMA,"base_ascii":old.decode("ascii"),
             "base_sha256":digest(old),"source_count":self.source_count,
             "temporal_transition":self.transition.data(),
             "temporal_reward":self.reward.data()}
        raw = canonical(d)
        require(len(raw) <= MAX_BYTES,"JEPA3_CHECKPOINT_LIMIT")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and pin(expected_sha) and digest(raw) == expected_sha,
                "JEPA3_CHECKPOINT_PIN")
        try:
            d=json.loads(raw.decode("ascii"))
            require(type(d) is dict and set(d) == {
                "schema","base_ascii","base_sha256","source_count",
                "temporal_transition","temporal_reward"
            } and d["schema"] == SCHEMA and canonical(d) == raw,
                    "JEPA3_CHECKPOINT_SCHEMA")
            base_raw=d["base_ascii"].encode("ascii")
            base=NativeMultiLearner.restore(base_raw,d["base_sha256"])
            source_count=d["source_count"]
            require(type(source_count) is int and
                    1 <= source_count <= len(base.native._ledger) <= MAX_EPISODES,
                    "JEPA3_SOURCE_COUNT")
            t=TemporalLatentSpecialist.from_data(d["temporal_transition"],"transition")
            r=TemporalLatentSpecialist.from_data(d["temporal_reward"],"reward")
            require(t.steps == r.steps == len(base.native._ledger)*STEPS,
                    "JEPA3_STEPS_SOURCE_PARITY")
            # Full authentic causal witness replay rejects forged latent
            # parameters even with an otherwise valid rehashed ZIP/checkpoint.
            rt,rr = _fit_history(base.native._ledger)
            require(canonical(t.data()) == canonical(rt.data()) and
                    canonical(r.data()) == canonical(rr.data()),
                    "JEPA3_WEIGHTS_SOURCE_PARITY")
            obj=cls(base,t,r,source_count)
            require(obj.checkpoint() == raw, "JEPA3_COLD_REPLAY")
            return obj
        except (ValueError, TypeError, KeyError, OverflowError, UnicodeError,
                AttributeError, RecursionError) as exc:
            raise ValueError("YGG_JEPA3_CHECKPOINT_REJECTED") from exc

