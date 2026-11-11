"""WSP15 generic threshold simulator and reward-modulated synaptic rewiring.

No symbolic program catalog/compiler or task mask enters this module. The
hand-designed policy is stochastic structural search; numeric realization
alone does not establish algorithmic novelty, efficiency or intelligence.
"""
from __future__ import annotations
import hashlib
import json
import random

PUBLIC = (0, 1, 2, 4, 7)
HIDDEN = (3, 5, 6)
SEEDS = (17, 29, 43, 71)
TRIALS = 1024
GATES = 6
LENGTHS = tuple(n for g in range(GATES) for n in (3+g, 3+g)) + (9,)
MAGIC = b"WSP15"
ARCHITECTURE = hashlib.sha256(b"WSP15|3raw|6NAND|12afferent+1output|75binary|strict-reward-v1").hexdigest()


def context(i):
    if type(i) is not int or i not in range(8):
        raise ValueError("WSP15_BAD_INDEX")
    return tuple((i >> j) & 1 for j in range(3))


def checked_context(x):
    if type(x) is not tuple or len(x) != 3 or any(type(v) is not int or v not in (0, 1) for v in x):
        raise ValueError("WSP15_BAD_CONTEXT")
    return x


def checked_examples(examples):
    if type(examples) is not tuple or len(examples) != 5:
        raise ValueError("WSP15_BAD_EXAMPLES")
    for pair, i in zip(examples, PUBLIC):
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("WSP15_BAD_EXAMPLES")
        x, y = pair
        if checked_context(x) != context(i) or type(y) is not int or y not in (0, 1):
            raise ValueError("WSP15_BAD_EXAMPLES")
    return examples


def threshold(value):
    """Fixed threshold activation; not an external task-specific selector."""
    return int(value >= 0)


def forward(rows, x):
    """Uniform numerical dynamics: afferent dot, NAND, output dot."""
    values = list(x)
    for g in range(GATES):
        a = sum(w*v for w, v in zip(rows[2*g], values))
        b = sum(w*v for w, v in zip(rows[2*g+1], values))
        values.append(threshold(1-a-b))
    return sum(w*v for w, v in zip(rows[-1], values))


def mismatch(rows, examples):
    """XOR mismatch neurons and scalar error integrator; no hidden labels."""
    total = 0
    for x, y in examples:
        signal = forward(rows, x) + y
        total += threshold(signal-1) - threshold(signal-2)
    return total


class PlasticNand:
    def __init__(self):
        self.rows = [[0]*n for n in LENGTHS]
        self.rows[-1][0] = 1
        self.proposals = self.accepted = self.gate_evaluations = 0
        self.scalar_ops = self.noise_draws = 0

    def canonical(self):
        return (type(self.rows) is list and len(self.rows) == len(LENGTHS)
                and all(type(row) is list and len(row) == n
                        and all(type(v) is int and v in (0, 1) for v in row)
                        and sum(row) in ((1,) if j == len(LENGTHS)-1 else (0, 1))
                        for j, (row, n) in enumerate(zip(self.rows, LENGTHS))))

    def predict(self, x):
        checked_context(x)
        if not self.canonical():
            raise ValueError("WSP15_BAD_SYNAPSES")
        return forward(self.rows, x)

    def trial(self, examples, row_index, source_index, mode="plastic"):
        """Noise selects a proposed row independent of evidence.

        The reward neuron (not host if/min/sort) selects the committed state.
        All modes evaluate the same current/proposed circuit. Lesion mode is
        an external experimental intervention, never task-dependent routing.
        """
        checked_examples(examples)
        if not self.canonical():
            raise ValueError("WSP15_BAD_SYNAPSES")
        if mode not in ("plastic", "random", "disabled"):
            raise ValueError("WSP15_BAD_MODE")
        if (type(row_index) is not int or row_index not in range(len(LENGTHS))
                or type(source_index) is not int or source_index not in range(LENGTHS[row_index])):
            raise ValueError("WSP15_BAD_NOISE")
        candidate = [row[:] for row in self.rows]
        candidate[row_index] = [int(k == source_index) for k in range(LENGTHS[row_index])]
        current_error = mismatch(self.rows, examples)
        trial_error = mismatch(candidate, examples)
        reward = threshold(current_error-trial_error-1)
        # Fixed, task-independent control interventions.
        reward = {"plastic": reward, "random": 1, "disabled": 0}[mode]
        self.rows = [[old + reward*(new-old) for old, new in zip(a, b)]
                     for a, b in zip(self.rows, candidate)]
        self.accepted += reward
        self.proposals += 1
        self.gate_evaluations += 2*len(examples)*GATES
        # Analytical scalar operation count: afferent multiply/add; NAND
        # arithmetic+threshold; output multiply/add; mismatch; reward; writes.
        self.scalar_ops += (2*len(examples)*(2*sum(LENGTHS)+3*GATES+5)
                            + 3 + 3*sum(LENGTHS))
        return current_error, trial_error, reward

    def learn(self, examples, seed, mode="plastic"):
        checked_examples(examples)
        if type(seed) is not int or seed not in SEEDS:
            raise ValueError("WSP15_BAD_SEED")
        noise = random.Random(seed)
        for _ in range(TRIALS):
            j = noise.randrange(len(LENGTHS))
            k = noise.randrange(LENGTHS[j])
            self.noise_draws += 2
            self.trial(examples, j, k, mode)
        return self

    def snapshot(self):
        if not self.canonical():
            raise ValueError("WSP15_BAD_SYNAPSES")
        data = {"schema": "wsp15.synapses.v1", "architecture": ARCHITECTURE, "rows": self.rows}
        body = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = MAGIC + len(body).to_bytes(4, "big") + body
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw):
        if (type(raw) is not bytes or not 41 <= len(raw) <= 2048 or raw[:5] != MAGIC
                or int.from_bytes(raw[5:9], "big") != len(raw)-41
                or hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP15_CHECKPOINT_REJECTED")
        try:
            d = json.loads(raw[9:-32].decode("ascii"))
            if (type(d) is not dict or set(d) != {"schema", "architecture", "rows"}
                    or d["schema"] != "wsp15.synapses.v1" or d["architecture"] != ARCHITECTURE):
                raise ValueError("schema")
            obj = cls()
            obj.rows = d["rows"]
            if not obj.canonical() or obj.snapshot() != raw:
                raise ValueError("noncanonical")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
            raise ValueError("WSP15_CHECKPOINT_REJECTED") from None
