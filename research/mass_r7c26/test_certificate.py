"""Source-only C26: no original MiniGrid import, reset, step, or heldout reads."""
import copy
import unittest

from research.mass_r7c26.certificate import (
    certify_frozen_selected_fit,
    certify_candidate_event_coverage,
)


def public(x=2, y=2, direction=0, front_blocked=False):
    return {
        "x": x, "y": y, "goal_x": 5, "goal_y": 5,
        "direction": direction, "front_blocked": front_blocked,
    }


def event(action, episode="public-fixture", seq=0, before=None, terminal=False):
    start = copy.deepcopy(before if before is not None else public())
    after = copy.deepcopy(start)
    if action == 0:
        after["direction"] = (after["direction"] - 1) % 4
    elif action == 1:
        after["direction"] = (after["direction"] + 1) % 4
    elif action == 2:
        after["x"] += 1
    return {
        "episode": episode, "seq": seq,
        "before": start, "action": action, "after": after,
        "reward": 0.0, "terminal": terminal,
    }


class SourceOnlyFitCoverage(unittest.TestCase):
    def test_original_selected_fit_has_no_turn_effect(self):
        report = certify_frozen_selected_fit()
        self.assertEqual(report["selected_actions"], {"0": 0, "1": 0, "2": 12})
        self.assertEqual(report["observed_legal_turn_effects_in_selected_fit"], 0)
        self.assertFalse(report["learnt_turn_value_identifiable_from_selected_fit_alone"])
        self.assertEqual(report["original_source_episodes_executed_by_this_certificate"], 0)

    def test_forward_only_selected_examples_fail_action_coverage(self):
        rows = [event(2, episode="forward-%02d" % i) for i in range(12)]
        report = certify_candidate_event_coverage(rows)
        self.assertEqual(report["selected_legal_action_counts"], {"0": 0, "1": 0, "2": 12})
        self.assertFalse(report["action_family_coverage"])

    def test_authored_all_three_action_fixture_covers_grammar_but_not_science(self):
        rows = [event(a, episode="fixture-%d" % a) for a in (0, 1, 2)]
        report = certify_candidate_event_coverage(rows)
        self.assertTrue(report["action_family_coverage"])
        self.assertEqual(report["learnt_value_of_information"] if "learnt_value_of_information" in report
                         else report["learned_value_of_information"], "NOT_TESTED")
        self.assertEqual(report["source_event_authenticity"], "UNVERIFIED_SOURCE_FREE_INPUT")
        self.assertEqual(report["science_admission"], "DENIED")

    def test_valid_contiguous_public_sequence(self):
        a = event(0)
        b = event(1, seq=1, before=a["after"])
        report = certify_candidate_event_coverage([a, b])
        self.assertEqual(report["selected_legal_action_counts"], {"0": 1, "1": 1, "2": 0})

    def test_duplicate_or_skipped_seq_rejected(self):
        a = event(0)
        with self.assertRaisesRegex(ValueError, "OUT_OF_ORDER"):
            certify_candidate_event_coverage([a, event(1, seq=0, before=a["after"])])
        with self.assertRaisesRegex(ValueError, "OUT_OF_ORDER"):
            certify_candidate_event_coverage([a, event(1, seq=2, before=a["after"])])

    def test_privileged_info_refused(self):
        a = event(0)
        a["env"] = object()
        with self.assertRaisesRegex(ValueError, "NONPUBLIC_EVENT"):
            certify_candidate_event_coverage([a])
        b = event(0)
        b["after"]["hidden_map"] = 4
        with self.assertRaisesRegex(ValueError, "NONPUBLIC_STATE"):
            certify_candidate_event_coverage([b])

    def test_turn_action_consequence_owner_mismatch_rejected(self):
        a = event(0)
        a["after"]["direction"] = 1
        with self.assertRaisesRegex(ValueError, "TURN_RETURN"):
            certify_candidate_event_coverage([a])

    def test_event_chain_must_reuse_returned_state(self):
        a = event(0)
        b = event(1, seq=1, before=public())
        with self.assertRaisesRegex(ValueError, "UNLINKED"):
            certify_candidate_event_coverage([a, b])

    def test_terminal_episode_cannot_resume(self):
        a = event(0, terminal=True)
        b = event(1, seq=1, before=a["after"])
        with self.assertRaisesRegex(ValueError, "ALREADY_TERMINAL"):
            certify_candidate_event_coverage([a, b])

    def test_illegal_action_bool_and_bad_reward_refused(self):
        a = event(0)
        a["action"] = True
        with self.assertRaisesRegex(ValueError, "ILLEGAL"):
            certify_candidate_event_coverage([a])
        b = event(0)
        b["reward"] = float("nan")
        with self.assertRaisesRegex(ValueError, "NONFINITE"):
            certify_candidate_event_coverage([b])

    def test_malformed_public_coordinate_or_goal_rejected(self):
        a = event(0)
        a["after"]["goal_x"] = 22
        with self.assertRaisesRegex(ValueError, "CHANGED_GOAL"):
            certify_candidate_event_coverage([a])
        b = event(0)
        b["before"]["x"] = -1
        with self.assertRaisesRegex(ValueError, "COORDINATE"):
            certify_candidate_event_coverage([b])


if __name__ == "__main__":
    unittest.main()
