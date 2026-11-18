"""Opt-in source-grounded numeric causal relation compilation, developer-only.

Not a transformer, not a next-token learner, and not a novel learned grammar:
the 697 possible <=3-term four-input Boolean ANF weight patterns are a
supplied conventional hypothesis class. All surviving native weight vectors
are learned only from authenticated witnessed intervention outcomes.
No production/owner admission, new source mode, or hidden labels.
"""
from __future__ import annotations

import itertools
import json

from yggdrasil.native_context_basis import canonical, digest, feature_row, pin, require, SOURCE_MODE
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.ckad.native-causal-relation-posterior.v1"
GRAMMAR = "CONVENTIONAL_UNIFORM_ANF_AT_MOST_THREE_OF_16"
MAX_MODELS = 697
MAX_BYTES = 16384


def _all_models():
    for size in range(4):
        for positions in itertools.combinations(range(16), size):
            yield sum(1 << i for i in positions)


class NativeCausalRelationPosterior:
    """Immutable numeric weights conditioned on prior witnessed consequences."""

    __slots__ = ("_bits", "_models", "_source", "_observations")

    @classmethod
    def fit_checkpoint(cls, raw, expected_sha256):
        require(type(raw) is bytes and digest(raw) == expected_sha256 and pin(expected_sha256),
                "CAUSAL_POSTERIOR_INPUT_PIN")
        native = NativeContextAccumulator.restore(raw, expected_sha256)
        bits = native._model.context_bits
        require(bits == 3, "CAUSAL_POSTERIOR_THREE_CONTEXT_BITS_ONLY")
        profiles = native._model._profiles
        require(profiles[0].degree == bits + 1
                and all(p.source_records == 0 for p in profiles[1:]),
                "CAUSAL_POSTERIOR_SINGLE_NATIVE_SOURCE_VIEW")
        seen = native._seen[0]
        n = seen.bit_count()
        require(8 <= n <= 16 and n % 4 == 0 and profiles[0].source_records == n,
                "CAUSAL_POSTERIOR_TRAINING_COUNT")
        witnessed = []
        for x in range(16):
            if seen & (1 << x):
                context, action = x & 7, x >> 3
                y = native.predict(0, context, action)
                require(type(y) is int and y in (0, 1), "CAUSAL_POSTERIOR_REVEALED_OUTCOME")
                witnessed.append((feature_row(x, 4), y))
        solutions = tuple(weight for weight in _all_models()
                          if all(((weight & row).bit_count() & 1) == y
                                 for row, y in witnessed))
        require(len(solutions) <= MAX_MODELS, "CAUSAL_POSTERIOR_CAPACITY")
        obj = cls()
        obj._bits = bits
        obj._models = solutions
        obj._source = expected_sha256
        obj._observations = n
        return obj

    @property
    def model_count(self):
        return len(self._models)

    def predict_fraction(self, context, action):
        require(type(context) is int and 0 <= context < 1 << self._bits,
                "CAUSAL_POSTERIOR_CONTEXT")
        PublicCausalCells._bit(action, "ACTION")
        if not self._models:
            # Inadequate supplied grammar: no confident extrapolation.
            return (1, 2)
        row = feature_row(context | (action << self._bits), self._bits + 1)
        ones = sum(((weights & row).bit_count() & 1) for weights in self._models)
        return (ones, len(self._models))

    def info(self):
        return {"source_checkpoint_sha256": self._source,
                "observations": self._observations,
                "models": self.model_count,
                "grammar": GRAMMAR,
                "status": "PROVISIONAL_CONVENTIONAL_ONLY",
                "accepted_native": False,
                "scientific_pass": False}

    def checkpoint(self):
        data = {"schema": SCHEMA, "context_bits": self._bits,
                "models": self._models, "info": self.info(),
                "source_mode": SOURCE_MODE, "accepted_native": False,
                "scientific_pass": False}
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "CAUSAL_POSTERIOR_CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and pin(expected_sha256) and digest(raw) == expected_sha256,
                "CAUSAL_POSTERIOR_RESTORE_PIN")
        try:
            def unique(pairs):
                value = {}
                for key, val in pairs:
                    require(key not in value, "CAUSAL_POSTERIOR_DUPLICATE_KEY")
                    value[key] = val
                return value

            data = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(data) is dict and set(data) == {
                "schema", "context_bits", "models", "info", "source_mode",
                "accepted_native", "scientific_pass"}
                and data["schema"] == SCHEMA and data["source_mode"] == SOURCE_MODE
                and data["accepted_native"] is False and data["scientific_pass"] is False
                and canonical(data) == raw, "CAUSAL_POSTERIOR_RESTORE_SCHEMA")
            require(type(data["context_bits"]) is int and data["context_bits"] == 3,
                    "CAUSAL_POSTERIOR_RESTORE_BITS")
            models = data["models"]
            require(type(models) is list and len(models) <= MAX_MODELS
                    and all(type(w) is int and 0 <= w < (1 << 16)
                            and w.bit_count() <= 3 for w in models)
                    and sorted(models, key=lambda w: (w.bit_count(),
                        tuple(i for i in range(16) if w & (1 << i)))) == models
                    and len(set(models)) == len(models),
                    "CAUSAL_POSTERIOR_RESTORE_MODELS")
            info = data["info"]
            require(type(info) is dict and pin(info["source_checkpoint_sha256"])
                    and type(info["observations"]) is int
                    and info["observations"] in (8, 12, 16),
                    "CAUSAL_POSTERIOR_RESTORE_INFO")
            obj = cls()
            obj._bits = data["context_bits"]
            obj._models = tuple(models)
            obj._source = info["source_checkpoint_sha256"]
            obj._observations = info["observations"]
            require(obj.info() == info and obj.checkpoint() == raw,
                    "CAUSAL_POSTERIOR_RESTORE_COLD_BYTES")
            return obj
        except (ValueError, TypeError, KeyError, AttributeError, UnicodeError) as exc:
            raise ValueError("CKAD_NATIVE_CAUSAL_POSTERIOR_REJECTED") from exc
