"""Development-only opt-in Wilson confidence abstention controls.

No sealed outcomes, no model calls, no scientific first-use claims.
The default chooser and original checkpoint compatibility are frozen.
"""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells


class WilsonConfidenceTests(unittest.TestCase):
    def test_untrained_and_single_arm_both_abstain(self):
        c = PublicCausalCells()
        self.assertIsNone(c.choose_wilson(0))
        c.observe(0, 0, 1)
        self.assertIsNone(c.choose_wilson(0))
        self.assertIsNone(c.choose_wilson(0, retained=True))

    def test_sparse_noisy_evidence_abstains_but_empirical_chooses(self):
        c = PublicCausalCells()
        c.observe(0, 0, 1)
        c.observe(0, 1, 0)
        self.assertEqual(c.choose(0), 0)
        self.assertIsNone(c.choose_wilson(0))

    def test_clear_public_evidence_selects_arm_zero(self):
        c = PublicCausalCells()
        for _ in range(24):
            c.observe(0, 0, 1)
            c.observe(0, 1, 0)
        self.assertEqual(c.choose_wilson(0), 0)

    def test_reverse_public_evidence_selects_arm_one(self):
        c = PublicCausalCells()
        for _ in range(24):
            c.observe(1, 0, 0)
            c.observe(1, 1, 1)
        self.assertEqual(c.choose_wilson(1), 1)

    def test_equal_public_outcomes_abstain(self):
        c = PublicCausalCells()
        for _ in range(16):
            c.observe(2, 0, 1)
            c.observe(2, 1, 1)
        self.assertIsNone(c.choose_wilson(2))

    def test_retained_and_active_slots_are_independent(self):
        c = PublicCausalCells()
        for _ in range(32):
            c.observe(0, 0, 1)
            c.observe(0, 1, 0)
            c.observe(0, 0, 0, retained=True)
            c.observe(0, 1, 1, retained=True)
        self.assertEqual(c.choose_wilson(0), 0)
        self.assertEqual(c.choose_wilson(0, retained=True), 1)
        self.assertIsNone(c.choose_wilson(1))
        self.assertIsNone(c.choose_wilson(1, retained=True))

    def test_readout_is_side_effect_free_and_checkpoint_byte_exact(self):
        c = PublicCausalCells()
        for _ in range(26):
            c.observe(3, 0, 1)
            c.observe(3, 1, 0)
        before = c.snapshot()
        self.assertEqual(len(before), 164)
        self.assertEqual(c.LEARNED_BYTES, 128)
        self.assertEqual(c.choose_wilson(3), 0)
        self.assertEqual(c.snapshot(), before)
        resumed = PublicCausalCells.restore(before)
        self.assertEqual(resumed.choose_wilson(3), 0)
        self.assertEqual(resumed.snapshot(), before)
        self.assertEqual(c.choose(3), 0)

    def test_invalid_address_never_mutates_original_memory(self):
        c = PublicCausalCells()
        before = c.snapshot()
        for address, retained in [(-1, False), (7, False),
                                  (9, True), (True, False),
                                  (0, 0)]:
            with self.subTest(address=address, retained=retained):
                with self.assertRaises(ValueError):
                    c.choose_wilson(address, retained=retained)
                self.assertEqual(c.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
