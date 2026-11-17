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

    def test_invalid_inputs(self):
        for rows, bits in (([(0, 0), (0, 1)], 4),
                           ([(True, 1)], 4), ([(0, 1)], 12)):
            with self.assertRaises(ValueError):
                program_pair_weights(rows, bits)


if __name__ == "__main__":
    unittest.main()
