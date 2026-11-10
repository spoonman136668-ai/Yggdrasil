"""WSP-05 public DEV: learn causal state signatures from opaque interventions.

No latent labels, generator or arbitrary rule families are supplied to the
weight writer. Generic two-step action-consequence signatures are compiled into
binary detectors only after genuine public experience. This is learning from
experience, not intelligence without experience or arbitrary ontology discovery.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass

SEEDS = tuple(range(32))
STATE_IDS = tuple(range(1000, 1012))
TRAIN_REPLICAS = (0, 1)
TEST_REPLICA = 2


def _state(x: int) -> int:
    if type(x) is not int or x not in STATE_IDS:
        raise ValueError("WSP05_INVALID_STATE")
    return x


def _bit(x: int, name: str) -> int:
    if type(x) is not int or x not in (0, 1):
        raise ValueError("WSP05_INVALID_" + name)
    return x


def _event(e: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if type(e) not in (tuple, list) or len(e) != 4:
        raise ValueError("WSP05_INVALID_EVENT")
    s, a, r, nxt = e
    return _state(s), _bit(a, "ACTION"), _bit(r, "REWARD"), _state(nxt)


class PublicWorld:
    """Synthetic evaluator only; do not inject instance, class or seed into learner."""

    def __init__(self, seed: int):
        if type(seed) is not int or seed not in SEEDS:
            raise ValueError("WSP05_INVALID_SEED")
        self.seed = seed
        rng = random.Random(seed * 8999 + 101)
        identities = list(STATE_IDS)
        rng.shuffle(identities)
        self._by_class = {(q, replica): identities[3*q + replica]
                          for q in range(4) for replica in range(3)}
        self._hidden = {value: key for key, value in self._by_class.items()}
        self.train = tuple(sorted(self._by_class[q, i]
                                  for q in range(4) for i in TRAIN_REPLICAS))
        self.test = tuple(sorted(self._by_class[q, TEST_REPLICA]
                                 for q in range(4)))

    def outcome(self, state: int, action: int, *,
                heldout_shift: bool = False) -> tuple[int, int, int, int]:
        _state(state)
        _bit(action, "ACTION")
        if type(heldout_shift) is not bool:
            raise ValueError("WSP05_INVALID_SHIFT")
        q, replica = self._hidden[state]
        if action == 0:
            reward = q & 1
            next_class = q >> 1
        else:
            reward = (self.seed % 16 >> q) & 1
            if heldout_shift and replica == TEST_REPLICA:
                reward ^= 1
            next_class = (q + 2) % 4
        next_state = self._by_class[next_class, (replica + 1) % 3]
        return state, action, reward, next_state

    def public_experiences(self) -> tuple[tuple[int, int, int, int], ...]:
        return (tuple(self.outcome(s, 0) for s in STATE_IDS) +
                tuple(self.outcome(s, 1) for s in self.train))


@dataclass(frozen=True)
class BinarySignatureGate:
    """Four binary one-hot connection weights and a threshold of two."""
    signature: tuple[int, int]
    weights: tuple[int, int, int, int]
    threshold: int
    learned_reward: int

    @classmethod
    def from_observation(cls, signature: tuple[int, int],
                         outcome: int) -> "BinarySignatureGate":
        b0, b1 = signature
        _bit(b0, "SIGNATURE_FIRST")
        _bit(b1, "SIGNATURE_SECOND")
        reward = _bit(outcome, "REWARD")
        return cls(signature, (1-b0, b0, 1-b1, b1), 2, reward)

    def fires(self, signature: tuple[int, int]) -> bool:
        x0, x1 = signature
        _bit(x0, "SIGNATURE_FIRST")
        _bit(x1, "SIGNATURE_SECOND")
        features = (1-x0, x0, 1-x1, x1)
        return sum(w * x for w, x in zip(self.weights, features)) >= self.threshold


class DirectSignatureCircuit:
    """Learns a new detector on the first action-1 reward of a causal signature."""
    MAGIC = b"WSP5"
    MAX_DETECTORS = 4
    GRADIENT_STEPS = 0

    def __init__(self):
        self.a0: dict[int, tuple[int, int]] = {}
        self.a1: dict[int, tuple[int, int]] = {}
        self.gates: dict[tuple[int, int], BinarySignatureGate] = {}
        self.events: list[tuple[int, int, int, int]] = []
        self.unsafe = False

    def _signature(self, state: int) -> tuple[int, int] | None:
        _state(state)
        if state not in self.a0:
            return None
        first, next_state = self.a0[state]
        if next_state not in self.a0:
            return None
        return first, self.a0[next_state][0]

    def observe(self, s: int, a: int, reward: int, nxt: int) -> None:
        s, a, reward, nxt = _event((s, a, reward, nxt))
        previous = self.a0.get(s) if a == 0 else self.a1.get(s)
        if previous is not None:
            if previous != (reward, nxt):
                self.unsafe = True
                self.events.append((s, a, reward, nxt))
            return
        if self.unsafe:
            return
        if a == 0:
            self.a0[s] = reward, nxt
        else:
            signature = self._signature(s)
            if signature is None:
                raise ValueError("WSP05_CAUSAL_EVIDENCE_MISSING")
            existing = self.gates.get(signature)
            if existing is not None and existing.learned_reward != reward:
                self.unsafe = True
            elif existing is None:
                if len(self.gates) >= self.MAX_DETECTORS:
                    self.unsafe = True
                else:
                    self.gates[signature] = BinarySignatureGate.from_observation(
                        signature, reward)
            self.a1[s] = reward, nxt
        self.events.append((s, a, reward, nxt))

    def predict_a1(self, state: int) -> int | None:
        signature = self._signature(state)
        if self.unsafe or signature is None:
            return None
        selected = [gate.learned_reward for gate in self.gates.values()
                    if gate.fires(signature)]
        return selected[0] if len(selected) == 1 else None

    @property
    def learned_connections(self) -> int:
        return 4 * len(self.gates)

    def programmed_sha256(self) -> str:
        data = bytearray()
        for signature, gate in sorted(self.gates.items()):
            data.extend((*signature, *gate.weights, gate.threshold,
                         gate.learned_reward))
        return hashlib.sha256(data).hexdigest()

    def snapshot(self) -> bytes:
        payload = json.dumps(
            {"schema": "wsp05.signature-state.v1",
             "events": self.events, "unsafe": self.unsafe,
             "gates": [[*sig, gate.learned_reward]
                       for sig, gate in sorted(self.gates.items())]},
            sort_keys=True, separators=(",", ":")).encode("ascii")
        if len(payload) > 4096:
            raise ValueError("WSP05_STATE_TOO_LARGE")
        prefix = self.MAGIC + len(payload).to_bytes(4, "big") + payload
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, blob: bytes) -> "DirectSignatureCircuit":
        if (type(blob) is not bytes or len(blob) < 42 or len(blob) > 4136 or
                blob[:4] != cls.MAGIC or
                len(blob) - 40 != int.from_bytes(blob[4:8], "big") or
                hashlib.sha256(blob[:-32]).digest() != blob[-32:]):
            raise ValueError("WSP05_CHECKPOINT_REJECTED")
        try:
            d = json.loads(blob[8:-32].decode("ascii"))
            if (type(d) is not dict or set(d) !=
                    {"schema", "events", "unsafe", "gates"} or
                    d["schema"] != "wsp05.signature-state.v1" or
                    type(d["unsafe"]) is not bool or
                    type(d["events"]) is not list or len(d["events"]) > 32):
                raise ValueError("BAD_SCHEMA")
            model = cls()
            for e in d["events"]:
                if type(e) is not list or len(e) != 4:
                    raise ValueError("BAD_EVENT")
                model.observe(*e)
            if model.snapshot() != blob:
                raise ValueError("NONCANONICAL")
            return model
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError):
            raise ValueError("WSP05_CHECKPOINT_REJECTED") from None


class ExactSymbolicSignature:
    """Independent causal-state signature mapping, no binary gate compilation."""
    def __init__(self):
        self.transitions: dict[int, tuple[int, int]] = {}
        self.rewards: dict[tuple[int, int], int] = {}
        self.unsafe = False

    def observe(self, s: int, a: int, r: int, nxt: int) -> None:
        s, a, r, nxt = _event((s, a, r, nxt))
        if self.unsafe:
            return
        if a == 0:
            if s in self.transitions and self.transitions[s] != (r, nxt):
                self.unsafe = True
            self.transitions[s] = r, nxt
        else:
            sig = self.signature(s)
            if sig is None:
                raise ValueError("WSP05_SYMBOLIC_CAUSAL_EVIDENCE_MISSING")
            if sig in self.rewards and self.rewards[sig] != r:
                self.unsafe = True
            self.rewards[sig] = r

    def signature(self, s: int) -> tuple[int, int] | None:
        _state(s)
        if s not in self.transitions:
            return None
        r, nxt = self.transitions[s]
        return (r, self.transitions[nxt][0]) if nxt in self.transitions else None

    def predict_a1(self, s: int) -> int | None:
        sig = self.signature(s)
        if self.unsafe or sig is None:
            return None
        return self.rewards.get(sig)


class OneStepControl:
    """Ablate causal successor: learn only initial action-0 reward associations."""
    def __init__(self):
        self.a0: dict[int, int] = {}
        self.rewards: dict[int, set[int]] = {0: set(), 1: set()}

    def observe(self, s: int, a: int, reward: int, nxt: int) -> None:
        s, a, r, _ = _event((s, a, reward, nxt))
        if a == 0:
            self.a0[s] = r
        elif s in self.a0:
            self.rewards[self.a0[s]].add(r)
        else:
            raise ValueError("WSP05_ABLATION_MISSING_EVIDENCE")

    def predict_a1(self, s: int) -> int | None:
        v = self.rewards.get(self.a0.get(_state(s), -1), set())
        return next(iter(v)) if len(v) == 1 else None


class IdentityControl:
    """Memorizes exposed identities and rewards, cannot transfer to new IDs."""
    def __init__(self):
        self.a1: dict[int, int] = {}

    def observe(self, s: int, a: int, r: int, nxt: int) -> None:
        s, a, r, nxt = _event((s, a, r, nxt))
        if a == 1:
            self.a1[s] = r

    def predict_a1(self, s: int) -> int | None:
        return self.a1.get(_state(s))


class TrainedMLPControl:
    """Fully train on same observed 2-bit signatures or disclose nonconvergence.

    2-input / 8-hidden / 1-output tanh sigmoid network, Adam gradient optimizer.
    Frozen max 2048 steps, loss stop <=.02, seed 17 and full public 8 examples.
    """
    SEED = 17
    HIDDEN = 8
    PARAMS = 33
    MAX_STEPS = 2048
    STOP_LOSS = 0.02
    LR = 0.03

    def __init__(self) -> None:
        rng = random.Random(self.SEED)
        self.w = [[rng.uniform(-0.5, 0.5) for _ in range(2)]
                  for _ in range(self.HIDDEN)]
        self.b = [0.0] * self.HIDDEN
        self.v = [rng.uniform(-0.5, 0.5) for _ in range(self.HIDDEN)]
        self.bias = 0.0
        self.loss: float | None = None
        self.steps = 0
        self.converged = False

    def _params(self) -> list[float]:
        return [x for row in self.w for x in row] + self.b + self.v + [self.bias]

    def _unpack(self, params: list[float]) -> None:
        if len(params) != self.PARAMS:
            raise ValueError("WSP05_INVALID_MLP_PARAMETERS")
        self.w = [params[2*i:2*i+2] for i in range(self.HIDDEN)]
        self.b = params[16:24]
        self.v = params[24:32]
        self.bias = params[32]

    def forward(self, signature: tuple[int, int]) -> tuple[list[float], float]:
        x, y = signature
        _bit(x, "SIGNATURE_FIRST")
        _bit(y, "SIGNATURE_SECOND")
        h = [math.tanh(row[0]*x + row[1]*y + b)
             for row, b in zip(self.w, self.b)]
        z = max(-40.0, min(40.0, sum(w*t for w,t in zip(self.v,h)) + self.bias))
        return h, 1 / (1 + math.exp(-z))

    def fit(self, examples: tuple[tuple[tuple[int, int], int], ...]) -> None:
        if (type(examples) is not tuple or len(examples) != 8 or
                any(type(sig) is not tuple or len(sig) != 2 or
                    any(type(bit) is not int or bit not in (0, 1) for bit in sig) or
                    type(y) is not int or y not in (0, 1)
                    for sig, y in examples)):
            raise ValueError("WSP05_MLP_DATA_BUDGET_REJECTED")
        n = len(examples)
        theta = self._params()
        first = [0.0] * len(theta)
        second = [0.0] * len(theta)
        for t in range(1, self.MAX_STEPS+1):
            grad = [0.0] * len(theta)
            loss = 0.0
            for sig, y in examples:
                h, p = self.forward(sig)
                p = max(1e-12, min(1-1e-12, p))
                loss += -(y*math.log(p) + (1-y)*math.log(1-p)) / n
                err = (p-y)/n
                grad[32] += err
                x0, x1 = sig
                for j in range(self.HIDDEN):
                    grad[24+j] += err*h[j]
                    back = err * self.v[j]*(1-h[j]*h[j])
                    grad[16+j] += back
                    grad[2*j] += back*x0
                    grad[2*j+1] += back*x1
            self.loss = loss
            self.steps = t-1
            if loss <= self.STOP_LOSS:
                self.converged = True
                break
            for i,g in enumerate(grad):
                first[i] = 0.9*first[i] + .1*g
                second[i] = .999*second[i] + .001*g*g
                mean = first[i]/(1-.9**t)
                var = second[i]/(1-.999**t)
                theta[i] -= self.LR*mean/(math.sqrt(var)+1e-8)
            self._unpack(theta)
            self.steps = t
        if not self.converged:
            self.loss = sum(
                -(y*math.log(max(1e-12, self.forward(sig)[1])) +
                  (1-y)*math.log(max(1e-12, 1-self.forward(sig)[1]))) / n
                for sig,y in examples)
            self.converged = self.loss <= self.STOP_LOSS

    def predict_a1(self, signature: tuple[int, int]) -> int:
        return int(self.forward(signature)[1] >= .5)
