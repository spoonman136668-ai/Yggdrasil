"""Pure contract tests; synthetic tuples only, no environment is imported/run."""
import unittest

from research.native.itd02.dtr_public_event_contract import (
    PUBLIC_KEYS, SCHEMA, SOURCE, project_reset, project_step,
    public_receipt_digest, validate_episode,
)


class PoisonInfo(dict):
    """Explode if a projector tries to inspect the upstream diagnostic info."""
    def __iter__(self):
        raise AssertionError("raw info must not be iterated")

    def items(self):
        raise AssertionError("raw info must not be copied")

    def keys(self):
        raise AssertionError("raw info must not be inspected")

    def get(self, *args, **kwargs):
        raise AssertionError("raw info must not be queried")


def make_events(s1=0, s2=1, y=1, x1=0, x2=1, seed=17):
    receipt = dict(SOURCE)
    reset = project_reset(
        (s1, PoisonInfo(stage=999, u=0.25, y=1, graph="hidden")),
        episode_seed=seed, source_receipt=receipt)
    first = project_step(
        (s2, 0, False, False,
         PoisonInfo(s1=1-s1, x1=1-x1, s2=1-s2, u=0.99, y=1)),
        episode_seed=seed, seq=1, stage_before=0, action=x1,
        source_receipt=receipt)
    terminal = project_step(
        (None, y, True, False,
         PoisonInfo(s1=1-s1, x1=1-x1, s2=1-s2, x2=1-x2, y=1-y, u=0.01)),
        episode_seed=seed, seq=2, stage_before=1, action=x2,
        source_receipt=receipt)
    return [reset, first, terminal]


class DTRPublicEventContractTests(unittest.TestCase):
    def test_info_is_never_read_and_never_serialized(self):
        events = make_events()
        self.assertEqual([set(event) for event in events], [PUBLIC_KEYS] * 3)
        encoded = repr(events)
        for private in ("graph", "'u'", "'s1'", "'x1'", "'x2'", "'y'"):
            self.assertNotIn(private, encoded)
        self.assertEqual(events[0]["stage_after"], 0)
        self.assertEqual(events[1]["stage_after"], 1)
        self.assertEqual(events[2]["stage_after"], 2)

    def test_all_binary_action_pairs_and_terminal_outcomes_validate(self):
        for s1 in (0, 1):
            for s2 in (0, 1):
                for x1 in (0, 1):
                    for x2 in (0, 1):
                        for y in (0, 1):
                            events = make_events(s1, s2, y, x1, x2)
                            self.assertEqual(len(validate_episode(events)), 3)

    def test_receipt_is_stable_and_changes_when_public_event_changes(self):
        events = make_events()
        digest = public_receipt_digest(events)
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, public_receipt_digest(events))
        changed = make_events(s1=1)
        self.assertNotEqual(digest, public_receipt_digest(changed))

    def test_rejects_wrong_source_or_malformed_tuple_without_leak(self):
        bad = dict(SOURCE)
        bad["commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_PIN_MISMATCH"):
            project_reset((0, PoisonInfo(u=0.3)), episode_seed=1, source_receipt=bad)
        for result in (None, (0,), [0, {}], (True, {}), (2, {})):
            with self.subTest(result_type=type(result).__name__):
                with self.assertRaises(ValueError):
                    project_reset(result, episode_seed=1, source_receipt=dict(SOURCE))
        for result in ((0, 0, False, False), (2, 0, False, False, {})):
            with self.assertRaises(ValueError):
                project_step(result, episode_seed=1, seq=1, stage_before=0,
                             action=0, source_receipt=dict(SOURCE))

    def test_rejects_invalid_stage_reward_and_action_transitions(self):
        cases = [
            ((1, 1, False, False, {}), 0, 0),
            ((1, 0, True, False, {}), 0, 0),
            ((1, 0, False, True, {}), 0, 0),
            ((None, 0, False, False, {}), 1, 1),
            ((0, 1, True, False, {}), 1, 1),
            ((None, 2, True, False, {}), 1, 1),
        ]
        for result, stage, action in cases:
            with self.subTest(result=result, stage=stage):
                with self.assertRaises(ValueError):
                    project_step(result, episode_seed=2, seq=stage + 1,
                                 stage_before=stage, action=action,
                                 source_receipt=dict(SOURCE))
        for invalid in (True, 2, -1, 0.0, "1", None):
            with self.assertRaises(ValueError):
                project_step((1, 0, False, False, {}), episode_seed=2,
                             seq=1, stage_before=0, action=invalid,
                             source_receipt=dict(SOURCE))

    def test_episode_rejects_extra_fields_sequence_drift_and_mixed_seed(self):
        events = make_events()
        contaminated = [dict(row) for row in events]
        contaminated[0]["u"] = 0.4
        with self.assertRaisesRegex(ValueError, "NONPUBLIC_EVENT_FIELDS"):
            validate_episode(contaminated)
        changed = [dict(row) for row in events]
        changed[1]["seq"] = 2
        with self.assertRaisesRegex(ValueError, "DTR_EPISODE_STAGE_OR_SEQUENCE_INVALID"):
            validate_episode(changed)
        changed = [dict(row) for row in events]
        changed[1]["episode_seed"] = 18
        with self.assertRaisesRegex(ValueError, "EPISODE_SEED_DRIFT"):
            validate_episode(changed)
        with self.assertRaisesRegex(ValueError, "DTR_EPISODE_MUST_HAVE_THREE_EVENTS"):
            validate_episode(events[:2])


if __name__ == "__main__":
    unittest.main()
