"""Synthetic PUBLIC-IMAGE unit fixtures only. NEVER original MiniGrid source runs."""
import unittest
from public_scaffold import (
    PublicOnlyNavigation, PublicView, ProtocolBlocked, Stage,
    KEY, BALL, WALL, EMPTY, LEFT, RIGHT, FORWARD,
    public_rule_choice, MISSION,
)


def public_obs(heading=0, front=EMPTY, at_two=None):
    image = [[[EMPTY, 0, 0] for y in range(7)] for x in range(7)]
    image[3][5][0] = front
    if at_two is not None:
        image[3][4][0] = at_two
    return {"image": image, "direction": heading, "mission": MISSION}


class MR34J3COfflineTests(unittest.TestCase):
    def test_strict_public_snapshot_no_hidden_fields(self):
        obs = public_obs(3, KEY)
        view = PublicView.from_observation(obs)
        self.assertEqual(len(view.image_bytes), 147)
        obs["image"][3][5][0] = BALL
        self.assertEqual(view.front(), KEY)
        obs["agent_pos"] = (1, 3)
        with self.assertRaisesRegex(ProtocolBlocked, "NONPUBLIC_OBSERVATION_FIELDS"):
            PublicView.from_observation(obs)

    def test_direction_and_mission_rejected(self):
        for direction in [-1, 4, "3", True]:
            with self.assertRaises(ProtocolBlocked):
                PublicView.from_observation(public_obs(direction))
        obs = public_obs()
        obs["mission"] = "oracle branch north"
        with self.assertRaises(ProtocolBlocked):
            PublicView.from_observation(obs)

    def test_malformed_visuals_rejected(self):
        obs = public_obs()
        obs["image"][0][0] = [0, 0]
        with self.assertRaises(ProtocolBlocked):
            PublicView.from_observation(obs)
        obs = public_obs()
        obs["image"][0][0][0] = 300
        with self.assertRaises(ProtocolBlocked):
            PublicView.from_observation(obs)

    def test_public_wall_cue_fork_sequence(self):
        n = PublicOnlyNavigation()
        self.assertEqual(n.advance(public_obs(0)).action, LEFT)
        self.assertEqual(n.advance(public_obs(3)).action, LEFT)
        self.assertEqual(n.advance(public_obs(2, EMPTY)).action, FORWARD)
        self.assertEqual(n.advance(public_obs(2, WALL)).action, RIGHT)
        cue = n.advance(public_obs(3, KEY))
        self.assertEqual(cue.event, "PUBLIC_CUE_EXPOSURE")
        self.assertTrue(n.cue_exposed)
        self.assertEqual(n.advance(public_obs(0, EMPTY)).action, FORWARD)
        self.assertEqual(n.advance(public_obs(0, WALL)).action, LEFT)
        fork = n.advance(public_obs(3, EMPTY, BALL))
        self.assertEqual(fork.action, None)
        self.assertEqual(fork.event, "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE")
        self.assertTrue(n.fork_exposed)
        self.assertEqual(n.stage, Stage.AWAIT_CHOICE)
        with self.assertRaisesRegex(ProtocolBlocked, "FORK_NEEDS_ONE_BRANCH_CHOICE"):
            n.advance(public_obs(3, EMPTY, BALL))
        self.assertEqual(n.commit("south").event, "BRANCH_CHOICE_ACCEPTED")
        self.assertEqual([n.advance(public_obs(3)).action,
                          n.advance(public_obs(0)).action,
                          n.advance(public_obs(1)).action], [RIGHT, RIGHT, FORWARD])
        self.assertEqual(n.advance(public_obs(1)).event, "COMMIT_ACTIONS_EXHAUSTED")
        with self.assertRaises(ProtocolBlocked):
            n.advance(public_obs(1))

    def test_north_one_step_commit(self):
        n = PublicOnlyNavigation()
        n.stage = Stage.AWAIT_CHOICE
        n.cue_exposed = n.fork_exposed = True
        self.assertIsNone(n.commit("north").action)
        self.assertEqual(n.advance(public_obs(3)).action, FORWARD)

    def test_unseen_or_unsupported_front_fails_closed(self):
        n = PublicOnlyNavigation()
        n.stage = Stage.SEEK_WEST
        with self.assertRaises(ProtocolBlocked):
            n.advance(public_obs(2, 0))
        n.stage = Stage.SCAN_CUE
        with self.assertRaisesRegex(ProtocolBlocked, "STARTING_CUE_NOT_PUBLICLY_EXPOSED"):
            n.advance(public_obs(3, EMPTY))
        n.stage = Stage.SCAN_FORK
        with self.assertRaisesRegex(ProtocolBlocked, "FORK_OBJECT_NOT_PUBLICLY_EXPOSED"):
            n.advance(public_obs(3, EMPTY, 0))

    def test_no_wrong_time_or_illegal_decisions(self):
        n = PublicOnlyNavigation()
        with self.assertRaises(ProtocolBlocked):
            n.commit("north")
        n.stage = Stage.AWAIT_CHOICE
        n.cue_exposed = n.fork_exposed = True
        with self.assertRaises(ProtocolBlocked):
            n.commit("oracle")

    def test_rule_memory_causal_contrast(self):
        ckey, cball = PublicView.from_observation(public_obs(3, KEY)), PublicView.from_observation(public_obs(3, BALL))
        fkey, fball = PublicView.from_observation(public_obs(3, EMPTY, KEY)), PublicView.from_observation(public_obs(3, EMPTY, BALL))
        self.assertEqual(public_rule_choice(ckey, fkey), "north")
        self.assertEqual(public_rule_choice(ckey, fball), "south")
        self.assertEqual(public_rule_choice(cball, fkey), "south")
        self.assertEqual(public_rule_choice(cball, fball), "north")
        with self.assertRaises(ProtocolBlocked):
            public_rule_choice(ckey, PublicView.from_observation(public_obs(3, EMPTY, EMPTY)))

    def test_safety_budget_stops(self):
        n = PublicOnlyNavigation(max_navigation_commands=2)
        n.advance(public_obs(0))
        n.advance(public_obs(3))
        with self.assertRaisesRegex(ProtocolBlocked, "SHARED_SCAFFOLD_BUDGET_EXCEEDED"):
            n.advance(public_obs(2, EMPTY))

if __name__ == "__main__":
    unittest.main()
