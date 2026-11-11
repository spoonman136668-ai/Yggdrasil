"""WSP-13: evidence-built conjunctive synaptic feature INSTANCES.

Five-bit observations arrive from the outside. The model starts with fixed
degree<=2 features; the identities of higher-order conjunctions are ABSENT
from its compiled feature grammar. Residual observations cause a homogeneous
threshold network to allocate blank synaptic slots and store stimulus bits.
No novel primitive TYPES, physics, or zero-information rule learning claimed.
"""
from __future__ import annotations

import hashlib
import json

N = 5
BASE = tuple(sorted((m for m in range(1 << N)
                     if m.bit_count() <= 2), key=lambda m: (m.bit_count(), m)))
# TRIPLES and HIDDEN are EVALUATOR CUSTODY ONLY. NumericRuleBuilder never
# indexes these lists, nor preloads their features/labels.
TRIPLES = tuple(m for m in range(1 << N) if m.bit_count() == 3)
HIDDEN = tuple(m for m in range(1 << N) if m.bit_count() >= 4)
SLOTS = 10
BASE_CODE = 0xA65D
GRADIENT_STEPS = 0
MAGIC = b"WSP13"
SCHEMA = "wsp13.evidence-built-composite.v1"


def stimulus(mask: int) -> tuple[int, ...]:
    if type(mask) is not int or mask not in range(1 << N):
        raise ValueError("WSP13_INVALID_CONTEXT_MASK")
    return tuple((mask >> j) & 1 for j in range(N))


def checked_context(context: tuple[int, ...]) -> tuple[int, ...]:
    if (type(context) is not tuple or len(context) != N or
            any(type(x) is not int or x not in (0, 1) for x in context)):
        raise ValueError("WSP13_INVALID_CONTEXT")
    return context


def checked_label(label: int) -> int:
    if type(label) is not int or label not in (0, 1):
        raise ValueError("WSP13_INVALID_LABEL")
    return label


class ThresholdVM:
    """One elementary rule: integer weighted sum >= integer threshold."""
    def __init__(self):
        self.gates = 0

    def fire(self, pairs: tuple[tuple[int, int], ...], threshold: int) -> int:
        if (type(pairs) is not tuple or type(threshold) is not int or
                any(type(p) is not tuple or len(p) != 2 or
                    type(p[0]) is not int or p[0] not in (0, 1) or
                    type(p[1]) is not int for p in pairs)):
            raise ValueError("WSP13_INVALID_GATE")
        self.gates += 1
        return int(sum(input_bit * weight for input_bit, weight in pairs)
                   >= threshold)

    def and_(self, *xs: int) -> int:
        return self.fire(tuple((x, 1) for x in xs), len(xs))

    def or_(self, *xs: int) -> int:
        return self.fire(tuple((x, 1) for x in xs), 1)

    def not_(self, x: int) -> int:
        return self.fire(((x, -1),), 0)

    def xor(self, a: int, b: int) -> int:
        present = self.or_(a, b)
        both = self.and_(a, b)
        return self.fire(((present, 1), (both, -1)), 1)

    def monomial(self, x: tuple[int, ...], mask: int) -> int:
        return self.and_(*(x[i] for i in range(N) if (mask >> i) & 1))

    def equal_context(self, x: tuple[int, ...], mask: int) -> int:
        return self.and_(*(x[i] if (mask >> i) & 1 else self.not_(x[i])
                           for i in range(N)))

    def subset_slot(self, x: tuple[int, ...], occupied: int,
                    address: list[int]) -> int:
        # A newly written address encodes a conjunction of required bits.
        # Each missing required input drives a numerical violation neuron.
        violations = [self.fire(((address[i], 1), (x[i], -1)), 1)
                      for i in range(N)]
        return self.and_(occupied, self.not_(self.or_(*violations)))


class NumericRuleBuilder:
    """All task-specific knowledge is in writable synaptic coefficients.

    Python validates the low-order observation ORDER, not the selected rule
    or the addresses of composite features. The ten composite addresses are
    all-zero on construction and populated by numerical eligibility gates.
    """
    def __init__(self):
        self.base_weights = [0] * len(BASE)
        self.base_seen = [0] * len(BASE)
        self.witness_occupied = [0] * SLOTS
        self.witness_addresses = [[0] * N for _ in range(SLOTS)]
        self.feature_occupied = [0] * SLOTS
        self.feature_addresses = [[0] * N for _ in range(SLOTS)]
        self.fault = 0
        self.vm = ThresholdVM()

    @staticmethod
    def architecture_sha256() -> str:
        grammar = ("WSP13|five-bit-degree<=2-v1|base=" +
                   ",".join(map(str, BASE)) +
                   "|10 generic blank 5-bit feature slots|" +
                   "threshold-only subset-and-parity-v1")
        return hashlib.sha256(grammar.encode("ascii")).hexdigest()

    def _base_prediction(self, x: tuple[int, ...]) -> int:
        current = 0
        for mask, weight in zip(BASE, self.base_weights):
            activated = self.vm.monomial(x, mask)
            synaptic_output = self.vm.fire(((activated, weight),), 1)
            current = self.vm.xor(current, synaptic_output)
        return current

    def predict(self, x: tuple[int, ...]) -> int | None:
        checked_context(x)
        if self.fault:
            return None
        current = self._base_prediction(x)
        for occupied, address in zip(self.feature_occupied,
                                     self.feature_addresses):
            triggered = self.vm.subset_slot(x, occupied, address)
            current = self.vm.xor(current, triggered)
        return current

    def _allocate(self, occupied: list[int], addresses: list[list[int]],
                  x: tuple[int, ...], should_write: int) -> None:
        """Priority chosen exclusively by numeric first-free eligibility."""
        already_chosen = 0
        for i in range(SLOTS):
            claim = self.vm.and_(should_write,
                                 self.vm.not_(occupied[i]),
                                 self.vm.not_(already_chosen))
            addresses[i] = [
                self.vm.or_(old, self.vm.and_(claim, bit))
                for old, bit in zip(addresses[i], x)]
            occupied[i] = self.vm.or_(occupied[i], claim)
            already_chosen = self.vm.or_(already_chosen, claim)

    def observe_training(self, x: tuple[int, ...], label: int) -> bool:
        checked_context(x)
        checked_label(label)
        if self.fault:
            raise ValueError("WSP13_FAULTED_TRAINING")
        base_count = sum(self.base_seen)
        if base_count < len(BASE):
            # External custody: only validates the frozen training schedule.
            if x != stimulus(BASE[base_count]):
                raise ValueError("WSP13_BASE_WITNESS_OUT_OF_ORDER")
            residual = self.vm.xor(self.predict(x), label)
            for i, mask in enumerate(BASE):
                match = self.vm.equal_context(x, mask)
                eligible = self.vm.and_(match, self.vm.not_(self.base_seen[i]))
                write = self.vm.and_(eligible, residual)
                self.base_weights[i] = self.vm.or_(self.base_weights[i], write)
                self.base_seen[i] = self.vm.or_(self.base_seen[i], eligible)
            return True

        if sum(self.witness_occupied) >= SLOTS:
            raise ValueError("WSP13_TRAINING_EXPOSURE_EXHAUSTED")
        if sum(x) != 3:
            raise ValueError("WSP13_EXPECTED_THREE_ACTIVE_BITS")
        # All witnessed triple contexts have exactly three active bits.
        # Subset match therefore also detects an *exact* repeated witness.
        duplicate = self.vm.or_(*(
            self.vm.subset_slot(x, occupied, addr)
            for occupied, addr in zip(self.witness_occupied,
                                      self.witness_addresses)))
        if duplicate:
            raise ValueError("WSP13_DUPLICATE_TRIPLE_WITNESS")
        residual = self.vm.xor(self.predict(x), label)
        # Record EVERY real witness, including no-residual observations.
        self._allocate(self.witness_occupied, self.witness_addresses, x, 1)
        # Create a new composite ONLY on real evidence of missing influence.
        self._allocate(self.feature_occupied, self.feature_addresses, x, residual)
        return True

    def verify_new_witness(self, x: tuple[int, ...], label: int) -> bool:
        checked_context(x)
        checked_label(label)
        if not self.is_complete():
            raise ValueError("WSP13_INCOMPLETE_TRAINING")
        if self.fault:
            return False
        discrepancy = self.vm.xor(self.predict(x), label)
        self.fault = self.vm.or_(self.fault, discrepancy)
        return not bool(self.fault)

    def is_complete(self) -> bool:
        return sum(self.base_seen) == len(BASE) and                sum(self.witness_occupied) == SLOTS

    def _canonical(self) -> bool:
        groups = (self.base_weights, self.base_seen,
                  self.witness_occupied, self.feature_occupied)
        if (any(type(group) is not list for group in groups) or
                len(self.base_weights) != len(BASE) or
                len(self.base_seen) != len(BASE) or
                len(self.witness_occupied) != SLOTS or
                len(self.feature_occupied) != SLOTS or
                type(self.fault) is not int or self.fault not in (0, 1)):
            return False
        if any(type(b) is not int or b not in (0, 1)
               for group in groups for b in group):
            return False
        if (any(type(rows) is not list or len(rows) != SLOTS
                for rows in (self.witness_addresses, self.feature_addresses)) or
                any(type(row) is not list or len(row) != N or
                    any(type(b) is not int or b not in (0, 1) for b in row)
                    for rows in (self.witness_addresses, self.feature_addresses)
                    for row in rows)):
            return False
        for seen in (self.base_seen, self.witness_occupied,
                     self.feature_occupied):
            count = sum(seen)
            if seen != [1]*count + [0]*(len(seen)-count):
                return False
        if any(weight and not seen for weight, seen
               in zip(self.base_weights, self.base_seen)):
            return False
        for occ, addresses in ((self.witness_occupied, self.witness_addresses),
                               (self.feature_occupied, self.feature_addresses)):
            if any(sum(addr) != (3 if used else 0)
                   for used, addr in zip(occ, addresses)):
                return False
        witnesses = {tuple(x) for used, x in zip(self.witness_occupied,
                                                self.witness_addresses) if used}
        features = [tuple(x) for used, x in zip(self.feature_occupied,
                                               self.feature_addresses) if used]
        return (len(witnesses) == sum(self.witness_occupied)
                and len(set(features)) == len(features)
                and all(feature in witnesses for feature in features))

    def snapshot(self) -> bytes:
        if not self._canonical():
            raise ValueError("WSP13_NONCANONICAL_STATE")
        raw = json.dumps({
            "schema": SCHEMA,
            "architecture_sha256": self.architecture_sha256(),
            "base_weights": self.base_weights,
            "base_seen": self.base_seen,
            "witness_occupied": self.witness_occupied,
            "witness_addresses": self.witness_addresses,
            "feature_occupied": self.feature_occupied,
            "feature_addresses": self.feature_addresses,
            "fault": self.fault
        }, sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = MAGIC + len(raw).to_bytes(4, "big") + raw
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw: bytes) -> "NumericRuleBuilder":
        if (type(raw) is not bytes or len(raw) < 42 or len(raw) > 16384
                or raw[:5] != MAGIC or len(raw) - 41 !=
                int.from_bytes(raw[5:9], "big") or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP13_CHECKPOINT_REJECTED")
        try:
            data = json.loads(raw[9:-32].decode("ascii"))
            expected = {"schema", "architecture_sha256", "base_weights",
                        "base_seen", "witness_occupied", "witness_addresses",
                        "feature_occupied", "feature_addresses", "fault"}
            if (type(data) is not dict or set(data) != expected or
                    data["schema"] != SCHEMA or
                    data["architecture_sha256"] != cls.architecture_sha256()):
                raise ValueError("invalid schema")
            c = cls()
            for key in ("base_weights", "base_seen", "witness_occupied",
                        "witness_addresses", "feature_occupied",
                        "feature_addresses", "fault"):
                setattr(c, key, data[key])
            if not c._canonical() or c.snapshot() != raw:
                raise ValueError("invalid checkpoint state")
            return c
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError):
            raise ValueError("WSP13_CHECKPOINT_REJECTED") from None


def oracle_truth(cubic_code: int, x: tuple[int, ...]) -> int:
    """Evaluator only: hidden code must NEVER be supplied to model runtime."""
    checked_context(x)
    if type(cubic_code) is not int or cubic_code not in range(1 << 10):
        raise ValueError("WSP13_INVALID_ORACLE_CODE")
    base = sum((BASE_CODE >> j) & 1
               for j, mask in enumerate(BASE)
               if all(x[i] for i in range(N) if (mask >> i) & 1)) % 2
    cubic = sum((cubic_code >> j) & 1
                for j, mask in enumerate(TRIPLES)
                if all(x[i] for i in range(N) if (mask >> i) & 1)) % 2
    return base ^ cubic


def symbolic_exact(observations: tuple, x: tuple[int, ...]) -> int:
    """Independent GF2 Moebius inversion with identical public information."""
    checked_context(x)
    if type(observations) is not tuple or len(observations) != 26:
        raise ValueError("WSP13_SYMBOLIC_INVALID_OBSERVATIONS")
    observed = {}
    for record in observations:
        if type(record) is not tuple or len(record) != 2:
            raise ValueError("WSP13_SYMBOLIC_INVALID_OBSERVATIONS")
        bits, label = record
        checked_context(bits)
        checked_label(label)
        address = sum(b << i for i, b in enumerate(bits))
        if address in observed:
            raise ValueError("WSP13_SYMBOLIC_DUPLICATE")
        observed[address] = label
    basis = BASE + TRIPLES
    if set(observed) != set(basis):
        raise ValueError("WSP13_SYMBOLIC_MISSING_WITNESS")
    coefficients = {}
    for mask in basis:
        value = observed[mask]
        for earlier, coefficient in coefficients.items():
            if earlier & mask == earlier:
                value ^= coefficient
        coefficients[mask] = value
    address = sum(b << i for i, b in enumerate(x))
    return sum(coefficient for mask, coefficient in coefficients.items()
               if mask & address == mask) % 2
