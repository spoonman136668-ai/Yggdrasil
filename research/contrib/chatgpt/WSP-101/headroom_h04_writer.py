"""WSP101 H04: bounded gradient-free direct numerical weight programming.

Fits a 56-bit quadratic GF(2) law from public delayed consequences, not
oracle coefficients. Stores actual coefficients as packed numerical weights.
Do not import the world/evaluator or third-party donor data.
"""
from __future__ import annotations

import hashlib
import struct

BITS = 10
TERMS = ((0,) + tuple(1 << i for i in range(BITS))
         + tuple((1 << i) | (1 << j)
                 for i in range(BITS) for j in range(i + 1, BITS)))
WEIGHT_BYTES = 7
SLOT_COUNT = 32
assert len(TERMS) == 56


def _check_source(events):
    if type(events) not in (tuple, list) or len(events) != len(TERMS):
        raise ValueError("H04 exact source size required")
    result = []
    for i, row in enumerate(events):
        if type(row) is not tuple or len(row) != 2:
            raise ValueError("H04 malformed observation")
        x, y = row
        if type(x) is not int or x != TERMS[i] or type(y) is not int or y not in (0, 1):
            raise ValueError("H04 unexpected action or outcome")
        result.append(y)
    return tuple(result)


def program_weights(public_events):
    """Möbius reconstruction on 0/1/2-bit intervention basis, no gradient."""
    y = _check_source(public_events)
    c0 = y[0]
    coefficients = [c0]
    single = []
    for i in range(BITS):
        single.append(y[1 + i] ^ c0)
        coefficients.append(single[-1])
    index = 1 + BITS
    for i in range(BITS):
        for j in range(i + 1, BITS):
            coefficients.append(y[index] ^ single[i] ^ single[j] ^ c0)
            index += 1
    assert len(coefficients) == 56 and index == 56
    weights = sum(int(c) << i for i, c in enumerate(coefficients))
    if any(predict_weights(weights, x) != b for x, b in public_events):
        raise ValueError("H04 fitted law disagrees with public consequences")
    return weights


def predict_weights(weights, action):
    if type(weights) is not int or not 0 <= weights < (1 << 56):
        raise ValueError("H04 invalid packed weights")
    if type(action) is not int or not 0 <= action < (1 << BITS):
        raise ValueError("H04 invalid predicted action")
    answer = weights & 1
    idx = 1
    for i in range(BITS):
        answer ^= ((weights >> idx) & 1) & ((action >> i) & 1)
        idx += 1
    for i in range(BITS):
        for j in range(i + 1, BITS):
            answer ^= ((weights >> idx) & 1) & ((action >> i) & 1) & ((action >> j) & 1)
            idx += 1
    return answer


class DirectWeightBank:
    """Independent development-memory slots; not accepted native weights."""

    def __init__(self, slots=SLOT_COUNT):
        if type(slots) is not int or not 1 <= slots <= SLOT_COUNT:
            raise ValueError("H04 invalid slot count")
        self.slots = slots
        self._bytes = bytearray(slots * WEIGHT_BYTES)
        self._known = bytearray(slots)

    def write(self, slot, public_events):
        if type(slot) is not int or not 0 <= slot < self.slots:
            raise ValueError("H04 invalid slot index")
        if self._known[slot]:
            raise ValueError("H04 write-once slot already used")
        packed = program_weights(public_events)
        lo = slot * WEIGHT_BYTES
        self._bytes[lo:lo + WEIGHT_BYTES] = packed.to_bytes(WEIGHT_BYTES, "little")
        self._known[slot] = 1

    def predict(self, slot, action):
        if type(slot) is not int or not 0 <= slot < self.slots:
            raise ValueError("H04 invalid slot index")
        if not self._known[slot]:
            return None
        lo = slot * WEIGHT_BYTES
        w = int.from_bytes(self._bytes[lo:lo + WEIGHT_BYTES], "little")
        return predict_weights(w, action)

    def cold_image(self):
        content = (struct.pack(">4sHH", b"W104", self.slots, WEIGHT_BYTES)
                   + bytes(self._bytes) + bytes(self._known))
        return content + hashlib.sha256(content).digest()

    @classmethod
    def restore(cls, image):
        if type(image) is not bytes or len(image) < 40:
            raise ValueError("H04 corrupt checkpoint")
        header = image[:8]
        try:
            magic, count, width = struct.unpack(">4sHH", header)
        except struct.error as exc:
            raise ValueError("H04 corrupt header") from exc
        if magic != b"W104" or not 1 <= count <= SLOT_COUNT or width != WEIGHT_BYTES:
            raise ValueError("H04 wrong checkpoint format")
        expected = 8 + count * (WEIGHT_BYTES + 1) + 32
        if len(image) != expected or hashlib.sha256(image[:-32]).digest() != image[-32:]:
            raise ValueError("H04 checkpoint digest/length mismatch")
        instance = cls(count)
        pos = 8
        instance._bytes[:] = image[pos:pos + count * WEIGHT_BYTES]
        pos += count * WEIGHT_BYTES
        instance._known[:] = image[pos:pos + count]
        if any(v not in (0, 1) for v in instance._known):
            raise ValueError("H04 invalid checkpoint validity flags")
        return instance

    @property
    def numeric_bytes(self):
        return len(self._bytes)

    @property
    def checkpoint_bytes(self):
        return len(self.cold_image())
