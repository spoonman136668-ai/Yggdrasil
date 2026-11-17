"""CKAD10 opt-in native pair escape; source-free, never admitted as truth."""
import json
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical, digest, feature_row, pin, require
from yggdrasil.native_prior_hypothesis import (
    NativePriorHypothesis, MAX_EDITS, input_order, program_weights
)

SCHEMA = "yggdrasil.ckad.native-pair-hypothesis.v1"
RULE = "CKAD10_STRICT_PAIR_ESCAPE16"


def program_pair_weights(rows, binary_inputs):
    """Take improving singles; at a stall take the best improving two-edit escape."""
    require(type(binary_inputs) is int and 2 <= binary_inputs <= 11,
            "PAIR_INPUT_BITS")
    require(type(rows) in (list, tuple) and 0 < len(rows) <= 2048
            and all(type(r) in (list, tuple) and len(r) == 2
                    and type(r[0]) is int and 0 <= r[0] < (1 << binary_inputs)
                    and type(r[1]) is int and r[1] in (0, 1) for r in rows)
            and len({r[0] for r in rows}) == len(rows), "PAIR_ROWS")
    xs = tuple(x for x, _ in rows)
    residual = sum(y << i for i, (_, y) in enumerate(rows))
    columns = tuple(sum(int((x & m) == m) << i for i, x in enumerate(xs))
                    for m in range(1 << binary_inputs))
    # A zero column cannot improve a stalled single or paired flip. For
    # identical nonzero columns, only the lowest (popcount, index) member
    # can win a paired tie; the two members of one class cancel entirely.
    # Source and labels are unchanged. This is a lossless search reduction.
    equivalence_classes = {}
    for m, col in enumerate(columns):
        if col:
            prev = equivalence_classes.get(col)
            if prev is None or (m.bit_count(), m) < (prev.bit_count(), prev):
                equivalence_classes[col] = m
    representatives = sorted(equivalence_classes.values())
    weights, writes = 0, []
    while residual and len(writes) < MAX_EDITS:
        best, key_best = None, None
        for m, col in enumerate(columns):
            gain = 2 * (residual & col).bit_count() - col.bit_count()
            if gain <= 0:
                continue
            key = (-gain, m.bit_count(), m)
            if key_best is None or key < key_best:
                best, key_best = (m,), key
        if best is None and len(writes) + 2 <= MAX_EDITS:
            old_errors = residual.bit_count()
            for idx, m in enumerate(representatives):
                once = residual ^ columns[m]
                for n in representatives[idx + 1:]:
                    gain = old_errors - (once ^ columns[n]).bit_count()
                    if gain <= 0:
                        continue
                    key = (-gain, m.bit_count() + n.bit_count(), m, n)
                    if key_best is None or key < key_best:
                        best, key_best = (m, n), key
        if best is None:
            break
        for m in best:
            residual ^= columns[m]
            weights ^= 1 << m
            writes.append(m)
    return weights, tuple(writes), residual.bit_count()


class NativePairHypothesis(NativePriorHypothesis):
    """Original native witnessed checkpoints in; separate provisional memory out."""
    __slots__ = ()

    @classmethod
    def fit_checkpoint(cls, raw, expected_sha256):
        source = NativeContextAccumulator.restore(raw, expected_sha256)
        profile = source._model._profiles[0]
        bits = source._model.context_bits
        require(profile.degree == bits + 1
                and all(p.source_records == 0 for p in source._model._profiles[1:]),
                "PAIR_ISOLATED_COMPLETE_BASIS_REQUIRED")
        n = profile.unique_inputs
        require(8 <= n <= 2048 and n % 4 == 0 and profile.source_records == n,
                "PAIR_VIEW_COUNT")
        masks = sorted(
            (x for x in range(1 << (bits + 1)) if source._seen[0] & (1 << x)),
            key=input_order,
        )
        rows = [(x, source.predict(0, x & ((1 << bits) - 1), x >> bits))
                for x in masks]
        require(all(type(y) is int and y in (0, 1) for _, y in rows),
                "PAIR_WITNESSED_ONLY")
        k = 3 * n // 4
        weights, writes, errors = program_pair_weights(rows[:k], bits + 1)
        calibration = sum(((weights & feature_row(x, bits + 1)).bit_count() & 1) != y
                          for x, y in rows[k:])
        model = cls()
        model._bits, model._weights, model._writes = bits, weights, writes
        model._source, model._n = expected_sha256, n
        model._fit_errors, model._calibration_errors = errors, calibration
        return model

    def checkpoint(self):
        obj = json.loads(super().checkpoint().decode("ascii"))
        obj["schema"], obj["rule"] = SCHEMA, RULE
        return canonical(obj)

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= 32768
                and pin(expected_sha256) and digest(raw) == expected_sha256,
                "PAIR_CHECKPOINT_PIN")
        def unique(pairs):
            d = {}
            for k, v in pairs:
                require(k not in d, "PAIR_DUPLICATE_KEY")
                d[k] = v
            return d
        try:
            obj = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(obj) is dict and obj.get("schema") == SCHEMA
                    and obj.get("rule") == RULE and canonical(obj) == raw,
                    "PAIR_CHECKPOINT_CONTRACT")
            obj["schema"] = "yggdrasil.ckad.native-prior-hypothesis.v1"
            obj["rule"] = "WSP147_STRICT_GAIN16_GENERIC_MONOMIALS"
            old_raw = canonical(obj)
            verified = NativePriorHypothesis.restore(old_raw, digest(old_raw))
            model = cls()
            for k in ("_bits", "_weights", "_writes", "_source", "_n",
                      "_fit_errors", "_calibration_errors"):
                setattr(model, k, getattr(verified, k))
            require(model.checkpoint() == raw, "PAIR_COLD_BYTES")
            return model
        except (TypeError, ValueError, KeyError, UnicodeError, AttributeError) as exc:
            raise ValueError("CKAD_NATIVE_PAIR_CHECKPOINT_REJECTED") from exc
