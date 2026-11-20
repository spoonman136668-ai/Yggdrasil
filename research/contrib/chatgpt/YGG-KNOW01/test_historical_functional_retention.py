"""KNOW08 fixture-only controls; original model and first-use source unused."""
from fractions import Fraction
import unittest

from historical_functional_retention import canonical, fingerprint


class FakeEpisodeReader:
    def __init__(self, ledger):
        self._ledger = tuple(ledger)


class FakeNative:
    def __init__(self, *, events=None, transition=Fraction(1, 2),
                 terminal=Fraction(1, 2)):
        self.events = (
            [("a"*64, ((0, 0), (1, 1)), 0, 1, 0, 0)]
            if events is None else events)
        self.transition = transition
        self.terminal = terminal

    def _episode_reader(self):
        return FakeEpisodeReader(self.events)

    def experience_forecast(self, view, first, state=None, second=None):
        return self.transition if state is None else self.terminal


class Know08Tests(unittest.TestCase):
    def test_deterministic_snapshot_and_fractional_in_sample_brier(self):
        a = fingerprint(FakeNative(), expected=1)
        b = fingerprint(FakeNative(), expected=1)
        self.assertEqual(a, b)
        self.assertEqual(a["witnesses"], 1)
        self.assertEqual(a["forecast_readouts"], 4)
        self.assertEqual(a["retrospective_mean_brier_fraction"], [1, 4])
        self.assertFalse(a["independent_heldout"])
        self.assertFalse(a["prequential"])

    def test_native_behavior_change_detected_by_full_readout_hash(self):
        original = fingerprint(FakeNative(), expected=1)
        changed = fingerprint(
            FakeNative(transition=Fraction(3, 4)), expected=1)
        self.assertNotEqual(original["retrospective_readout_sha256"],
                            changed["retrospective_readout_sha256"])

    def test_mismatched_history_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "HISTORICAL_LEDGER_LENGTH"):
            fingerprint(FakeNative(), expected=1025)
        with self.assertRaisesRegex(ValueError, "HISTORICAL_LEDGER_LENGTH"):
            fingerprint(FakeNative(), expected=1153)

    def test_bad_identity_and_duplicate_witness_rejected(self):
        one = ("a"*64, ((0, 0), (1, 1)), 0, 1, 0, 0)
        with self.assertRaisesRegex(ValueError, "WITNESS_IDENTITY"):
            fingerprint(FakeNative(events=[("bad", *one[1:])]), expected=1)
        with self.assertRaisesRegex(ValueError, "WITNESS_IDENTITY"):
            fingerprint(FakeNative(events=[one, one]), expected=2)

    def test_boolean_bits_and_bad_views_rejected(self):
        for events in (
            [("a"*64, ((0, 0), (1, 1)), True, 1, 0, 0)],
            [("a"*64, ((0, 0), (1, 2)), 0, 1, 0, 0)],
            [("a"*64, ([0, 0], (1, 1)), 0, 1, 0, 0)],
        ):
            with self.assertRaisesRegex(ValueError, "PUBLIC_EVENT_BITS"):
                fingerprint(FakeNative(events=events), expected=1)

    def test_nonprobability_or_invalid_forecast_rejected(self):
        for bad in (float("nan"), 2, Fraction(5, 4), -Fraction(1, 2)):
            with self.assertRaisesRegex(ValueError, "PUBLIC_FORECAST_RANGE"):
                fingerprint(FakeNative(transition=bad), expected=1)

    def test_replay_scores_not_independent_science(self):
        actual = fingerprint(FakeNative(), expected=1)
        self.assertFalse(actual["prequential"])
        self.assertFalse(actual["independent_heldout"])
        self.assertNotIn("scientific_pass", actual)

    def test_json_canonicalization(self):
        self.assertEqual(canonical({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}')


if __name__ == "__main__":
    unittest.main()
