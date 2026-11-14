"""Original-free WSP101 synthetic association truth and source generator.

Evaluation parameters are NEVER passed to numerical or symbolic learners.
This is not Wikidata, human commonsense, or any original scientific cohort.
"""
import hashlib

def rank(d, r, purpose, index):
    s = f"WSP101|WIDE|v1|{d}|{r}|{purpose}|{index}".encode("ascii")
    return int.from_bytes(hashlib.sha256(s).digest(), "big")

def rol(x, shift, bits):
    mask = (1 << bits) - 1
    return ((x << shift) | (x >> (bits-shift))) & mask

def _hidden(d, r, bits):
    mask = (1 << bits) - 1
    op = rank(d, r, "OP", 0) % 4
    key = rank(d, r, "KEY", 0) & mask
    factor = (rank(d, r, "FACTOR", 0) | 1) & mask
    shift = 1 + rank(d, r, "SHIFT", 0) % (bits-1)
    return op, factor, shift, key

def _target(d, r, bits, x):
    # Deliberately inaccessible to source-only models.
    op, factor, shift, key = _hidden(d, r, bits)
    mask = (1 << bits) - 1
    if op == 0:
        return (x + key) & mask
    if op == 1:
        return x ^ key
    if op == 2:
        return rol(x, shift, bits) ^ key
    return (factor * x + key) & mask

def inputs(d, r, bits, name, total, excluded=()):
    limit = 1 << bits
    seen = set(excluded)
    results = []
    for index in range(total * 32 + 256):
        x = rank(d, r, name, index) % limit
        if x not in seen:
            seen.add(x)
            results.append(x)
            if len(results) == total:
                return tuple(results)
    raise ValueError("not enough distinct inputs for frozen budget")

def source(d, r, bits):
    xs = (0, 1) + inputs(d, r, bits, "SOURCE", 6, excluded=(0, 1))
    return tuple((x, _target(d, r, bits, x)) for x in xs)

def heldout(d, r, bits, count=128):
    observed = tuple(x for x, _ in source(d, r, bits))
    return inputs(d, r, bits, "HELDOUT", count, excluded=observed)

def answer(d, r, bits, x):
    if type(x) is not int or not 0 <= x < 1 << bits:
        raise ValueError("invalid evaluator input")
    return _target(d, r, bits, x)
