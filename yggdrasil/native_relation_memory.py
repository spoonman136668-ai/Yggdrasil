"""Optional, bounded native contextual causal relationships for Yggdrasil.

NKR-01: only actual public deterministic intervention consequences may program
numeric GF(2) weights. Nothing here reads heldout labels, clones WSP checkpoints,
or changes the accepted 16-cell PublicCausalCells learned bytes. This is an
opt-in developmental extension, not automatic accepted-state promotion.
"""
from __future__ import annotations

import hashlib
import json
import struct

from yggdrasil.public_causal_cells import PublicCausalCells


class NativeRelationMemory:
    """Sixteen native addresses, four context bits, two interventions, ten weights.

    A unique (address, context, intervention) has ONE consequence, independently
    of how often or by how many source labels that same fact is submitted.
    Different observations must be true environment consequences; source_ref is
    a trace label, not a trusted signature or proof of experimental qualification.
    """

    __slots__ = ("_events", "_basis", "_weights", "_rank", "_intern")

    SCHEMA = "yggdrasil.native-relations.v1"
    ADDRESSES = 16
    CONTEXT_BITS = 4
    WEIGHTS_PER_RELATION = 10
    MAX_OBSERVATIONS_PER_ADDRESS = 32
    MAX_UNIQUE_OBSERVATIONS = ADDRESSES * MAX_OBSERVATIONS_PER_ADDRESS
    MAX_CHECKPOINT_BYTES = 65000

    def __init__(self):
        self._events = [{} for _ in range(self.ADDRESSES)]
        self._basis = [{} for _ in range(self.ADDRESSES)]
        zero = tuple(0.0 for _ in range(self.WEIGHTS_PER_RELATION))
        self._weights = [zero for _ in range(self.ADDRESSES)]
        self._rank = [0] * self.ADDRESSES
        self._intern = {zero: zero}

    @staticmethod
    def _context(value):
        if type(value) is not int or not 0 <= value < 16:
            raise ValueError("NATIVE_RELATION_CONTEXT_INVALID")
        return value

    @staticmethod
    def _source(source_ref):
        if (type(source_ref) is not str or not 1 <= len(source_ref) <= 128
                or not source_ref.isascii()
                or any(ord(c) < 33 or ord(c) > 126 for c in source_ref)):
            raise ValueError("NATIVE_RELATION_SOURCE_INVALID")
        return source_ref

    @classmethod
    def _row(cls, context, action):
        return 1 | (context << 1) | (action << 5) | ((context * action) << 6)

    @staticmethod
    def _insert(basis, row, outcome):
        vector, rhs = row, outcome
        while vector:
            pivot = vector.bit_length() - 1
            old = basis.get(pivot)
            if old is None:
                basis[pivot] = (vector, rhs)
                return
            vector ^= old[0]
            rhs ^= old[1]
        if rhs:
            raise ValueError("NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE")

    @classmethod
    def _fit(cls, events):
        basis = {}
        for (context, action), (outcome, _source) in sorted(events.items()):
            cls._insert(basis, cls._row(context, action), outcome)
        coefficients = 0
        for pivot in sorted(basis):
            row, rhs = basis[pivot]
            bit = rhs ^ ((coefficients & row).bit_count() & 1)
            coefficients |= bit << pivot
        if coefficients >= (1 << cls.WEIGHTS_PER_RELATION):
            raise AssertionError("programmed coefficient out of range")
        weights = tuple(struct.unpack("<f", struct.pack("<f", float((coefficients >> k) & 1)))[0]
                        for k in range(cls.WEIGHTS_PER_RELATION))
        return basis, weights

    def observe_public(self, address, context, action, outcome, source_ref,
                       *, retained=False):
        """Idempotent actual-public evidence, atomically programmed without SGD.

        Identical readings are duplicates, NOT new learning. Contradictory
        outcomes are rejected, including contradictions implied by the current
        known linear/quadratic-grammar (here affine action-context) relations.
        """
        slot = PublicCausalCells._address(address, retained)
        context = self._context(context)
        action = PublicCausalCells._bit(action, "ACTION")
        outcome = PublicCausalCells._bit(outcome, "PUBLIC_OUTCOME")
        source_ref = self._source(source_ref)
        old = self._events[slot]
        key = (context, action)
        if key in old:
            if old[key][0] != outcome:
                raise ValueError("NATIVE_RELATION_CONFLICTING_DUPLICATE")
            return False
        if len(old) >= self.MAX_OBSERVATIONS_PER_ADDRESS:
            raise ValueError("NATIVE_RELATION_CAPACITY_EXCEEDED")
        # Build and fit privately before changing any native state.
        candidate = dict(old)
        candidate[key] = (outcome, source_ref)
        basis, weights = self._fit(candidate)
        self._events[slot] = candidate
        self._basis[slot] = basis
        self._rank[slot] = len(basis)
        # Canonicalize equivalent numerical relation templates across native
        # slots; address-bound evidence stays separate, as its meaning differs.
        intern = {}
        for i, existing in enumerate(self._weights):
            value = weights if i == slot else existing
            intern.setdefault(value, value)
        self._intern = intern
        self._weights = [intern[weights if i == slot else existing]
                         for i, existing in enumerate(self._weights)]
        return True

    def predict(self, address, context, action, *, retained=False):
        """Use programmed float32 synapses only when consequences are identified.

        Under-determined queries return None, never a guessed counterfactual.
        """
        slot = PublicCausalCells._address(address, retained)
        context = self._context(context)
        action = PublicCausalCells._bit(action, "ACTION")
        vector = self._row(context, action)
        basis = self._basis[slot]
        while vector:
            old = basis.get(vector.bit_length() - 1)
            if old is None:
                return None
            vector ^= old[0]
        row = self._row(context, action)
        return sum(int(weight) for k, weight in enumerate(self._weights[slot])
                   if (row >> k) & 1) & 1

    def rank(self, address, *, retained=False):
        return self._rank[PublicCausalCells._address(address, retained)]

    @property
    def unique_observations(self):
        return sum(map(len, self._events))

    @property
    def unique_programmed_profiles(self):
        return len({self._weights[i] for i in range(self.ADDRESSES)
                    if self._events[i]})

    def checkpoint(self):
        """Self-validating separate bounded checkpoint; legacy YPC1 untouched."""
        events = [[slot, context, action, value, source]
                  for slot, group in enumerate(self._events)
                  for (context, action), (value, source) in sorted(group.items())]
        data = {
            "schema": self.SCHEMA,
            "events": events,
            "ranks": self._rank,
            "weights_float32_le": [
                struct.pack("<10f", *weights).hex() for weights in self._weights
            ],
            "unique_programmed_profiles": self.unique_programmed_profiles,
        }
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        envelope = {"sha256": hashlib.sha256(encoded).hexdigest(), "data": data}
        checkpoint = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        if len(checkpoint) > self.MAX_CHECKPOINT_BYTES:
            raise ValueError("NATIVE_RELATION_CHECKPOINT_CAPACITY")
        return checkpoint

    @classmethod
    def restore(cls, checkpoint):
        if type(checkpoint) is not bytes or len(checkpoint) > cls.MAX_CHECKPOINT_BYTES:
            raise ValueError("NATIVE_RELATION_CHECKPOINT_INVALID")
        try:
            env = json.loads(checkpoint)
            data = env["data"]
            if data["schema"] != cls.SCHEMA:
                raise ValueError("schema")
            encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
            if hashlib.sha256(encoded).hexdigest() != env["sha256"]:
                raise ValueError("integrity")
            fresh = cls()
            for entry in data["events"]:
                if type(entry) is not list or len(entry) != 5:
                    raise ValueError("event")
                slot, context, action, outcome, source = entry
                if type(slot) is not int or not 0 <= slot < cls.ADDRESSES:
                    raise ValueError("slot")
                retained = slot >= PublicCausalCells.ACTIVE_SLOTS
                local = slot - PublicCausalCells.ACTIVE_SLOTS if retained else slot
                if not fresh.observe_public(local, context, action, outcome, source, retained=retained):
                    raise ValueError("duplicate")
            if fresh.checkpoint() != checkpoint:
                raise ValueError("replay mismatch")
            return fresh
        except (TypeError, KeyError, AttributeError, IndexError, ValueError, UnicodeError,
                json.JSONDecodeError) as exc:
            raise ValueError("NATIVE_RELATION_CHECKPOINT_REJECTED") from exc
