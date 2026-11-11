"""WSP-14 public DEV: finite NAND program synthesis and numeric wiring.

This is EXTERNAL Python bounded program search over NAND, followed by direct
synaptic circuit programming. It is NOT autonomous neural operator invention.
The synthesis engine receives ONLY five observed input/output pairs, never a
target mask or hidden label. All candidate truth masks are *hypotheses*.
"""
from __future__ import annotations

import functools
import hashlib
import json
import math

INPUT_COUNT = 3
TABLE_BITS = 8
FULL_MASK = (1 << TABLE_BITS) - 1
MAX_NANDS = 14
MAX_SITES = 14
OBSERVED = (0, 1, 2, 4, 7)
HIDDEN = (3, 5, 6)
MAGIC = b"WSP14"
SCHEMA = "wsp14.numeric-nand-program.v1"
GRADIENT_STEPS_DIRECT = 0


def bits(index: int) -> tuple[int, int, int]:
    if type(index) is not int or not 0 <= index < TABLE_BITS:
        raise ValueError("WSP14_INVALID_CONTEXT_INDEX")
    return tuple((index >> i) & 1 for i in range(INPUT_COUNT))


def checked_bits(x: tuple[int, ...]) -> tuple[int, ...]:
    if (type(x) is not tuple or len(x) != INPUT_COUNT or
            any(type(v) is not int or v not in (0, 1) for v in x)):
        raise ValueError("WSP14_INVALID_CONTEXT")
    return x


def checked_label(y: int) -> int:
    if type(y) is not int or y not in (0, 1):
        raise ValueError("WSP14_INVALID_OUTCOME")
    return y


def validate_examples(observations: tuple) -> tuple[int, ...]:
    if type(observations) is not tuple or len(observations) != len(OBSERVED):
        raise ValueError("WSP14_INVALID_EXAMPLES")
    labels = []
    for pair, expected_index in zip(observations, OBSERVED):
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("WSP14_INVALID_EXAMPLES")
        x, y = pair
        checked_bits(x)
        checked_label(y)
        if x != bits(expected_index):
            raise ValueError("WSP14_EXAMPLE_ORDER_OR_CONTENT")
        labels.append(y)
    return tuple(labels)


def truth_mask_of_input(i: int) -> int:
    return sum(((x >> i) & 1) << x for x in range(TABLE_BITS))


@functools.lru_cache(maxsize=1)
def catalog():
    """Minimal NAND EXPRESSION TREE for each of all 256 truth functions.

    No XOR, MUX, majority, parity or truth-table lookup operator is exposed
    to the synthesizer. All 256 masks are computed from low-level NAND search.
    Node forms: (0, raw_input_index) or (1, left_node, right_node).
    """
    levels: list[dict[int, tuple]] = [dict() for _ in range(MAX_NANDS + 1)]
    for i in range(INPUT_COUNT):
        levels[0][truth_mask_of_input(i)] = (0, i)
    cheapest: dict[int, tuple[int, tuple]] = {
        mask: (0, node) for mask, node in levels[0].items()
    }
    for cost in range(1, MAX_NANDS + 1):
        found: dict[int, tuple] = {}
        for left_cost in range(cost):
            right_cost = cost - left_cost - 1
            for lm, left in sorted(levels[left_cost].items()):
                for rm, right in sorted(levels[right_cost].items()):
                    if lm > rm:
                        continue  # NAND operands are commutative.
                    output = FULL_MASK ^ (lm & rm)
                    if output in cheapest:
                        continue
                    candidate = (1, left, right)
                    previous = found.get(output)
                    if previous is None or repr(candidate) < repr(previous):
                        found[output] = candidate
        levels[cost] = dict(sorted(found.items()))
        for mask, node in levels[cost].items():
            cheapest[mask] = (cost, node)
        if len(cheapest) == 256:
            break
    if len(cheapest) != 256:
        raise ValueError("WSP14_NAND_CATALOG_INCOMPLETE")
    return cheapest


def observed_world(mask: int) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Evaluator fixture only. Never called by the program search."""
    if type(mask) is not int or not 0 <= mask <= 255:
        raise ValueError("WSP14_INVALID_TARGET_MASK")
    return tuple((bits(i), (mask >> i) & 1) for i in OBSERVED)


def symbolic_eval(program: tuple, x: tuple[int, ...]) -> int:
    """Independent recursive evaluator for the compiled program's semantics."""
    checked_bits(x)
    if program[0] == 0:
        return x[program[1]]
    if program[0] == 1:
        return 1 - (symbolic_eval(program[1], x) &
                    symbolic_eval(program[2], x))
    raise ValueError("WSP14_INVALID_OPERATOR")


@functools.lru_cache(maxsize=32)
def _select_signature(signature: tuple[int, ...]) -> tuple[int, int, tuple]:
    if (type(signature) is not tuple or len(signature) != len(OBSERVED)
            or any(type(y) is not int or y not in (0, 1) for y in signature)):
        raise ValueError("WSP14_INVALID_SIGNATURE")
    compatible = [
        (cost, mask, program)
        for mask, (cost, program) in catalog().items()
        if all(((mask >> i) & 1) == y
               for i, y in zip(OBSERVED, signature))
    ]
    if not compatible:
        raise ValueError("WSP14_NO_COMPATIBLE_NAND_PROGRAM")
    return min(compatible, key=lambda t: (t[0], t[1]))


def synthesize(observations: tuple):
    """Bounded MDL-style external synthesis, NO target truth-mask input."""
    return _select_signature(validate_examples(observations))


class NumericNand:
    """Numeric neuron network with blank parameter slots before compilation.

    Every NAND node is a fixed weighted threshold gate: -a-b >= -1.
    All task-specific edge addresses/weights and output start unprogrammed.
    """
    def __init__(self):
        self.sources = [[-1, -1] for _ in range(MAX_SITES)]
        self.weights = [[0, 0] for _ in range(MAX_SITES)]
        self.used = 0
        self.output = -1
        self.gate_calls = 0

    @staticmethod
    def architecture_sha256():
        return hashlib.sha256(
            b"WSP14|three-input-nand2|14 blank weighted-threshold gates|v1"
        ).hexdigest()

    @classmethod
    def from_program(cls, tree: tuple) -> "NumericNand":
        result = cls()

        def write_node(node):
            if node[0] == 0:
                idx = node[1]
                if type(idx) is not int or idx not in range(INPUT_COUNT):
                    raise ValueError("WSP14_INVALID_INPUT_NODE")
                return idx
            if node[0] != 1 or len(node) != 3:
                raise ValueError("WSP14_INVALID_GATE_NODE")
            left = write_node(node[1])
            right = write_node(node[2])
            if result.used == MAX_SITES:
                raise ValueError("WSP14_GATE_CAPACITY_EXCEEDED")
            address = result.used
            result.sources[address] = [left, right]
            result.weights[address] = [-1, -1]
            result.used += 1
            return INPUT_COUNT + address

        result.output = write_node(tree)
        if not result._canonical():
            raise ValueError("WSP14_COMPILER_NONCANONICAL")
        return result

    def predict(self, x: tuple[int, ...]) -> int:
        checked_bits(x)
        if not self._canonical():
            raise ValueError("WSP14_UNPROGRAMMED_OR_NONCANONICAL")
        values = list(x)
        for gate in range(self.used):
            src_a, src_b = self.sources[gate]
            weight_a, weight_b = self.weights[gate]
            values.append(int(
                values[src_a]*weight_a + values[src_b]*weight_b >= -1
            ))
            self.gate_calls += 1
        return values[self.output]

    def _canonical(self) -> bool:
        if (type(self.used) is not int or not 0 <= self.used <= MAX_SITES or
                type(self.output) is not int or
                not 0 <= self.output < INPUT_COUNT + self.used):
            return False
        if (type(self.sources) is not list or type(self.weights) is not list
                or len(self.sources) != MAX_SITES or
                len(self.weights) != MAX_SITES):
            return False
        for j in range(MAX_SITES):
            a, b = self.sources[j] if type(self.sources[j]) is list and len(self.sources[j]) == 2 else (None, None)
            w = self.weights[j]
            if type(w) is not list or len(w) != 2:
                return False
            if j < self.used:
                if (type(a) is not int or type(b) is not int or
                        not 0 <= a < INPUT_COUNT+j or
                        not 0 <= b < INPUT_COUNT+j or w != [-1,-1]):
                    return False
            elif [a,b] != [-1,-1] or w != [0,0]:
                return False
        seen = set()

        def reachable(node):
            if node < INPUT_COUNT:
                return
            gate = node - INPUT_COUNT
            if gate in seen:
                return
            seen.add(gate)
            for src in self.sources[gate]:
                reachable(src)

        reachable(self.output)
        return seen == set(range(self.used))

    def snapshot(self) -> bytes:
        if not self._canonical():
            raise ValueError("WSP14_NONCANONICAL_CIRCUIT")
        body = json.dumps({
            "schema": SCHEMA, "architecture_sha256": self.architecture_sha256(),
            "used": self.used, "output": self.output,
            "sources": self.sources, "weights": self.weights,
        }, sort_keys=True, separators=(",", ":")).encode("ascii")
        raw = MAGIC + len(body).to_bytes(4, "big") + body
        return raw + hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls, raw: bytes) -> "NumericNand":
        if (type(raw) is not bytes or len(raw) < 42 or len(raw) > 8192 or
                raw[:5] != MAGIC or
                int.from_bytes(raw[5:9], "big") != len(raw)-41 or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP14_CHECKPOINT_REJECTED")
        try:
            data = json.loads(raw[9:-32].decode("ascii"))
            if (type(data) is not dict or
                    set(data) != {"schema","architecture_sha256","used",
                                  "output","sources","weights"} or
                    data["schema"] != SCHEMA or
                    data["architecture_sha256"] != cls.architecture_sha256()):
                raise ValueError("invalid schema")
            result = cls()
            result.used = data["used"]
            result.output = data["output"]
            result.sources = data["sources"]
            result.weights = data["weights"]
            if not result._canonical() or result.snapshot() != raw:
                raise ValueError("invalid canonical bytes")
            return result
        except (ValueError, TypeError, OverflowError, KeyError, UnicodeError,
                RecursionError):
            raise ValueError("WSP14_CHECKPOINT_REJECTED") from None


def fully_train_8hot(observations: tuple) -> tuple[tuple[float, ...], int, float]:
    """Full-batch deterministic Adam, identical five observations; no OOD labels.

    Eight independent one-hot logits, initialized to zero. Unknown logits
    remain zero; a logit must exceed zero to predict class 1.
    """
    signature = validate_examples(observations)
    return _train_signature(signature)


@functools.lru_cache(maxsize=32)
def _train_signature(signature: tuple[int, ...]):
    weights = [0.0]*8
    moment = [0.0]*8
    velocity = [0.0]*8
    lr = 0.1
    final_loss = math.inf
    for step in range(1,2049):
        gradients = [0.0]*8
        loss = 0.0
        for index, label in zip(OBSERVED, signature):
            w = weights[index]
            prob = 1/(1+math.exp(-w))
            gradients[index] = (prob - label)/5
            loss += (math.log1p(math.exp(-w)) if label
                     else math.log1p(math.exp(w)))
        final_loss = loss/5
        if final_loss <= 0.02:
            return tuple(weights), step-1, final_loss
        for index in OBSERVED:
            moment[index] = 0.9*moment[index] + 0.1*gradients[index]
            velocity[index] = 0.999*velocity[index] + 0.001*gradients[index]**2
            mhat = moment[index]/(1 - 0.9**step)
            vhat = velocity[index]/(1 - 0.999**step)
            weights[index] -= lr*mhat/(math.sqrt(vhat)+1e-8)
    return tuple(weights), 2048, final_loss


def trained_predict(weights: tuple[float, ...], index: int) -> int:
    if type(index) is not int or index not in range(8):
        raise ValueError("WSP14_INVALID_TRAINED_CONTEXT")
    return int(weights[index] > 0)
