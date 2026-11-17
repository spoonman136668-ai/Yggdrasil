"""Optional stationary same-relation accumulation; engineering witnesses only.

The learned coefficient vector and input support jointly encode sufficient
linear constraints. Earlier raw outcomes need not be replayed or checkpointed.
This does not discover a model class or authenticate real-world causal truth.
"""
from __future__ import annotations
import json

from yggdrasil.native_context_basis import (
    NativeContextBasis, _Profile, canonical, digest, feature_row, pin, require,
    SOURCE_MODE, SOURCE_KIND, MAX_RECORDS,
)
from yggdrasil.native_relation_memory import NativeRelationMemory, NativeRelationReadout
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.ckad.native-context-accumulator.v1"
MAX_BYTES = 10 * 1024 * 1024
MAX_BATCHES = 64


class NativeContextAccumulator:
    """Immutable fixed-class cumulative evidence in sixteen native slots."""
    __slots__ = ("_model", "_seen", "_batches")

    def __init__(self, context_bits=10):
        self._model = NativeContextBasis(context_bits)
        self._seen = (0,) * 16
        self._batches = ((),) * 16

    def stage_update(self, address, records, expected_source_sha256, *, max_degree=None,
                     retained=False, source_mode=SOURCE_MODE, source_kind=SOURCE_KIND):
        # The unchanged native fitter validates public tuples, engineering-only
        # source type, byte pin and internal consistency before any replay return.
        fresh = NativeContextBasis(self._model.context_bits).stage_fit(
            address, records, expected_source_sha256, max_degree=max_degree,
            retained=retained, source_mode=source_mode, source_kind=source_kind)
        slot = PublicCausalCells._address(address, retained)
        previous = self._model._profiles[slot]
        added = fresh._profiles[slot]
        batches = self._batches[slot]
        require(not batches or previous.degree == added.degree, "CUMULATIVE_CLASS_DRIFT")
        if any(h == expected_source_sha256 for h, n in batches):
            return self
        require(len(batches) < MAX_BATCHES and previous.source_records + len(records) <= MAX_RECORDS,
                "CUMULATIVE_CAPACITY")
        # Input-only RREF rows are constraints, with their outcomes calculated
        # from the learned vector; this preserves ALL old identified answers.
        basis = {}
        for row in previous.support:
            NativeRelationMemory._insert(basis, row, (row & previous.coefficients).bit_count() & 1)
        try:
            for row in added.support:
                NativeRelationMemory._insert(basis, row, (row & added.coefficients).bit_count() & 1)
        except ValueError as exc:
            if str(exc) == "NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE":
                raise ValueError("CKAD_NATIVE_CUMULATIVE_MODEL_INADEQUATE") from exc
            raise
        coefficients = 0
        for pivot in sorted(basis):
            row, rhs = basis[pivot]
            coefficients |= (rhs ^ ((coefficients & row).bit_count() & 1)) << pivot
        seen = self._seen[slot]
        for context, action, outcome in records:
            seen |= 1 << (context | (action << self._model.context_bits))
        ledger = batches + ((expected_source_sha256, len(records)),)
        support = NativeRelationReadout._reduced(row for row, rhs in basis.values())
        profile = _Profile(added.degree, coefficients, support, digest(canonical(ledger)),
                           previous.source_records + len(records), seen.bit_count())
        candidate = NativeContextAccumulator(self._model.context_bits)
        candidate._model._profiles = (self._model._profiles[:slot] + (profile,)
                                     + self._model._profiles[slot + 1:])
        candidate._seen = self._seen[:slot] + (seen,) + self._seen[slot + 1:]
        candidate._batches = self._batches[:slot] + (ledger,) + self._batches[slot + 1:]
        return candidate

    def predict(self, address, context, action, *, retained=False):
        return self._model.predict(address, context, action, retained=retained)

    def predict_partial(self, address, value_mask, known_mask, action, *, retained=False):
        return self._model.predict_partial(address, value_mask, known_mask, action, retained=retained)

    def profile_info(self, address, *, retained=False):
        slot = PublicCausalCells._address(address, retained)
        return dict(self._model.profile_info(address, retained=retained), batches=len(self._batches[slot]))

    def checkpoint(self):
        raw = canonical({"schema": SCHEMA, "native_basis_ascii": self._model.checkpoint().decode("ascii"),
            "observed_input_masks": [format(s, "x") for s in self._seen],
            "batch_ledgers": self._batches, "source_mode": SOURCE_MODE,
            "accepted_native": False, "scientific_pass": False})
        require(len(raw) <= MAX_BYTES, "CUMULATIVE_CHECKPOINT_CAPACITY")
        return raw

    @property
    def checkpoint_sha256(self):
        return digest(self.checkpoint())

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and pin(expected_sha256)
                and digest(raw) == expected_sha256, "CUMULATIVE_CHECKPOINT_PIN")
        def unique(pairs):
            result = {}
            for k, v in pairs:
                require(k not in result, "CUMULATIVE_DUPLICATE_KEY")
                result[k] = v
            return result
        try:
            d = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(d) is dict and set(d) == {"schema", "native_basis_ascii",
                    "observed_input_masks", "batch_ledgers", "source_mode", "accepted_native", "scientific_pass"}
                    and d["schema"] == SCHEMA and d["source_mode"] == SOURCE_MODE
                    and d["accepted_native"] is False and d["scientific_pass"] is False
                    and canonical(d) == raw, "CUMULATIVE_CHECKPOINT_CONTRACT")
            base = d["native_basis_ascii"].encode("ascii")
            model = NativeContextBasis.restore(base, digest(base))
            candidate = cls(model.context_bits)
            masks, ledgers = d["observed_input_masks"], d["batch_ledgers"]
            require(type(masks) is list and type(ledgers) is list and len(masks) == len(ledgers) == 16,
                    "CUMULATIVE_SLOTS")
            seen, batches = [], []
            for slot, (mask, ledger) in enumerate(zip(masks, ledgers)):
                require(type(mask) is str and 0 < len(mask) <= 512, "CUMULATIVE_INPUT_MASK")
                bits = int(mask, 16)
                require(bits >= 0 and bits.bit_length() <= 1 << (model.context_bits + 1)
                        and format(bits, "x") == mask, "CUMULATIVE_INPUT_MASK")
                require(type(ledger) is list and len(ledger) <= MAX_BATCHES
                        and all(type(e) is list and len(e) == 2 and pin(e[0])
                                and type(e[1]) is int and 0 < e[1] <= MAX_RECORDS for e in ledger)
                        and len({e[0] for e in ledger}) == len(ledger), "CUMULATIVE_LEDGER")
                p = model._profiles[slot]
                require(sum(n for h, n in ledger) == p.source_records
                        and bits.bit_count() == p.unique_inputs
                        and p.source_sha256 == (digest(canonical(ledger)) if ledger else "0" * 64),
                        "CUMULATIVE_PROVENANCE")
                rows = (feature_row(i, p.degree) for i in range(1 << (model.context_bits + 1)) if bits & (1 << i))
                require(NativeRelationReadout._reduced(rows) == p.support, "CUMULATIVE_SUPPORT")
                seen.append(bits); batches.append(tuple((h, n) for h, n in ledger))
            candidate._model = model; candidate._seen = tuple(seen); candidate._batches = tuple(batches)
            require(candidate.checkpoint() == raw, "CUMULATIVE_COLD_BYTES")
            return candidate
        except (ValueError, TypeError, KeyError, UnicodeError, AttributeError) as exc:
            raise ValueError("CKAD_NATIVE_CUMULATIVE_CHECKPOINT_REJECTED") from exc
