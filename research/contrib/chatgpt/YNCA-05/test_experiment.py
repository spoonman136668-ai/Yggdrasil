"""YNCA-05 focused, source-free exact-enumeration tests."""
import unittest
import experiment as m


class IdentifiabilityCeilingTests(unittest.TestCase):
    def test_all_256_boolean_tables_and_conditioned_64(self):
        self.assertEqual(1 << (1 << 3), 256)
        self.assertEqual(len(m.LAWS), 64)
        self.assertEqual(len(set(m.LAWS)), 64)
        self.assertTrue(all(f[0] == 0 and f[7] == 1 for f in m.LAWS))

    def test_each_offdiagonal_bit_independent(self):
        for action in m.OFF_DIAGONAL:
            ones = sum(f[action] for f in m.LAWS)
            self.assertEqual(ones, 32)

    def test_two_distinct_noiseless_probes_leave_16(self):
        result = m.identifiability()
        self.assertEqual(result["0"]["max_compatible_class"], 64)
        self.assertEqual(result["2"]["min_compatible_class"], 16)
        self.assertEqual(result["2"]["max_compatible_class"], 16)
        self.assertEqual(result["6"]["max_compatible_class"], 1)

    def test_posterior_branches_probability(self):
        prior = m.unit_prior()
        branches = m.posterior_branches(prior, 3)
        self.assertEqual(len(branches), 4)
        self.assertAlmostEqual(sum(p for p, _ in branches), 1)
        for _, after in branches:
            self.assertAlmostEqual(sum(after), 1)

    def test_intervention_outside_terminal_pair_has_no_value(self):
        w = m.unit_prior()
        for action in (3, 4, 5, 6):
            self.assertAlmostEqual(m.expected_after(w, (1, 2), action),
                                   m.utility(w, (1, 2)), places=12)
            self.assertGreater(m.probe_cost(action), 0)

    def test_independent_terminal_pair_value_nonnegative_before_cost(self):
        w = m.unit_prior()
        for a in (1, 2):
            self.assertGreaterEqual(
                m.expected_after(w, (1, 2), a) - m.utility(w, (1, 2)), -1e-12)

    def test_cost_accounting(self):
        self.assertAlmostEqual(m.probe_cost(0), 0.018)
        self.assertAlmostEqual(m.probe_cost(7), 0.054)
        self.assertAlmostEqual(m.terminal_cost(7), 0.24)

    def test_expected_independent_law_value(self):
        w = m.unit_prior()
        self.assertAlmostEqual(m.truth_oracle_utility(w, (1, 2)), 0.67)
        self.assertAlmostEqual(m.utility(w, (1, 2)), 0.42)

    def test_exact_decision_oracle_dominates(self):
        d=m.means()
        q=d["mean_total_regret_and_charged_probe_cost"]
        for method,score in q.items():
            self.assertLessEqual(q["bayes_value"], score + 1e-12, method)


if __name__=="__main__":
    unittest.main()
