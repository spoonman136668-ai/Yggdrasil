"""Pure symbolic falsification tests, no source or model execution."""
import unittest
from fractions import Fraction
from finite_probe import (ADVISORY_ERROR, BUDGET, WORLDS, audit,
                          binomial_pmf, minimum_rare_probes,
                          oracle_bayes_error, rare_trigger_error)


class FiniteProbeAuditTest(unittest.TestCase):
    def test_zero_evidence_and_world_exchange(self):
        for p, q in WORLDS.values():
            self.assertEqual(oracle_bayes_error(0, p, q), Fraction(1, 2))
            self.assertEqual(oracle_bayes_error(BUDGET, p, q),
                             oracle_bayes_error(BUDGET, q, p))

    def test_exact_binomial_normalization(self):
        for p, _ in WORLDS.values():
            self.assertEqual(sum((binomial_pmf(BUDGET, p, k)
                                  for k in range(BUDGET + 1)), Fraction(0)), 1)

    def test_strong_moderate_weak_and_equivalent_laws(self):
        risks = {name: oracle_bayes_error(BUDGET, *prob)
                 for name, prob in WORLDS.items()}
        self.assertLess(risks["STRONG"], ADVISORY_ERROR)
        self.assertGreater(risks["MODERATE"], ADVISORY_ERROR)
        self.assertLess(risks["STRONG"], risks["MODERATE"])
        self.assertLess(risks["MODERATE"], risks["WEAK"])
        self.assertLess(risks["WEAK"], risks["UNIDENTIFIABLE"])
        self.assertEqual(risks["UNIDENTIFIABLE"], Fraction(1, 2))

    def test_rare_latent_exact_error(self):
        self.assertEqual(rare_trigger_error(BUDGET), Fraction(1, 2)
                         * Fraction(63, 64) ** BUDGET)
        self.assertGreater(rare_trigger_error(BUDGET), Fraction(3, 10))
        needed = minimum_rare_probes()
        self.assertEqual(needed, 147)
        self.assertGreater(rare_trigger_error(needed - 1), ADVISORY_ERROR)
        self.assertLessEqual(rare_trigger_error(needed), ADVISORY_ERROR)

    def test_invalid_probabilities_and_budget_fail_closed(self):
        for n, p, q in ((-1, Fraction(1, 2), Fraction(1, 2)),
                        (32, Fraction(-1, 4), Fraction(1, 2)),
                        (32, Fraction(1, 2), Fraction(5, 4))):
            with self.assertRaises(ValueError):
                oracle_bayes_error(n, p, q)
        with self.assertRaises(TypeError):
            oracle_bayes_error(32, .3, Fraction(1, 2))
        with self.assertRaises(ValueError):
            minimum_rare_probes(Fraction(0))
        with self.assertRaises(ValueError):
            minimum_rare_probes(Fraction(1, 20), Fraction(0))

    def test_audit_never_confers_source_or_controller_authority(self):
        report = audit()
        self.assertEqual(report["probe_budget"], 32)
        self.assertFalse(report["scientific_first_use"])
        self.assertFalse(report["source_generator_created"])
        self.assertEqual(report["sampled_experiment_rows"], 0)
        self.assertTrue(report["privileged_known_likelihood_oracle_only"])
        self.assertEqual(report["actual_r10_source_certificate"], "NOT_ESTABLISHED")
        self.assertEqual(report["ckb_controller_admission"], "NOT_OBSERVED")
        self.assertEqual(report["rare_latent_world"]["minimum_probes_for_error_le_5pct"], 147)


if __name__ == "__main__":
    unittest.main()
