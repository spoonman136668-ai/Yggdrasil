"""Independent exact controls on OBS-01 retrospective diagnostic."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import unittest

spec = importlib.util.spec_from_file_location("observability_bound", Path(__file__).parent / "observability_bound.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Source-frozen old/new public conditional probabilities, no new world samples.
PINNED = {
    "shared_static_readout_only": True, "includes_outcomes_generated": 0,
    "old_transition_probability": ["5/32", "27/32", "5/32", "27/32", "7/32", "25/32", "7/32", "25/32"],
    "new_transition_probability": ["27/32", "5/32", "27/32", "5/32", "7/32", "7/32", "7/32", "7/32"],
}


class ObservabilityTests(unittest.TestCase):
    def test_no_information_action_is_exact_half_even_at_eight_probes(self):
        p = F(7, 32)
        for n in range(9):
            self.assertEqual(module.posterior_optimum(((p, p),), n), F(1, 2))

    def test_one_probe_exact_total_variation_identity(self):
        for p, q in ((F(5, 32), F(27, 32)), (F(25, 32), F(7, 32))):
            expected = (1 + abs(p - q)) / 2
            self.assertEqual(module.posterior_optimum(((p, q),), 1), expected)

    def test_adaptive_never_worse_than_fixed_same_information(self):
        o = module.run(PINNED)
        for case in o["cases"]:
            for a, b, c in zip(case["best_adaptive_map_accuracy"], case["fixed_action0_accuracy"], case["fixed_action1_accuracy"], strict=True):
                self.assertGreaterEqual(F(a), max(F(b), F(c)))

    def test_two_probes_do_not_reach_95_percent(self):
        for case in module.run(PINNED)["cases"]:
            self.assertLess(F(case["best_adaptive_map_accuracy"][2]), F(19, 20))

    def test_noisier_observations_cannot_improve_the_optimum(self):
        result = module.run(PINNED)["cases"]
        for i in (0, 2):
            for clean, noisy in zip(result[i]["best_adaptive_map_accuracy"], result[i+1]["best_adaptive_map_accuracy"], strict=True):
                self.assertGreaterEqual(F(clean), F(noisy))

    def test_cold_determinism_and_no_generated_world_outcomes(self):
        self.assertEqual(module.run(PINNED), module.run(PINNED))
        self.assertEqual(module.run(PINNED)["source_world_actions"], 0)
        self.assertFalse(module.run(PINNED)["scientific_gain_verified"])

    def test_source_alteration_is_rejected(self):
        forged = dict(PINNED, old_transition_probability=list(PINNED["old_transition_probability"]))
        forged["old_transition_probability"][0] = "1/2"
        with self.assertRaisesRegex(ValueError, "OBS01_PINNED_SOURCE_MISMATCH"):
            module.run(forged)

    def test_disallowed_budgets_and_invalid_laws(self):
        with self.assertRaisesRegex(ValueError, "OBS01_BUDGET"):
            module.posterior_optimum(((F(1,2), F(1,4)),), 9)
        with self.assertRaisesRegex(ValueError, "OBS01_NOT_PINNED_ANALYTIC_INPUT"):
            module.run({"shared_static_readout_only": False})

if __name__ == "__main__":
    unittest.main()
