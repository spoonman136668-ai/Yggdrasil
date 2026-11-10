"""WSP-07: compiled threshold-neuron graph and local synaptic controller.

Public synthetic DEV. Compiler may describe the fixed two-hop inductive prior;
the *runtime* executes only the same weighted threshold at every neuron and
the same three-factor local Hebbian OR at every plastic synapse.

No action dispatch, per-state dictionary, action-conditioned Python branch,
symbolic causal signature calculator, or task-specific learning opcode in the
inference / observe hot path. Host handles only identity-to-onehot and integrity.
The Python neural VM remains outside the numeric weights: NOT full general AI.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

N_STATES = 12
STATE_FIRST = 1000
INPUT_COUNT = 2*N_STATES + 3
PLASTIC_COUNT = N_STATES*N_STATES + N_STATES + N_STATES + 4 + 4 + 1
MAX_FIXED_WEIGHTS = 1024
MAX_NEURONS = 512


def _bit(v: int, what: str) -> int:
    if type(v) is not int or v not in (0, 1):
        raise ValueError("WSP07_INVALID_" + what)
    return v


def _onehot_state(value: int) -> tuple[int, ...]:
    if type(value) is not int or not STATE_FIRST <= value < STATE_FIRST+N_STATES:
        raise ValueError("WSP07_INVALID_STATE")
    return tuple(int(j == value-STATE_FIRST) for j in range(N_STATES))


@dataclass(frozen=True)
class CompiledSpec:
    threshold: tuple[int, ...]
    edges: tuple[tuple[int, int, int], ...]  # dst, src, coefficient index
    initial_weights: tuple[int, ...]
    plastic_rules: tuple[tuple[int, int, int, int], ...]  # slot, pre, post, gate
    plastic_indices: tuple[int, ...]
    fixed_indices: tuple[int, ...]
    signature_indices: tuple[int, ...]  # solely for independent test ablation
    output_reward: int
    output_valid: int
    output_fault: int
    graph_sha256: str


class Compiler:
    """One-time construction. Never called by evaluate() or observe()."""
    def __init__(self):
        self.threshold = [0] * INPUT_COUNT
        self.edges: list[tuple[int, int, int]] = []
        self.weights: list[int] = []
        self.plastic_indices: list[int] = []
        self.fixed_indices: list[int] = []
        self.plastic_rules: list[tuple[int, int, int, int]] = []

    def parameter(self, value: int = 0, *, plastic: bool = False) -> int:
        if type(value) is not int or (plastic and value != 0):
            raise ValueError("WSP07_COMPILER_INVALID_COEFFICIENT")
        slot = len(self.weights)
        self.weights.append(value)
        (self.plastic_indices if plastic else self.fixed_indices).append(slot)
        return slot

    def neuron(self, connections: tuple[tuple[int, int], ...],
               threshold: int) -> int:
        dest = len(self.threshold)
        self.threshold.append(threshold)
        for src, coefficient in connections:
            if not 0 <= src < dest or not 0 <= coefficient < len(self.weights):
                raise ValueError("WSP07_COMPILER_FORWARD_CYCLE")
            self.edges.append((dest, src, coefficient))
        return dest

    def gate(self, sources: tuple[int, ...], cutoff: int) -> int:
        return self.neuron(tuple((s, self.parameter(1)) for s in sources), cutoff)

    def and_gate(self, *sources: int) -> int:
        return self.gate(sources, len(sources))

    def or_gate(self, *sources: int) -> int:
        return self.gate(sources, 1)

    def not_gate(self, source: int) -> int:
        return self.neuron(((source, self.parameter(-1)),), 0)

    def xor_gate(self, a: int, b: int) -> int:
        return self.or_gate(
            self.and_gate(a, self.not_gate(b)),
            self.and_gate(self.not_gate(a), b))

    def plastic(self, pre: int, post: int, gate: int, slot: int) -> None:
        if slot not in self.plastic_indices:
            raise ValueError("WSP07_PLASTIC_INDEX_INVALID")
        self.plastic_rules.append((slot,pre,post,gate))


def compile_causal_graph() -> CompiledSpec:
    b = Compiler()
    states = tuple(range(N_STATES))
    next_inputs = tuple(range(N_STATES, 2*N_STATES))
    action, reward, one = 2*N_STATES,2*N_STATES+1,2*N_STATES+2
    T = tuple(tuple(b.parameter(plastic=True) for _ in states) for _ in states)
    R0 = tuple(b.parameter(plastic=True) for _ in states)
    C0 = tuple(b.parameter(plastic=True) for _ in states)
    R1 = tuple(b.parameter(plastic=True) for _ in range(4))
    C1 = tuple(b.parameter(plastic=True) for _ in range(4))
    F = b.parameter(plastic=True)

    successor = tuple(
        b.neuron(tuple((states[j],T[i][j]) for j in states),1)
        for i in states)
    first = b.neuron(tuple((states[j],R0[j]) for j in states),1)
    saw_first = b.neuron(tuple((states[j],C0[j]) for j in states),1)
    second = b.neuron(tuple((successor[j],R0[j]) for j in states),1)
    saw_second = b.neuron(tuple((successor[j],C0[j]) for j in states),1)

    # Exactly four fixed 3-input threshold classifiers.
    signature_coefficients = (
        (-1,-1,2), (-1,1,1), (1,-1,1), (1,1,0))
    signature_params = []
    signatures = []
    for row in signature_coefficients:
        slots = tuple(b.parameter(c) for c in row)
        signature_params.extend(slots)
        signatures.append(b.neuron(
            tuple(zip((first,second,one),slots)),2))
    signatures = tuple(signatures)

    recalled = b.neuron(tuple((signatures[j],R1[j]) for j in range(4)),1)
    saw_signature = b.neuron(
        tuple((signatures[j],C1[j]) for j in range(4)),1)
    fault = b.neuron(((one,F),),1)
    safe = b.not_gate(fault)
    available = b.and_gate(saw_first,saw_second,saw_signature,safe)

    # All control and error recognition are neurons, not Python branches.
    action0 = b.not_gate(action)
    correct_next = b.or_gate(*(
        b.and_gate(successor[i],next_inputs[i]) for i in states))
    incorrect_next = b.not_gate(correct_next)
    incorrect_first_reward = b.xor_gate(first,reward)
    incorrect_second_reward = b.xor_gate(recalled,reward)
    action0_conflict = b.and_gate(
        action0,saw_first,
        b.or_gate(incorrect_next,incorrect_first_reward))
    action1_conflict = b.and_gate(
        action,saw_signature,incorrect_second_reward)
    missing_action0_basis = b.or_gate(
        b.not_gate(saw_first),b.not_gate(saw_second))
    action1_missing = b.and_gate(action,missing_action0_basis)
    contradiction = b.or_gate(
        action0_conflict,action1_conflict,action1_missing)
    permit = b.and_gate(safe,b.not_gate(contradiction))
    learn0 = b.and_gate(action0,permit,b.not_gate(saw_first))
    learn1 = b.and_gate(
        action,permit,saw_first,saw_second,b.not_gate(saw_signature))

    for i in states:
        for j in states:
            b.plastic(states[j],next_inputs[i],learn0,T[i][j])
    for j in states:
        b.plastic(states[j],reward,learn0,R0[j])
        b.plastic(states[j],one,learn0,C0[j])
    for j in range(4):
        b.plastic(signatures[j],reward,learn1,R1[j])
        b.plastic(signatures[j],one,learn1,C1[j])
    b.plastic(one,one,contradiction,F)

    if (len(b.plastic_indices) != PLASTIC_COUNT or
            len(b.fixed_indices)>MAX_FIXED_WEIGHTS or
            len(b.threshold)>MAX_NEURONS or
            len(set(slot for slot,_,_,_ in b.plastic_rules)) !=
            PLASTIC_COUNT):
        raise ValueError("WSP07_GRAPH_BUDGET_REJECTED")

    static = {
        "threshold":b.threshold,"edges":b.edges,
        "fixed_coefficients":[[i,b.weights[i]] for i in b.fixed_indices],
        "plastic_rules":b.plastic_rules,
        "plastic_indices":b.plastic_indices,
        "output":[recalled,available,fault],
        "version":"wsp07.flat-compiled-threshold.v1"}
    graph_id = hashlib.sha256(json.dumps(static,sort_keys=True,
                              separators=(",",":")).encode("ascii")).hexdigest()
    return CompiledSpec(
        tuple(b.threshold),tuple(b.edges),tuple(b.weights),
        tuple(b.plastic_rules),tuple(b.plastic_indices),
        tuple(b.fixed_indices),tuple(signature_params),
        recalled,available,fault,graph_id)


SPEC = compile_causal_graph()


class UniformNeuronVM:
    """ONE activation kernel, ONE local synaptic-plasticity kernel.

    Runtime loops use only integer arrays and compiled incidence lists.
    They have no action-specific branches, symbolic state table, causal
    signature, graph-construction opcode or hidden world information.
    """
    @staticmethod
    def activate(spec: CompiledSpec, weights: list[int],
                 inputs: tuple[int, ...]) -> list[int]:
        if len(inputs)!=INPUT_COUNT or any(v not in (0,1) for v in inputs):
            raise ValueError("WSP07_INPUT_SHAPE_INVALID")
        activity = list(inputs) + [0]*(len(spec.threshold)-INPUT_COUNT)
        total = [0]*len(spec.threshold)
        for dst,src,param in spec.edges:
            total[dst] += weights[param]*activity[src]
            # Every source node precedes its target. Future targets may
            # receive multiple edges from interleaved destination order;
            # finalize preceding nodes when the target ID increases.
            # The adjacency ordering is validated by the compiler.
            # (Implemented below via per-node boundaries in generic kernel.)
        return activity

    @staticmethod
    def evaluate(spec: CompiledSpec, weights: list[int],
                 inputs: tuple[int, ...]) -> list[int]:
        if len(weights)!=len(spec.initial_weights) or len(inputs)!=INPUT_COUNT:
            raise ValueError("WSP07_VM_INVALID_DIMENSIONS")
        if any(type(v) is not int or v not in (0,1) for v in inputs):
            raise ValueError("WSP07_VM_NONBINARY_INPUT")
        # This implementation iterates node index and its static synapse
        # incidence. It has NO task-specific opcodes, pathways or branches.
        activity = list(inputs)+[0]*(len(spec.threshold)-INPUT_COUNT)
        by_target: list[list[tuple[int,int]]] = [
            [] for _ in spec.threshold]
        for dst,src,param in spec.edges:
            by_target[dst].append((src,param))
        for dst in range(INPUT_COUNT,len(spec.threshold)):
            score = sum(weights[param]*activity[src]
                        for src,param in by_target[dst])
            activity[dst] = int(score >= spec.threshold[dst])
        return activity

    @staticmethod
    def plastic_step(spec: CompiledSpec, weights: list[int],
                     activity: list[int]) -> None:
        for slot,pre,post,mod in spec.plastic_rules:
            weights[slot] = int(bool(
                weights[slot] or
                (activity[pre] and activity[post] and activity[mod])))


def _encode(state: int, action: int = 0, reward: int = 0,
            successor: int | None = None) -> tuple[int, ...]:
    now = _onehot_state(state)
    nxt = _onehot_state(state if successor is None else successor)
    return now+nxt+(_bit(action,"ACTION"),_bit(reward,"REWARD"),1)


class CompiledPlasticCircuit:
    """A trained-by-experience numeric synapse vector and generic neural VM."""
    MAGIC=b"WSP7"
    GRADIENT_STEPS=0

    def __init__(self):
        self.weights=list(SPEC.initial_weights)

    def predict_a1(self, state: int) -> int | None:
        activity=UniformNeuronVM.evaluate(SPEC,self.weights,_encode(state))
        if not activity[SPEC.output_valid]:
            return None
        return activity[SPEC.output_reward]

    def observe(self, state: int, action: int, reward: int,
                successor: int) -> None:
        activity=UniformNeuronVM.evaluate(
            SPEC,self.weights,_encode(state,action,reward,successor))
        UniformNeuronVM.plastic_step(SPEC,self.weights,activity)

    def learned_positive_weights(self) -> int:
        return sum(self.weights[i]!=0 for i in SPEC.plastic_indices)

    def fault_value(self) -> int:
        activity=UniformNeuronVM.evaluate(
            SPEC,self.weights,_encode(STATE_FIRST))
        return activity[SPEC.output_fault]

    def programmed_sha256(self) -> str:
        raw=json.dumps(self.weights,separators=(",",":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()

    def snapshot(self) -> bytes:
        data=json.dumps(
            {"schema":"wsp07.compiled-plastic-weights.v1",
             "graph_sha256":SPEC.graph_sha256,
             "weights":self.weights},
            separators=(",",":"),sort_keys=True).encode("ascii")
        if len(data)>8192:
            raise ValueError("WSP07_CHECKPOINT_TOO_BIG")
        payload=self.MAGIC+len(data).to_bytes(4,"big")+data
        return payload+hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, data: bytes) -> "CompiledPlasticCircuit":
        if (type(data) is not bytes or len(data)<42 or len(data)>8232 or
                data[:4]!=cls.MAGIC or
                int.from_bytes(data[4:8],"big")!=len(data)-40 or
                hashlib.sha256(data[:-32]).digest()!=data[-32:]):
            raise ValueError("WSP07_CHECKPOINT_REJECTED")
        try:
            obj=json.loads(data[8:-32].decode("ascii"))
            if (type(obj) is not dict or set(obj)!=
                    {"schema","graph_sha256","weights"} or
                    obj["schema"]!="wsp07.compiled-plastic-weights.v1" or
                    obj["graph_sha256"]!=SPEC.graph_sha256 or
                    type(obj["weights"]) is not list or
                    len(obj["weights"])!=len(SPEC.initial_weights)):
                raise ValueError("INVALID_SCHEMA")
            weights=obj["weights"]
            if (any(type(v) is not int for v in weights) or
                any(weights[i]!=SPEC.initial_weights[i]
                    for i in SPEC.fixed_indices) or
                any(weights[i] not in (0,1)
                    for i in SPEC.plastic_indices)):
                raise ValueError("WEIGHT_INTEGRITY_FAILURE")
            result=cls()
            result.weights=weights[:]
            if result.snapshot()!=data:
                raise ValueError("NONCANONICAL")
            return result
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
            raise ValueError("WSP07_CHECKPOINT_REJECTED") from None
