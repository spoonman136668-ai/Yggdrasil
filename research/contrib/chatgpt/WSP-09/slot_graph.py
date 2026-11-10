"""WSP-09 public DEV: synaptic self-allocation into blank representation slots.

The *runtime* uses one generic weighted-threshold rule plus one uniform
three-factor local OR plasticity rule. It neither dispatches on a named task
opcode nor chooses slots, addresses, or labels in Python.

A one-time Python compiler supplies the universal equality, first-free and
associative-memory *type*, not an enumerated set of functions/identities.
This constructs novel association INSTANCES, not novel operator TYPES.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

INPUT_BITS = 4
SLOTS = 16
INPUT_NODES = INPUT_BITS + 2
PLASTIC_COUNT = SLOTS * (1 + INPUT_BITS + 1) + 1
MAX_NODES = 512
MAX_EDGES = 1600


def raw_bits(bits: tuple[int, ...]) -> tuple[int, ...]:
    if type(bits) is not tuple or len(bits) != INPUT_BITS or any(
            type(x) is not int or x not in (0, 1) for x in bits):
        raise ValueError("WSP09_INVALID_INPUT_BITS")
    return bits


def raw_label(label: int) -> int:
    if type(label) is not int or label not in (0, 1):
        raise ValueError("WSP09_INVALID_LABEL")
    return label


@dataclass(frozen=True)
class Graph:
    thresholds: tuple[int, ...]
    edges: tuple[tuple[int, int, int], ...]
    incoming: tuple[tuple[tuple[int, int], ...], ...]
    initial_weights: tuple[int, ...]
    fixed_indices: tuple[int, ...]
    plastic_indices: tuple[int, ...]
    plastic_rules: tuple[tuple[int, int, int, int], ...]
    used_indices: tuple[int, ...]
    address_indices: tuple[tuple[int, ...], ...]
    label_indices: tuple[int, ...]
    fault_index: int
    output: int
    valid: int
    fault: int
    source_sha256: str


class GraphBuilder:
    def __init__(self):
        self.thresholds = [0] * INPUT_NODES
        self.edges: list[tuple[int, int, int]] = []
        self.weights: list[int] = []
        self.fixed_indices: list[int] = []
        self.plastic_indices: list[int] = []
        self.rules: list[tuple[int, int, int, int]] = []
        self.plus = self.parameter(1)
        self.minus = self.parameter(-1)

    def parameter(self, value: int = 0, *, plastic: bool = False) -> int:
        if type(value) is not int or (plastic and value != 0):
            raise ValueError("WSP09_INVALID_COMPILED_WEIGHT")
        idx = len(self.weights)
        self.weights.append(value)
        (self.plastic_indices if plastic else self.fixed_indices).append(idx)
        return idx

    def neuron(self, incoming: tuple[tuple[int, int], ...], threshold: int) -> int:
        index = len(self.thresholds)
        self.thresholds.append(threshold)
        for source, slot in incoming:
            if not 0 <= source < index or not 0 <= slot < len(self.weights):
                raise ValueError("WSP09_INVALID_GRAPH_TOPOLOGY")
            self.edges.append((index, source, slot))
        return index

    def AND(self, *nodes: int) -> int:
        return self.neuron(tuple((x, self.plus) for x in nodes), len(nodes))

    def OR(self, *nodes: int) -> int:
        return self.neuron(tuple((x, self.plus) for x in nodes), 1)

    def NOT(self, node: int) -> int:
        return self.neuron(((node, self.minus),), 0)

    def XOR(self, left: int, right: int) -> int:
        return self.OR(self.AND(left, self.NOT(right)),
                       self.AND(self.NOT(left), right))

    def read(self, source: int, weight_slot: int) -> int:
        return self.neuron(((source, weight_slot),), 1)

    def plastic(self, weight_slot: int, pre: int, post: int, mod: int) -> None:
        if weight_slot not in self.plastic_indices:
            raise ValueError("WSP09_INVALID_PLASTIC_TARGET")
        self.rules.append((weight_slot, pre, post, mod))


def compile_graph() -> Graph:
    b = GraphBuilder()
    patterns = tuple(range(INPUT_BITS))
    label_input, one = INPUT_BITS, INPUT_BITS + 1

    # All address, use and label memory starts blank. Every slot is identical.
    used_slots = tuple(b.parameter(plastic=True) for _ in range(SLOTS))
    addresses = tuple(tuple(b.parameter(plastic=True) for _ in patterns)
                      for _ in range(SLOTS))
    labels = tuple(b.parameter(plastic=True) for _ in range(SLOTS))
    fault_slot = b.parameter(plastic=True)

    used = tuple(b.read(one, slot) for slot in used_slots)
    stored_bits = tuple(tuple(b.read(one, addresses[i][j])
                              for j in patterns) for i in range(SLOTS))
    stored_labels = tuple(b.read(one, slot) for slot in labels)
    not_inputs = tuple(b.NOT(j) for j in patterns)

    matches = []
    positives = []
    for i in range(SLOTS):
        eq = []
        for j in patterns:
            a = b.AND(j, stored_bits[i][j])
            z = b.AND(not_inputs[j], b.NOT(stored_bits[i][j]))
            eq.append(b.OR(a, z))
        present = b.AND(used[i], *eq)
        matches.append(present)
        positives.append(b.AND(present, stored_labels[i]))

    known = b.OR(*matches)
    reward_output = b.OR(*positives)
    fault = b.read(one, fault_slot)
    safe = b.NOT(fault)
    valid = b.AND(known, safe)
    contradiction = b.AND(known, b.XOR(reward_output, label_input))
    fresh = b.AND(b.NOT(known), safe)
    prefix = one

    # The learning destination is selected by neural activity, not Python.
    for i in range(SLOTS):
        pick = b.AND(fresh, b.NOT(used[i]), prefix)
        b.plastic(used_slots[i], one, one, pick)
        for j in patterns:
            b.plastic(addresses[i][j], j, one, pick)
        b.plastic(labels[i], label_input, one, pick)
        prefix = b.AND(prefix, used[i])
    b.plastic(fault_slot, one, one, contradiction)

    if (len(b.plastic_indices) != PLASTIC_COUNT or
            len(b.rules) != PLASTIC_COUNT or
            len(set(rule[0] for rule in b.rules)) != PLASTIC_COUNT or
            len(b.thresholds) > MAX_NODES or len(b.edges) > MAX_EDGES):
        raise ValueError("WSP09_COMPILED_BUDGET_EXCEEDED " + str(
            (len(b.thresholds), len(b.edges), len(b.plastic_indices))))

    incoming = [[] for _ in b.thresholds]
    for dest, source, weight in b.edges:
        incoming[dest].append((source, weight))
    canonical = {
        "schema": "wsp09.generic-associative-slot-graph.v1",
        "thresholds": b.thresholds, "edges": b.edges,
        "fixed": [[i, b.weights[i]] for i in b.fixed_indices],
        "plastic": b.plastic_indices, "rules": b.rules,
        "out": [reward_output, valid, fault],
    }
    digest = hashlib.sha256(json.dumps(
        canonical, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return Graph(
        tuple(b.thresholds), tuple(b.edges),
        tuple(tuple(row) for row in incoming), tuple(b.weights),
        tuple(b.fixed_indices), tuple(b.plastic_indices), tuple(b.rules),
        used_slots, addresses, labels, fault_slot,
        reward_output, valid, fault, digest)


SPEC = compile_graph()


class UniformNeuronVM:
    """Uniform numeric activation and local plastic update; no task branches."""
    @staticmethod
    def evaluate(spec: Graph, weights: list[int],
                 inputs: tuple[int, ...]) -> list[int]:
        if (len(weights) != len(spec.initial_weights) or
                len(inputs) != INPUT_NODES or
                any(type(x) is not int or x not in (0, 1) for x in inputs)):
            raise ValueError("WSP09_GENERIC_VM_INVALID_INPUT")
        activity = list(inputs) + [0] * (len(spec.thresholds) - INPUT_NODES)
        for node in range(INPUT_NODES, len(spec.thresholds)):
            activation = sum(weights[slot] * activity[src]
                             for src, slot in spec.incoming[node])
            activity[node] = int(activation >= spec.thresholds[node])
        return activity

    @staticmethod
    def update(spec: Graph, weights: list[int],
               activity: list[int]) -> None:
        for slot, pre, post, mod in spec.plastic_rules:
            weights[slot] = int(bool(weights[slot] or
                                     (activity[pre] and activity[post] and
                                      activity[mod])))


def encode(bits: tuple[int, ...], label: int = 0) -> tuple[int, ...]:
    return raw_bits(bits) + (raw_label(label), 1)


class SelfAllocatingCircuit:
    MAGIC = b"WSP9"
    GRADIENT_STEPS = 0

    def __init__(self):
        self.weights = list(SPEC.initial_weights)

    def observe(self, bits: tuple[int, ...], reward: int) -> None:
        activation = UniformNeuronVM.evaluate(
            SPEC, self.weights, encode(bits, reward))
        UniformNeuronVM.update(SPEC, self.weights, activation)

    def predict(self, bits: tuple[int, ...]) -> int | None:
        a = UniformNeuronVM.evaluate(SPEC, self.weights, encode(bits))
        return a[SPEC.output] if a[SPEC.valid] else None

    @property
    def fault(self) -> int:
        return self.weights[SPEC.fault_index]

    @property
    def allocated_slots(self) -> int:
        return sum(self.weights[i] for i in SPEC.used_indices)

    @property
    def positive_plastic(self) -> int:
        return sum(self.weights[i] for i in SPEC.plastic_indices)

    def programmed_sha256(self) -> str:
        return hashlib.sha256(json.dumps(
            self.weights, separators=(",", ":")).encode("ascii")).hexdigest()

    def snapshot(self) -> bytes:
        payload = json.dumps(
            {"schema": "wsp09.numeric-associative-state.v1",
             "graph_sha256": SPEC.source_sha256,
             "weights": self.weights},
            sort_keys=True, separators=(",", ":")).encode("ascii")
        if len(payload) > 8192:
            raise ValueError("WSP09_CHECKPOINT_TOO_LARGE")
        prefix = self.MAGIC + len(payload).to_bytes(4, "big") + payload
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw: bytes) -> "SelfAllocatingCircuit":
        if (type(raw) is not bytes or len(raw) < 42 or len(raw) > 8232 or
                raw[:4] != cls.MAGIC or
                len(raw) - 40 != int.from_bytes(raw[4:8], "big") or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP09_CHECKPOINT_REJECTED")
        try:
            d = json.loads(raw[8:-32].decode("ascii"))
            if (type(d) is not dict or set(d) !=
                    {"schema", "graph_sha256", "weights"} or
                    d["schema"] != "wsp09.numeric-associative-state.v1" or
                    d["graph_sha256"] != SPEC.source_sha256 or
                    type(d["weights"]) is not list or
                    len(d["weights"]) != len(SPEC.initial_weights)):
                raise ValueError("INVALID_SCHEMA")
            values = d["weights"]
            if (any(type(w) is not int for w in values) or
                    any(values[i] != SPEC.initial_weights[i]
                        for i in SPEC.fixed_indices) or
                    any(values[i] not in (0, 1)
                        for i in SPEC.plastic_indices)):
                raise ValueError("INVALID_WEIGHTS")
            model = cls()
            model.weights = values[:]
            if model.snapshot() != raw:
                raise ValueError("NONCANONICAL_CHECKPOINT")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError):
            raise ValueError("WSP09_CHECKPOINT_REJECTED") from None
