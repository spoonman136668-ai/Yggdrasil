"""WSP-01: directly compiled, recurrent binary threshold network (DEV only).

All 384 connection weights are generated once from an explicit public causal
rule family. They are never optimized or updated. Public interventions change
only 16 recurrent hypothesis-state bits. This is an algorithm compiled into
weights, not evidence of generalized cognition.
"""

from __future__ import annotations

import hashlib


SPEC = ("WSP01:v1|h=(context_mask:2,action_flip:1,bias:1)|"
        "reward=parity(context&mask)^(action&flip)^bias|"
        "observe=(0,0),(1,0),(2,0),(0,1)|transfer_context=3|"
        "hypotheses=0..15|order=context_mask,flip,bias")
SPEC_SHA256 = "ccb1a24ad20a91d3e3c5f5962045749f98a5edb67c5a18e950729fa5d9543926"
OBSERVATIONS = ((0, 0), (1, 0), (2, 0), (0, 1))


def _bit(value: int, name: str) -> int:
    if type(value) is not int or value not in (0, 1):
        raise ValueError(f"WSP01_{name}_INVALID")
    return value


def _context(context: int) -> int:
    if type(context) is not int or not 0 <= context < 4:
        raise ValueError("WSP01_CONTEXT_INVALID")
    return context


def public_rule(hypothesis: int, context: int, action: int) -> int:
    """Public source-family generator, used only to compile and score DEV data."""
    if type(hypothesis) is not int or not 0 <= hypothesis < 16:
        raise ValueError("WSP01_HYPOTHESIS_INVALID")
    _context(context)
    _bit(action, "ACTION")
    mask, flip, bias = hypothesis >> 2, (hypothesis >> 1) & 1, hypothesis & 1
    return ((mask & context).bit_count() & 1) ^ (flip & action) ^ bias


def correct_decision(hypothesis: int, context: int) -> int | None:
    p0 = public_rule(hypothesis, context, 0)
    p1 = public_rule(hypothesis, context, 1)
    return 0 if p0 > p1 else (1 if p1 > p0 else None)


class WeightWrittenNetwork:
    """Explicit input->candidate and candidate->action integer weights.

    Candidate update: state[h]' = step(state[h] + W[h,input] - 2).
    Readout: choose an action iff *all* surviving candidates favor that
    action. Empty, ambiguous or tied states abstain. No gradient calls.
    """

    __slots__ = ("_compat", "_votes", "_state")
    MAGIC = b"WSP1"
    HYPOTHESES = 16
    STATIC_WEIGHT_COUNT = 16 * 16 + 4 * 2 * 16
    LEARNED_WEIGHT_COUNT = 0
    STATE_BITS = 16
    CHECKPOINT_BYTES = 4 + 2 + 32

    def __init__(self) -> None:
        # One-hot input slots: (context * 2 + action) * 2 + actual_reward.
        self._compat = tuple(tuple(
            int(public_rule(h, c, a) == outcome)
            for c in range(4) for a in (0, 1) for outcome in (0, 1)
        ) for h in range(self.HYPOTHESES))
        # Nonzero readout weights mean candidate h strictly prefers action.
        self._votes = tuple(tuple(tuple(
            int(correct_decision(h, c) == a)
            for h in range(self.HYPOTHESES)) for a in (0, 1))
            for c in range(4))
        self._state = (1,) * self.HYPOTHESES

    def observe(self, context: int, action: int, public_outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(public_outcome, "OUTCOME")
        slot = (context * 2 + action) * 2 + public_outcome
        self._state = tuple(int(active + row[slot] >= 2)
                            for active, row in zip(self._state, self._compat))

    def choose(self, context: int) -> int | None:
        _context(context)
        viable = sum(self._state)
        if viable == 0:
            return None
        for action in (0, 1):
            votes = sum(bit * weight for bit, weight in
                        zip(self._state, self._votes[context][action]))
            if votes == viable:
                return action
        return None

    @property
    def remaining(self) -> int:
        return sum(self._state)

    def fixed_weights_sha256(self) -> str:
        packed = bytes(v for row in self._compat for v in row)
        packed += bytes(v for ctx in self._votes for row in ctx for v in row)
        assert len(packed) == self.STATIC_WEIGHT_COUNT
        return hashlib.sha256(packed).hexdigest()

    def snapshot(self) -> bytes:
        state_mask = sum(active << h for h, active in enumerate(self._state))
        prefix = self.MAGIC + state_mask.to_bytes(2, "big")
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, blob: bytes) -> "WeightWrittenNetwork":
        if (type(blob) is not bytes or len(blob) != cls.CHECKPOINT_BYTES or
                blob[:4] != cls.MAGIC or
                hashlib.sha256(blob[:-32]).digest() != blob[-32:]):
            raise ValueError("WSP01_CHECKPOINT_REJECTED")
        model = cls()
        state_mask = int.from_bytes(blob[4:6], "big")
        model._state = tuple((state_mask >> h) & 1 for h in range(16))
        return model


class SymbolicVersionSpace:
    """Strong exact-knowledge control: enumerator without connection weights."""

    def __init__(self) -> None:
        self.remaining = set(range(16))

    def observe(self, context: int, action: int, public_outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(public_outcome, "OUTCOME")
        self.remaining = {h for h in self.remaining
                          if public_rule(h, context, action) == public_outcome}

    def choose(self, context: int) -> int | None:
        _context(context)
        if not self.remaining:
            return None
        choices = {correct_decision(h, context) for h in self.remaining}
        return next(iter(choices)) if len(choices) == 1 else None


class TabularControl:
    """Identical public observations; no hand-coded cross-context transfer."""

    def __init__(self) -> None:
        self.counts = [[[0, 0] for _ in range(2)] for _ in range(4)]

    def observe(self, context: int, action: int, public_outcome: int) -> None:
        _context(context)
        _bit(action, "ACTION")
        _bit(public_outcome, "OUTCOME")
        self.counts[context][action][public_outcome] += 1

    def choose(self, context: int) -> int | None:
        _context(context)
        arm0, arm1 = self.counts[context]
        n0, n1 = sum(arm0), sum(arm1)
        if not n0 or not n1:
            return None
        diff = arm0[1] * n1 - arm1[1] * n0
        return 0 if diff > 0 else (1 if diff < 0 else None)
