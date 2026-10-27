"""Development-only public-observation causal cells with local plasticity.

Sixteen total addresses: seven fast active cells and nine slow retained cells.
The mechanism stores only action-conditioned public-outcome traces. It has no
outcome oracle, transformer, model API, source-family selection, or scientific
authority. This source is a candidate mechanism, not an experimental result.
"""

from __future__ import annotations

import hashlib
import struct


class PublicCausalCells:
    """Fixed 16 x 2 action x 2 locally plastic public-outcome traces.

    Active cells apply bounded decay to a non-saturated acted-on outcome trace;
    retained cells are saturating count traces. Saturated traces remain at the
    representable maximum when reinforced, preserving fixed-width checkpoint
    semantics while sacrificing further frequency resolution at that ceiling.
    """

    __slots__ = ("_counts",)

    ACTIVE_SLOTS = 7
    RETAINED_SLOTS = 9
    LEARNED_BYTES = 16 * 2 * 2 * 2
    MAGIC = b"YPC1"
    CHECKPOINT_BYTES = len(MAGIC) + LEARNED_BYTES + 32
    _ACTIVE_LEAK_SHIFT = 3
    _COUNT_MAX = 65535

    def __init__(self) -> None:
        self._counts = [[[0, 0] for _ in range(2)] for _ in range(16)]

    @staticmethod
    def _bit(value: int, name: str) -> int:
        if type(value) is not int or value not in (0, 1):
            raise ValueError(f"PUBLIC_CAUSAL_{name}_INVALID")
        return value

    @classmethod
    def _address(cls, address: int, retained: bool) -> int:
        if type(retained) is not bool:
            raise ValueError("PUBLIC_CAUSAL_RETAINED_FLAG_INVALID")
        limit = cls.RETAINED_SLOTS if retained else cls.ACTIVE_SLOTS
        if type(address) is not int or not 0 <= address < limit:
            raise ValueError("PUBLIC_CAUSAL_ADDRESS_INVALID")
        return address + (cls.ACTIVE_SLOTS if retained else 0)

    def observe(self, address: int, action: int, public_outcome: int, *,
                retained: bool = False) -> None:
        """Update only the acted-on arm after a revealed public outcome.

        Active traces decay only while the reinforced outcome remains below the
        fixed-width ceiling. This avoids turning repeated reinforcement of an
        already saturated trace into an unintended decrement.
        """
        cell = self._address(address, retained)
        arm = self._bit(action, "ACTION")
        result = self._bit(public_outcome, "PUBLIC_OUTCOME")
        traces = self._counts[cell][arm]
        if not retained and traces[result] < self._COUNT_MAX:
            traces[0] -= traces[0] >> self._ACTIVE_LEAK_SHIFT
            traces[1] -= traces[1] >> self._ACTIVE_LEAK_SHIFT
        traces[result] = min(self._COUNT_MAX, traces[result] + 1)

    def choose(self, address: int, *, retained: bool = False) -> int | None:
        """Choose the arm with the greater learned public success rate."""
        cell = self._address(address, retained)
        (zero0, one0), (zero1, one1) = self._counts[cell]
        trials0 = zero0 + one0
        trials1 = zero1 + one1
        if not trials0 or not trials1:
            return None
        lhs, rhs = one0 * trials1, one1 * trials0
        if lhs == rhs:
            return None
        return 0 if lhs > rhs else 1

    def snapshot(self) -> bytes:
        """Return an immutable, versioned checkpoint with SHA-256 integrity."""
        raw = bytearray(self.MAGIC)
        for cell in self._counts:
            for arm in cell:
                for count in arm:
                    raw.extend(struct.pack(">H", count))
        digest = hashlib.sha256(raw).digest()
        return bytes(raw) + digest

    @classmethod
    def restore(cls, checkpoint: bytes) -> "PublicCausalCells":
        if (type(checkpoint) is not bytes or
                len(checkpoint) != cls.CHECKPOINT_BYTES or
                checkpoint[:len(cls.MAGIC)] != cls.MAGIC or
                hashlib.sha256(checkpoint[:-32]).digest() != checkpoint[-32:]):
            raise ValueError("PUBLIC_CAUSAL_CHECKPOINT_REJECTED")
        learned = checkpoint[len(cls.MAGIC):-32]
        cells = cls()
        iterator = iter(struct.unpack(">" + ("H" * 64), learned))
        for i in range(16):
            for arm in range(2):
                for outcome in range(2):
                    cells._counts[i][arm][outcome] = next(iterator)
        return cells
