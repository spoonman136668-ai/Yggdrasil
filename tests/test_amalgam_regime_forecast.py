from fractions import Fraction
from pathlib import Path
import sys
import unittest


AMALGAM = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(AMALGAM))
from regime_forecast import RegimeForecast, fitted_old_readout
sys.path.remove(str(AMALGAM))


def old(_view, _first, *terminal):
    return Fraction(1, 2) if terminal else Fraction(1, 4)


class RegimeForecastTests(unittest.TestCase):
    def setUp(self):
        self.fit = [[str(i), ((1, 0), (1, 1)), {"x1": 1, "s2": 1}] for i in range(8)]

    def test_matched_arms_share_the_same_initial_posterior(self):
        models = [RegimeForecast(old, self.fit, assignment=mode)
                  for mode in ("fixed", "all", "posterior")]
        initial = [model.forecast((1, 0), 1) for model in models]
        self.assertEqual(len(set(initial)), 1)
        for model in models:
            model.observe((1, 0), 1, 1)
        fixed, all_rows, posterior = [model.forecast((1, 0), 1) for model in models]
        self.assertLess(fixed, posterior)
        self.assertLess(posterior, all_rows)

    def test_update_is_local_and_preserves_terminal(self):
        model = RegimeForecast(old, self.fit, assignment="posterior")
        for _ in range(8):
            model.observe((1, 0), 1, 1)
        self.assertGreater(model.forecast((1, 0), 1), 0.75)
        self.assertEqual(model.forecast((1, 0), 0), Fraction(1, 4))
        self.assertEqual(model.forecast((1, 0), 1, 1, 0), Fraction(1, 2))

    def test_return_evidence_reactivates_immutable_old_law(self):
        model = RegimeForecast(old, self.fit, assignment="posterior")
        for _ in range(8):
            model.observe((1, 0), 1, 1)
        for _ in range(8):
            model.observe((1, 0), 1, 0)
        self.assertLess(model.forecast((1, 0), 1), 0.35)

    def test_old_refit_matches_exact_counter_and_uses_anchor_for_unseen_arms(self):
        fitted = fitted_old_readout(old, self.fit)
        self.assertAlmostEqual(fitted((1, 0), 1), 9 / 10)
        self.assertEqual(fitted((1, 0), 0), old((1, 0), 0))
        self.assertEqual(fitted((1, 0), 1, 1, 0), old((1, 0), 1, 1, 0))
