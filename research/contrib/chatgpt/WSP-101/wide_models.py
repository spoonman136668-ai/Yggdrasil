"""Independent public-grammar direct numerical writer and symbolic control.

These models see ONLY eight source pairs per relation. A small, published
four-operator grammar is a strong simplifying assumption, not open-ended AGI.
"""
from array import array
import struct

UNSET = (1 << 32) - 1

def _rot(x, r, bits):
    mask = (1 << bits) - 1
    return ((x << r) | (x >> (bits - r))) & mask

def _compute(family, a, k, x, bits):
    mask = (1 << bits) - 1
    if family == 0: return (x + k) & mask
    if family == 1: return x ^ k
    if family == 2: return _rot(x, a, bits) ^ k
    if family == 3: return (a * x + k) & mask
    raise ValueError("invalid family")

def write_weights_from_source(pairs, bits):
    """Analytic source-fit into three numeric slots; NO gradient updates."""
    if len(pairs) != 8 or pairs[0][0] != 0 or pairs[1][0] != 1:
        raise ValueError("wrong source protocol")
    mask = (1 << bits) - 1
    y0, y1 = pairs[0][1], pairs[1][1]
    candidates = [(0, 0, y0), (1, 0, y0)]
    candidates += [(2, rotation, y0) for rotation in range(1, bits)]
    a = (y1 - y0) & mask
    if a & 1:
        candidates.append((3, a, y0))
    good = sorted(set(c for c in candidates if all(
        _compute(*c, x, bits) == y for x,y in pairs)))
    if not good:
        raise ValueError("no source-consistent numerical rule")
    first = good[0]
    # If multiple hypotheses disagree anywhere, don't pretend the source
    # identifies the unknown rule. This is a source-only exhaustive check.
    for alternative in good[1:]:
        for x in range(1 << bits):
            if _compute(*first, x, bits) != _compute(*alternative, x, bits):
                raise ValueError("ambiguous underdetermined source")
    return first

class DirectWeightMemory:
    def __init__(self, n, bits):
        self.bits = bits
        self.slots = array("I", [0]) * (3 * n)
        self.known = bytearray(n)
    def write(self, idx, pairs):
        if not 0 <= idx < len(self.known) or self.known[idx]:
            raise ValueError("numeric slot not available")
        code, factor, key = write_weights_from_source(pairs, self.bits)
        self.slots[3*idx:3*idx+3] = array("I", (code, factor, key))
        self.known[idx] = 1
    def predict(self, idx, x):
        if not self.known[idx]:
            return None
        offset = idx * 3
        return _compute(*self.slots[offset:offset+3], x, self.bits)
    def cold_image(self):
        return (self.slots.tobytes(), bytes(self.known))
    @classmethod
    def restore(cls, n, bits, image):
        obj = cls(n,bits)
        data, flags = image
        if len(data) != n * 3 * 4 or len(flags) != n:
            raise ValueError("cold image capacity mismatch")
        obj.slots = array("I")
        obj.slots.frombytes(data)
        obj.known = bytearray(flags)
        if any(x not in (0,1) for x in obj.known):
            raise ValueError("cold image invalid flags")
        return obj
    @property
    def bytes(self):
        a,b = self.cold_image()
        return len(a) + len(b)

def _symbolic_apply(program, x, bits):
    t, m, offset = program
    if t == "plus": return (x + offset) % (1 << bits)
    if t == "xor": return x ^ offset
    if t == "rot-xor": return _rot(x, m, bits) ^ offset
    if t == "affine": return (x * m + offset) % (1 << bits)
    raise ValueError("invalid symbolic family")

def infer_symbolic(pairs, bits):
    """Independent symbolic version-space control; no direct writer import."""
    if len(pairs) != 8 or pairs[0][0] != 0 or pairs[1][0] != 1:
        raise ValueError("unexpected symbolic evidence")
    base = pairs[0][1]
    proposal = [("plus",0,base), ("xor",0,base)]
    proposal.extend(("rot-xor",j,base) for j in range(1,bits))
    coefficient = (pairs[1][1] - base) % (1 << bits)
    if coefficient % 2:
        proposal.append(("affine",coefficient,base))
    accepted = [p for p in proposal if all(
        _symbolic_apply(p,x,bits) == y for x,y in pairs)]
    if not accepted:
        raise ValueError("no symbolic explanation")
    for other in accepted[1:]:
        if any(_symbolic_apply(accepted[0],x,bits) !=
               _symbolic_apply(other,x,bits) for x in range(1<<bits)):
            raise ValueError("symbolic source nonidentifiable")
    return accepted[0]

def predict_symbolic(model, x, bits):
    return _symbolic_apply(model, x, bits)

def baseline_lookup(pairs):
    return dict(pairs)
