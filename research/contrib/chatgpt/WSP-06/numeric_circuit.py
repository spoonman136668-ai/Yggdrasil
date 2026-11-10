"""WSP-06 public DEV: entire bounded WSP-05 solver in numeric synapses.

The host merely encodes state identities, executes a GENERIC numerical tape,
and handles input/byte-integrity errors. Causal inference and action-conditioned
plastic memory writes use explicit matrices and thresholds, not Python maps of
latent state, successor relation, signature or reward. This is a software
simulator of a small recurrent circuit, NOT an entire general cognitive model.
"""
from __future__ import annotations

import hashlib
import json

N = 12
STATE_FIRST = 1000
PLASTIC_SHAPES = {
    "T0": (12, 12),  # learned successor synapses
    "R0": (1, 12),   # learned action-0 reward synapses
    "C0": (1, 12),   # learned action-0 coverage
    "R1": (1, 4),    # learned consequence-signature reward synapses
    "C1": (1, 4),    # learned signature coverage
    "F": (1, 1),     # plastic contradiction/fail-closed latch
}
PLASTIC_COUNT = sum(rows*columns for rows,columns in PLASTIC_SHAPES.values())
FIXED_SIGNATURE = [
    [-1, -1, 2],
    [-1,  1, 1],
    [ 1, -1, 1],
    [ 1,  1, 0],
]
FIXED_ROUTE = [[-1, 1], [1, 0]]
FIXED_COUNT = sum(map(len, FIXED_SIGNATURE)) + sum(map(len, FIXED_ROUTE))

# This is a declarative *numerical network program*. No state IDs, hidden
# causal classes, learned reward tables or environmental rules occur in it.
READ_TAPE = (
    ("dot", "first", "R0", "x"),
    ("dot", "successor", "T0", "x"),
    ("dot", "second", "R0", "successor"),
    ("dot", "saw_first", "C0", "x"),
    ("dot", "saw_second", "C0", "successor"),
    ("stack", "sig_inputs", "first", "second", "one"),
    ("dot", "sig_scores", "SIG", "sig_inputs"),
    ("threshold", "sig", "sig_scores", 1.5),
    ("dot", "recalled", "R1", "sig"),
    ("dot", "saw_sig", "C1", "sig"),
    ("dot", "fault", "F", "one"),
    ("mul", "coverage", "saw_first", "saw_second", "saw_sig"),
    ("minus", "not_fault", "one", "fault"),
    ("mul", "valid", "coverage", "not_fault"),
)
LEARN_TAPE = (
    ("stack", "route_inputs", "action", "one"),
    ("dot", "routes", "ROUTE", "route_inputs"),
    ("index", "gate0", "routes", 0),
    ("index", "gate1", "routes", 1),
    ("minus", "ready_missing", "one", "saw_first"),
    ("minus", "next_missing", "one", "saw_second"),
    ("sum", "missing_parts", "ready_missing", "next_missing"),
    ("threshold", "missing_bit", "missing_parts", 0.5),
    ("mul", "missing", "gate1", "missing_bit"),
    ("absdiff", "reward0_error", "first", "reward"),
    ("l1diff", "transition_error", "successor", "next"),
    ("sum", "delta0", "reward0_error", "transition_error"),
    ("threshold", "err0", "delta0", 0.5),
    ("absdiff", "reward1_error", "recalled", "reward"),
    ("threshold", "err1", "reward1_error", 0.5),
    ("mul", "bad0", "gate0", "saw_first", "err0"),
    ("mul", "bad1", "gate1", "saw_sig", "err1"),
    ("sum", "bad", "bad0", "bad1"),
    ("sum", "hazard0", "bad", "missing"),
    ("sum", "hazard", "hazard0", "fault"),
    ("threshold", "block", "hazard", 0.5),
    ("minus", "allow", "one", "block"),
    ("mul", "learn0", "gate0", "allow"),
    ("mul", "learn1", "gate1", "allow"),
    ("outer_or", "F", "bad", "one", "one"),
    ("outer_or", "T0", "next", "x", "learn0"),
    ("outer_or", "R0", "reward", "x", "learn0"),
    ("outer_or", "C0", "one", "x", "learn0"),
    ("outer_or", "R1", "reward", "sig", "learn1"),
    ("outer_or", "C1", "one", "sig", "learn1"),
)
PROGRAM = (READ_TAPE, LEARN_TAPE)
PROGRAM_SHA256 = hashlib.sha256(
    json.dumps(PROGRAM, separators=(",", ":")).encode("ascii")).hexdigest()


def _raw_state(s: int) -> list[int]:
    """Fixed raw ID-to-onehot transducer, no environmental class lookup."""
    if type(s) is not int or not STATE_FIRST <= s < STATE_FIRST + N:
        raise ValueError("WSP06_INVALID_RAW_STATE")
    return [int(i == s-STATE_FIRST) for i in range(N)]


def _bit(v: int, name: str) -> list[int]:
    if type(v) is not int or v not in (0, 1):
        raise ValueError("WSP06_INVALID_" + name)
    return [v]


def _zeros(rows: int, columns: int) -> list[list[int]]:
    return [[0] * columns for _ in range(rows)]


class NumericalTape:
    """Same small tensor primitives run every layer; no WSP05 symbol decoder."""

    @staticmethod
    def run(program: tuple, weights: dict, tensors: dict) -> dict:
        data = {k: list(v) for k,v in tensors.items()}
        for ins in program:
            op, destination, *args = ins
            if op == "dot":
                matrix = weights[args[0]]
                vector = data[args[1]]
                if not matrix or any(len(row) != len(vector) for row in matrix):
                    raise ValueError("WSP06_TENSOR_SHAPE_INVALID")
                data[destination] = [sum(w*x for w,x in zip(row, vector))
                                     for row in matrix]
            elif op == "stack":
                data[destination] = [v for name in args for v in data[name]]
            elif op == "threshold":
                vector, threshold = args
                data[destination] = [int(v >= threshold) for v in data[vector]]
            elif op == "index":
                vector, index = args
                data[destination] = [data[vector][index]]
            elif op == "mul":
                vectors = [data[name] for name in args]
                if any(len(v) != 1 for v in vectors):
                    raise ValueError("WSP06_SCALAR_MULTIPLY_REQUIRED")
                result = 1
                for v in vectors:
                    result *= v[0]
                data[destination] = [result]
            elif op == "sum":
                vectors = [data[name] for name in args]
                if any(len(v) != 1 for v in vectors):
                    raise ValueError("WSP06_SCALAR_SUM_REQUIRED")
                data[destination] = [sum(v[0] for v in vectors)]
            elif op == "minus":
                left, right = (data[name] for name in args)
                if len(left) != len(right):
                    raise ValueError("WSP06_SUBTRACTION_SHAPE_INVALID")
                data[destination] = [x-y for x,y in zip(left,right)]
            elif op == "absdiff":
                left, right = (data[name] for name in args)
                if len(left) != len(right):
                    raise ValueError("WSP06_ABS_DIFF_SHAPE_INVALID")
                data[destination] = [abs(x-y) for x,y in zip(left,right)]
            elif op == "l1diff":
                left, right = (data[name] for name in args)
                if len(left) != len(right):
                    raise ValueError("WSP06_L1_SHAPE_INVALID")
                data[destination] = [sum(abs(x-y) for x,y in zip(left,right))]
            elif op == "outer_or":
                name = destination
                post, pre, gate = args
                matrix = weights[name]
                post_v, pre_v, gate_v = (data[x] for x in (post,pre,gate))
                if len(gate_v) != 1 or len(matrix) != len(post_v) or any(
                        len(row) != len(pre_v) for row in matrix):
                    raise ValueError("WSP06_PLASTIC_SHAPE_INVALID")
                if gate_v[0] not in (0,1) or any(v not in (0,1)
                                                for v in post_v+pre_v):
                    raise ValueError("WSP06_PLASTIC_BINARY_REQUIRED")
                gate_bit = gate_v[0]
                for i,v in enumerate(post_v):
                    for j,w in enumerate(pre_v):
                        matrix[i][j] = int(bool(matrix[i][j] or
                                                (gate_bit and v and w)))
            else:
                raise ValueError("WSP06_UNKNOWN_NUMERICAL_OPCODE")
        return data


class CompleteTaskCircuit:
    """All learned task memory held as plastic numeric synaptic matrices."""
    MAGIC = b"WSP6"
    GRADIENT_STEPS = 0
    FIXED_WEIGHT_COUNT = FIXED_COUNT
    PLASTIC_WEIGHT_COUNT = PLASTIC_COUNT

    def __init__(self):
        self.weights = {name: _zeros(*shape)
                        for name,shape in PLASTIC_SHAPES.items()}
        self.weights["SIG"] = [r[:] for r in FIXED_SIGNATURE]
        self.weights["ROUTE"] = [r[:] for r in FIXED_ROUTE]

    @staticmethod
    def _inputs(state: int, action: int = 0, reward: int = 0,
                successor: int | None = None) -> dict:
        # No task-specific state relation or hidden class is constructed here.
        raw = _raw_state(state)
        next_raw = _raw_state(successor if successor is not None else state)
        return {"x":raw, "next":next_raw, "action":_bit(action,"ACTION"),
                "reward":_bit(reward,"REWARD"),"one":[1]}

    def predict_a1(self, state: int) -> int | None:
        activations = NumericalTape.run(READ_TAPE, self.weights,
                                        self._inputs(state))
        if activations["valid"] != [1]:
            return None
        return int(activations["recalled"][0] >= 0.5)

    def observe(self, state: int, action: int, reward: int,
                successor: int) -> None:
        inputs = self._inputs(state, action, reward, successor)
        activations = NumericalTape.run(READ_TAPE, self.weights, inputs)
        numerical = NumericalTape.run(LEARN_TAPE, self.weights, activations)
        if numerical["missing"] != [0]:
            # Boundary validation only: no invalid action-1 write occurs.
            raise ValueError("WSP06_PUBLIC_CAUSAL_EVIDENCE_MISSING")

    def programmed_sha256(self) -> str:
        raw = json.dumps(self.weights, sort_keys=True,
                         separators=(",", ":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()

    def learned_positive_synapses(self) -> int:
        return sum(int(v != 0) for name in PLASTIC_SHAPES
                   for row in self.weights[name] for v in row)

    def snapshot(self) -> bytes:
        payload = json.dumps({"schema":"wsp06.numeric-weight-state.v1",
                              "program_sha256":PROGRAM_SHA256,
                              "weights":self.weights},
                             sort_keys=True,separators=(",", ":")).encode("ascii")
        if len(payload) > 8192:
            raise ValueError("WSP06_CHECKPOINT_SIZE_INVALID")
        prefix = self.MAGIC + len(payload).to_bytes(4,"big") + payload
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw: bytes) -> "CompleteTaskCircuit":
        if (type(raw) is not bytes or len(raw) < 42 or len(raw) > 8232 or
                raw[:4] != cls.MAGIC or
                int.from_bytes(raw[4:8],"big") != len(raw)-40 or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP06_CHECKPOINT_REJECTED")
        try:
            obj = json.loads(raw[8:-32].decode("ascii"))
            if (type(obj) is not dict or set(obj) !=
                    {"schema","program_sha256","weights"} or
                    obj["schema"] != "wsp06.numeric-weight-state.v1" or
                    obj["program_sha256"] != PROGRAM_SHA256 or
                    type(obj["weights"]) is not dict):
                raise ValueError("BAD_SCHEMA")
            circuit = cls()
            supplied = obj["weights"]
            if set(supplied) != set(circuit.weights):
                raise ValueError("MISSING_LAYER")
            if (supplied["SIG"] != FIXED_SIGNATURE or
                    supplied["ROUTE"] != FIXED_ROUTE):
                raise ValueError("ALTERED_PROGRAMMED_LAYER")
            for name,shape in PLASTIC_SHAPES.items():
                m = supplied[name]
                if (type(m) is not list or len(m) != shape[0] or
                    any(type(row) is not list or len(row) != shape[1] or
                        any(type(v) is not int or v not in (0,1) for v in row)
                        for row in m)):
                    raise ValueError("INVALID_PLASTIC_SYNAPSE")
            circuit.weights = {name:[list(row) for row in matrix]
                               for name,matrix in supplied.items()}
            if circuit.snapshot() != raw:
                raise ValueError("NONCANONICAL")
            return circuit
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
            raise ValueError("WSP06_CHECKPOINT_REJECTED") from None
