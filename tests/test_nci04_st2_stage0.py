"""Source-free negative controls for ST2 frozen stage-0 gating.

These count fixtures do not call MiniGrid or consume original source seeds.
"""
import unittest

from research.nci04_st2.event_memory import correspondences, cross_position_headroom
from research.nci04_st2.stage0_consumed_headroom import (
    FAMILIES, SEEDS, headroom_verdict
)


def counts(a, b):
    return {
        FAMILIES[0]: dict(zip(SEEDS, a)),
        FAMILIES[1]: dict(zip(SEEDS, b)),
    }


class ST2Stage0Fixture(unittest.TestCase):
    def test_boundary_exact_32_requires_two_seeds_each_family(self):
        result = headroom_verdict(counts([8, 8, 0], [8, 8, 0]))
        self.assertTrue(result["eligible"])
        self.assertEqual(result["cross_position_total"], 32)
        self.assertEqual(result["necessary_reset_seeds_per_family"], 2)
        self.assertEqual(result["disposition"],
                         "STAGE0_IDENTIFIABLE_DEV_ONLY_NOT_SCIENCE")

    def test_31_matches_is_no_go_even_with_two_seeds_each(self):
        result = headroom_verdict(counts([8, 8, 0], [8, 7, 0]))
        self.assertFalse(result["eligible"])
        self.assertEqual(result["disposition"],
                         "SOURCE_ENTITY_IDENTIFIABILITY_NO_GO")

    def test_ample_total_cannot_substitute_for_seed_coverage(self):
        result = headroom_verdict(counts([40, 0, 0], [1, 1, 0]))
        self.assertFalse(result["eligible"])
        self.assertEqual(result["cross_position_total"], 42)
        self.assertEqual(result["qualified_reset_seeds_per_family"][FAMILIES[0]], 1)

    def test_zero_and_source_absence_no_go(self):
        self.assertFalse(headroom_verdict(counts([0]*3, [0]*3))["eligible"])
        for incorrect in (
            {FAMILIES[0]: dict(zip(SEEDS, (1, 2, 3)))},
            counts([1, -1, 40], [1, 1, 1]),
            counts([1, True, 40], [1, 1, 1]),
        ):
            with self.assertRaises(ValueError):
                headroom_verdict(incorrect)

    def test_future_frame_is_not_part_of_current_match(self):
        before = (0,) * 24
        now = list(before)
        after = list(before)
        after[0:3] = [3, 4, 5]
        now[3:6] = [3, 4, 5]
        self.assertEqual(correspondences(before, now), (None,) * 8)
        self.assertEqual(cross_position_headroom(before, now), 0)
        self.assertEqual(cross_position_headroom(now, after), 1)
        self.assertEqual(cross_position_headroom(None, now), 0)


if __name__ == "__main__":
    unittest.main()
