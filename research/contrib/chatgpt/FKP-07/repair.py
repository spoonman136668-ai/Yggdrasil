"""FKP-07 fixed-capacity direct causal-pair weight updates and independent replay.

The shared 496 unsigned counters are actual mutable numerical weights. A
revision updates the SAME context slot and counter array, subtracting the
old learnt pair contributions before adding new ones, without appending a
posterior/version slot. There are no native Yggdrasil production writes.
"""
from __future__ import annotations
from array import array
import hashlib
import struct

N_INPUT = 32
SLOTS = 32
PAIRS = tuple((i, j) for i in range(N_INPUT) for j in range(i + 1, N_INPUT))
PAIR_INDEX = {p: i for i, p in enumerate(PAIRS)}
assert len(PAIRS) == 496
RAW_LEARNED_BYTES = 496 * 2 + 32 * 4
MAGIC = b"FP07"
CHECKPOINT_BYTES = len(MAGIC) + RAW_LEARNED_BYTES + 4 + 32


def pair_indices(law: tuple[int, int, int, int]) -> tuple[int, int]:
    if (not isinstance(law, tuple) or len(law) != 4 or
            any(type(v) is not int or not 0 <= v < N_INPUT for v in law) or
            len(set(law)) != 4):
        raise ValueError("FKP07_LAW_NOT_FOUR_DISTINCT_PARENTS")
    return (PAIR_INDEX[tuple(sorted(law[:2]))],
            PAIR_INDEX[tuple(sorted(law[2:]))])


def predict_law(law: tuple[int, ...], state: int) -> int:
    if type(state) is not int or not 0 <= state < (1 << N_INPUT):
        raise ValueError("FKP07_STATE_INVALID")
    a, b, c, d = law
    return (((state >> a) & (state >> b) & 1) ^
            ((state >> c) & (state >> d) & 1))


class SharedWeights:
    """One 1,120-byte learned-state area, no dynamically added slots."""

    __slots__ = ("counters", "programs", "occupied")

    def __init__(self):
        self.counters = array("H", [0] * len(PAIRS))
        self.programs = bytearray(SLOTS * 4)
        self.occupied = 0

    def program(self, slot: int) -> tuple[int, int, int, int] | None:
        if type(slot) is not int or not 0 <= slot < SLOTS:
            raise ValueError("FKP07_SLOT_OUTSIDE_FIXED_CAPACITY")
        if not (self.occupied >> slot) & 1:
            return None
        return tuple(self.programs[slot * 4:slot * 4 + 4])

    def update(self, slot: int, law: tuple[int, int, int, int]) -> None:
        # Fail closed before modifying any old weights or evidence.
        if type(slot) is not int or not 0 <= slot < SLOTS:
            raise ValueError("FKP07_SLOT_OUTSIDE_FIXED_CAPACITY")
        new = pair_indices(law)
        previous = self.program(slot)
        old = pair_indices(previous) if previous is not None else ()
        if previous == law:
            return
        delta: dict[int, int] = {}
        for idx in old:
            delta[idx] = delta.get(idx, 0) - 1
        for idx in new:
            delta[idx] = delta.get(idx, 0) + 1
        if any(not 0 <= self.counters[idx] + step <= 65535
               for idx, step in delta.items()):
            raise ValueError("FKP07_WEIGHT_REPAIR_BOUNDS")
        for idx, step in delta.items():
            self.counters[idx] += step
        self.programs[slot * 4:slot * 4 + 4] = bytes(law)
        self.occupied |= 1 << slot

    def predict(self, slot: int, state: int) -> int | None:
        law = self.program(slot)
        return None if law is None else predict_law(law, state)

    def snapshot(self) -> bytes:
        payload = (MAGIC + struct.pack(">" + "H" * len(PAIRS), *self.counters) +
                   bytes(self.programs) + struct.pack(">I", self.occupied))
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, snapshot: bytes) -> "SharedWeights":
        if (type(snapshot) is not bytes or len(snapshot) != CHECKPOINT_BYTES or
                snapshot[:4] != MAGIC or
                hashlib.sha256(snapshot[:-32]).digest() != snapshot[-32:]):
            raise ValueError("FKP07_SNAPSHOT_TAMPER_OR_SCHEMA")
        obj = cls()
        pos = 4
        weights_len = len(PAIRS) * 2
        parsed = struct.unpack(">" + "H" * len(PAIRS), snapshot[pos:pos + weights_len])
        obj.counters = array("H", parsed)
        pos += weights_len
        obj.programs = bytearray(snapshot[pos:pos + SLOTS * 4])
        pos += SLOTS * 4
        obj.occupied = struct.unpack(">I", snapshot[pos:pos + 4])[0]
        # Recalculate independently from ONLY recorded learnt programs.
        replay = ReplayControl()
        for slot in range(SLOTS):
            program = obj.program(slot)
            if program is not None:
                replay.update(slot, program)
        if tuple(replay.counters) != tuple(obj.counters):
            raise ValueError("FKP07_SNAPSHOT_WEIGHTS_INCONSISTENT_WITH_CAUSAL_MEMORY")
        return obj


class ReplayControl:
    """Independent, fully informed conventional exact replay at same capacity."""
    __slots__ = ("records", "counters")

    def __init__(self):
        self.records: list[tuple[int, int, int, int] | None] = [None] * SLOTS
        self.counters = array("H", [0] * 496)

    def update(self, slot: int, law: tuple[int, int, int, int]):
        if type(slot) is not int or not 0 <= slot < SLOTS:
            raise ValueError("FKP07_REPLAY_SLOT_INVALID")
        pair_indices(law)
        self.records[slot] = law
        new_counts = array("H", [0] * 496)
        # Deliberately independent of SharedWeights' delta mechanism.
        for record in self.records:
            if record is None:
                continue
            for pair in (tuple(sorted(record[:2])), tuple(sorted(record[2:]))):
                idx = PAIRS.index(pair)
                new_counts[idx] += 1
        self.counters = new_counts

    def predict(self, slot: int, state: int) -> int | None:
        if type(slot) is not int or not 0 <= slot < SLOTS:
            raise ValueError("FKP07_REPLAY_SLOT_INVALID")
        record = self.records[slot]
        return None if record is None else predict_law(record, state)


class NaiveOverwrite:
    """Negative: most recent causal rule displaces ALL previously held rules."""
    __slots__ = ("current",)

    def __init__(self):
        self.current: tuple[int, int, int, int] | None = None

    def update(self, slot: int, law: tuple[int, int, int, int]):
        pair_indices(law)
        self.current = law

    def predict(self, slot: int, state: int) -> int | None:
        return None if self.current is None else predict_law(self.current, state)
