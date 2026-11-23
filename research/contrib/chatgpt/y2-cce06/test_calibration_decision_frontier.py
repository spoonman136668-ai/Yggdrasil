"""Decision-focused Bayesian policy in the paired DEV frontier; no science gate."""
import unittest

from calibration_decision_bayes import DecisionFocusedBayesianPolicy
from calibration_policy_frontier import (
    PolicySpec, matched_target_report, run_dev_frontier)
from test_calibration_policy_frontier_paired import (
    PairedShockFixture, fixture)


class DecisionPolicyFrontierFixtures(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997, 45), fixture(998, 45))
        self.terminal = (fixture(999, 35),)
        self.specs = (
            PolicySpec('information-gain', kind='active', probe_penalty=0),
            PolicySpec('decision-focused', kind='decision', probe_penalty=0),
            PolicySpec('no-action', kind='noop', probe_penalty=0),
        )

    def run_frontier(self):
        return run_dev_frontier(
            self.train, self.terminal, PairedShockFixture,
            specs=self.specs, budgets=(0, 3, 5),
            seeds=(1001, 1002), steps=12,
            paired_noise_required=True)

    def test_decision_policy_runs_with_paired_noise_and_same_audit(self):
        result = self.run_frontier()
        self.assertEqual(len(result['results']), 9)
        self.assertTrue(result['paired_noise_receipts_matched'])
        self.assertFalse(result['custody_verified'])
        self.assertFalse(result['gain_verified'])
        for seed in result['seeds']:
            digests = {
                row['paired_noise_digest']
                for item in result['results']
                for row in item['per_seed'] if row['seed'] == seed
            }
            self.assertEqual(len(digests), 1)

    def test_decision_policy_obeys_budget_and_replays_deterministically(self):
        a, b = self.run_frontier(), self.run_frontier()
        self.assertEqual(a, b)
        for row in a['results']:
            self.assertLessEqual(row['mean_paid_actions'], row['budget'])
            self.assertTrue(all(len(x['actions']) == 12 for x in row['per_seed']))

    def test_zero_budget_decision_policy_falls_back_to_free_action(self):
        result = run_dev_frontier(
            self.train, self.terminal, PairedShockFixture,
            specs=(self.specs[1],), budgets=(0,), seeds=(1001,),
            steps=12, paired_noise_required=True)
        self.assertEqual(result['results'][0]['mean_paid_actions'], 0)
        self.assertTrue(all(a == 0 for a in result['results'][0]['per_seed'][0]['actions']))

    def test_fixed_target_report_includes_decision_policy_without_science_claim(self):
        result = self.run_frontier()
        report = matched_target_report(
            result, target_brier=1, reference_policy='no-action')
        self.assertEqual(report['status'], 'ZERO_COST_REFERENCE_NO_SAVING_CLAIM')
        self.assertFalse(report['scientific_gain_verified'])

    def test_policy_kind_is_not_accepted_as_an_untyped_shortcut(self):
        with self.assertRaises(ValueError):
            run_dev_frontier(
                self.train, self.terminal, PairedShockFixture,
                specs=(PolicySpec('bad', kind='oracle'),), budgets=(0,),
                seeds=(1001,), steps=12, paired_noise_required=True)


if __name__ == '__main__':
    unittest.main()
