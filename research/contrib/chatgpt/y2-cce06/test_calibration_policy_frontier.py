"""Fixture tests: on-policy cost frontier, no CAL/PRIMARY data or custody."""
import random
import unittest
from calibration_policy_frontier import PolicySpec, run_dev_frontier
from calibration_active_bayes import ActiveBayesianPolicy


def fixture(seed, n=45):
    rng = random.Random(seed)
    obs = [rng.randrange(2), rng.randrange(2)]
    rows = []
    for _ in range(n):
        a = rng.randrange(3)
        new = [obs[0] ^ int(a == 1 and rng.random() < .8),
               obs[1] ^ int(a == 2 and rng.random() < .8)]
        rows.append(dict(observation=obs[:], action=a, next_observation=new[:]))
        obs = new
    return tuple(rows)


class InteractiveFixture:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.obs = None
        self.received = []

    def reset(self):
        self.obs = [self.rng.randrange(2), self.rng.randrange(2)]
        return self.obs[:]

    def step(self, action):
        self.received.append(action)
        self.obs = [self.obs[0] ^ int(action == 1 and self.rng.random() < .8),
                    self.obs[1] ^ int(action == 2 and self.rng.random() < .8)]
        return self.obs[:]


class BadOracleEnv(InteractiveFixture):
    def step(self, action):
        return {'hidden_state': [1, 0, 1], 'next': [0, 1]}


class ActivePolicyFrontierFixtures(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997), fixture(998))
        self.terminal = (fixture(999, 35),)
        self.specs = (PolicySpec('active-low', probe_penalty=0.0),
                      PolicySpec('active-high', probe_penalty=0.4),
                      PolicySpec('no-action', kind='noop', probe_penalty=0),
                      PolicySpec('alternating', kind='alternating', probe_penalty=0))

    def run_small(self, **kw):
        return run_dev_frontier(self.train, self.terminal, InteractiveFixture,
                                specs=kw.pop('specs', self.specs),
                                budgets=kw.pop('budgets', (0, 2, 5)),
                                seeds=kw.pop('seeds', (1001, 1002)), steps=12, **kw)

    def test_exact_same_terminal_audit_for_all_policy_budget_pairs(self):
        out = self.run_small()
        self.assertEqual(out['status'], 'DEV_FIXTURE_ONLY_SCIENCE_UNVERIFIED')
        self.assertEqual(len(out['results']), 12)
        self.assertEqual(len({out['terminal_sha256']}), 1)
        self.assertFalse(out['custody_verified'])
        self.assertFalse(out['gain_verified'])
        self.assertEqual(out['terminal_events'], 35)
        self.assertTrue(all(0 <= r['mean_terminal_brier'] <= 1 for r in out['results']))

    def test_budget_enforcement_and_no_action_reference(self):
        out = self.run_small()
        for r in out['results']:
            self.assertLessEqual(r['mean_paid_actions'], r['budget'])
            if r['budget'] == 0 or r['kind'] == 'noop':
                self.assertEqual(r['mean_paid_actions'], 0)
            self.assertTrue(all(len(row['actions']) == 12 for row in r['per_seed']))

    def test_alternating_policy_actually_probes_and_follows_its_own_actions(self):
        out = self.run_small()
        alternating = [r for r in out['results'] if r['kind'] == 'alternating' and r['budget'] == 5][0]
        self.assertEqual(alternating['mean_paid_actions'], 5)
        self.assertEqual(alternating['per_seed'][0]['actions'][:5], (1, 2, 1, 2, 1))

    def test_environment_receives_exact_chosen_actions(self):
        seen = []
        def factory(seed):
            env = InteractiveFixture(seed)
            seen.append(env)
            return env
        out = run_dev_frontier(self.train, self.terminal, factory,
                               specs=(self.specs[0], self.specs[3]),
                               budgets=(2,), seeds=(1001,), steps=12)
        self.assertEqual(len(seen), 2)
        for env, row in zip(seen, out['results']):
            self.assertEqual(env.received, list(row['per_seed'][0]['actions']))
        self.assertEqual(out['results'][1]['mean_paid_actions'], 2)

    def test_deterministic_paired_seeds_and_public_receipts(self):
        self.assertEqual(self.run_small(), self.run_small())

    def test_train_equals_audit_rejected(self):
        with self.assertRaisesRegex(ValueError, 'IDENTICAL'):
            run_dev_frontier(self.train, self.train, InteractiveFixture,
                             specs=self.specs, budgets=(0,), seeds=(1001,), steps=5)

    def test_oracle_leak_from_environment_fails_closed(self):
        with self.assertRaises(ValueError):
            run_dev_frontier(self.train, self.terminal, BadOracleEnv,
                             specs=(self.specs[0],), budgets=(1,), seeds=(1001,), steps=5)

    def test_oracle_leak_from_training_and_audit_fails_closed(self):
        bad = list(self.train[0])
        bad[-1] = dict(bad[-1], oracle=1)
        with self.assertRaises(ValueError):
            run_dev_frontier((tuple(bad),), self.terminal, InteractiveFixture,
                             specs=self.specs, budgets=(1,), seeds=(1001,), steps=5)
        bad = list(self.terminal[0])
        bad[-1] = dict(bad[-1], latent=[0, 1])
        with self.assertRaises(ValueError):
            run_dev_frontier(self.train, (tuple(bad),), InteractiveFixture,
                             specs=self.specs, budgets=(1,), seeds=(1001,), steps=5)

    def test_invalid_budgets_seeds_and_names_rejected(self):
        for budgets, seeds, specs in (
            ((-1,), (1001,), self.specs), ((13,), (1001,), self.specs),
            ((0,), (1001, 1001), self.specs),
            ((0, 0), (1001,), self.specs),
            ((0,), (1001,), (self.specs[0], self.specs[0])),
        ):
            with self.subTest(budgets=budgets, seeds=seeds, specs=specs):
                with self.assertRaises(ValueError):
                    self.run_small(budgets=budgets, seeds=seeds, specs=specs)

    def test_pending_action_is_never_replayed(self):
        p = ActiveBayesianPolicy().fit(self.train)
        p.start([0, 0], paid_budget=2)
        action = p.choose()
        with self.assertRaises(ValueError):
            p.update(dict(observation=[0, 0], action=(action + 1) % 3,
                          next_observation=[0, 0]))


if __name__ == '__main__':
    unittest.main()
