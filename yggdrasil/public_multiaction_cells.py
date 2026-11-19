"""YGG-ACT01: opt-in four-action, four-outcome *native* public causal cells.

The original PYC1 binary causal-cell class/checkpoint is untouched. This
capacity extension stores only actually observed public interventions and
their observed outcomes, preserves a byte-exact optional PYC1 origin, and
requires receipt identities for every new witness. Those IDs are NOT an
external source-owner signature. No actor, source access or science claim.
"""
from __future__ import annotations

import hashlib
import re
import struct

from yggdrasil.public_causal_cells import PublicCausalCells


class NativeMultiActionCells:
    """16 original native slots, four physical action and outcome identities.

    The counted memory is a conventional multicategorical contingency table,
    NOT a novel causal inference algorithm. An action may only be predicted
    after *that* action has genuine witnessed public outcomes. No cross-action
    mapping is hardcoded and no unobserved counterfactual is admitted.
    """

    __slots__ = ("_counts", "_origin", "_events", "_ids")

    MAGIC = b"YAC2"
    ACTIVE_SLOTS = PublicCausalCells.ACTIVE_SLOTS
    RETAINED_SLOTS = PublicCausalCells.RETAINED_SLOTS
    ACTIONS = 4
    OUTCOMES = 4
    MAX_EVENTS = 256
    LEARNED_BYTES = 16 * ACTIONS * OUTCOMES * 2
    EVENT_BYTES = 36
    ORIGIN_BYTES = PublicCausalCells.CHECKPOINT_BYTES
    HEADER_BYTES = len(MAGIC) + ORIGIN_BYTES + 2
    MIN_CHECKPOINT_BYTES = HEADER_BYTES + LEARNED_BYTES + 32
    MAX_CHECKPOINT_BYTES = MIN_CHECKPOINT_BYTES + EVENT_BYTES * MAX_EVENTS
    _NO_ORIGIN = bytes(ORIGIN_BYTES)

    def __init__(self):
        self._counts = [[[0] * self.OUTCOMES for _ in range(self.ACTIONS)]
                        for _ in range(self.ACTIVE_SLOTS + self.RETAINED_SLOTS)]
        self._origin = self._NO_ORIGIN
        self._events = []
        self._ids = {}

    @staticmethod
    def _choice(value, stop, label):
        if type(value) is not int or not 0 <= value < stop:
            raise ValueError(f"NATIVE_ACTION_{label}_INVALID")
        return value

    @classmethod
    def _cell(cls, address, retained):
        if type(retained) is not bool:
            raise ValueError("NATIVE_ACTION_RETAINED_FLAG_INVALID")
        stop = cls.RETAINED_SLOTS if retained else cls.ACTIVE_SLOTS
        return cls._choice(address, stop, "ADDRESS") + (
            cls.ACTIVE_SLOTS if retained else 0)

    @staticmethod
    def _source_id(source_id):
        if type(source_id) is not str or re.fullmatch(
                r"[0-9a-f]{64}", source_id) is None:
            raise ValueError("NATIVE_ACTION_SOURCE_ID_INVALID")
        return source_id

    @classmethod
    def migrate(cls, original_binary_snapshot):
        """Carry the exact original PYC1 learned bytes into 4x4 native space."""
        if type(original_binary_snapshot) is not bytes:
            raise ValueError("NATIVE_ACTION_ORIGIN_TYPE")
        legacy = PublicCausalCells.restore(original_binary_snapshot)
        new = cls()
        new._origin = original_binary_snapshot
        for address in range(cls.ACTIVE_SLOTS + cls.RETAINED_SLOTS):
            for action in (0, 1):
                for outcome in (0, 1):
                    new._counts[address][action][outcome] = (
                        legacy._counts[address][action][outcome])
        return new

    def original_binary_snapshot(self):
        """No recomputation or reinterpretation of the old trained checkpoint."""
        return None if self._origin == self._NO_ORIGIN else self._origin

    def observe(self, source_id, address, action, observed_outcome, *,
                retained=False):
        """Append *one actually witnessed public* action/outcome only.

        Return False for an exactly duplicate source receipt; any attempt
        to alter an already consumed source receipt fails closed.
        """
        ref = self._source_id(source_id)
        cell = self._cell(address, retained)
        arm = self._choice(action, self.ACTIONS, "ACTION")
        outcome = self._choice(observed_outcome, self.OUTCOMES, "OUTCOME")
        event = (ref, address, arm, outcome, retained)
        previous = self._ids.get(ref)
        if previous is not None:
            if previous != event:
                raise ValueError("NATIVE_ACTION_CONFLICTING_SOURCE")
            return False
        if len(self._events) >= self.MAX_EVENTS:
            raise ValueError("NATIVE_ACTION_SOURCE_BUDGET")
        old = self._counts[cell][arm][outcome]
        self._counts[cell][arm][outcome] = min(65535, old + 1)
        self._events.append(event)
        self._ids[ref] = event
        return True

    def counts(self, address, action, *, retained=False):
        """Return exact public-count state as four immutable integer counts."""
        cell = self._cell(address, retained)
        arm = self._choice(action, self.ACTIONS, "ACTION")
        return tuple(self._counts[cell][arm])

    def probability(self, address, action, observed_outcome, *, retained=False):
        """Return exact Dirichlet(1) rational count/total; None when unseen.

        This is a *fully conventional, explicit* baseline, not novel transfer.
        """
        row = self.counts(address, action, retained=retained)
        index = self._choice(observed_outcome, self.OUTCOMES, "OUTCOME")
        total = sum(row)
        if not total:
            return None
        return (row[index] + 1, total + self.OUTCOMES)

    def choose(self, address, target_outcome, *, retained=False):
        """Abstain until all four arms witnessed; compare exact integer rates.

        There is no source actor here and no claim that observed rates imply
        effects of unchosen interventions. Ties abstain rather than guess.
        """
        cell = self._cell(address, retained)
        outcome = self._choice(target_outcome, self.OUTCOMES, "OUTCOME")
        rows = self._counts[cell]
        totals = [sum(row) for row in rows]
        if not all(totals):
            return None
        winner = 0
        tied = False
        for arm in range(1, self.ACTIONS):
            left = rows[arm][outcome] * totals[winner]
            right = rows[winner][outcome] * totals[arm]
            if left > right:
                winner, tied = arm, False
            elif left == right:
                tied = True
        return None if tied else winner

    def snapshot(self):
        """Versioned causal memory, exact optional origin, ordered source tape."""
        if len(self._events) > self.MAX_EVENTS:
            raise ValueError("NATIVE_ACTION_SOURCE_BUDGET")
        raw = bytearray(self.MAGIC)
        raw.extend(self._origin)
        raw.extend(struct.pack(">H", len(self._events)))
        for row in self._counts:
            for action in row:
                for v in action:
                    if type(v) is not int or not 0 <= v <= 65535:
                        raise ValueError("NATIVE_ACTION_COUNT_OUT_OF_RANGE")
                    raw.extend(struct.pack(">H", v))
        for ref, address, action, outcome, retained in self._events:
            raw.extend(bytes.fromhex(ref))
            raw.extend(bytes((address, action, outcome, int(retained))))
        if not self.MIN_CHECKPOINT_BYTES <= len(raw) + 32 <= self.MAX_CHECKPOINT_BYTES:
            raise ValueError("NATIVE_ACTION_CHECKPOINT_BOUNDS")
        return bytes(raw) + hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls, checkpoint):
        """Reconstruct from origin + source tape; count bytes must match.

        A self-consistently forged complete alternative source history
        cannot be ruled out by SHA256 alone; authenticated source custody
        must be separately provided by the independent owner.
        """
        if type(checkpoint) is not bytes or not (
                cls.MIN_CHECKPOINT_BYTES <= len(checkpoint) <=
                cls.MAX_CHECKPOINT_BYTES) or (
                checkpoint[:4] != cls.MAGIC or
                hashlib.sha256(checkpoint[:-32]).digest() != checkpoint[-32:]):
            raise ValueError("NATIVE_ACTION_CHECKPOINT_REJECTED")
        original = checkpoint[4:4 + cls.ORIGIN_BYTES]
        count = struct.unpack(">H", checkpoint[
            4 + cls.ORIGIN_BYTES:cls.HEADER_BYTES])[0]
        if count > cls.MAX_EVENTS or len(checkpoint) != (
                cls.MIN_CHECKPOINT_BYTES + cls.EVENT_BYTES * count):
            raise ValueError("NATIVE_ACTION_CHECKPOINT_LENGTH")
        try:
            if original == cls._NO_ORIGIN:
                state = cls()
            else:
                state = cls.migrate(original)
            stored = checkpoint[cls.HEADER_BYTES:
                                cls.HEADER_BYTES + cls.LEARNED_BYTES]
            i = cls.HEADER_BYTES + cls.LEARNED_BYTES
            for _ in range(count):
                ref = checkpoint[i:i + 32].hex()
                address, arm, result, retained = checkpoint[i + 32:i + 36]
                if retained not in (0, 1):
                    raise ValueError("NATIVE_ACTION_EVENT_RETAINED")
                state.observe(ref, address, arm, result,
                              retained=bool(retained))
                i += cls.EVENT_BYTES
            actual = bytearray()
            for row in state._counts:
                for arm in row:
                    for value in arm:
                        actual.extend(struct.pack(">H", value))
            if bytes(actual) != stored or state.snapshot() != checkpoint:
                raise ValueError("NATIVE_ACTION_WITNESS_REPLAY_MISMATCH")
            return state
        except (IndexError, TypeError, OverflowError, struct.error) as exc:
            raise ValueError("NATIVE_ACTION_CHECKPOINT_REPLAY") from exc
