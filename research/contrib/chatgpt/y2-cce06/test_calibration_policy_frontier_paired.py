"""CCE06 local only: paired exogenous shocks and matched-target negative gates.

No CAL/PRIMARY seeds, evaluator imports, protected data or authority.
"""
import hashlib
import json
import random
import unittest

from calibration_policy_frontier import (
    PolicySpec, matched_target_report, run_dev_frontier)
from test_calibration_policy_frontier import InteractiveFixture, fixture


class PairedShockFixture:
    """Pre-draw all action-dependent shocks, independent of chosen actions."""
    def __init__(self, seed):
        self.seed = seed
        rng = random.Random(seed)
        self.first = [rng.randrange(2), rng.randrange(2)]
        self.shocks = tuple((rng.random(), rng.random()) for _ in range(40))
        self.paired_noise_digest = hashlib.sha256(json.dumps(
            (self.first, self.shocks), separators=(',', ':')).encode()).hexdigest()
        self.obs = None
        self.cursor = 0
        self.actions = []

    def reset(self):
        self.obs = self.first[:]
        self.cursor = 0
        return self.obs[:]

    def step(self, action):
        s0, s1 = self.shocks[self.cursor]
        self.cursor += 1
        self.actions.append(action)
        self.obs = [self.obs[0] ^ int(action == 1 and s0 < .8),
                    self.obs[1] ^ int(action == 2 and s1 < .8)]
        return self.obs[:]


class ChangingReceiptFixture(PairedShockFixture):
    def step(self, action):
        result = super().step(action)
        self.paired_noise_digest = 'f' * 64
        return result


class PairedShockContracts(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997, 45), fixture(998, 45))
        self.terminal = (fixture(999, 35),)
        self.specs = (PolicySpec('bayes', probe_penalty=0),
                      PolicySpec('no-action', kind='noop', probe_penalty=0),
                      PolicySpec('alternating', kind='alternating', probe_penalty=0))

    def run_fixture(self, factory=PairedShockFixture, **kw):
        return run_dev_frontier(self.train, self.terminal, factory,
                                specs=kw.pop('specs', self.specs),
                                budgets=kw.pop('budgets', (0, 3, 5)),
                                seeds=kw.pop('seeds', (1001, 1002)),
                                steps=12, paired_noise_required=True, **kw)

    def test_equal_seed_proves_equal_exogenous_tape_at_evaluator(self):
        a, b = PairedShockFixture(1001), PairedShockFixture(1001)
        self.assertEqual(a.paired_noise_digest, b.paired_noise_digest)
        self.assertNotEqual(a.paired_noise_digest,
                            PairedShockFixture(1002).paired_noise_digest)
        self.assertEqual(a.reset(), b.reset())
        for x, y in ((0, 2), (2, 1), (1, 0), (1, 2)):
            a.step(x)
            b.step(y)
        self.assertEqual(a.paired_noise_digest, b.paired_noise_digest)
        self.assertNotEqual(a.actions, b.actions)

    def test_on_policy_paired_receipts_and_budgets(self):
        result = self.run_fixture()
        self.assertTrue(result['paired_noise_receipts_matched'])
        self.assertFalse(result['paired_noise_custody_verified'])
        self.assertFalse(result['custody_verified'])
        self.assertFalse(result['gain_verified'])
        self.assertEqual(len(result['results']), 9)
        for r in result['results']:
            self.assertLessEqual(r['mean_paid_actions'], r['budget'])
            for row in r['per_seed']:
                self.assertEqual(row['paired_noise_digest'],
                                 PairedShockFixture(row['seed']).paired_noise_digest)
        self.assertEqual(result, self.run_fixture())

    def test_reject_missing_tape_receipt_even_when_seeds_match(self):
        with self.assertRaisesRegex(ValueError, 'PAIRED_NOISE_RECEIPT_REQUIRED'):
            self.run_fixture(InteractiveFixture)

    def test_reject_mutated_tape_receipt_mid_episode(self):
        with self.assertRaisesRegex(ValueError, 'NOISE_RECEIPT_CHANGED'):
            self.run_fixture(ChangingReceiptFixture)

    def test_reject_different_tape_digest_for_same_seed(self):
        calls = [0]
        def inconsistent_factory(seed):
            calls[0] += 1
            return PairedShockFixture(seed + calls[0])
        with self.assertRaisesRegex(ValueError, 'UNPAIRED_EXOGENOUS_NOISE'):
            self.run_fixture(inconsistent_factory)

    def test_reject_shared_tape_across_different_seeds(self):
        with self.assertRaisesRegex(ValueError, 'NONINDEPENDENT_NOISE_SEEDS'):
            self.run_fixture(lambda seed: PairedShockFixture(1001))

    def test_fixed_target_reports_no_feasible_policy(self):
        result = self.run_fixture()
        match = matched_target_report(result, target_brier=0,
                                      reference_policy='bayes')
        self.assertEqual(match['status'], 'REFERENCE_TARGET_INFEASIBLE')
        self.assertFalse(match['scientific_gain_verified'])
        self.assertEqual(match['feasible_costs'], {})

    def test_zero_cost_reference_cannot_claim_percent_savings(self):
        result = self.run_fixture()
        match = matched_target_report(result, target_brier=1,
                                      reference_policy='no-action')
        self.assertEqual(match['status'], 'ZERO_COST_REFERENCE_NO_SAVING_CLAIM')
        self.assertTrue(all(v is None for v in
                            match['fractional_probe_savings'].values()))

    def test_explicit_matched_accuracy_vs_cost_arithmetic(self):
        # Hand-constructed DEV receipt checks only the arithmetic, not science.
        frontier = {'status': 'DEV_FIXTURE_ONLY_SCIENCE_UNVERIFIED',
                    'results': (
                        dict(policy='reference', budget=5, mean_paid_actions=5,
                             mean_terminal_brier=.10,
                             per_seed=({'terminal_brier':.10}, {'terminal_brier':.10})),
                        dict(policy='candidate', budget=4, mean_paid_actions=4,
                             mean_terminal_brier=.11,
                             per_seed=({'terminal_brier':.11}, {'terminal_brier':.11})),
                        dict(policy='deceptive-average', budget=2, mean_paid_actions=2,
                             mean_terminal_brier=.10,
                             per_seed=({'terminal_brier':.05}, {'terminal_brier':.15}))) }
        report = matched_target_report(frontier, target_brier=.12,
                                       reference_policy='reference')
        self.assertEqual(report['status'], 'DESCRIPTIVE_MATCHED_TARGET_ONLY')
        self.assertAlmostEqual(report['fractional_probe_savings']['candidate'], .2)
        self.assertNotIn('deceptive-average', report['feasible_costs'])
        self.assertFalse(report['scientific_gain_verified'])
        loose = matched_target_report(frontier, target_brier=.12,
                                     reference_policy='reference',
                                     require_each_seed=False)
        self.assertIn('deceptive-average', loose['feasible_costs'])

    def test_bad_targets_or_unknown_reference_rejected(self):
        result = self.run_fixture()
        for goal in (-.1, 1.1, float('nan'), '0.1'):
            with self.subTest(goal=goal):
                with self.assertRaises(ValueError):
                    matched_target_report(result, target_brier=goal,
                                          reference_policy='bayes')
        with self.assertRaises(ValueError):
            matched_target_report(result, target_brier=.12,
                                  reference_policy='not-in-study')


if __name__ == '__main__':
    unittest.main()
