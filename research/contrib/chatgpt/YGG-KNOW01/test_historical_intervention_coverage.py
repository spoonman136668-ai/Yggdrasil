"""KNOW09 static bounded support tests: zero original-world actions."""
from fractions import Fraction
import unittest

from historical_intervention_coverage import audit


def make_event(n, *, view=(0, 0), x1=0, s2=0, x2=0, y=0, other=None):
    return (format(n + 1, "064x"), (view, view if other is None else other),
            x1, s2, x2, y)


class FakeNative:
    def __init__(self, events):
        self.events = tuple(events)

    def _episode_reader(self):
        class Reader:
            pass
        reader = Reader()
        reader._ledger = self.events
        return reader

    def experience_forecast(self, view, first, next_state=None, second=None):
        return Fraction(1, 2)


class DriftingNative(FakeNative):
    def __init__(self, events, later):
        super().__init__(events)
        self.later = tuple(later)
        self.read_count = 0

    def _episode_reader(self):
        self.read_count += 1
        if self.read_count >= 3:
            return FakeNative(self.later)._episode_reader()
        return super()._episode_reader()


class Know09Tests(unittest.TestCase):
    def test_no_action_overlap_is_not_causal_support(self):
        events = [make_event(i, x1=0, s2=i % 2, x2=0,
                             y=i % 2, other=(1, 1)) for i in range(8)]
        out = audit(FakeNative(events), expected=8)
        self.assertEqual(out["native_witnesses"], 8)
        for p in out["reports"]:
            self.assertEqual(p["first_action_cells_observed_of_8"], 1)
            self.assertEqual(p["first_view_contexts_with_both_actions_of_4"], 0)
            self.assertEqual(p["terminal_public_prefixes_with_both_actions_of_16"], 0)
        self.assertFalse(out["causal_effect_identified"])
        self.assertEqual(out["new_source_actions"], 0)

    def test_balanced_full_coverage_still_does_not_identify_effects(self):
        events = []
        for v in ((0, 0), (0, 1), (1, 0), (1, 1)):
            for x1 in (0, 1):
                for s2 in (0, 1):
                    for x2 in (0, 1):
                        events.append(make_event(
                            len(events), view=v, x1=x1, s2=s2, x2=x2,
                            y=x1 ^ x2))
        out = audit(FakeNative(events), expected=32)
        for p in out["reports"]:
            self.assertEqual(p["first_action_cells_observed_of_8"], 8)
            self.assertEqual(p["first_view_contexts_with_both_actions_of_4"], 4)
            self.assertEqual(p["terminal_action_cells_observed_of_32"], 32)
            self.assertEqual(
                p["terminal_public_prefixes_with_both_actions_of_16"], 16)
            self.assertEqual(p["first_view_contexts_with_8_each_action_of_4"], 0)
            self.assertEqual(
                p["terminal_public_prefixes_with_8_each_action_of_16"], 0)
        self.assertFalse(out["causal_effect_identified"])
        self.assertFalse(out["randomized_treatment_assignment_verified"])

    def test_views_not_mistaken_for_two_independent_episodes(self):
        events = [make_event(0, view=(0, 0), other=(1, 1))]
        out = audit(FakeNative(events), expected=1)
        self.assertEqual(out["historical_witnesses_independent_per_projection"], 1)
        self.assertEqual([p["witnesses"] for p in out["reports"]], [1, 1])

    def test_mixed_outcomes_do_not_count_as_identified_causal_effect(self):
        events = [make_event(i, y=i % 2) for i in range(4)]
        out = audit(FakeNative(events), expected=4)
        self.assertEqual(out["reports"][0]["terminal_cells_with_both_outcomes"], 1)
        self.assertFalse(out["causal_effect_identified"])

    def test_drift_between_readout_validation_and_audit_is_caught(self):
        first = [make_event(0)]
        changed = [make_event(0, s2=1)]
        with self.assertRaisesRegex(ValueError, "RETROSPECTIVE_READOUT_DRIFT"):
            audit(DriftingNative(first, changed), expected=1)

    def test_public_events_still_require_valid_native_contract(self):
        with self.assertRaisesRegex(ValueError, "PUBLIC_EVENT_BITS"):
            audit(FakeNative([make_event(0, x1=True)]), expected=1)
        with self.assertRaisesRegex(ValueError, "WITNESS_IDENTITY"):
            audit(FakeNative([make_event(0), make_event(0)]), expected=2)

    def test_summary_never_contains_event_identifiers_or_source_events(self):
        event = make_event(8, view=(0, 1), other=(1, 0), y=1)
        out = audit(FakeNative([event]), expected=1)
        encoded = repr(out)
        self.assertNotIn(event[0], encoded)
        self.assertNotIn("source_private", encoded)
        self.assertNotIn("events", out)
        self.assertNotIn("ledger", out)
        self.assertFalse(out["disjoint_scientific_evaluation"])


if __name__ == "__main__":
    unittest.main()
