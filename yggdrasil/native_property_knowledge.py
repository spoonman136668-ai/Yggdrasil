"""CKAD optional engineering-only property state joined to native relations.

Explicit binary facts are STORED knowledge, not learned semantic understanding.
Relation coefficients are learned by NativeContextBasis. Namespace/hash binding
is a synthetic-source integrity check, never real-world causal authentication.
"""
from __future__ import annotations
from functools import lru_cache
import json
import struct

from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest, pin, SOURCE_MODE
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.ckad.native-property-knowledge.v1"
PROPERTY_KIND = "engineering_observed_binary_property"
CONSEQUENCE_KIND = "engineering_observed_entity_consequence"
MAX_BYTES = 10 * 1024 * 1024


def need(ok, reason):
    if not ok:
        raise ValueError("CKAD_KNOWLEDGE_" + reason)


class NativePropertyKnowledge:
    """Immutable native known/value planes and independently staged relations."""
    __slots__ = ("_namespace", "_entities", "_bits", "_known", "_values",
                 "_property_sources", "_relation_sources", "_relations")

    def __init__(self, namespace, *, entities=10000, context_bits=10):
        need(type(namespace) is str and 1 <= len(namespace) <= 96 and namespace.isascii()
             and all(33 <= ord(c) < 127 for c in namespace), "NAMESPACE")
        need(type(entities) is int and 1 <= entities <= 10000, "ENTITIES")
        self._relations = NativeContextBasis(context_bits)
        self._namespace = namespace; self._entities = entities; self._bits = context_bits
        self._known = (0,) * entities; self._values = (0,) * entities
        self._property_sources = (); self._relation_sources = ("0" * 64,) * 16

    def _copy(self):
        candidate = NativePropertyKnowledge(self._namespace, entities=self._entities, context_bits=self._bits)
        candidate._known = self._known; candidate._values = self._values
        candidate._property_sources = self._property_sources
        candidate._relation_sources = self._relation_sources; candidate._relations = self._relations
        return candidate

    @property
    def property_count(self):
        return sum(mask.bit_count() for mask in self._known)

    def _entity(self, entity):
        need(type(entity) is int and 0 <= entity < self._entities, "ENTITY")
        return entity

    def _admit(self, namespace, mode):
        need(namespace == self._namespace and mode == SOURCE_MODE,
             "UNVERIFIED_OR_MISMATCHED_SOURCE_JOIN")

    def stage_properties(self, records, expected_sha256, *, source_namespace,
                         source_mode=SOURCE_MODE, source_kind=PROPERTY_KIND):
        self._admit(source_namespace, source_mode)
        need(source_kind == PROPERTY_KIND, "FACTS_ARE_NOT_CAUSAL_LABELS")
        need(type(records) is list and 0 < len(records) <= 100000, "PROPERTY_ROWS")
        need(pin(expected_sha256) and digest(canonical(records)) == expected_sha256, "SOURCE_PIN")
        if expected_sha256 in self._property_sources:
            return self
        need(len(self._property_sources) < 16, "SOURCE_LEDGER_CAPACITY")
        known = list(self._known); values = list(self._values)
        for row in records:
            need(type(row) is list and len(row) == 3, "PROPERTY_ROW")
            entity, property_bit, value = row
            self._entity(entity)
            need(type(property_bit) is int and 0 <= property_bit < self._bits, "PROPERTY_BIT")
            PublicCausalCells._bit(value, "PROPERTY_VALUE")
            bit = 1 << property_bit
            need(not known[entity] & bit or ((values[entity] >> property_bit) & 1) == value,
                 "CONFLICTING_PROPERTY")
            known[entity] |= bit
            if value: values[entity] |= bit
        candidate = self._copy()
        candidate._known = tuple(known); candidate._values = tuple(values)
        candidate._property_sources = self._property_sources + (expected_sha256,)
        return candidate

    def stage_relation(self, address, observations, expected_sha256, *, source_namespace,
                       max_degree=2, retained=False, source_mode=SOURCE_MODE,
                       source_kind=CONSEQUENCE_KIND):
        self._admit(source_namespace, source_mode)
        need(source_kind == CONSEQUENCE_KIND, "FACTS_ARE_NOT_CAUSAL_LABELS")
        slot = PublicCausalCells._address(address, retained)
        need(type(observations) is list and 0 < len(observations) <= 4096, "CONSEQUENCE_ROWS")
        need(pin(expected_sha256) and digest(canonical(observations)) == expected_sha256, "SOURCE_PIN")
        rows = []
        for row in observations:
            need(type(row) is list and len(row) == 3, "CONSEQUENCE_ROW")
            entity, action, outcome = row
            self._entity(entity)
            PublicCausalCells._bit(action, "ACTION")
            PublicCausalCells._bit(outcome, "PUBLIC_OUTCOME")
            need(self._known[entity] == (1 << self._bits) - 1, "INCOMPLETE_TRAINING_CONTEXT")
            rows.append([self._values[entity], action, outcome])
        relations = self._relations.stage_fit(address, rows, digest(canonical(rows)),
                                              max_degree=max_degree, retained=retained)
        candidate = self._copy(); candidate._relations = relations
        candidate._relation_sources = (self._relation_sources[:slot] + (expected_sha256,)
                                       + self._relation_sources[slot + 1:])
        return candidate

    @lru_cache(maxsize=32768)
    def _partial(self, address, values, known, action, retained):
        # The entire staged model is immutable; model identity scopes this cache.
        return self._relations.predict_partial(address, values, known, action, retained=retained)

    def predict_entity(self, address, entity, action, *, visible_mask=None, retained=False):
        self._entity(entity)
        mask = (1 << self._bits) - 1 if visible_mask is None else visible_mask
        need(type(mask) is int and 0 <= mask < (1 << self._bits), "VISIBILITY")
        PublicCausalCells._address(address, retained)
        PublicCausalCells._bit(action, "ACTION")
        known = self._known[entity] & mask
        return self._partial(address, self._values[entity] & known, known, action, retained)

    def checkpoint(self):
        planes = b"".join(struct.pack("<HH", k, v) for k, v in zip(self._known, self._values))
        raw = canonical({"schema": SCHEMA, "source_namespace": self._namespace,
            "entities": self._entities, "context_bits": self._bits,
            "known_value_planes_uint16le": planes.hex(), "property_sources": list(self._property_sources),
            "relation_sources": list(self._relation_sources),
            "native_relations_ascii": self._relations.checkpoint().decode("ascii"),
            "source_mode": SOURCE_MODE, "accepted_native": False, "scientific_pass": False})
        need(len(raw) <= MAX_BYTES, "CHECKPOINT_CAPACITY")
        return raw

    @property
    def checkpoint_sha256(self):
        return digest(self.checkpoint())

    @classmethod
    def restore(cls, raw, expected_sha256):
        need(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and pin(expected_sha256)
             and digest(raw) == expected_sha256, "CHECKPOINT_PIN")
        def unique(pairs):
            result = {}
            for k, v in pairs:
                need(k not in result, "DUPLICATE_JSON_KEY")
                result[k] = v
            return result
        try:
            d = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            need(set(d) == {"schema", "source_namespace", "entities", "context_bits",
                "known_value_planes_uint16le", "property_sources", "relation_sources",
                "native_relations_ascii", "source_mode", "accepted_native", "scientific_pass"}
                and d["schema"] == SCHEMA and d["source_mode"] == SOURCE_MODE
                and d["accepted_native"] is False and d["scientific_pass"] is False
                and canonical(d) == raw, "CHECKPOINT_CONTRACT")
            model = cls(d["source_namespace"], entities=d["entities"], context_bits=d["context_bits"])
            planes = bytes.fromhex(d["known_value_planes_uint16le"])
            need(len(planes) == 4 * model._entities, "PROPERTY_PLANES")
            pairs = list(struct.iter_unpack("<HH", planes))
            limit = (1 << model._bits) - 1
            need(all(k <= limit and v & ~k == 0 for k, v in pairs), "UNKNOWN_PROPERTY_VALUE")
            model._known = tuple(k for k, v in pairs); model._values = tuple(v for k, v in pairs)
            sources = d["property_sources"]
            need(type(sources) is list and len(sources) <= 16 and len(set(sources)) == len(sources)
                 and all(pin(s) for s in sources) and (not model.property_count or sources), "PROPERTY_SOURCES")
            model._property_sources = tuple(sources)
            sources = d["relation_sources"]
            need(type(sources) is list and len(sources) == 16 and all(pin(s) for s in sources), "RELATION_SOURCES")
            model._relation_sources = tuple(sources)
            native = d["native_relations_ascii"].encode("ascii")
            model._relations = NativeContextBasis.restore(native, digest(native))
            need(model._relations.context_bits == model._bits, "CONTEXT_JOIN")
            need(model.checkpoint() == raw, "COLD_BYTES")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, AttributeError) as exc:
            raise ValueError("CKAD_KNOWLEDGE_CHECKPOINT_REJECTED") from exc
