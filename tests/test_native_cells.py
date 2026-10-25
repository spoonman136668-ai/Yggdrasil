"""Real focused tests for public native-cell learning, retention and controls.

These are DEV checks of a simple fixed-budget comparator, not a scientific
first-use experiment. There are no hidden labels, paid APIs or source claims.
"""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells


class NativeCausalCellsTests(unittest.TestCase):
    def test_untrained_or_single_arm_abstains(self):
        cells = PublicCausalCells()
        self.assertIsNone(cells.choose(0))
        cells.observe(0, 1, 1)
        self.assertIsNone(cells.choose(0))
        self.assertIsNone(cells.choose(0, retained=True))

    def test_learns_from_public_interventions_and_changes_decision(self):
        cells = PublicCausalCells()
        for _ in range(4):
            cells.observe(0, 0, 1)
            cells.observe(0, 1, 0)
        self.assertEqual(cells.choose(0), 0)
        for _ in range(9):
            cells.observe(0, 0, 0)
            cells.observe(0, 1, 1)
        self.assertEqual(cells.choose(0), 1)
        self.assertIsNone(cells.choose(1))

    def test_retained_and_active_addresses_remain_independent(self):
        cells = PublicCausalCells()
        for _ in range(10):
            cells.observe(0, 0, 1)
            cells.observe(0, 1, 0)
            cells.observe(0, 0, 0, retained=True)
            cells.observe(0, 1, 1, retained=True)
        self.assertEqual(cells.choose(0), 0)
        self.assertEqual(cells.choose(0, retained=True), 1)
        self.assertIsNone(cells.choose(8, retained=True))
        self.assertIsNone(cells.choose(6))

    def test_checkpoint_survives_restart_and_equal_subsequent_experience(self):
        original = PublicCausalCells()
        for index in range(7):
            for _ in range(3):
                original.observe(index, 0, 1)
                original.observe(index, 1, 0)
        for index in range(9):
            original.observe(index, 0, 0, retained=True)
            original.observe(index, 1, 1, retained=True)
        snapshot = original.snapshot()
        self.assertEqual(len(snapshot), 164)
        resumed = PublicCausalCells.restore(snapshot)
        self.assertEqual(resumed.snapshot(), snapshot)
        for index in range(7):
            for cells in (original, resumed):
                cells.observe(index, 0, 0)
                cells.observe(index, 1, 1)
        self.assertEqual(original.snapshot(), resumed.snapshot())

    def test_invalid_observations_do_not_change_memory(self):
        cells = PublicCausalCells()
        prior = cells.snapshot()
        bad = [
            (-1, 0, 0, False), (7, 0, 0, False),
            (9, 0, 0, True), (0, 2, 0, False),
            (0, 0, -1, False), (True, 0, 0, False),
            (0, True, 0, False), (0, 0, True, False),
            (0, 0, 1, 1),
        ]
        for address, action, outcome, retained in bad:
            with self.subTest(case=(address, action, outcome, retained)):
                with self.assertRaises(ValueError):
                    cells.observe(address, action, outcome, retained=retained)
                self.assertEqual(cells.snapshot(), prior)
        with self.assertRaises(ValueError):
            cells.choose(9, retained=True)

    def test_checkpoint_tamper_truncation_and_type_rejected(self):
        cells = PublicCausalCells()
        cells.observe(1, 0, 1)
        original = cells.snapshot()
        wrong = bytearray(original)
        wrong[10] ^= 1
        for data in (
            bytes(wrong),
            original[:-1],
            b"ABCD" + original[4:],
            bytearray(original),
        ):
            with self.subTest(candidate_type=type(data), size=len(data)):
                with self.assertRaises(ValueError):
                    PublicCausalCells.restore(data)
        self.assertEqual(cells.snapshot(), original)

    def test_saturating_counter_never_grows_or_wraps(self):
        cells = PublicCausalCells()
        cells._counts[0][0][1] = 65535
        prior = len(cells.snapshot())
        for _ in range(30):
            cells.observe(0, 0, 1)
        self.assertEqual(cells._counts[0][0][1], 65535)
        self.assertEqual(len(cells.snapshot()), prior)
        self.assertEqual(cells.LEARNED_BYTES, 128)
        self.assertEqual(cells.ACTIVE_SLOTS, 7)
        self.assertEqual(cells.RETAINED_SLOTS, 9)

    def test_equal_evidence_has_no_unjustified_preference(self):
        cells = PublicCausalCells()
        for _ in range(5):
            cells.observe(2, 0, 0)
            cells.observe(2, 1, 0)
        self.assertIsNone(cells.choose(2))


if __name__ == "__main__":
    unittest.main()
