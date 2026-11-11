"""WSP-12 numeric threshold rule selection from public observed outcomes.

The FEATURE GRAMMAR (constant, four first-order, six pairwise monomials),
frozen observation schedule and threshold rules are supplied by the programmer.
No hidden task coefficient, truth table, or evaluator function enters this model.
Each selected coefficient is a PLASTIC SYNAPTIC WEIGHT, initially zero.
"""
from __future__ import annotations

import hashlib
import json

GRAMMAR = (0, 1, 2, 4, 8, 3, 5, 9, 6, 10, 12)
HIDDEN = (7, 11, 13, 14, 15)
MAGIC = b"WSP12"
SCHEMA = "wsp12.numeric-monomial-state.v1"
GRADIENT_STEPS = 0


def checked_bits(bits: tuple[int, ...]) -> tuple[int, ...]:
    if (type(bits) is not tuple or len(bits) != 4 or
            any(type(b) is not int or b not in (0, 1) for b in bits)):
        raise ValueError("WSP12_INVALID_CONTEXT")
    return bits


def checked_label(label: int) -> int:
    if type(label) is not int or label not in (0, 1):
        raise ValueError("WSP12_INVALID_OUTCOME")
    return label


def context(mask: int) -> tuple[int, ...]:
    """Public stimulus schedule, not an evaluator outcome lookup."""
    if type(mask) is not int or mask not in range(16):
        raise ValueError("WSP12_INVALID_MASK")
    return tuple((mask >> j) & 1 for j in range(4))


class ThresholdVM:
    """Only computational primitive: a weighted sum >= numeric threshold.

    The helpers are fixed circuits of this same primitive; no model-side
    Python XOR or task-indexed operation dispatch.
    """
    def __init__(self) -> None:
        self.threshold_calls = 0

    def fire(self, inputs: tuple[tuple[int, int], ...], cutoff: int) -> int:
        if (type(inputs) is not tuple or type(cutoff) is not int or
                any(type(x) is not tuple or len(x) != 2 or
                    type(x[0]) is not int or x[0] not in (0, 1) or
                    type(x[1]) is not int for x in inputs)):
            raise ValueError("WSP12_INVALID_NUMERIC_GATE")
        self.threshold_calls += 1
        return int(sum(value * weight for value, weight in inputs) >= cutoff)

    def and_(self, *bits: int) -> int:
        return self.fire(tuple((b, 1) for b in bits), len(bits))

    def or_(self, *bits: int) -> int:
        return self.fire(tuple((b, 1) for b in bits), 1)

    def not_(self, bit: int) -> int:
        return self.fire(((bit, -1),), 0)

    def xor(self, a: int, b: int) -> int:
        any_on = self.or_(a, b)
        both_on = self.and_(a, b)
        return self.fire(((any_on, 1), (both_on, -1)), 1)

    def recognizes(self, bits: tuple[int, ...], mask: int) -> int:
        # Fixed polarity encoding is NOT a discovered feature or operation.
        polarities = tuple(b if (mask >> j) & 1 else 1-b
                           for j, b in enumerate(bits))
        return self.and_(*polarities)

    def monomial(self, bits: tuple[int, ...], mask: int) -> int:
        return self.and_(*(bits[j] for j in range(4) if (mask >> j) & 1))


class NumericRuleMemory:
    """Select the active supplied monomial rule coefficients in synaptic weights.

    Input validation/schedule are external Python custody; every candidate
    write gate, residual, feature recognizer, and prediction is numerical.
    """
    def __init__(self) -> None:
        self.weights = [0] * len(GRAMMAR)
        self.seen = [0] * len(GRAMMAR)
        self.fault = 0
        self.vm = ThresholdVM()

    @staticmethod
    def architecture_sha256() -> str:
        descriptor = ("wsp12-four-bit-degree2-threshold-v1|" +
                      ",".join(str(x) for x in GRAMMAR) +
                      "|sum-threshold-xor3|numeric-monotone-OR-write")
        return hashlib.sha256(descriptor.encode("ascii")).hexdigest()

    def predict(self, bits: tuple[int, ...]) -> int | None:
        checked_bits(bits)
        if self.fault:
            return None
        value = 0
        for monomial, synaptic_weight in zip(GRAMMAR, self.weights):
            activated = self.vm.monomial(bits, monomial)
            # Synaptic memory is read as the coefficient on the connection.
            contribution = self.vm.fire(((activated, synaptic_weight),), 1)
            value = self.vm.xor(value, contribution)
        return value

    def observe(self, bits: tuple[int, ...], label: int) -> bool:
        checked_bits(bits)
        checked_label(label)
        if self.fault:
            return False
        # Python validates only the predeclared exposure order and prevents
        # information leakage. It never chooses a rule coefficient to write.
        count = sum(self.seen)
        if count < len(GRAMMAR) and bits != context(GRAMMAR[count]):
            raise ValueError("WSP12_OBSERVATION_OUT_OF_ORDER")
        prior = self.predict(bits)
        residual = self.vm.xor(prior, label)
        matched = tuple(self.vm.recognizes(bits, mask) for mask in GRAMMAR)
        known_mismatch = self.vm.or_(*(
            self.vm.and_(matching, seen, residual)
            for matching, seen in zip(matched, self.seen)))
        complete = self.vm.and_(*self.seen)
        unknown_observation = self.vm.not_(self.vm.or_(*matched))
        hidden_mismatch = self.vm.and_(
            complete, unknown_observation, residual)
        next_fault = self.vm.or_(self.fault, known_mismatch, hidden_mismatch)
        next_weights = []
        next_seen = []
        for old_weight, old_seen, matching in zip(
                self.weights, self.seen, matched):
            eligible = self.vm.and_(matching, self.vm.not_(old_seen),
                                    residual)
            next_weights.append(self.vm.or_(old_weight, eligible))
            next_seen.append(self.vm.or_(old_seen, matching))
        self.weights = next_weights
        self.seen = next_seen
        self.fault = next_fault
        return not bool(self.fault)

    def checkpoint(self) -> bytes:
        if not self._canonical():
            raise ValueError("WSP12_NONCANONICAL_STATE")
        body = json.dumps({
            "schema": SCHEMA,
            "architecture_sha256": self.architecture_sha256(),
            "weights": self.weights,
            "seen": self.seen,
            "fault": self.fault
        }, sort_keys=True, separators=(",", ":")).encode("ascii")
        data = MAGIC + len(body).to_bytes(4, "big") + body
        return data + hashlib.sha256(data).digest()

    def _canonical(self) -> bool:
        if (type(self.weights) is not list or type(self.seen) is not list or
                len(self.weights) != len(GRAMMAR) or
                len(self.seen) != len(GRAMMAR) or
                type(self.fault) is not int or self.fault not in (0, 1)):
            return False
        if any(type(x) is not int or x not in (0, 1)
               for x in self.weights + self.seen):
            return False
        count = sum(self.seen)
        return (self.seen == [1] * count + [0] * (len(GRAMMAR)-count)
                and all(not self.weights[i] or self.seen[i]
                        for i in range(len(GRAMMAR))))

    @classmethod
    def restore(cls, raw: bytes) -> "NumericRuleMemory":
        if (type(raw) is not bytes or len(raw) < 42 or len(raw) > 8192
                or not raw.startswith(MAGIC)
                or int.from_bytes(raw[5:9], "big") != len(raw)-41
                or hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP12_CHECKPOINT_REJECTED")
        try:
            state = json.loads(raw[9:-32].decode("ascii"))
            if (type(state) is not dict or
                    set(state) != {"schema", "architecture_sha256",
                                   "weights", "seen", "fault"} or
                    state["schema"] != SCHEMA or
                    state["architecture_sha256"] != cls.architecture_sha256()):
                raise ValueError("invalid checkpoint schema")
            model = cls()
            model.weights = state["weights"]
            model.seen = state["seen"]
            model.fault = state["fault"]
            if not model._canonical() or model.checkpoint() != raw:
                raise ValueError("invalid checkpoint state")
            return model
        except (KeyError, ValueError, TypeError, OverflowError, UnicodeError):
            raise ValueError("WSP12_CHECKPOINT_REJECTED") from None


def oracle_truth(coefficient_code: int, stimulus: tuple[int, ...]) -> int:
    """INDEPENDENT EVALUATOR ONLY. Never a model input or part of its runtime."""
    checked_bits(stimulus)
    if type(coefficient_code) is not int or not 0 <= coefficient_code < (1 << 11):
        raise ValueError("WSP12_INVALID_ORACLE_CODE")
    return sum(((coefficient_code >> i) & 1)
               for i, mask in enumerate(GRAMMAR)
               if all(stimulus[j] for j in range(4) if (mask >> j) & 1)) % 2


def independent_symbolic(observations: tuple, stimulus: tuple[int, ...]) -> int:
    """Independent exact GF2 Möbius inversion, same public evidence."""
    checked_bits(stimulus)
    if (type(observations) is not tuple or len(observations) != 11):
        raise ValueError("WSP12_SYMBOLIC_INVALID_OBSERVATIONS")
    lookup = {}
    for pair in observations:
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("WSP12_SYMBOLIC_INVALID_OBSERVATIONS")
        x, y = pair
        checked_bits(x)
        checked_label(y)
        idx = sum(v << j for j, v in enumerate(x))
        if idx in lookup:
            raise ValueError("WSP12_SYMBOLIC_DUPLICATE")
        lookup[idx] = y
    if set(lookup) != set(GRAMMAR):
        raise ValueError("WSP12_SYMBOLIC_BAD_BASIS")
    coefficients = {}
    for key in GRAMMAR:
        value = lookup[key]
        for other, previous in coefficients.items():
            if other & key == other:
                value ^= previous
        coefficients[key] = value
    index = sum(bit << j for j, bit in enumerate(stimulus))
    answer = 0
    for monomial, weight in coefficients.items():
        if monomial & index == monomial:
            answer ^= weight
    return answer
