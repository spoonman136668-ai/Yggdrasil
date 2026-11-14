"""H05 numerical weight repair from public causal contradiction signatures.

Reuses H04's already qualified quadratic weight fitting. No import of H05
worlds, generator labels, evaluator mode, hidden cubic indices, or donor weights.
"""
from __future__ import annotations
import hashlib
import struct
from itertools import combinations
from functools import lru_cache

from headroom_h04_writer import program_weights, predict_weights

BITS = 10
QUAD_BYTES = 7
CUBIC_BYTES = 15
WEIGHT_BYTES = QUAD_BYTES + CUBIC_BYTES
SLOTS = 32
TRIPLES = tuple(combinations(range(BITS), 3))
REPAIR_ACTIONS = (
    932,710,430,811,316,617,702,890,756,371,662,941,803,574,856,842,
    468,335,923,62,692,462,623,254,620,527,315,159,822,1013,902,909,
    899,683,929,433,223,817,1012,1004,501,997,758,837,597,248,419,362
)
assert len(TRIPLES) == 120 and len(REPAIR_ACTIONS) == 48

TRIPLE_MASKS = tuple(sum(1 << i for i in triple) for triple in TRIPLES)
FEATURE_VECTOR = tuple(sum(1 << i for i, mask in enumerate(TRIPLE_MASKS)
                           if action & mask == mask) for action in range(1024))


def _checked_repair(events):
    if type(events) not in (tuple, list) or len(events) != len(REPAIR_ACTIONS):
        raise ValueError("H05 exact repair source required")
    for i, row in enumerate(events):
        if type(row) is not tuple or len(row) != 2:
            raise ValueError("H05 invalid repair record")
        action, reward = row
        if (type(action) is not int or action != REPAIR_ACTIONS[i]
            or type(reward) is not int or reward not in (0, 1)):
            raise ValueError("H05 invalid action/consequence")
    return tuple(events)


@lru_cache(maxsize=1)
def _sparse_syndrome_decoder():
    signatures = []
    for mask in TRIPLE_MASKS:
        signature = sum(int(action & mask == mask) << k
                        for k, action in enumerate(REPAIR_ACTIONS))
        signatures.append(signature)
    decoder = {0: ()}
    for i, sig in enumerate(signatures):
        if sig in decoder:
            raise ValueError("H05 ambiguous single cubic codeword")
        decoder[sig] = (i,)
    for i, a in enumerate(signatures):
        for j in range(i + 1, len(signatures)):
            syndrome = a ^ signatures[j]
            if syndrome in decoder:
                raise ValueError("H05 ambiguous sparse cubic repair source")
            decoder[syndrome] = (i, j)
    if len(decoder) != 7261:
        raise ValueError("H05 incomplete two-sparse causal signatures")
    return decoder


class DirectRepairBank:
    def __init__(self, slots=SLOTS):
        if type(slots) is not int or not 1 <= slots <= SLOTS:
            raise ValueError("H05 invalid memory capacity")
        self.slots = slots
        self._weights = bytearray(slots * WEIGHT_BYTES)
        self._flags = bytearray(slots)  # 0=unlearned,1=quadratic,2=repaired

    def _offset(self, slot):
        if type(slot) is not int or not 0 <= slot < self.slots:
            raise ValueError("H05 invalid world slot")
        return slot * WEIGHT_BYTES

    def fit_quadratic(self, slot, observations):
        off = self._offset(slot)
        if self._flags[slot] != 0:
            raise ValueError("H05 numeric weights already programmed")
        base = program_weights(observations)
        self._weights[off:off + QUAD_BYTES] = base.to_bytes(QUAD_BYTES, "little")
        self._flags[slot] = 1

    def repair_cubic(self, slot, observations):
        off = self._offset(slot)
        if self._flags[slot] != 1:
            raise ValueError("H05 repair requires unmodified fitted quadratic base")
        source = _checked_repair(observations)
        base_bytes = bytes(self._weights[off:off + QUAD_BYTES])
        quad = int.from_bytes(base_bytes, "little")
        signature = sum((consequence ^ predict_weights(quad, action)) << i
                        for i, (action, consequence) in enumerate(source))
        code = _sparse_syndrome_decoder().get(signature)
        if code is None:
            raise ValueError("H05 unseen/not-identifiable cubic law; fail closed")
        cubic = sum(1 << i for i in code)
        self._weights[off + QUAD_BYTES:off + WEIGHT_BYTES] = cubic.to_bytes(CUBIC_BYTES, "little")
        if bytes(self._weights[off:off + QUAD_BYTES]) != base_bytes:
            raise AssertionError("H05 changed previously learned quadratic coefficients")
        self._flags[slot] = 2
        if any(self.predict(slot, a) != y for a, y in source):
            raise ValueError("H05 repair did not explain observed causal outcomes")
        return len(code)

    def base_bytes(self, slot):
        off = self._offset(slot)
        return bytes(self._weights[off:off + QUAD_BYTES])

    def predict(self, slot, action):
        off = self._offset(slot)
        if not self._flags[slot]:
            return None
        if type(action) is not int or not 0 <= action < 1024:
            raise ValueError("H05 invalid prediction input")
        quad = int.from_bytes(self._weights[off:off + QUAD_BYTES], "little")
        prediction = predict_weights(quad, action)
        if self._flags[slot] == 2:
            cubic = int.from_bytes(self._weights[off + QUAD_BYTES:off + WEIGHT_BYTES], "little")
            prediction ^= (cubic & FEATURE_VECTOR[action]).bit_count() & 1
        return prediction

    def cold_image(self):
        data = (struct.pack(">4sHH", b"W105", self.slots, WEIGHT_BYTES)
                + bytes(self._weights) + bytes(self._flags))
        return data + hashlib.sha256(data).digest()

    @classmethod
    def restore(cls, data):
        if type(data) is not bytes or len(data) < 40:
            raise ValueError("H05 corrupt image")
        magic, slots, width = struct.unpack(">4sHH", data[:8])
        if magic != b"W105" or not 1 <= slots <= SLOTS or width != WEIGHT_BYTES:
            raise ValueError("H05 wrong checkpoint format")
        expected = 8 + slots * (WEIGHT_BYTES + 1) + 32
        if len(data) != expected or hashlib.sha256(data[:-32]).digest() != data[-32:]:
            raise ValueError("H05 checkpoint content tampering")
        bank = cls(slots)
        end = 8 + slots * WEIGHT_BYTES
        bank._weights[:] = data[8:end]
        bank._flags[:] = data[end:end + slots]
        if any(f not in (0, 1, 2) for f in bank._flags):
            raise ValueError("H05 malformed native memory flags")
        return bank

    @property
    def numeric_bytes(self):
        return len(self._weights)

    @property
    def checkpoint_bytes(self):
        return len(self.cold_image())
