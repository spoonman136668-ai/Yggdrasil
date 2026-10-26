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


def episode(seed, prior_marker, decision_marker=9, decision_action=0, reward=0.64):
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
        # This is the action selected at the shared decision observation.
        # It need not itself be the terminal action.
        project_step((obs(8, 3), 0.0, False, False, {}),
                     episode_seed=seed, seq=3, action=decision_action,
                     source_receipt=receipt),
        # Both traces later succeed with the same terminal action.
        project_step((obs(4, 0), reward, True, False, {"success_pos": [1, 2]}),
                     episode_seed=seed, seq=4, action=2,
                     source_receipt=receipt),
    ]


class PublicHistoryWitnessTests(unittest.TestCase):
    def test_same_decision_view_different_history_and_decision_actions(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=3, decision_action=1)
        receipt = verify_history_witness_pair(
            a, b, decision_seq_a=2, decision_seq_b=2)
        reverse = verify_history_witness_pair(
            b, a, decision_seq_a=2, decision_seq_b=2)
        self.assertEqual(receipt["decision_observation_sha256"],
                         reverse["decision_observation_sha256"])
        self.assertNotEqual(receipt["history_a_sha256"], receipt["history_b_sha256"])
        self.assertNotEqual(receipt["decision_action_a"], receipt["decision_action_b"])
        # Important: terminal action is identical in both episodes.
        self.assertEqual(a[-1]["action"], b[-1]["action"])
        self.assertEqual(receipt["claim"],
                         "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED")

    def test_rejects_different_decision_observation(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=3, decision_marker=10, decision_action=1)
        with self.assertRaisesRegex(ValueError, "WITNESS_DECISION_OBSERVATION_MISMATCH"):
            verify_history_witness_pair(a, b, decision_seq_a=2, decision_seq_b=2)

    def test_rejects_identical_prior_history(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=2, decision_action=1)
        with self.assertRaisesRegex(ValueError, "WITNESS_PRIOR_HISTORIES_IDENTICAL"):
            verify_history_witness_pair(a, b, decision_seq_a=2, decision_seq_b=2)

    def test_rejects_same_decision_action_even_if_terminal_actions_differ(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=3, decision_action=0)
        with self.assertRaisesRegex(ValueError, "WITNESS_DECISION_ACTIONS_NOT_DISTINCT"):
            verify_history_witness_pair(a, b, decision_seq_a=2, decision_seq_b=2)

    def test_rejects_zero_reward_or_nonterminal_pair(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=3, decision_action=1, reward=0.0)
        with self.assertRaisesRegex(ValueError, "WITNESS_B_NO_PUBLIC_SUCCESS_REWARD"):
            verify_history_witness_pair(a, b, decision_seq_a=2, decision_seq_b=2)
        c = episode(20002, prior_marker=3, decision_action=1)
        c[-1]["terminated"] = False
        with self.assertRaisesRegex(ValueError, "WITNESS_B_NOT_TERMINAL_SUCCESS"):
            verify_history_witness_pair(a, c, decision_seq_a=2, decision_seq_b=2)

    def test_rejects_unpreregistered_or_out_of_range_decision_sequence(self):
        a = episode(10001, prior_marker=2, decision_action=0)
        b = episode(20001, prior_marker=3, decision_action=1)
        for value in (True, -1, 4, "2"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    verify_history_witness_pair(a, b, decision_seq_a=value,
                                                decision_seq_b=2)


if __name__ == "__main__":
    unittest.main()
