"""ACE03 reference control: bounded, public-keyed marginal Beta counters.

Jointly observed binary outputs only. No hidden context IDs, learning claims,
source authority, or automatic eviction. The caller supplies a public key.
"""
import hashlib
import struct
from fractions import Fraction

HEADER = struct.Struct('<8sHHQ')
CELL = struct.Struct('<5H')
MAGIC = b'ACE03SC1'
PATTERNS = 512
LIMIT = 65535


class SharedCountControl:
    def __init__(self, public_keys=3):
        if type(public_keys) is not int or not 1 <= public_keys <= 16:
            raise ValueError('public key capacity')
        self.public_keys = public_keys
        self.cursor = 0
        self._cells = bytearray(public_keys * PATTERNS * CELL.size)

    def _offset(self, key, pattern):
        if (type(key) is not int or not 0 <= key < self.public_keys
                or type(pattern) is not int or not 0 <= pattern < PATTERNS):
            raise ValueError('invalid public key or pattern')
        return (key * PATTERNS + pattern) * CELL.size

    def predict(self, key, pattern):
        n, *counts = CELL.unpack_from(self._cells, self._offset(key, pattern))
        return tuple(Fraction(k + 1, n + 2) for k in counts)

    def observe(self, sequence, key, pattern, outcomes):
        if type(sequence) is not int or sequence != self.cursor or sequence >= 2**64 - 1:
            raise ValueError('sequence mismatch or exhaustion')
        if (type(outcomes) is not tuple or len(outcomes) != 4
                or any(type(x) is not int or x not in (0, 1) for x in outcomes)):
            raise ValueError('four jointly observed binary outputs required')
        offset = self._offset(key, pattern)
        n, *counts = CELL.unpack_from(self._cells, offset)
        if n == LIMIT:
            raise OverflowError('counter capacity exhausted')
        CELL.pack_into(self._cells, offset, n + 1, *(k + y for k, y in zip(counts, outcomes)))
        self.cursor += 1

    def checkpoint(self):
        payload = HEADER.pack(MAGIC, self.public_keys, PATTERNS, self.cursor) + self._cells
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw) < HEADER.size + 32:
            raise ValueError('checkpoint envelope')
        if len(raw) > HEADER.size + 16 * PATTERNS * CELL.size + 32:
            raise ValueError('checkpoint size')
        payload, digest = raw[:-32], raw[-32:]
        if hashlib.sha256(payload).digest() != digest:
            raise ValueError('checkpoint digest')
        magic, keys, patterns, cursor = HEADER.unpack_from(payload)
        if magic != MAGIC or patterns != PATTERNS:
            raise ValueError('checkpoint schema')
        model = cls(keys)
        if len(payload) != HEADER.size + len(model._cells):
            raise ValueError('checkpoint length')
        model._cells[:] = payload[HEADER.size:]
        total = 0
        for n, *counts in CELL.iter_unpack(model._cells):
            if any(k > n for k in counts):
                raise ValueError('invalid evidence counts')
            total += n
        if total != cursor:
            raise ValueError('cursor/count inconsistency')
        model.cursor = cursor
        return model
