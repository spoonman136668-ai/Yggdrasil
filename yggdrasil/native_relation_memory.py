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

    __slots__ = ("_events", "_basis", "_weights", "_rank", "_intern", "_exceptions")

    SCHEMA = "yggdrasil.native-relations.v1"
    VERIFIED_SCHEMA = "yggdrasil.native-relations.v2"
    MAX_VERIFIED_CHECKPOINT_BYTES = 160000
    ADDRESSES = 16
    CONTEXT_BITS = 4
    WEIGHTS_PER_RELATION = 10
    MAX_OBSERVATIONS_PER_ADDRESS = 32
    MAX_UNIQUE_OBSERVATIONS = ADDRESSES * MAX_OBSERVATIONS_PER_ADDRESS
    MAX_CHECKPOINT_BYTES = 65000

    def __init__(self):
        self._events = [{} for _ in range(self.ADDRESSES)]
        self._exceptions = [{} for _ in range(self.ADDRESSES)]
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
        # The verified extension shares exactly one canonical evidence identity.
        # Do not store an already-evidenced consequence in both stores.
        if key in self._exceptions[slot]:
            if self._exceptions[slot][key][0] != outcome:
                raise ValueError("NATIVE_RELATION_CONFLICTING_DUPLICATE")
            return False
        if key in old:
            if old[key][0] != outcome:
                raise ValueError("NATIVE_RELATION_CONFLICTING_DUPLICATE")
            return False
        if len(old) + len(self._exceptions[slot]) >= self.MAX_OBSERVATIONS_PER_ADDRESS:
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

    def observe_public_verified(self, address, context, action, outcome,
                                source_ref, *, retained=False):
        """Explicitly record fresh public truth outside the affine grammar.

        The legacy API still rejects inconsistent observations. This opt-in
        addition retains them as *address-bound verified exceptions*, never
        rewriting or duplicating a previously programmed synaptic coefficient.
        Upstream callers remain responsible for ensuring source_ref denotes a
        genuine observed intervention consequence, not an inferred label.
        """
        slot = PublicCausalCells._address(address, retained)
        context = self._context(context)
        action = PublicCausalCells._bit(action, "ACTION")
        outcome = PublicCausalCells._bit(outcome, "PUBLIC_OUTCOME")
        source_ref = self._source(source_ref)
        key = (context, action)
        for store in (self._events[slot], self._exceptions[slot]):
            if key in store:
                if store[key][0] != outcome:
                    raise ValueError("NATIVE_RELATION_CONFLICTING_DUPLICATE")
                return False
        if (len(self._events[slot]) + len(self._exceptions[slot]) >=
                self.MAX_OBSERVATIONS_PER_ADDRESS):
            raise ValueError("NATIVE_RELATION_CAPACITY_EXCEEDED")
        try:
            return self.observe_public(address, context, action, outcome,
                                       source_ref, retained=retained)
        except ValueError as exc:
            if str(exc) != "NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE":
                raise
        # Rejected by *model grammar*, not by genuine public source evidence.
        # No base weights, bases, ranks or existing source records are modified.
        self._exceptions[slot][key] = (outcome, source_ref)
        return True

    def observed_action_pair(self, address, context, *, retained=False):
        """Exact observed consequences for both actions, or None. No guesses."""
        slot = PublicCausalCells._address(address, retained)
        context = self._context(context)
        values = []
        for action in (0, 1):
            key = (context, action)
            evidence = self._events[slot].get(key)
            if evidence is None:
                evidence = self._exceptions[slot].get(key)
            if evidence is None:
                return None
            values.append(evidence[0])
        return tuple(values)

    @property
    def verified_exception_count(self):
        return sum(map(len, self._exceptions))

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
        return sum(map(len, self._events)) + self.verified_exception_count

    @property
    def unique_programmed_profiles(self):
        return len({self._weights[i] for i in range(self.ADDRESSES)
                    if self._events[i]})

    def compact_inference(self):
        """Read-only research view, without observation or answer records.

        Retains affine coefficients and outcome-free input support. The full
        training checkpoint remains the provenance source. Verified exceptions
        cannot be represented, so export rejects rather than dropping them.
        This method does not activate any accepted-model capability.
        """
        return NativeRelationReadout.from_memory(self)

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
        if not self.verified_exception_count:
            # Exact legacy NKR-01 bytes and SHA-256, even after the upgrade.
            return checkpoint
        # Only exception observations are additional; the original base
        # checkpoint remains one canonical copy, not an expanded duplicate.
        repaired = {
            "schema": self.VERIFIED_SCHEMA,
            "base_checkpoint_ascii": checkpoint.decode("ascii"),
            "verified_exceptions": [
                [slot, context, action, value, source]
                for slot, group in enumerate(self._exceptions)
                for (context, action), (value, source) in sorted(group.items())
            ]
        }
        canonical = json.dumps(repaired, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True).encode("ascii")
        envelope2 = {"data": repaired, "sha256": hashlib.sha256(canonical).hexdigest()}
        out = json.dumps(envelope2, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
        if len(out) > self.MAX_VERIFIED_CHECKPOINT_BYTES:
            raise ValueError("NATIVE_RELATION_VERIFIED_CHECKPOINT_CAPACITY")
        return out

    @classmethod
    def restore(cls, checkpoint):
        if type(checkpoint) is not bytes or len(checkpoint) > cls.MAX_VERIFIED_CHECKPOINT_BYTES:
            raise ValueError("NATIVE_RELATION_CHECKPOINT_INVALID")
        try:
            env = json.loads(checkpoint)
            data = env["data"]
            if data["schema"] == cls.VERIFIED_SCHEMA:
                canonical = json.dumps(data, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=True).encode("ascii")
                if hashlib.sha256(canonical).hexdigest() != env["sha256"]:
                    raise ValueError("verified integrity")
                base = data["base_checkpoint_ascii"]
                if type(base) is not str or not base.isascii():
                    raise ValueError("bad canonical base")
                fresh = cls.restore(base.encode("ascii"))
                entries = data["verified_exceptions"]
                if type(entries) is not list or len(entries) > cls.MAX_UNIQUE_OBSERVATIONS:
                    raise ValueError("invalid verified entries")
                for row in entries:
                    if type(row) is not list or len(row) != 5:
                        raise ValueError("bad verified observation")
                    slot, context, action, outcome, source = row
                    if type(slot) is not int or not 0 <= slot < cls.ADDRESSES:
                        raise ValueError("invalid verified slot")
                    ret = slot >= PublicCausalCells.ACTIVE_SLOTS
                    addr = slot - PublicCausalCells.ACTIVE_SLOTS if ret else slot
                    if not fresh.observe_public_verified(
                            addr, context, action, outcome, source, retained=ret):
                        raise ValueError("duplicated verified evidence")
                    if (context, action) not in fresh._exceptions[slot]:
                        raise ValueError("unnecessary duplicate verified exception")
                if fresh.checkpoint() != checkpoint:
                    raise ValueError("verified cold replay mismatch")
                return fresh
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


class NativeRelationReadout:
    """NKR-18 compact read-only view of the SAME native affine coefficients.

    Contains no training events, source text, outcome lookup table or external
    data dependency. Input-support row spaces prevent unsupported extrapolation
    *within the declared affine family*. They do not prove that family true.
    A pinned digest proves byte identity, never source truth or admission.
    """
    __slots__ = ("_raw", "_support", "_weights", "_training_sha256")
    SCHEMA = "yggdrasil.native-relations.compact-inference.v1"
    MAX_BYTES = 16384

    @staticmethod
    def _canonical(doc):
        return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")

    @staticmethod
    def _reduced(vectors):
        # Unique reduced row-space representation; these rows contain INPUT
        # features only, not right-hand sides/observed outcomes.
        pivots = {}
        for value in vectors:
            row = value
            for pivot in sorted(pivots, reverse=True):
                if row & (1 << pivot):
                    row ^= pivots[pivot]
            if row:
                pivots[row.bit_length() - 1] = row
        for low in sorted(pivots):
            for high in sorted(pivots):
                if high > low and pivots[high] & (1 << low):
                    pivots[high] ^= pivots[low]
        return tuple(pivots[p] for p in sorted(pivots, reverse=True))

    def __init__(self, raw, expected_sha256):
        try:
            if (type(raw) is not bytes or len(raw) > self.MAX_BYTES
                    or type(expected_sha256) is not str
                    or len(expected_sha256) != 64
                    or hashlib.sha256(raw).hexdigest() != expected_sha256):
                raise ValueError("pin or size")
            doc = json.loads(raw.decode("ascii"))
            if (type(doc) is not dict or set(doc) != {
                    "schema", "training_checkpoint_sha256", "support_rows",
                    "weights_float32_le", "accepted_native", "scientific_pass"}
                    or doc["schema"] != self.SCHEMA
                    or doc["accepted_native"] is not False
                    or doc["scientific_pass"] is not False
                    or raw != self._canonical(doc)):
                raise ValueError("schema or canonical form")
            pin = doc["training_checkpoint_sha256"]
            if (type(pin) is not str or len(pin) != 64
                    or any(c not in "0123456789abcdef" for c in pin)):
                raise ValueError("training provenance pin")
            groups, profiles = doc["support_rows"], doc["weights_float32_le"]
            if (type(groups) is not list or len(groups) != 16
                    or type(profiles) is not list or len(profiles) != 16):
                raise ValueError("address capacity")
            support, weights = [], []
            for rows, packed in zip(groups, profiles):
                if (type(rows) is not list or len(rows) > 10
                        or any(type(r) is not int or not 0 < r < 1024 for r in rows)
                        or tuple(rows) != self._reduced(rows)):
                    raise ValueError("support row space")
                if (type(packed) is not str or len(packed) != 80
                        or any(c not in "0123456789abcdef" for c in packed)):
                    raise ValueError("coefficient bytes")
                values = struct.unpack("<10f", bytes.fromhex(packed))
                if (any(v not in (0.0, 1.0) for v in values)
                        or struct.pack("<10f", *(float(int(v)) for v in values)).hex()
                        != packed or (not rows and any(values))):
                    raise ValueError("non-binary or unsupported coefficients")
                support.append(tuple(rows))
                weights.append(tuple(int(v) for v in values))
            self._raw = raw
            self._support, self._weights = tuple(support), tuple(weights)
            self._training_sha256 = pin
        except (ValueError, TypeError, KeyError, UnicodeError, struct.error) as exc:
            raise ValueError("NATIVE_COMPACT_CHECKPOINT_REJECTED") from exc

    @classmethod
    def from_memory(cls, memory):
        if not isinstance(memory, NativeRelationMemory):
            raise ValueError("NATIVE_COMPACT_TRAINER_INVALID")
        if memory.verified_exception_count:
            raise ValueError("NATIVE_COMPACT_CANNOT_DROP_VERIFIED_EXCEPTIONS")
        doc = {
            "schema": cls.SCHEMA,
            "training_checkpoint_sha256": hashlib.sha256(memory.checkpoint()).hexdigest(),
            "support_rows": [list(cls._reduced(v for v, _ in group.values()))
                             for group in memory._basis],
            "weights_float32_le": [struct.pack("<10f", *w).hex()
                                   for w in memory._weights],
            "accepted_native": False, "scientific_pass": False,
        }
        raw = cls._canonical(doc)
        return cls(raw, hashlib.sha256(raw).hexdigest())

    def checkpoint(self):
        return self._raw

    @property
    def checkpoint_sha256(self):
        return hashlib.sha256(self._raw).hexdigest()

    @property
    def training_checkpoint_sha256(self):
        return self._training_sha256

    def predict(self, address, context, action, *, retained=False):
        slot = PublicCausalCells._address(address, retained)
        context = NativeRelationMemory._context(context)
        action = PublicCausalCells._bit(action, "ACTION")
        row = NativeRelationMemory._row(context, action)
        remaining = row
        for vector in self._support[slot]:
            if remaining & (1 << (vector.bit_length() - 1)):
                remaining ^= vector
        if remaining:
            return None
        return sum(w for bit, w in enumerate(self._weights[slot])
                   if row & (1 << bit)) & 1
