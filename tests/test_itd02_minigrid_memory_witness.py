"""Tests for public-history witness receipt validation; no environment runs."""
import unittest

from research.native.itd02.minigrid_memory_event_contract import (
    MISSION, SOURCE, project_reset, project_step,
)
from research.native.itd02.minigrid_memory_witness import verify_history_witness_pair


def obs(marker=0, direction=0):
    image = [[[0, 0, 0] for _ in range(7)] for _ in range(7)]
    image[2][3][0] = marker
    return {"image": image, "direction": direction, "mission": MISSION}


def episode(seed, prior_marker, decision_marker=5, decision_action=0, reward=0.64):
    receipt = dict(SOURCE)
    return [
        project_reset((obs(prior_marker), {"hidden": "ignored"}),
                      episode_seed=seed, source_receipt=receipt),
        project_step((obs(prior_marker, 1), 0.0, False, False, {"private": 1}),
                     episode_seed=seed, seq=1, action=2,
                     source_receipt=receipt),
        project_step((obs(decision_marker, 2), 0.0, False, False, {}),
                     episode_seed=seed, seq=2, action=2,
                     source_receipt=receipt),
        project_step((obs(8, 3), 0.0, False, False, {}),
                     episode_seed=seed, seq=3, action=decision_action,
                     source_receipt=receipt),
        project_step((obs(4, 0), reward, True, False, {"success_pos": [1, 2]}),
                     episode_seed=seed, seq=4, action=2,
                     source_receipt=receipt),
    ]


def verify(a, b, cue_cell_a=(2, 3), cue_cell_b=(2, 3), upper_cell=(2, 3)):
    return verify_history_witness_pair(
        a, b, decision_seq_a=2, decision_seq_b=2,
        public_cue_cell_a=cue_cell_a, public_cue_cell_b=cue_cell_b,
        public_upper_object_cell=upper_cell, agent_direction_a=0, agent_direction_b=0,
    )


class PublicHistoryWitnessTests(unittest.TestCase):
    def test_same_decision_view_different_history_rule_action_and_later_success(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_action=1)
        receipt = verify(a, b)
        reverse = verify(b, a)
        self.assertEqual(receipt["decision_observation_sha256"],
                         reverse["decision_observation_sha256"])
        self.assertNotEqual(receipt["history_a_sha256"], receipt["history_b_sha256"])
        self.assertEqual(receipt["expected_action_a"], 0)
        self.assertEqual(receipt["expected_action_b"], 1)
        self.assertEqual(receipt["terminal_reward_a"], receipt["terminal_reward_b"])
        self.assertEqual(a[-1]["action"], b[-1]["action"])
        self.assertEqual(receipt["claim"],
                         "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED")

    def test_rejects_different_decision_observation(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_marker=10, decision_action=1)
        with self.assertRaisesRegex(ValueError, "WITNESS_DECISION_OBSERVATION_MISMATCH"):
            verify(a, b)

    def test_rejects_identical_prior_history(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=5, decision_action=0)
        with self.assertRaisesRegex(ValueError, "WITNESS_PRIOR_HISTORIES_IDENTICAL"):
            verify(a, b)

    def test_rejects_action_that_disagrees_with_public_rule(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_action=0)
        with self.assertRaisesRegex(ValueError, "WITNESS_B_ACTION_DOES_NOT_MATCH_PUBLIC_SOURCE_RULE"):
            verify(a, b)

    def test_rejects_missing_forward_route_continuation(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_action=1)
        b[4]["action"] = 1
        with self.assertRaisesRegex(ValueError, "WITNESS_B_DID_NOT_CONTINUE_FORWARD"):
            verify(a, b)

    def test_rejects_zero_reward_or_nonterminal_pair(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_action=1, reward=0.0)
        with self.assertRaisesRegex(ValueError, "WITNESS_B_NO_PUBLIC_SUCCESS_REWARD"):
            verify(a, b)
        c = episode(20002, prior_marker=6, decision_action=1)
        c[-1]["terminated"] = False
        with self.assertRaisesRegex(ValueError, "WITNESS_B_NOT_TERMINAL_SUCCESS"):
            verify(a, c)

    def test_rejects_invalid_decision_sequence(self):
        a = episode(10001, prior_marker=5, decision_action=0)
        b = episode(20001, prior_marker=6, decision_action=1)
        with self.assertRaises(ValueError):
            verify_history_witness_pair(
                a, b, decision_seq_a=True, decision_seq_b=2,
                public_cue_cell_a=(2, 3), public_cue_cell_b=(2, 3),
                public_upper_object_cell=(2, 3), agent_direction_a=0, agent_direction_b=0,
            )


if __name__ == "__main__":
    unittest.main()
