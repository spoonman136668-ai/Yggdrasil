"""Focused behavioral tests for the held opt-in adaptive rescaling proposal.

These tests qualify only local method semantics. They do not override the
separate G29 atlas failure or grant F139 worker/science authority.
"""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells


class RescaledObservationTests(unittest.TestCase):
    def test_below_saturation_matches_baseline_observe(self):
        baseline = PublicCausalCells()
        adaptive = PublicCausalCells()
        for i in range(250):
            address = i % 7
            retained = (i % 3 == 0)
            action = (i // 2) % 2
            outcome = (i // 5) % 2
            baseline.observe(address, action, outcome, retained=retained)
            adaptive.observe_rescaled(address, action, outcome, retained=retained)
        self.assertEqual(adaptive.snapshot(), baseline.snapshot())

    def test_saturation_halves_all_four_counters_in_only_selected_cell(self):
        cells = PublicCausalCells()
        cells._counts[3] = [[65535, 13], [21, 31]]
        cells._counts[4] = [[17, 19], [23, 29]]
        unrelated = [list(arm) for arm in cells._counts[4]]
        cells.observe_rescaled(3, 0, 0)
        self.assertEqual(cells._counts[3], [[32768, 6], [10, 15]])
        self.assertEqual(cells._counts[4], unrelated)

    def test_no_rescaling_when_the_selected_counter_is_not_full(self):
        cells = PublicCausalCells()
        cells._counts[2] = [[65535, 9], [7, 11]]
        cells.observe_rescaled(2, 0, 1)
        self.assertEqual(cells._counts[2], [[65535, 10], [7, 11]])

    def test_retained_address_rescales_its_own_cell_only(self):
        cells = PublicCausalCells()
        cells._counts[0] = [[41, 43], [47, 53]]
        cells._counts[7] = [[65535, 15], [17, 19]]
        active_before = [list(arm) for arm in cells._counts[0]]
        cells.observe_rescaled(0, 0, 0, retained=True)
        self.assertEqual(cells._counts[7], [[32768, 7], [8, 9]])
        self.assertEqual(cells._counts[0], active_before)

    def test_invalid_observation_cannot_trigger_rescaling(self):
        cells = PublicCausalCells()
        cells._counts[1] = [[65535, 9], [7, 11]]
        before = cells.snapshot()
        invalid = [
            (8, 0, 0, False),
            (1, 2, 0, False),
            (1, 0, 2, False),
            (1, 0, 0, 1),
        ]
        for address, action, outcome, retained in invalid:
            with self.subTest(case=(address, action, outcome, retained)):
                with self.assertRaises(ValueError):
                    cells.observe_rescaled(address, action, outcome, retained=retained)
                self.assertEqual(cells.snapshot(), before)

    def test_baseline_observe_remains_saturating_and_unchanged(self):
        cells = PublicCausalCells()
        cells._counts[1] = [[65535, 9], [7, 11]]
        cells.observe(1, 0, 0)
        self.assertEqual(cells._counts[1], [[65535, 9], [7, 11]])

    def test_checkpoint_roundtrip_preserves_rescaled_state(self):
        cells = PublicCausalCells()
        cells._counts[5] = [[65535, 111], [222, 333]]
        cells.observe_rescaled(5, 0, 0)
        checkpoint = cells.snapshot()
        self.assertEqual(len(checkpoint), 164)
        restored = PublicCausalCells.restore(checkpoint)
        self.assertEqual(restored.snapshot(), checkpoint)
        cells.observe_rescaled(5, 1, 1)
        restored.observe_rescaled(5, 1, 1)
        self.assertEqual(restored.snapshot(), cells.snapshot())

    def test_checkpoint_size_and_learned_memory_remain_fixed(self):
        cells = PublicCausalCells()
        initial = cells.snapshot()
        for i in range(50):
            cell = i % 16
            retained = cell >= PublicCausalCells.ACTIVE_SLOTS
            address = cell - PublicCausalCells.ACTIVE_SLOTS if retained else cell
            cells._counts[cell][0][0] = 65535
            cells.observe_rescaled(address, 0, 0, retained=retained)
        self.assertEqual(len(cells.snapshot()), len(initial))
        self.assertEqual(cells.LEARNED_BYTES, 128)
        self.assertEqual(cells.CHECKPOINT_BYTES, 164)

    def test_all_counter_values_stay_in_unsigned_16_bit_range(self):
        cells = PublicCausalCells()
        cells._counts[0] = [[65535, 65535], [65535, 65535]]
        for _ in range(50):
            cells.observe_rescaled(0, 1, 1)
            for arm in cells._counts[0]:
                for value in arm:
                    self.assertGreaterEqual(value, 0)
                    self.assertLessEqual(value, 65535)


if __name__ == "__main__":
    unittest.main()
