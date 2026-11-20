"""Exact arithmetic controls: logged observations are not interventions."""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "research/contrib/chatgpt/CAUSAL-AMALGAM"
          / "observational_action_identifiability.py")
SPEC = spec_from_file_location("amalgam_logged_action_identification", SOURCE)
LAW = module_from_spec(SPEC)
SPEC.loader.exec_module(LAW)


class ObservationalActionIdentifiabilityTests(unittest.TestCase):
    def test_authenticates_original_world_equations_without_running_world(self):
        self.assertEqual(LAW.require_original_source(), LAW.SOURCE_PIN)

    def test_exact_logged_vs_intervention_transition_table(self):
        expected = {
            (0, 0): (Fraction(5, 32), Fraction(47, 368), -Fraction(21, 736)),
            (0, 1): (Fraction(27, 32), Fraction(37, 48), -Fraction(7, 96)),
            (1, 0): (Fraction(7, 32), Fraction(7, 48), -Fraction(7, 96)),
            (1, 1): (Fraction(25, 32), Fraction(277, 368), -Fraction(21, 736)),
        }
        for (s1, x1), (causal, logged, bias) in expected.items():
            with self.subTest(s1=s1, x1=x1):
                self.assertEqual(LAW.conditional_transition(s1, x1, logged=False),
                                 causal)
                self.assertEqual(LAW.conditional_transition(s1, x1, logged=True),
                                 logged)
                self.assertEqual(logged - causal, bias)

    def test_randomized_action_logging_removes_hidden_variable_bias(self):
        for s1 in (0, 1):
            for x1 in (0, 1):
                self.assertEqual(
                    LAW.conditional_transition(
                        s1, x1, logged=True, logger_match=Fraction(1, 2)),
                    LAW.conditional_transition(s1, x1, logged=False))

    def test_homogeneous_transition_noise_removes_confounding(self):
        uniform_noise = (Fraction(1, 8), Fraction(1, 8))
        for s1 in (0, 1):
            for x1 in (0, 1):
                self.assertEqual(
                    LAW.conditional_transition(
                        s1, x1, logged=True, noise_by_hidden=uniform_noise),
                    LAW.conditional_transition(
                        s1, x1, logged=False, noise_by_hidden=uniform_noise))

    def test_proper_brier_excess_is_squared_probability_bias(self):
        observed = LAW.report()
        self.assertEqual(Fraction(observed["balanced_do_queries_excess_brier"]),
                         Fraction(14945, 4875264))
        for row in observed["rows"]:
            self.assertEqual(
                Fraction(row["brier_excess_if_logged_prediction_used_under_do"]),
                Fraction(row["logged_minus_do"]) ** 2)
        self.assertEqual(observed["source_episodes_generated"], 0)
        self.assertEqual(observed["source_actions"], 0)
        self.assertFalse(observed["scientific_pass"])

    def test_deterministic_logger_conditions_on_hidden_state(self):
        # Every public state has positive probability under either hidden
        # state; a deterministic logger thus still has positive support.
        self.assertEqual(
            LAW.conditional_transition(0, 1, logged=True,
                                       logger_match=Fraction(1)),
            Fraction(3, 4))
        with self.assertRaisesRegex(ValueError, "exact binary"):
            LAW.conditional_transition(0, True, logged=False)
        with self.assertRaisesRegex(ValueError, "exact binary"):
            LAW.conditional_transition(1, 1, logged="yes")
        with self.assertRaisesRegex(ValueError, "exact binary"):
            LAW.conditional_transition(
                0, 0, logged=True, noise_by_hidden=(Fraction(-1, 3), Fraction(1, 4)))


if __name__ == "__main__":
    unittest.main()
