"""NCI06 isolated source-free operator-composition engineering kernel.

No source-world executor, prospective seeds, native checkpoint, or owner action.
A toy public witness interface, not evidence of native cognition.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math

SCHEMA = "nci06.operator-core.v1"
NOISE = 0.06
PRIMITIVES = 12
PRIMITIVE_WITNESSES = 128
TRAIN_WITNESSES = 96
VALID_WITNESSES = 64
GATES = ("xor3", "and_xor", "xor_and", "majority")


def _bit(v):
    if type(v) is not int or v not in (0, 1):
        raise ValueError("binary public witness required")
    return v


def _context(bits, action):
    if type(bits) not in (tuple, list) or len(bits) != 5:
        raise ValueError("five public state bits required")
    state = tuple(_bit(v) for v in bits)
    action = _bit(action)
    return state, action, sum(v << i for i, v in enumerate((*state, action)))


def _wire(gate, a, b, c):
    if gate == "xor3":
        return a ^ b ^ c
    if gate == "and_xor":
        return (a & b) ^ c
    if gate == "xor_and":
        return (a ^ b) & c
    if gate == "majority":
        return int(a + b + c >= 2)
    raise ValueError("unrecognized composition gate")


def _programs():
    return tuple((gate, p) for gate in GATES for p in itertools.permutations(range(3)))


def _sealed(payload):
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    if len(body) > 25000:
        raise ValueError("operator checkpoint budget exceeded")
    return b"NC06" + len(body).to_bytes(4, "big") + body + hashlib.sha256(body).digest()


def _unseal(data):
    if type(data) is not bytes or len(data) < 40 or data[:4] != b"NC06":
        raise ValueError("invalid operator checkpoint")
    length = int.from_bytes(data[4:8], "big")
    if length > 25000 or len(data) != 40 + length:
        raise ValueError("invalid operator checkpoint length")
    body = data[8:-32]
    if hashlib.sha256(body).digest() != data[-32:]:
        raise ValueError("operator checkpoint digest mismatch")
    return json.loads(body)


class OperatorBank:
    """Learn primitive public action-effect tables, then make them immutable."""

    def __init__(self):
        self._rows = {}
        self._frozen = set()

    def observe(self, name, bits, action, public_outcome):
        if type(name) is not str or not name or len(name) > 32 or not all(
                c.isascii() and (c.isalnum() or c in "_-") for c in name):
            raise ValueError("invalid public world key")
        _, _, ctx = _context(bits, action)
        y = _bit(public_outcome)
        if name in self._frozen:
            raise ValueError("immutable primitive cannot be updated")
        if name not in self._rows:
            if len(self._rows) >= PRIMITIVES:
                raise ValueError("primitive world limit exceeded")
            self._rows[name] = [[0, 0] for _ in range(64)]
        rows = self._rows[name]
        if sum(a + b for a, b in rows) >= PRIMITIVE_WITNESSES:
            raise ValueError("primitive witness budget exhausted")
        rows[ctx][y] += 1

    def freeze(self, name):
        if name not in self._rows or sum(sum(pair) for pair in self._rows[name]) != PRIMITIVE_WITNESSES:
            raise ValueError("primitive needs exactly 128 public witnesses")
        self._frozen.add(name)

    def read(self, name, bits, action):
        _, _, ctx = _context(bits, action)
        if name not in self._frozen:
            raise ValueError("primitive not trained and frozen")
        neg, pos = self._rows[name][ctx]
        if neg + pos < 2 or neg == pos:
            return None
        return int(pos > neg)

    def snapshot(self):
        return _sealed({"schema": SCHEMA, "rows": self._rows,
                        "frozen": sorted(self._frozen)})

    @classmethod
    def restore(cls, blob):
        raw = _unseal(blob)
        if type(raw) is not dict or raw.get("schema") != SCHEMA:
            raise ValueError("unexpected operator checkpoint schema")
        rows, frozen = raw.get("rows"), raw.get("frozen")
        if type(rows) is not dict or type(frozen) is not list or len(rows) > PRIMITIVES:
            raise ValueError("invalid operator checkpoint contents")
        obj = cls()
        for name, matrix in rows.items():
            if type(name) is not str or not name or len(name) > 32 or not all(
                    c.isascii() and (c.isalnum() or c in "_-") for c in name):
                raise ValueError("invalid checkpoint public key")
            if type(matrix) is not list or len(matrix) != 64:
                raise ValueError("invalid checkpoint matrix")
            if any(type(row) is not list or len(row) != 2 or any(
                    type(v) is not int or v < 0 or v > PRIMITIVE_WITNESSES for v in row)
                    for row in matrix):
                raise ValueError("invalid checkpoint counters")
            if sum(sum(row) for row in matrix) > PRIMITIVE_WITNESSES:
                raise ValueError("checkpoint witnesses exceeded")
            obj._rows[name] = matrix
        if (any(type(n) is not str or n not in rows for n in frozen) or
                len(frozen) != len(set(frozen))):
            raise ValueError("invalid frozen primitive list")
        obj._frozen = set(frozen)
        for name in obj._frozen:
            if sum(sum(row) for row in obj._rows[name]) != PRIMITIVE_WITNESSES:
                raise ValueError("invalid frozen primitive evidence")
        if obj.snapshot() != blob:
            raise ValueError("noncanonical operator checkpoint")
        return obj


def _signals(bank, keys, bits, action):
    if type(keys) not in (tuple, list) or len(keys) != 3 or len(set(keys)) != 3:
        raise ValueError("three distinct public primitive keys required")
    signals = tuple(bank.read(n, bits, action) for n in keys)
    return None if any(v is None for v in signals) else signals


def _predict(program, signals):
    gate, p = program
    return _wire(gate, *(signals[i] for i in p))


class CausalComposer:
    """Bounded contradiction-gated composition; never rewrites primitive memories."""

    def __init__(self, bank, keys):
        _signals(bank, keys, (0, 0, 0, 0, 0), 0)  # validates frozen IDs; abstention is legal
        self.bank = bank
        self.keys = tuple(keys)
        self.bank_sha256 = hashlib.sha256(bank.snapshot()).hexdigest()
        self.train = []
        self.valid = []
        self.binding = None

    def observe(self, bits, action, public_outcome, *, phase):
        state, act, _ = _context(bits, action)
        outcome = _bit(public_outcome)
        if phase not in ("TRAIN", "VALID") or self.binding is not None:
            raise ValueError("invalid or finished target observation phase")
        if phase == "VALID" and len(self.train) != TRAIN_WITNESSES:
            raise ValueError("validation cannot precede complete fit set")
        dest, cap = (self.train, TRAIN_WITNESSES) if phase == "TRAIN" else (self.valid, VALID_WITNESSES)
        if len(dest) >= cap:
            raise ValueError("target witness budget exceeded")
        dest.append((state, act, outcome))

    def _brier(self, program, examples):
        errors = []
        for bits, action, y in examples:
            sig = _signals(self.bank, self.keys, bits, action)
            if sig is None:
                return None
            label = sig[0] if program is None else _predict(program, sig)
            forecast = NOISE + (1 - 2 * NOISE) * label
            errors.append((forecast - y) ** 2)
        return sum(errors) / len(errors)

    def _select_binding(self):
        if len(self.train) != TRAIN_WITNESSES or len(self.valid) != VALID_WITNESSES:
            raise ValueError("incomplete fit/validation public witnesses")
        if hashlib.sha256(self.bank.snapshot()).hexdigest() != self.bank_sha256:
            raise ValueError("primitive state changed during composition")
        both = {}
        for bits, action, _ in self.train:
            both.setdefault(bits, set()).add(action)
        paired = sum(len(actions) == 2 for actions in both.values())
        base = self._brier(None, self.valid)
        if paired < 4 or base is None:
            return None
        ranks = [(self._brier(p, self.train), p) for p in _programs()]
        candidates = [(v, p) for v, p in ranks if v is not None]
        if not candidates:
            return None
        _, best = min(candidates)
        new = self._brier(best, self.valid)
        if new is None or base - new < 0.04:
            return None
        if not any(_predict(best, _signals(self.bank, self.keys, bits, action)) !=
                   _signals(self.bank, self.keys, bits, action)[0]
                   for bits, action, _ in self.valid):
            return None
        return best

    def compile(self):
        if self.binding is not None:
            raise ValueError("already-bound target cannot be recompiled")
        best = self._select_binding()
        if best is None:
            return False
        self.binding = best
        return True

    def predict(self, bits, action):
        signals = _signals(self.bank, self.keys, bits, action)
        if signals is None:
            return None
        return NOISE + (1 - 2 * NOISE) * (
            signals[0] if self.binding is None else _predict(self.binding, signals))

    def snapshot(self):
        return _sealed({"schema": SCHEMA, "bank": self.bank_sha256,
                        "keys": self.keys, "train": self.train,
                        "valid": self.valid, "binding": self.binding})

    @classmethod
    def restore(cls, bank, blob):
        raw = _unseal(blob)
        if type(raw) is not dict or raw.get("schema") != SCHEMA:
            raise ValueError("wrong composer schema")
        obj = cls(bank, raw.get("keys"))
        if raw.get("bank") != obj.bank_sha256:
            raise ValueError("cold primitive lineage mismatch")
        for phase in ("train", "valid"):
            val = raw.get(phase)
            if type(val) is not list or len(val) > (TRAIN_WITNESSES if phase == "train" else VALID_WITNESSES):
                raise ValueError("invalid checkpoint training evidence")
            for entry in val:
                if type(entry) is not list or len(entry) != 3:
                    raise ValueError("invalid checkpoint public witness")
                obj.observe(entry[0], entry[1], entry[2], phase=phase.upper())
        b = raw.get("binding")
        if b is not None:
            if type(b) is not list or len(b) != 2 or type(b[1]) is not list or (
                    b[0], tuple(b[1])) not in _programs():
                raise ValueError("invalid composed binding")
            expected = obj._select_binding()
            if expected != (b[0], tuple(b[1])):
                raise ValueError("checkpoint binding contradicts public evidence")
            obj.binding = expected
        if obj.snapshot() != blob:
            raise ValueError("noncanonical composer checkpoint")
        return obj


class ExactCompositionBayes:
    """Separate fully enumerated same-grammar Bayesian reference, no target labels."""

    def __init__(self, bank, keys):
        _signals(bank, keys, (0, 0, 0, 0, 0), 0)
        self.bank = bank
        self.keys = tuple(keys)
        self.posterior = None

    def fit(self, witnessed_fit):
        if type(witnessed_fit) not in (list, tuple) or len(witnessed_fit) != TRAIN_WITNESSES:
            raise ValueError("exact control requires identical 96 public fit tuples")
        scores = []
        for program in _programs():
            loglike = 0.0
            for bits, action, obs in witnessed_fit:
                _context(bits, action)
                obs = _bit(obs)
                sig = _signals(self.bank, self.keys, bits, action)
                if sig is None:
                    raise ValueError("exact reference lacks equal primitive evidence")
                loglike += math.log(1 - NOISE if _predict(program, sig) == obs else NOISE)
            scores.append(loglike)
        top = max(scores)
        weights = [math.exp(s - top) for s in scores]
        norm = sum(weights)
        self.posterior = tuple(w / norm for w in weights)
        return self

    def predict(self, bits, action):
        if self.posterior is None:
            raise ValueError("exact control not fitted")
        sig = _signals(self.bank, self.keys, bits, action)
        if sig is None:
            return None
        return NOISE + (1 - 2 * NOISE) * sum(
            weight * _predict(program, sig)
            for weight, program in zip(self.posterior, _programs()))
