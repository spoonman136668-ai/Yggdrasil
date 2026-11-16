"""CB3: learn which PUBLIC features gate four delayed-reward causal relations.

Unknown source feature positions are never passed here. This is bounded,
source-blind synthetic development, not native Yggdrasil or scientific first use.
Candidate uses a two-stage contradiction-gated search; conventional comparator
independently enumerates every four-feature Boolean truth table.
"""
from __future__ import annotations
from itertools import combinations
from hashlib import sha256
import struct

from binding import _credit_public, _feature_bits, _history, _state

FEATURES = 38
CREDITS = 512
MAX_CHECKPOINT = 128
MAGIC = b"FCB3"

def _score_bins(samples, features, minimum=4):
    n = 1 << len(features)
    cells = [[0, 0] for _ in range(n)]
    for bits, label in samples:
        idx = 0
        for feature in features:
            idx = (idx << 1) | ((bits >> feature) & 1)
        cells[idx][label] += 1
    if any(sum(row) < minimum for row in cells):
        return None
    score = sum(max(row) for row in cells)
    truth = sum((int(pos > neg) << i) for i, (neg, pos) in enumerate(cells))
    return score, truth

def _extract(row):
    credit, packed = _credit_public(row)
    if credit is None:
        return None, packed
    bits, label = credit
    if type(bits) is not int or bits >> FEATURES or label not in (0, 1):
        raise ValueError("CB3_PUBLIC_FEATURE_RANGE")
    return (bits, label), packed

def _fit_base(samples):
    best = None
    for a, b in combinations(range(FEATURES), 2):
        scored = _score_bins(samples, (a, b))
        if scored is None:
            continue
        score, truth = scored
        if best is None or score > best[0]:
            best = score, a, b, truth
    if best is None:
        raise ValueError("CB3_BASE_PAIR_UNIDENTIFIABLE")
    return best

def _fit_conditional(samples, a, b):
    best = None
    for g0, g1 in combinations((x for x in range(FEATURES) if x not in (a, b)), 2):
        scored = _score_bins(samples, (a, b, g0, g1))
        if scored is None:
            continue
        score, truth = scored
        if best is None or score > best[0]:
            best = score, a, b, g0, g1, truth
        if best[0] == len(samples):
            break  # lexicographically first perfect gate-pair already found
    if best is None:
        raise ValueError("CB3_GATE_PAIR_UNIDENTIFIABLE")
    return best

class DiscoveredGateBinder:
    """During fit 512 credited public examples; after seal only four bit IDs and 16-bit table."""

    RAW_EVIDENCE_BYTES = CREDITS * 6
    CHECKPOINT_BYTES = 4 + 4 + 2 + 2 + 2 + 32 + 32  # 78
    def __init__(self):
        self._samples = bytearray()
        self._digest = sha256()
        self._count = 0
        self._binding = None
        self._cold_digest = None

    def observe_public(self, row):
        if self._binding is not None:
            raise ValueError("CB3_SEALED")
        if self._count >= CREDITS:
            raise ValueError("CB3_BUDGET")
        credit, packed = _extract(row)
        if credit is None:
            return
        self._samples.extend(packed)
        self._digest.update(packed)
        self._count += 1

    def seal(self):
        if self._binding is not None:
            raise ValueError("CB3_ALREADY_SEALED")
        if self._count != CREDITS:
            raise ValueError("CB3_INCOMPLETE_PUBLIC_EXPOSURE")
        examples = [(int.from_bytes(self._samples[i:i+5], "little"), self._samples[i+5])
                    for i in range(0, len(self._samples), 6)]
        base_score, a, b, base_truth = _fit_base(examples)
        if base_score / CREDITS >= .90:
            raise ValueError("CB3_NO_CONTRADICTION_NEEDS_NO_GATE")
        score, a, b, g0, g1, truth = _fit_conditional(examples, a, b)
        if score < int(.95 * CREDITS):
            raise ValueError("CB3_NO_SUPPORTED_CONTEXT_GATE")
        self._binding = (a, b, g0, g1, truth, base_score, score)
        self._samples.clear()
        return self

    def choose_public(self, before, history):
        if self._binding is None:
            return None
        state = _state(before)
        past = _history(history, state)
        prior = past[-1].action if past else 0
        older = past[-2].action if len(past) > 1 else 0
        bits = _feature_bits(state, prior, older)
        a, b, g0, g1, truth, _, _ = self._binding
        key = (((bits >> a) & 1) << 3 | ((bits >> b) & 1) << 2 |
               ((bits >> g0) & 1) << 1 | ((bits >> g1) & 1))
        return (truth >> key) & 1

    @property
    def learned(self):
        return self._binding

    def snapshot(self):
        if self._binding is None:
            raise ValueError("CB3_NOT_SEALED")
        a, b, g0, g1, truth, base_score, correct = self._binding
        digest = self._cold_digest if self._cold_digest is not None else self._digest.digest()
        payload = struct.pack(">4s4BHHH", MAGIC, a, b, g0, g1, truth, base_score, correct) + digest
        snap = payload + sha256(payload).digest()
        if len(snap) > MAX_CHECKPOINT:
            raise ValueError("CB3_SERIALIZED_CAPACITY")
        return snap

    @classmethod
    def restore(cls, snapshot):
        if type(snapshot) is not bytes or len(snapshot) != cls.CHECKPOINT_BYTES:
            raise ValueError("CB3_INVALID_SNAPSHOT")
        if sha256(snapshot[:-32]).digest() != snapshot[-32:]:
            raise ValueError("CB3_INVALID_CHECKSUM")
        head = struct.calcsize(">4s4BHHH")
        magic, a, b, g0, g1, truth, base_score, score = struct.unpack(">4s4BHHH", snapshot[:head])
        if (magic != MAGIC or not 0 <= a < b < FEATURES or
            not 0 <= g0 < g1 < FEATURES or len({a, b, g0, g1}) != 4 or
            not 0 <= truth <= 65535 or not 0 <= base_score < int(.9*CREDITS) or
            not int(.95*CREDITS) <= score <= CREDITS):
            raise ValueError("CB3_INVALID_MODEL_FIELDS")
        model = cls()
        model._binding = a, b, g0, g1, truth, base_score, score
        model._count = CREDITS
        model._cold_digest = snapshot[head:head+32]
        if model.snapshot() != snapshot:
            raise ValueError("CB3_INVALID_NONCANONICAL_SNAPSHOT")
        return model

    def receipt(self):
        return sha256(self.snapshot()).hexdigest()

class ConventionalExhaustiveFour:
    """Independently implemented exact conventional search of all 73,815 4-bit forms."""

    def __init__(self):
        self.samples = []
        self.fitted = None

    def observe_public(self, row):
        if self.fitted is not None or len(self.samples) >= CREDITS:
            raise ValueError("CB3_SYMBOLIC_BUDGET_OR_SEALED")
        credit, _ = _extract(row)
        if credit is not None:
            self.samples.append(credit)

    def seal(self):
        if self.fitted is not None or len(self.samples) != CREDITS:
            raise ValueError("CB3_SYMBOLIC_INCOMPLETE")
        # Independent bitset cross-check of arbitrary four-input Boolean functions.
        full = (1 << CREDITS) - 1
        positive = 0
        flags = [0] * FEATURES
        for i, (bits, answer) in enumerate(self.samples):
            if answer:
                positive |= 1 << i
            for j in range(FEATURES):
                if (bits >> j) & 1:
                    flags[j] |= 1 << i
        negative = full ^ positive
        zero = [full ^ f for f in flags]
        best = None
        for aa, bb, cc, dd in combinations(range(FEATURES), 4):
            # Build 16 full public-state truth bins. A perfect representation
            # makes early stopping valid and preserves lexicographic tie order.
            score, truth = 0, 0
            missing = False
            for cell in range(16):
                group = (flags[aa] if cell & 8 else zero[aa]) & (flags[bb] if cell & 4 else zero[bb])
                group &= (flags[cc] if cell & 2 else zero[cc])
                group &= (flags[dd] if cell & 1 else zero[dd])
                pos = (group & positive).bit_count()
                neg = (group & negative).bit_count()
                if pos + neg < 4:
                    missing = True
                    break
                score += max(pos, neg)
                if pos > neg:
                    truth |= 1 << cell
            if missing:
                continue
            if best is None or score > best[0]:
                best = score, (aa, bb, cc, dd), truth
            if best is not None and best[0] == CREDITS:
                break
        if best is None or best[0] < int(.95 * CREDITS):
            raise ValueError("CB3_SYMBOLIC_NO_SUPPORTED_RULE")
        self.fitted = best
        self.samples.clear()
        return self

    def choose_public(self, before, history):
        if self.fitted is None:
            return None
        state = _state(before)
        past = _history(history, state)
        p = past[-1].action if past else 0
        q = past[-2].action if len(past) > 1 else 0
        bits = _feature_bits(state, p, q)
        _, features, truth = self.fitted
        idx = 0
        for feature in features:
            idx = (idx << 1) | ((bits >> feature) & 1)
        return (truth >> idx) & 1
