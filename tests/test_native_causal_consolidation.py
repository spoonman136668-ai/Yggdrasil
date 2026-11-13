"""DG1-NCM02 source-only engineering tests, not AGI/scientific acceptance."""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells


def train(cells, address, preferred, retained=False, n=24):
    for _ in range(n):
        cells.observe(address, 0, int(preferred == 0), retained=retained)
        cells.observe(address, 1, int(preferred == 1), retained=retained)


class NativeCausalConsolidationTests(unittest.TestCase):
    def test_retained_skill_survives_recycled_active_contradiction(self):
        cells = PublicCausalCells()
        baseline = PublicCausalCells()
        train(cells, 0, 0)
        train(baseline, 0, 0)
        self.assertEqual(cells.choose(0), 0)
        cells.consolidate_and_recycle(0, 0)
        self.assertIsNone(cells.choose(0))
        self.assertEqual(cells.choose(0, retained=True), 0)
        train(cells, 0, 1)
        train(baseline, 0, 1)
        self.assertEqual(cells.choose(0), 1)
        self.assertEqual(cells.choose(0, retained=True), 0)
        self.assertIsNone(baseline.choose(0))  # interference without archive
        self.assertEqual(len(cells.snapshot()), 164)
        restored = PublicCausalCells.restore(cells.snapshot())
        self.assertEqual(restored.snapshot(), cells.snapshot())
        self.assertEqual(restored.choose(0, retained=True), 0)
        self.assertEqual(restored.choose(0), 1)

    def test_original_observation_and_chooser_unchanged_without_opt_in(self):
        cells = PublicCausalCells()
        train(cells, 3, 1, n=4)
        self.assertEqual(cells.choose(3), 1)
        self.assertEqual(cells.observed_action_contrast(3), (4*4, 4*4))
        self.assertEqual(len(cells.snapshot()), PublicCausalCells.CHECKPOINT_BYTES)
        self.assertIsNone(cells.choose(0, retained=True))

    def test_fail_closed_on_occupied_retained_destination(self):
        cells = PublicCausalCells()
        train(cells, 0, 0)
        cells.observe(0, 0, 1, retained=True)
        before = cells.snapshot()
        with self.assertRaisesRegex(ValueError, "DESTINATION_OCCUPIED"):
            cells.consolidate_and_recycle(0, 0)
        self.assertEqual(cells.snapshot(), before)

    def test_fail_closed_on_single_arm_or_empty_source(self):
        cells = PublicCausalCells()
        before = cells.snapshot()
        with self.assertRaisesRegex(ValueError, "INSUFFICIENT_EVIDENCE"):
            cells.consolidate_and_recycle(0, 0)
        self.assertEqual(cells.snapshot(), before)
        cells.observe(0, 0, 1)
        before = cells.snapshot()
        with self.assertRaisesRegex(ValueError, "INSUFFICIENT_EVIDENCE"):
            cells.consolidate_and_recycle(0, 0)
        self.assertEqual(cells.snapshot(), before)

    def test_invalid_addresses_are_atomic(self):
        cells = PublicCausalCells()
        train(cells, 0, 0)
        before = cells.snapshot()
        for source, target in [(-1, 0), (7, 0), (True, 0),
                               (0, -1), (0, 9), (0, True)]:
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    cells.consolidate_and_recycle(source, target)
                self.assertEqual(cells.snapshot(), before)

    def test_exact_existing_capacity_and_independent_retained_slots(self):
        cells = PublicCausalCells()
        for address in range(9):
            src = address % 7
            train(cells, src, address % 2)
            self.assertEqual(cells.choose(src), address % 2)
            cells.consolidate_and_recycle(src, address)
            self.assertEqual(cells.choose(address, retained=True), address % 2)
        for address in range(9):
            self.assertEqual(cells.choose(address, retained=True), address % 2)
        self.assertEqual(cells.LEARNED_BYTES, 128)
        self.assertEqual(cells.ACTIVE_SLOTS, 7)
        self.assertEqual(cells.RETAINED_SLOTS, 9)
        self.assertEqual(len(cells.snapshot()), 164)
        self.assertEqual(PublicCausalCells.restore(cells.snapshot()).snapshot(),
                         cells.snapshot())

    def test_unrelated_active_and_retained_cells_unchanged(self):
        cells = PublicCausalCells()
        train(cells, 0, 0)
        train(cells, 1, 1)
        train(cells, 1, 0, retained=True)
        untouched = (cells.choose(1), cells.choose(1, retained=True))
        cells.consolidate_and_recycle(0, 2)
        self.assertEqual((cells.choose(1), cells.choose(1, retained=True)),
                         untouched)
        self.assertEqual(cells.choose(2, retained=True), 0)

    def test_tampered_checkpoint_still_rejected(self):
        cells = PublicCausalCells()
        train(cells, 0, 1)
        cells.consolidate_and_recycle(0, 0)
        payload = bytearray(cells.snapshot())
        payload[10] ^= 1
        with self.assertRaises(ValueError):
            PublicCausalCells.restore(bytes(payload))


if __name__ == "__main__":
    unittest.main()
