"""Optional CKAD native GF(2) context basis; never accepted-model admission.

Reuses native evidence elimination and outcome-free support. Ten property bits
are numeric observations, not text tokens. A larger declared polynomial class
is a modeling assumption, not discovery of an unrestricted relationship family.
Only engineering witnesses are admitted until independent real-source custody
and a typed grounding join exist. A digest authenticates bytes, not their truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
import struct

from yggdrasil.native_relation_memory import NativeRelationMemory, NativeRelationReadout
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.ckad.native-context-basis.v1"
SOURCE_MODE = "engineering_fixture_only"
SOURCE_KIND = "engineering_public_binary_consequence"
MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 4096


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError("CKAD_NATIVE_" + reason)


def pin(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


@lru_cache(maxsize=65536)
def feature_row(mask, degree):
    """Pure input-derived monomials, indexed by their variable subset mask."""
    row = 1
    subset = mask
    while subset:
        if subset.bit_count() <= degree:
            row |= 1 << subset
        subset = (subset - 1) & mask
    return row


@lru_cache(maxsize=128)
def terms(bits, degree):
    return tuple(i for i in range(1 << (bits + 1)) if i.bit_count() <= degree)


@lru_cache(maxsize=256)
def support_map(rows):
    return {row.bit_length() - 1: row for row in rows}


@dataclass(frozen=True)
class _Profile:
    degree: int = 1
    coefficients: int = 0
    support: tuple = ()
    source_sha256: str = "0" * 64
    source_records: int = 0
    unique_inputs: int = 0


class NativeContextBasis:
    """Immutable staged profiles in the same seven-active/nine-retained slots.

    Checkpoints hold numeric coefficients and input-only support, not source
    events or per-query outcome answers. Unsupported consequences abstain.
    """
    __slots__ = ("_bits", "_profiles")

    def __init__(self, context_bits=10):
        require(type(context_bits) is int and 1 <= context_bits <= 10, "CONTEXT_BITS")
        self._bits = context_bits
        self._profiles = tuple(_Profile() for _ in range(16))

    @property
    def context_bits(self):
        return self._bits

    def _context(self, context):
        require(type(context) is int and 0 <= context < (1 << self._bits), "CONTEXT")
        return context

    def stage_fit(self, address, records, expected_source_sha256, *, max_degree=None,
                  retained=False, source_mode=SOURCE_MODE, source_kind=SOURCE_KIND):
        # Refuse factual triples/self-asserted real authority BEFORE interpreting
        # them as interventions. Real source admission is intentionally absent.
        require(source_mode == SOURCE_MODE and source_kind == SOURCE_KIND,
                "CAUSAL_GROUNDING_OR_SOURCE_AUTHORITY_ABSENT")
        slot = PublicCausalCells._address(address, retained)
        degree = self._bits + 1 if max_degree is None else max_degree
        require(type(degree) is int and 1 <= degree <= self._bits + 1, "DEGREE")
        require(type(records) is list and 0 < len(records) <= MAX_RECORDS, "RECORDS")
        require(pin(expected_source_sha256) and digest(canonical(records)) == expected_source_sha256,
                "SOURCE_PIN")
        observations = {}
        for row in records:
            require(type(row) is list and len(row) == 3, "PUBLIC_ROW")
            context, action, outcome = row
            self._context(context)
            PublicCausalCells._bit(action, "ACTION")
            PublicCausalCells._bit(outcome, "PUBLIC_OUTCOME")
            key = (context, action)
            require(key not in observations or observations[key] == outcome,
                    "STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE")
            observations[key] = outcome
        basis = {}
        try:
            for (context, action), outcome in sorted(observations.items()):
                NativeRelationMemory._insert(basis,
                    feature_row(context | (action << self._bits), degree), outcome)
        except ValueError as exc:
            if str(exc) == "NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE":
                raise ValueError("CKAD_NATIVE_MODEL_CLASS_INADEQUATE") from exc
            raise
        coefficients = 0
        for pivot in sorted(basis):
            row, rhs = basis[pivot]
            bit = rhs ^ ((coefficients & row).bit_count() & 1)
            coefficients |= bit << pivot
        reduced = NativeRelationReadout._reduced(row for row, _ in basis.values())
        profile = _Profile(degree, coefficients, reduced, expected_source_sha256,
                           len(records), len(observations))
        candidate = NativeContextBasis(self._bits)
        candidate._profiles = self._profiles[:slot] + (profile,) + self._profiles[slot + 1:]
        return candidate

    def predict(self, address, context, action, *, retained=False):
        slot = PublicCausalCells._address(address, retained)
        context = self._context(context)
        action = PublicCausalCells._bit(action, "ACTION")
        profile = self._profiles[slot]
        row = feature_row(context | (action << self._bits), profile.degree)
        remaining = row
        pivots = support_map(profile.support)
        while remaining:
            vector = pivots.get(remaining.bit_length() - 1)
            if vector is None:
                return None
            remaining ^= vector
        return (profile.coefficients & row).bit_count() & 1

    def predict_partial(self, address, value_mask, known_mask, action, *, retained=False):
        self._context(value_mask)
        self._context(known_mask)
        require(value_mask & ~known_mask == 0, "VALUE_WITHOUT_KNOWLEDGE")
        PublicCausalCells._address(address, retained)
        PublicCausalCells._bit(action, "ACTION")
        unknown = ((1 << self._bits) - 1) ^ known_mask
        subset = unknown
        result = None
        while True:
            prediction = self.predict(address, value_mask | subset, action, retained=retained)
            if prediction is None or (result is not None and prediction != result):
                return None
            result = prediction
            if subset == 0:
                return result
            subset = (subset - 1) & unknown

    def profile_info(self, address, *, retained=False):
        p = self._profiles[PublicCausalCells._address(address, retained)]
        return {"degree": p.degree, "rank": len(p.support),
                "feature_count": sum(math.comb(self._bits + 1, k) for k in range(p.degree + 1)),
                "source_records": p.source_records, "unique_inputs": p.unique_inputs,
                "source_sha256": p.source_sha256}

    def _document(self):
        profiles = []
        for p in self._profiles:
            feature_ids = terms(self._bits, p.degree)
            weights = [float((p.coefficients >> feature) & 1) for feature in feature_ids]
            profiles.append({"degree": p.degree,
                "weights_float32_le": struct.pack("<" + "f" * len(weights), *weights).hex(),
                "support_rows": [format(row, "x") for row in p.support],
                "source_sha256": p.source_sha256, "source_records": p.source_records,
                "unique_inputs": p.unique_inputs})
        return {"schema": SCHEMA, "context_bits": self._bits, "profiles": profiles,
                "source_mode": SOURCE_MODE, "accepted_native": False, "scientific_pass": False}

    def checkpoint(self):
        raw = canonical(self._document())
        require(len(raw) <= MAX_BYTES, "CHECKPOINT_CAPACITY")
        return raw

    @property
    def checkpoint_sha256(self):
        return digest(self.checkpoint())

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and pin(expected_sha256) and digest(raw) == expected_sha256, "CHECKPOINT_PIN")
        def unique(pairs):
            value = {}
            for key, val in pairs:
                require(key not in value, "DUPLICATE_JSON_KEY")
                value[key] = val
            return value
        try:
            doc = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(doc) is dict and set(doc) == {"schema", "context_bits", "profiles",
                    "source_mode", "accepted_native", "scientific_pass"}
                    and doc["schema"] == SCHEMA and doc["source_mode"] == SOURCE_MODE
                    and doc["accepted_native"] is False and doc["scientific_pass"] is False
                    and canonical(doc) == raw, "CHECKPOINT_CONTRACT")
            model = cls(doc["context_bits"])
            require(type(doc["profiles"]) is list and len(doc["profiles"]) == 16, "PROFILES")
            profiles = []
            for d in doc["profiles"]:
                require(type(d) is dict and set(d) == {"degree", "weights_float32_le",
                    "support_rows", "source_sha256", "source_records", "unique_inputs"}, "PROFILE_FIELDS")
                degree = d["degree"]
                require(type(degree) is int and 1 <= degree <= model._bits + 1, "PROFILE_DEGREE")
                feature_ids = terms(model._bits, degree)
                packed = d["weights_float32_le"]
                require(type(packed) is str and len(packed) == 8 * len(feature_ids), "WEIGHT_BYTES")
                weights = struct.unpack("<" + "f" * len(feature_ids), bytes.fromhex(packed))
                require(all(w in (0.0, 1.0) for w in weights)
                        and struct.pack("<" + "f" * len(weights), *(float(int(w)) for w in weights)).hex()
                        == packed, "BINARY_WEIGHTS")
                coefficients = sum(int(w) << feature for w, feature in zip(weights, feature_ids))
                entries = d["support_rows"]
                require(type(entries) is list and len(entries) <= len(feature_ids), "SUPPORT_COUNT")
                support = tuple(int(value, 16) for value in entries)
                allowed = sum(1 << feature for feature in feature_ids)
                require(all(type(v) is str and format(row, "x") == v and row > 0
                            and row & ~allowed == 0 for v, row in zip(entries, support))
                        and NativeRelationReadout._reduced(support) == support, "SUPPORT_SPACE")
                n, u = d["source_records"], d["unique_inputs"]
                require(type(n) is int and type(u) is int and 0 <= u <= n <= MAX_RECORDS
                        and u <= (1 << (model._bits + 1)) and len(support) <= u
                        and pin(d["source_sha256"]), "SOURCE_PROVENANCE")
                require((n > 0 and u > 0 and bool(support)) or
                        (n == u == 0 and not support and coefficients == 0), "EMPTY_PROFILE")
                profiles.append(_Profile(degree, coefficients, support, d["source_sha256"], n, u))
            model._profiles = tuple(profiles)
            require(model.checkpoint() == raw, "COLD_BYTES")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, struct.error) as exc:
            raise ValueError("CKAD_NATIVE_CHECKPOINT_REJECTED") from exc
