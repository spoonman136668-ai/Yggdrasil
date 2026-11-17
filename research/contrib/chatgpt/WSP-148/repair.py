"""WSP148 source-blind coordinated numerical GF(2) coefficient editing.

Each learner receives ONLY 32 charged typed (intervention, consequence) rows.
No law-family primitive, generator import, hidden question, or evaluator read.
A block is accepted only when it strictly reduces observed Hamming error.
"""
from hashlib import sha256
from time import perf_counter_ns, process_time_ns

MASKS = tuple(range(64))
MAX_WRITES = 24
SINGLES = tuple((m,) for m in MASKS)
PAIRS = tuple((a, b) for a in MASKS for b in range(a + 1, 64))
DEGREES = tuple(m.bit_count() for m in MASKS)


def _validate(rows):
    if (type(rows) not in (tuple, list) or len(rows) != 32
        or len({x for x, y in rows}) != 32
        or any(type(x) is not int or not 0 <= x < 64
               or type(y) is not int or y not in (0, 1) for x, y in rows)):
        raise ValueError("WSP148_EXACT_32_TYPED_EFFECTS_REQUIRED")
    return tuple(rows)


def _signature(mask, xs):
    return sum(int((x & mask) == mask) << i for i, x in enumerate(xs))


def program(rows, *, block_width=2):
    """Fit up to 24 coefficient-bit writes; block_width=1 is capacity control."""
    rows = _validate(rows)
    if type(block_width) is not int or block_width not in (1, 2):
        raise ValueError("WSP148_BAD_BLOCK_WIDTH")
    cpu0 = process_time_ns()
    wall0 = perf_counter_ns()
    xs = tuple(x for x, y in rows)
    residual = sum(y << i for i, (x, y) in enumerate(rows))
    signs = tuple(_signature(m, xs) for m in MASKS)
    weights = 0
    writes = 0
    trace = []
    candidates = SINGLES + PAIRS if block_width == 2 else SINGLES
    while residual and writes < MAX_WRITES:
        best = None
        best_key = None
        current = residual.bit_count()
        for block in candidates:
            if writes + len(block) > MAX_WRITES:
                continue
            effect = signs[block[0]]
            if len(block) == 2:
                effect ^= signs[block[1]]
            after = residual ^ effect
            gain = current - after.bit_count()
            if gain <= 0:
                continue
            toggle_bits = sum(1 << mask for mask in block)
            resulting_active = (weights ^ toggle_bits).bit_count()
            key = (-gain, len(block), resulting_active,
                   sum(DEGREES[m] for m in block), block)
            if best_key is None or key < best_key:
                best_key = key
                best = (block, after, toggle_bits, gain)
        if best is None:
            break
        block, after, toggle_bits, gain = best
        if after.bit_count() >= residual.bit_count():
            raise AssertionError("WSP148_NON_IMPROVING_WEIGHT_EDIT")
        trace.append((block, gain, residual.bit_count(), after.bit_count()))
        residual = after
        weights ^= toggle_bits
        writes += len(block)
    return {
        "weights": weights,
        "edits": tuple(trace),
        "individual_writes": writes,
        "residual_errors": residual.bit_count(),
        "has_exact_fit": residual == 0,
        "block_width": block_width,
        "source_rows_sha256": sha256(repr(rows).encode()).hexdigest(),
        "cpu_s": round((process_time_ns() - cpu0) / 1e9, 6),
        "wall_s": round((perf_counter_ns() - wall0) / 1e9, 6),
    }


def predict(model, x):
    if type(x) is not int or not 0 <= x < 64:
        raise ValueError("WSP148_BAD_INPUT")
    if not model["has_exact_fit"]:
        return None
    weights = model["weights"]
    return sum((weights >> m) & 1 for m in MASKS if (x & m) == m) & 1


def predictions(model):
    return tuple(predict(model, x) for x in range(64))


def restore(saved, rows):
    if type(saved) is not dict or saved.get("block_width") not in (1, 2):
        raise ValueError("WSP148_BAD_SAVED_WEIGHTS")
    reconstructed = program(rows, block_width=saved["block_width"])
    for key in ("weights", "edits", "individual_writes", "residual_errors",
                "has_exact_fit", "block_width", "source_rows_sha256"):
        if reconstructed[key] != saved.get(key):
            raise ValueError("WSP148_COLD_WEIGHT_RESTORE_MISMATCH")
    return reconstructed
