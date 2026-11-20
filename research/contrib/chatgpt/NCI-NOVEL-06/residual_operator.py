"""NCI06 source-free residual invention, not native training or scientific first use.

Learn a new eight-bit operator from public causal witnesses. An independent
256-truth-function exact Bayesian control gets the identical 96 fit examples.
"""
from __future__ import annotations

import hashlib
import math
from operator_core import (CausalComposer, NOISE, TRAIN_WITNESSES,
                           VALID_WITNESSES, _context, _programs,
                           _predict, _sealed, _signals, _unseal)

SCHEMA = "nci06.residual-invention.v1"
MIN_PER_PATTERN = 3
MIN_PAIRED_CONTRASTS = 4
VALID_BRIER_GAIN = 0.04


def _index(sig):
    return sig[0] | (sig[1] << 1) | (sig[2] << 2)


def _mask(program):
    return sum(_predict(program, (i & 1, (i >> 1) & 1, (i >> 2) & 1)) << i
               for i in range(8))


FIXED_MASKS = frozenset(_mask(program) for program in _programs())
assert len(_programs()) == 24 and len(FIXED_MASKS) == 8


def _forecast(value):
    return NOISE + (1 - 2 * NOISE) * value


class ResidualComposer:
    """Bounded NEW truth function outside the preauthored 24-program class."""

    def __init__(self, bank, keys):
        self.base = CausalComposer(bank, keys)
        self.bank_sha = hashlib.sha256(bank.snapshot()).hexdigest()
        self.mask = None

    def observe(self, bits, action, outcome, *, phase):
        if self.mask is not None:
            raise ValueError("learned binding frozen")
        self.base.observe(bits, action, outcome, phase=phase)

    def _derive(self):
        if len(self.base.train) != TRAIN_WITNESSES or len(self.base.valid) != VALID_WITNESSES:
            raise ValueError("incomplete residual fit and validation evidence")
        if hashlib.sha256(self.base.bank.snapshot()).hexdigest() != self.bank_sha:
            raise ValueError("primitive lineage changed")
        counts = [[0, 0] for _ in range(8)]
        pairs = {}
        for bits, action, y in self.base.train:
            sig = _signals(self.base.bank, self.base.keys, bits, action)
            if sig is None:
                return None
            counts[_index(sig)][y] += 1
            pairs.setdefault(bits, {})[action] = y
        if any(sum(row) < MIN_PER_PATTERN or row[0] == row[1] for row in counts):
            return None
        # Matching publicly witnessed interventions are necessary, not
        # proof of authentic source-level do-operator effects.
        contrasts = 0
        for bits, actions in pairs.items():
            if len(actions) == 2 and actions[0] != actions[1]:
                s0 = _signals(self.base.bank, self.base.keys, bits, 0)
                s1 = _signals(self.base.bank, self.base.keys, bits, 1)
                if s0 is not None and s1 is not None and s0 != s1:
                    contrasts += 1
        if contrasts < MIN_PAIRED_CONTRASTS:
            return None
        mask = sum(int(pos > neg) << i for i, (neg, pos) in enumerate(counts))
        if mask in FIXED_MASKS:
            return None
        best = min(_programs(), key=lambda p: (
            sum((_forecast(_predict(p, _signals(self.base.bank, self.base.keys, b, a))) - y) ** 2
                for b, a, y in self.base.train), p))
        fixed, invented = 0.0, 0.0
        for bits, action, y in self.base.valid:
            sig = _signals(self.base.bank, self.base.keys, bits, action)
            if sig is None:
                return None
            fixed += (_forecast(_predict(best, sig)) - y) ** 2
            invented += (_forecast((mask >> _index(sig)) & 1) - y) ** 2
        return mask if (fixed - invented) / VALID_WITNESSES >= VALID_BRIER_GAIN else None

    def compile(self):
        if self.mask is not None:
            raise ValueError("already compiled")
        self.mask = self._derive()
        return self.mask is not None

    def predict(self, bits, action):
        _context(bits, action)
        if self.mask is None:
            return None
        if hashlib.sha256(self.base.bank.snapshot()).hexdigest() != self.bank_sha:
            raise ValueError("primitive changed after invention")
        sig = _signals(self.base.bank, self.base.keys, bits, action)
        return None if sig is None else _forecast((self.mask >> _index(sig)) & 1)

    def snapshot(self):
        return _sealed({"schema": SCHEMA, "bank": self.bank_sha, "keys": self.base.keys,
                        "train": self.base.train, "valid": self.base.valid,
                        "mask": self.mask})

    @classmethod
    def restore(cls, bank, blob):
        raw = _unseal(blob)
        if type(raw) is not dict or raw.get("schema") != SCHEMA:
            raise ValueError("invalid residual checkpoint schema")
        obj = cls(bank, raw.get("keys"))
        if raw.get("bank") != obj.bank_sha:
            raise ValueError("primitive cold-restore lineage mismatch")
        for phase, maximum in (("train", TRAIN_WITNESSES), ("valid", VALID_WITNESSES)):
            rows = raw.get(phase)
            if type(rows) is not list or len(rows) > maximum:
                raise ValueError("invalid residual witness budget")
            for row in rows:
                if type(row) is not list or len(row) != 3:
                    raise ValueError("invalid residual witness")
                obj.observe(row[0], row[1], row[2], phase=phase.upper())
        stored = raw.get("mask")
        if stored is not None:
            if type(stored) is not int or not 0 <= stored <= 255 or obj._derive() != stored:
                raise ValueError("residual binding contradicts witnessed outcomes")
            obj.mask = stored
        if obj.snapshot() != blob:
            raise ValueError("noncanonical residual checkpoint")
        return obj


class ExactTruthTableBayes:
    """FULL 256-function independent comparator; exact, uniformly prior weighted."""

    def __init__(self, bank, keys):
        self.bank, self.keys = bank, tuple(keys)
        self.bank_sha = hashlib.sha256(bank.snapshot()).hexdigest()
        _signals(bank, keys, (0, 0, 0, 0, 0), 0)
        self.posterior = None

    def fit(self, train):
        if type(train) not in (tuple, list) or len(train) != TRAIN_WITNESSES:
            raise ValueError("exact 256-function control needs 96 public fit witnesses")
        if hashlib.sha256(self.bank.snapshot()).hexdigest() != self.bank_sha:
            raise ValueError("exact comparator primitive lineage mismatch")
        rows = [[0, 0] for _ in range(8)]
        for bits, action, outcome in train:
            _context(bits, action)
            if type(outcome) is not int or outcome not in (0, 1):
                raise ValueError("invalid public outcome")
            sig = _signals(self.bank, self.keys, bits, action)
            if sig is None:
                raise ValueError("exact comparator lacks equal public evidence")
            rows[_index(sig)][outcome] += 1
        loglike = []
        for mask in range(256):
            ll = sum(
                rows[k][(mask >> k) & 1] * math.log(1 - NOISE)
                + rows[k][1 - ((mask >> k) & 1)] * math.log(NOISE)
                for k in range(8))
            loglike.append(ll)
        peak = max(loglike)
        mass = [math.exp(v - peak) for v in loglike]
        total = sum(mass)
        self.posterior = tuple(v / total for v in mass)
        return self

    def predict(self, bits, action):
        if self.posterior is None:
            raise ValueError("full exact comparator not fitted")
        if hashlib.sha256(self.bank.snapshot()).hexdigest() != self.bank_sha:
            raise ValueError("exact comparator primitive lineage mismatch")
        sig = _signals(self.bank, self.keys, bits, action)
        return None if sig is None else _forecast(
            sum(weight for mask, weight in enumerate(self.posterior)
                if (mask >> _index(sig)) & 1))
