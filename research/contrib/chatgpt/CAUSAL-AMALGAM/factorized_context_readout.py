"""FCR01-S: read-only, independently weighted causal-stage forecasts.

Engineering-only research adapter. It never observes a world, updates native
models, claims causal authority, or changes an accepted checkpoint. The source
learner must accept every public witness before this adapter may advance.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

SCHEMA = "yggdrasil.fcr01.factorized-readout.dev.v1"
MAX_BYTES = 256 * 1024
REFRESH_RATE = Fraction(1, 32)  # existing native context refresh, not tuned


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(cond, tag):
    if not cond:
        raise ValueError("FCR01_" + tag)


def _bit(value):
    require(type(value) is int and value in (0, 1), "PUBLIC_BIT")
    return value


def _weights(values):
    values = tuple(values)
    require(bool(values) and all(isinstance(x, Fraction) and x >= 0 for x in values)
            and sum(values) == 1, "POSTERIOR_WEIGHTS")
    return values


def _identities(native):
    return digest(canonical([list(model[:3]) for model in native._context_models]))


def _posterior(weights, probabilities, value):
    _bit(value)
    require(len(weights) == len(probabilities), "MODEL_COUNT")
    terms = tuple(w * (p if value else 1 - p)
                  for w, p in zip(weights, probabilities))
    require(all(isinstance(p, Fraction) and 0 < p < 1 for p in probabilities)
            and sum(terms) > 0, "SOURCE_PREDICTION")
    total = sum(terms)
    return _weights(tuple(t / total for t in terms))


def _refresh(weights, prior):
    return _weights(tuple((1 - REFRESH_RATE) * x + REFRESH_RATE * y
                          for x, y in zip(weights, prior)))


class FactorizedContextReadout:
    """Alternative readout of *existing* context experts, not a new trainer.

    Each new *native-admitted* episode contributes two separate prequential
    likelihood updates. Unlike the native joint-context posterior, the reward
    posterior does not condition on a transition model's popularity.
    """
    __slots__ = ("_native", "_native_sha", "_models", "_transition", "_reward")

    def __init__(self, native, transition=None, reward=None):
        require(native._context_start is not None and len(native._context_models) >= 2,
                "CONTEXT_REQUIRED")
        self._native = native
        self._native_sha = digest(native.checkpoint())
        self._models = _identities(native)
        n = len(native._context_models)
        source = _weights(native._context_weights)
        self._transition = _weights(source if transition is None else transition)
        self._reward = _weights(source if reward is None else reward)
        require(len(self._transition) == len(self._reward) == n, "MODEL_COUNT")

    def _intact(self):
        require(digest(self._native.checkpoint()) == self._native_sha
                and _identities(self._native) == self._models,
                "NATIVE_SOURCE_DRIFT")

    def transition(self, view, first):
        self._intact()
        _bit(first)
        probabilities = self._native._context_predictions(view, first, None, None)
        return sum((w * p for w, p in zip(self._transition, probabilities)), Fraction())

    def reward(self, view, first, state, second):
        self._intact()
        _bit(first); _bit(state); _bit(second)
        probabilities = self._native._context_predictions(view, first, state, second)
        return sum((w * p for w, p in zip(self._reward, probabilities)), Fraction())

    def advance(self, native):
        """Advance only for exactly one additional *native-admitted* public row.

        Score on this snapshot BEFORE binding the successor. This prevents
        using the already-updated novel expert to predict its training row.
        """
        self._intact()
        old = self._native._ledger
        new = native._ledger
        require(len(new) == len(old) + 1 and new[:-1] == old,
                "REPLAY_OR_NONADMITTED_WITNESS")
        require(native._context_start == self._native._context_start
                and len(native._context_models) == len(self._native._context_models)
                and native._refresh_start == self._native._refresh_start,
                "EXPERT_SET_DRIFT")
        for previous, next_ in zip(self._native._context_models, native._context_models):
            require(previous[:3] == next_[:3] or
                    (self._native._context_novel and previous is self._native._context_models[-1]
                     and next_ is native._context_models[-1] and previous[0] == next_[0]),
                    "EXPERT_PROVENANCE_DRIFT")
        identity, views, first, state, second, reward = new[-1]
        require(type(identity) is str and len(identity) == 64
                and all(c in "0123456789abcdef" for c in identity)
                and type(views) is tuple and len(views) == 2,
                "PUBLIC_WITNESS")
        for item in (first, state, second, reward):
            _bit(item)
        require(new[-1][1] == views, "PUBLIC_VIEW")
        view = views[0]
        stage1 = self._native._context_predictions(view, first, None, None)
        stage2 = self._native._context_predictions(view, first, state, second)
        t = _posterior(self._transition, stage1, state)
        r = _posterior(self._reward, stage2, reward)
        if self._native._refresh_start is not None:
            # Equal existing refresh policy; no new scientific tuning.
            prior = self._native._context_prior()
            t = _refresh(t, prior)
            r = _refresh(r, prior)
        return FactorizedContextReadout(native, t, r)

    def checkpoint(self):
        self._intact()
        data = {"schema": SCHEMA, "native_sha256": self._native_sha,
                "models_sha256": self._models,
                "transition_weights": [[v.numerator, v.denominator] for v in self._transition],
                "reward_weights": [[v.numerator, v.denominator] for v in self._reward],
                "scientific_pass": False, "accepted_native": False}
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, native, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and type(expected_sha256) is str and digest(raw) == expected_sha256,
                "COLD_PIN")
        try:
            def unique(pairs):
                result = {}
                for name, value in pairs:
                    require(name not in result, "COLD_DUPLICATE_KEY")
                    result[name] = value
                return result
            data = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(data) is dict and set(data) == {
                "schema", "native_sha256", "models_sha256",
                "transition_weights", "reward_weights", "scientific_pass", "accepted_native"
            } and data["schema"] == SCHEMA and data["scientific_pass"] is False
                    and data["accepted_native"] is False and canonical(data) == raw
                    and data["native_sha256"] == digest(native.checkpoint())
                    and data["models_sha256"] == _identities(native), "COLD_CONTRACT")
            def read_weights(items):
                require(type(items) is list and len(items) == len(native._context_models),
                        "COLD_WEIGHTS")
                values = []
                for pair in items:
                    require(type(pair) is list and len(pair) == 2
                            and all(type(i) is int for i in pair) and pair[1] > 0,
                            "COLD_FRACTION")
                    f = Fraction(*pair)
                    require([f.numerator, f.denominator] == pair, "COLD_CANONICAL_FRACTION")
                    values.append(f)
                return _weights(values)
            out = cls(native, read_weights(data["transition_weights"]),
                      read_weights(data["reward_weights"]))
            require(out.checkpoint() == raw, "COLD_REPLAY")
            return out
        except (ValueError, KeyError, TypeError, UnicodeError, ZeroDivisionError) as err:
            raise ValueError("FCR01_COLD_REJECTED") from err
