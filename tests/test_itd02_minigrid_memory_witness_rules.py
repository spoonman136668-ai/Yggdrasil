"""Tests for the frozen public cue/order rule; algebraic fixtures only."""
import unittest

from research.native.itd02.minigrid_memory_witness_rules import (
    LEFT, RIGHT, expected_branch_action, public_object_at, public_key_ball_cells,
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

    def test_object_class_comes_from_public_image_channel_zero(self):
        image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
        image[2][3][0] = 5
        observation = {"image": image, "direction": 0, "mission": "public"}
        self.assertEqual(public_object_at(observation, (2, 3)), "key")
        image[2][3][0] = 6
        self.assertEqual(public_object_at(observation, (2, 3)), "ball")

    def test_object_classifier_rejects_invalid_cells_and_nonobjects(self):
        image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
        observation = {"image": image}
        for coordinate in ((-1, 0), (7, 2), (True, 1), (1,), None):
            with self.subTest(coordinate=coordinate):
                with self.assertRaises(ValueError):
                    public_object_at(observation, coordinate)
        image[2][3][0] = 2  # wall, not a key/ball label
        with self.assertRaisesRegex(ValueError, "PUBLIC_CELL_NOT_KEY_OR_BALL"):
            public_object_at(observation, (2, 3))

    def test_inventory_finds_only_visible_key_ball_cells(self):
        image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
        image[0][6][0] = 5
        image[4][1][0] = 6
        observation = {"image": image, "direction": 0, "mission": "public"}
        self.assertEqual(public_key_ball_cells(observation), [
            {"coordinate": [0, 6], "object": "key"},
            {"coordinate": [4, 1], "object": "ball"},
        ])

    def test_inventory_fails_closed_on_wrong_shape_or_cell_encoding(self):
        for observation in (
            {"image": [[[0, 0, 0] for _ in range(6)] for _ in range(7)]},
            {"image": [[[0, 0] for _ in range(7)] for _ in range(7)]},
            {"image": []},
            {},
        ):
            with self.subTest(observation_shape=repr(observation)[:30]):
                with self.assertRaises(ValueError):
                    public_key_ball_cells(observation)


if __name__ == "__main__":
    unittest.main()
