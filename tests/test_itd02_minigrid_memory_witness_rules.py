"""Tests for the frozen public cue/order rule; algebraic fixtures only."""
import unittest

from research.native.itd02.minigrid_memory_witness_rules import (
    LEFT, RIGHT, expected_branch_action,
)


class PublicCueRuleTests(unittest.TestCase):
    def test_all_four_cue_and_upper_object_combinations(self):
        self.assertEqual(expected_branch_action("key", "key", agent_direction=0), LEFT)
        self.assertEqual(expected_branch_action("ball", "ball", agent_direction=0), LEFT)
        self.assertEqual(expected_branch_action("key", "ball", agent_direction=0), RIGHT)
        self.assertEqual(expected_branch_action("ball", "key", agent_direction=0), RIGHT)

    def test_invalid_or_nonpublic_object_class_fails_closed(self):
        for cue, upper in (
            ("box", "key"), ("key", "box"), ("hidden-goal", "key"),
            (None, "key"), ("key", None),
        ):
            with self.subTest(cue=cue, upper=upper):
                with self.assertRaisesRegex(ValueError, "PUBLIC_OBJECT_CLASS_INVALID"):
                    expected_branch_action(cue, upper, agent_direction=0)

    def test_wrong_pose_fails_closed(self):
        for direction in (1, 2, 3, True, "east"):
            with self.subTest(direction=direction):
                with self.assertRaisesRegex(ValueError, "WITNESS_POSE_NOT_EAST_FACING"):
                    expected_branch_action("key", "key", agent_direction=direction)


if __name__ == "__main__":
    unittest.main()
