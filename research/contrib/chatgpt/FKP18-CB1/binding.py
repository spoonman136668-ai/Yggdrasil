"""Research-only compact two-feature relation creation from public delayed feedback.

This is not FKP-17 native admission or an out-of-grammar intelligence claim.
"""
from __future__ import annotations

import hashlib
import json
import struct

REGISTERS = 8
FEATURES = 38  # 8x4 public register bits; last / second-last action 3 bits each
ROWS_LIMIT = 128
CHECKPOINT_MAGIC = b"FCB1"
CHECKPOINT_STRUCT = ">4sBBBHH"
FIELDS = ("before", "action", "after", "reward", "done", "history")
PAST_FIELDS = ("before", "action", "reward", "after", "done")


def _state(state):
    if type(state) not in (tuple, list) or len(state) != REGISTERS or any(
        type(v) is not int or not 0 <= v < 16 for v in state
    ):
        raise ValueError("CB1_PUBLIC_STATE")
    return tuple(state)


def _action(value):
    if type(value) is not int or not 0 <= value < 8:
        raise ValueError("CB1_PUBLIC_ACTION")
    return value


def _history(history, before):
    if type(history) is not tuple or len(history) > 16:
        raise ValueError("CB1_PUBLIC_HISTORY")
    for i, event in enumerate(history):
        if tuple(getattr(event, "_fields", ())) != PAST_FIELDS:
            raise ValueError("CB1_PRIVATE_HISTORY_FIELD")
        _state(event.before)
        _state(event.after)
        _action(event.action)
        if type(event.reward) not in (int, float) or event.reward not in (-1, 0, 1):
            raise ValueError("CB1_PUBLIC_PAST_REWARD")
        if type(event.done) is not bool or event.done:
            raise ValueError("CB1_PUBLIC_PAST_DONE")
        if i and history[i - 1].after != event.before:
            raise ValueError("CB1_HISTORY_GAP")
    if history and history[-1].after != before:
        raise ValueError("CB1_HISTORY_NOT_CURRENT")
    return history


def _feature_bits(state, previous, older):
    state = _state(state)
    _action(previous)
    _action(older)
    bits = sum(state[reg] << (4 * reg) for reg in range(REGISTERS))
    return bits | (previous << 32) | (older << 35)


def _credit_public(row):
    if tuple(getattr(row, "_fields", ())) != FIELDS:
        raise ValueError("CB1_PUBLIC_FIELDS_ONLY")
    before = _state(row.before)
    _state(row.after)
    _action(row.action)
    past = _history(row.history, before)
    if type(row.reward) not in (int, float) or row.reward not in (-1, 0, 1):
        raise ValueError("CB1_PUBLIC_REWARD")
    if type(row.done) is not bool or row.done:
        raise ValueError("CB1_PUBLIC_TERMINATION_UNSUPPORTED")
    if len(past) < 3:
        if row.reward != 0:
            raise ValueError("CB1_PREMATURE_REWARD")
        return None, b""
    if row.reward == 0:
        raise ValueError("CB1_MISSING_DELAYED_REWARD")
    eligible = past[-2]
    if eligible.action not in (0, 1):
        raise ValueError("CB1_BINARY_CREDIT_ACTION_ONLY")
    # Credit the action and publicly observed context from t-2,
    # NOT the current action or the present environment state.
    previous = past[-3].action
    older = past[-4].action if len(past) >= 4 else 0
    bits = _feature_bits(eligible.before, previous, older)
    correct_action = eligible.action if row.reward == 1 else 1 - eligible.action
    return (bits, correct_action), bits.to_bytes(5, "little") + bytes([correct_action])


def _infer(samples):
    if len(samples) < 32 * 6 or len(samples) > ROWS_LIMIT * 6 or len(samples) % 6:
        raise ValueError("CB1_UNFIT_SAMPLE_COUNT")
    best = None
    n = len(samples) // 6
    evidence = [(int.from_bytes(samples[i:i+5], "little"), samples[i+5])
                for i in range(0, len(samples), 6)]
    for a in range(FEATURES):
        for b in range(a + 1, FEATURES):
            bins = [[0, 0] for _ in range(4)]
            for bits, label in evidence:
                x = ((bits >> a) & 1) * 2 | ((bits >> b) & 1)
                bins[x][label] += 1
            if any(sum(pair) == 0 for pair in bins):
                continue
            score = sum(max(pair) for pair in bins)
            truth = sum(int(pair[1] > pair[0]) << i for i, pair in enumerate(bins))
            # Highest empirical fit, deterministic lexicographic tie break.
            if best is None or score > best[0]:
                best = (score, a, b, truth)
    if best is None or best[0] * 10 < 9 * n:
        raise ValueError("CB1_NO_SUPPORTED_TWO_FEATURE_RELATION")
    return best


class ConditionalTemporalBinder:
    """Fast microfeedback recording; after seal only one learned relation remains."""

    RAW_EVIDENCE_LIMIT = ROWS_LIMIT * 6
    CHECKPOINT_BYTES = struct.calcsize(CHECKPOINT_STRUCT) + 32 + 32

    def __init__(self):
        self._samples = bytearray()
        self._digest = hashlib.sha256()
        self._credited = 0
        self._sealed = False
        self._binding = None
        self._stored_digest = None

    def observe_public(self, row):
        if self._sealed:
            raise ValueError("CB1_SEALED_NO_UPDATE")
        if self._credited >= ROWS_LIMIT:
            raise ValueError("CB1_EVIDENCE_CAP")
        credit, packed = _credit_public(row)
        if credit is None:
            return
        # Atomic validation before mutation, no source-law or future labels.
        self._samples.extend(packed)
        self._digest.update(packed)
        self._credited += 1

    def seal(self):
        if self._sealed:
            raise ValueError("CB1_ALREADY_SEALED")
        score, a, b, table = _infer(self._samples)
        self._binding = (a, b, table, self._credited, score)
        self._samples = bytearray()  # no retaining full episodes after fit
        self._sealed = True
        return self

    def choose_public(self, before, history):
        if not self._sealed:
            return None
        state = _state(before)
        past = _history(history, state)
        previous = past[-1].action if past else 0
        older = past[-2].action if len(past) >= 2 else 0
        bits = _feature_bits(state, previous, older)
        a, b, table, _, _ = self._binding
        index = (((bits >> a) & 1) << 1) | ((bits >> b) & 1)
        return (table >> index) & 1

    @property
    def binding(self):
        return self._binding

    def snapshot(self):
        if not self._sealed:
            raise ValueError("CB1_UNSEALED_CHECKPOINT")
        a, b, table, n, correct = self._binding
        payload = struct.pack(CHECKPOINT_STRUCT, CHECKPOINT_MAGIC, a, b,
                              table, n, correct) + (self._stored_digest if self._stored_digest is not None else self._digest.digest())
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, checkpoint):
        if (type(checkpoint) is not bytes or len(checkpoint) != cls.CHECKPOINT_BYTES or
                hashlib.sha256(checkpoint[:-32]).digest() != checkpoint[-32:]):
            raise ValueError("CB1_INVALID_CHECKPOINT")
        width = struct.calcsize(CHECKPOINT_STRUCT)
        magic, a, b, table, n, correct = struct.unpack(CHECKPOINT_STRUCT, checkpoint[:width])
        if (magic != CHECKPOINT_MAGIC or not 0 <= a < b < FEATURES or not 0 <= table < 16 or
                not 32 <= n <= ROWS_LIMIT or correct * 10 < n * 9 or correct > n):
            raise ValueError("CB1_INVALID_CHECKPOINT_FIELDS")
        obj = cls()
        obj._binding = (a, b, table, n, correct)
        obj._sealed = True
        # Exact digest of source-public credited evidence, but no raw episodes.
        obj._digest = None
        obj._stored_digest = checkpoint[width:width+32]
        return obj

    def receipt(self):
        return hashlib.sha256(self.snapshot()).hexdigest()
