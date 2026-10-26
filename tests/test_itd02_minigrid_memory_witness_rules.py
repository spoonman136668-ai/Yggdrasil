"""Tests for the frozen public cue/order rule; algebraic fixtures only."""
import unittest

from research.native.itd02.minigrid_memory_witness_rules import (
    LEFT, RIGHT, expected_branch_action, public_object_at, public_key_ball_cells, rotate_left_cell_coordinate, east_facing_public_view_coordinate, east_facing_public_view_coordinate,
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

    def test_pinned_rotate_left_mapping_matches_witness_target_coordinate(self):
        # In the 7x7 view the local pre-rotation upper target (1,1)
        # maps to image coordinate (1,5), not (1,6).
        self.assertEqual(rotate_left_cell_coordinate(1, 1), (1, 5))
        self.assertEqual(rotate_left_cell_coordinate(0, 0), (0, 6))
        self.assertEqual(rotate_left_cell_coordinate(6, 6), (6, 0))

    def test_rotate_left_mapping_rejects_invalid_coordinate_and_dimensions(self):
        for x, y in ((-1, 0), (7, 0), (0, 7), (True, 0)):
            with self.subTest(x=x, y=y):
                with self.assertRaisesRegex(ValueError, "GRID_COORDINATE_INVALID"):
                    rotate_left_cell_coordinate(x, y)
        with self.assertRaisesRegex(ValueError, "GRID_DIMENSION_INVALID"):
            rotate_left_cell_coordinate(0, 0, width=0)


    def test_global_geometry_maps_start_cue_only_at_visible_endpoint(self):
        # MemoryS7 has height 7, so agent_y=3 and the cue is global (1,2).
        # At agent_x=1 it maps to public image (2,6).
        self.assertEqual(east_facing_public_view_coordinate(1, 2, 1, 3), (2, 6))
        # Moving the agent right makes that cue fall outside the public view.
        with self.assertRaisesRegex(ValueError, "GLOBAL_CELL_OUTSIDE_PUBLIC_VIEW"):
            east_facing_public_view_coordinate(1, 2, 2, 3)

    def test_global_geometry_maps_upper_target_to_correct_public_cell(self):
        # At hallway_end, the upper object is one cell ahead and two cells north.
        hallway_end = 8
        agent_y = 5
        self.assertEqual(
            east_facing_public_view_coordinate(
                hallway_end + 1, agent_y - 2, hallway_end, agent_y
            ),
            (1, 5),
        )

    def test_global_public_view_transform_rejects_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError, "GLOBAL_VIEW_COORDINATE_INVALID"):
            east_facing_public_view_coordinate(1, 4, True, 5)
        with self.assertRaisesRegex(ValueError, "WITNESS_VIEW_SIZE_MISMATCH"):
            east_facing_public_view_coordinate(1, 4, 1, 5, view_size=5)


if __name__ == "__main__":
    unittest.main()
