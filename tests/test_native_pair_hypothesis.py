"""No protected source imports or held outcomes; fabricated rows only."""
import json
import unittest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_prior_hypothesis import program_weights, input_order
from yggdrasil.native_pair_hypothesis import NativePairHypothesis, program_pair_weights


def native_view(labels):
    rows = [[x & 3, x >> 2, int(y)] for x, y in enumerate(labels)]
    return NativeContextAccumulator(2).stage_update(
        0, rows, digest(canonical(rows)), max_degree=3
    )


class PairNativeTests(unittest.TestCase):
    def test_exposed_fabricated_local_optimum(self):
        masks = (11, 1, 15, 9)
        rows = [(x, sum((x & m) == m for m in masks) & 1) for x in range(16)]
        self.assertEqual(program_weights(rows, 4)[2], 1)
        fixed = program_pair_weights(rows, 4)
        self.assertEqual(fixed[2], 0)
        self.assertLessEqual(len(fixed[1]), 16)
        self.assertEqual(fixed, program_pair_weights(rows, 4))

    def test_same_singles_no_pair_side_effect(self):
        rows = [(x, x & 1) for x in range(16)]
        self.assertEqual(program_pair_weights(rows, 4), program_weights(rows, 4))

    def test_native_source_cold_persistent_provisional(self):
        src = native_view([x & 1 for x in range(8)])
        before = src.checkpoint()
        candidate = NativePairHypothesis.fit_checkpoint(before, digest(before))
        self.assertTrue(candidate.eligible)
        self.assertEqual([candidate.predict_provisional(x & 3, x >> 2)
                          for x in range(8)], [x & 1 for x in range(8)])
        stored = candidate.checkpoint()
        loaded = NativePairHypothesis.restore(stored, digest(stored))
        self.assertEqual(loaded.checkpoint(), stored)
        self.assertEqual(src.checkpoint(), before)

    def test_source_pin_and_other_address_rejected(self):
        src = native_view([1] * 8)
        raw = src.checkpoint()
        with self.assertRaises(ValueError):
            NativePairHypothesis.fit_checkpoint(raw, "0" * 64)
        rows = [[x & 3, x >> 2, 1] for x in range(8)]
        mixed = src.stage_update(1, rows, digest(canonical(rows)), max_degree=3)
        raw = mixed.checkpoint()
        with self.assertRaisesRegex(ValueError, "ISOLATED"):
            NativePairHypothesis.fit_checkpoint(raw, digest(raw))

    def test_calibration_failure_abstains(self):
        order = sorted(range(8), key=input_order)
        labels = [0] * 8
        labels[order[-1]] = 1
        src = native_view(labels)
        raw = src.checkpoint()
        candidate = NativePairHypothesis.fit_checkpoint(raw, digest(raw))
        self.assertFalse(candidate.eligible)
        self.assertGreater(candidate.info()["calibration_errors"], 0)
        self.assertTrue(all(candidate.predict_provisional(x & 3, x >> 2) is None
                            for x in range(8)))

    def test_checkpoint_tampering_rejected(self):
        src = native_view([1] * 8)
        raw = src.checkpoint()
        candidate = NativePairHypothesis.fit_checkpoint(raw, digest(raw))
        checkpoint = candidate.checkpoint()
        for k, value in (("scientific_pass", True), ("accepted_native", True),
                         ("rule", "unapproved"), ("source_mode", "original"),
                         ("writes", []), ("fit_errors", 999)):
            obj = json.loads(checkpoint)
            obj[k] = value
            forged = canonical(obj)
            with self.subTest(field=k), self.assertRaises(ValueError):
                NativePairHypothesis.restore(forged, digest(forged))


    def test_exhaustive_pair_equivalence_to_full_frozen_search(self):
        # Independent complete pair enumeration: no equivalence compression.
        # All three-bit truth tables, plus four- and five-bit fabricated cases.
        def original_reference(rows, binary_inputs):
            xs = [x for x, _ in rows]
            columns = [
                sum(int((x & m) == m) << i for i, x in enumerate(xs))
                for m in range(1 << binary_inputs)
            ]
            residual = sum(y << i for i, (_, y) in enumerate(rows))
            weights, writes = 0, []
            while residual and len(writes) < 16:
                singles = [
                    (-gain, m.bit_count(), m)
                    for m, col in enumerate(columns)
                    for gain in [2 * (residual & col).bit_count() - col.bit_count()]
                    if gain > 0
                ]
                if singles:
                    m = min(singles)[-1]
                    chosen = (m,)
                elif len(writes) + 2 <= 16:
                    old_error = residual.bit_count()
                    pairs = [
                        (-gain, m.bit_count() + n.bit_count(), m, n)
                        for m in range(len(columns))
                        for n in range(m + 1, len(columns))
                        for gain in [old_error - (residual ^ columns[m] ^ columns[n]).bit_count()]
                        if gain > 0
                    ]
                    chosen = min(pairs)[-2:] if pairs else ()
                else:
                    chosen = ()
                if not chosen:
                    break
                for m in chosen:
                    residual ^= columns[m]
                    weights ^= 1 << m
                    writes.append(m)
            return weights, tuple(writes), residual.bit_count()

        for bits in (2, 3):
            for labels_mask in range(1 << (1 << bits)):
                rows = [(x, (labels_mask >> x) & 1) for x in range(1 << bits)]
                with self.subTest(bits=bits, labels=labels_mask):
                    self.assertEqual(program_pair_weights(rows, bits),
                                     original_reference(rows, bits))
        for bits in (4, 5, 6):
            for seed in range(24):
                samples = [x for x in range(1 << bits) if (x * 17 + seed) % 7 != 0]
                rows = [(x, ((x * (seed + 3) + (x >> 1)) ^ (seed * x >> 2)) & 1)
                        for x in samples]
                with self.subTest(bits=bits, seed=seed):
                    self.assertEqual(program_pair_weights(rows, bits),
                                     original_reference(rows, bits))

    def test_full_width_diagnostic_exact_reference(self):
        # No protected source input: deterministic invented masks and labels.
        import hashlib
        from time import perf_counter
        bits = 11
        xs = sorted(range(1 << bits), key=lambda x:
                    hashlib.sha256(str(x).encode("ascii")).digest())[:384]
        rows = [(x, int((x & 11) == 11) ^ int((x & 960) == 960)
                 ^ int((x & 17) == 17)) for x in xs]
        # Two independent code paths must return exactly the same weights,
        # edit trace, and residual errors at the full declared input width.
        def dense_reference(rows, bits):
            residual = sum(y << i for i, (_, y) in enumerate(rows))
            cols = tuple(sum(int((x & m) == m) << i
                             for i, (x, _) in enumerate(rows))
                         for m in range(1 << bits))
            weights, writes = 0, []
            while residual and len(writes) < 16:
                singles = []
                for m, col in enumerate(cols):
                    gain = 2 * (residual & col).bit_count() - col.bit_count()
                    if gain > 0:
                        singles.append((-gain, m.bit_count(), m))
                if singles:
                    chosen = (min(singles)[-1],)
                elif len(writes) + 1 < 16:
                    old = residual.bit_count()
                    best = None
                    for m, col in enumerate(cols):
                        once = residual ^ col
                        for n in range(m + 1, len(cols)):
                            gain = old - (once ^ cols[n]).bit_count()
                            if gain > 0:
                                key = (-gain, m.bit_count() + n.bit_count(), m, n)
                                if best is None or key < best:
                                    best = key
                    chosen = best[-2:] if best else ()
                else:
                    chosen = ()
                if not chosen:
                    break
                for m in chosen:
                    residual ^= cols[m]
                    weights ^= 1 << m
                    writes.append(m)
            return weights, tuple(writes), residual.bit_count()
        start = perf_counter()
        baseline = dense_reference(rows, bits)
        base_seconds = perf_counter() - start
        start = perf_counter()
        candidate = program_pair_weights(rows, bits)
        candidate_seconds = perf_counter() - start
        self.assertEqual(candidate, baseline)
        print("CKAD10_PAIR_EQUIVALENCE_REFERENCE_SECONDS="
              + format(base_seconds, ".6f")
              + " CANDIDATE_SECONDS=" + format(candidate_seconds, ".6f"),
              flush=True)

    def test_invalid_inputs(self):
        for rows, bits in (([(0, 0), (0, 1)], 4),
                           ([(True, 1)], 4), ([(0, 1)], 12)):
            with self.assertRaises(ValueError):
                program_pair_weights(rows, bits)


if __name__ == "__main__":
    unittest.main()
