"""No-import exact-rational CVH03 static source-law audit tests."""
from fractions import Fraction as F
import ast
from pathlib import Path
import unittest
import source_law as law


class SourceLawAudit(unittest.TestCase):
    def test_exact_source_identity(self):
        self.assertEqual(law.SOURCE_GIT_BLOB, "6264ec5450754c009e98c3e85f6d5927ece0a9ab")
        self.assertEqual(law.SOURCE_SHA, "c94e9a4cd3641588b6b8507e71ccee5c27032bdf")

    def test_eight_exogenous_outcomes_exact_joint_probability(self):
        rows = list(law.exogenous_outcomes())
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(p for _, p in rows), 1)
        self.assertTrue(all(p > 0 for _, p in rows))

    def test_binary_reward_ceiling(self):
        for s in (0, 1):
            self.assertEqual(law.reward_expectation(s, s), F(41, 50))
            self.assertEqual(law.reward_expectation(s, 1-s), F(9, 50))
            self.assertEqual(law.reward_expectation(s, s) - law.reward_expectation(s, 1-s), F(16, 25))

    def test_original_state_transition_conditional_probabilities(self):
        self.assertEqual(law.next_state_one_probability(0, 0), F(41, 50))
        for s, a in ((0, 1), (1, 0), (1, 1)):
            self.assertEqual(law.next_state_one_probability(s, a), F(9, 50))

    def test_full_joint_distribution_all_state_actions(self):
        for s in (0, 1):
            for a in (0, 1):
                kernel = law.joint_kernel(s, a)
                self.assertEqual(len(kernel), 4)
                self.assertEqual(sum(kernel.values()), 1)
                self.assertTrue(all(x >= 0 for x in kernel.values()))

    def test_bellman_independent_optimality_every_horizon(self):
        for horizon, details, values in law.independent_bellman(31):
            self.assertEqual(values[0], horizon * F(41, 50))
            self.assertEqual(values[1], horizon * F(41, 50))
            for s in (0, 1):
                self.assertEqual(details[s]["optimal_action"], s)
                self.assertEqual(details[s]["q_match"] - details[s]["q_opposite"], F(16, 25))

    def test_episode_truncation_off_by_one(self):
        self.assertEqual(law.MAX_STEP, 30)
        self.assertEqual(law.ACTUAL_HORIZON, 31)
        self.assertEqual(law.analytic_result()["optimal_full_episode_mean"], F(1271, 50))

    def test_negative_drift_in_original_exogenous_law(self):
        # Changing source probabilities MUST invalidate the original 0.82 result.
        drift = (F(1, 2), F(1, 10), F(1, 10))
        self.assertNotEqual(law.reward_expectation(0, 0, probs=drift), F(41, 50))
        self.assertEqual(law.reward_expectation(0, 0, probs=drift), F(1, 2))

    def test_invalid_inputs_fail_closed(self):
        for bad in (True, 2, -1, 1.0, None):
            with self.assertRaises(ValueError): law.source_law(bad, 0, 1, 0, 1)
        with self.assertRaises(ValueError): law.joint_kernel(0, True)
        with self.assertRaises(ValueError): list(law.exogenous_outcomes(F(11, 10), F(1,10), F(1,10)))
        with self.assertRaises(ValueError): law.independent_bellman(32)

    def test_no_original_source_calls_or_imports(self):
        tree = ast.parse(Path(law.__file__).read_text())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.extend(x.name for x in node.names)
            if isinstance(node, ast.ImportFrom): imports.append(node.module)
        self.assertNotIn("causal_gym", imports)
        self.assertNotIn("numpy", imports)
        self.assertNotIn("gymnasium", imports)
        self.assertEqual(law.analytic_result()["actual_source_actions"], 0)


if __name__ == "__main__": unittest.main()
