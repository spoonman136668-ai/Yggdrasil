"""CCE05 engineering fixtures, NOT primary experiment seed/split."""
import hashlib
import json
import random
import unittest
from cce05 import PredictiveEcology, FullSuffixTable, EPISODES, HORIZON
from run_cce05 import dataset, FittedActionHMM, SEEDS


def fixture(action_influence=True):
    rng = random.Random(99431)
    for _ in range(EPISODES):
        actions = tuple(rng.randrange(3) for _ in range(HORIZON))
        obs = [rng.randrange(2)]
        for t, a in enumerate(actions):
            # Fully public deterministic history process; no latent labels.
            next_obs = (a == 2 and t > 0 and actions[t - 1] == 1) if action_influence else 0
            obs.append(int(next_obs))
        yield tuple(obs), actions


class CCE05Unit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = PredictiveEcology()
        cls.full = FullSuffixTable(3)
        for obs, actions in fixture():
            cls.model.observe_episode(obs, actions)
            cls.full.observe_episode(obs, actions)
        cls.model.freeze()

    def test_dynamic_growth_bounded(self):
        self.assertLessEqual(len(self.model.selected), 3*64)
        self.assertGreater(len(self.model.selected), 0)
        self.assertEqual(EPISODES*HORIZON, self.model.events)

    def test_correct_conditional_direction(self):
        hobs = (0, 0, 0)
        hist = (0, 1)
        p2 = self.model.predict(hobs, hist, 2)
        p0 = self.model.predict(hobs, hist, 0)
        self.assertGreater(p2, p0)

    def test_full_history_baseline_independent(self):
        self.assertGreater(len(self.full.counts), len(self.model.counts))
        self.assertTrue(0 <= self.full.predict((0,0), (1,), 2) <= 1)

    def test_exact_cold_prediction_recovery(self):
        restored = PredictiveEcology.restore(self.model.snapshot())
        self.assertEqual(restored.snapshot(), self.model.snapshot())
        for a in range(3):
            for b in range(3):
                self.assertEqual(self.model.predict((0,1), (a,), b),
                                 restored.predict((0,1), (a,), b))

    def test_corruption_rejected(self):
        damaged = bytearray(self.model.snapshot())
        damaged[-1] ^= 1
        with self.assertRaises(ValueError):
            PredictiveEcology.restore(bytes(damaged))

    def test_semantic_forgery_inconsistent_totals_rejected(self):
        state = json.loads(self.model.snapshot().split(b'.',2)[2])
        for e in state['entries']:
            if e[1] == []:
                e[2] += 1
                break
        raw = json.dumps(state, sort_keys=True, separators=(',',':')).encode('ascii')
        forged = b'CCE05.' + hashlib.sha256(raw).hexdigest().encode('ascii') + b'.'+raw
        with self.assertRaises(ValueError):
            PredictiveEcology.restore(forged)

    def test_malformed_public_event_rejected(self):
        bad = PredictiveEcology()
        for obs, acts in [((0,1),(0,)), ((0,)*25,(0,)*23), ((0,)*25,(True,)*24), ((0,)*25,(3,)*24)]:
            with self.assertRaises(ValueError):
                bad.observe_episode(obs, acts)
        self.assertEqual(bad.events, 0)

    def test_disjoint_action_sequences_and_public_only_control(self):
        train = dataset(997, True, False)
        evals = dataset(997, True, True)
        self.assertEqual(0, sum(tuple(a[i:i+3]) == (2,1,2)
                                for _, a in train for i in range(len(a)-2)))
        self.assertTrue(all(a[7:10] == (2,1,2) for _, a in evals))
        self.assertNotIn(997, SEEDS)

    def test_fitted_four_state_hmm_uses_public_histories(self):
        train = dataset(997, True, False)
        model, ll = FittedActionHMM.fit(train)
        self.assertLess(ll, 0.0)
        self.assertTrue(all(abs(sum(row)-1) < 1e-10
                            for matrix in model.transitions for row in matrix))
        self.assertTrue(all(0 < e < 1 for e in model.emit))
        p = model.predict((0,1), (2,), 1)
        self.assertTrue(0 < p < 1)
        self.assertFalse(hasattr(model, 'hidden_world_truth'))

    def test_one_shot_frozen_no_additional_learning(self):
        with self.assertRaises(ValueError):
            self.model.observe_episode(*next(fixture()))
        with self.assertRaises(ValueError):
            self.model.freeze()
        with self.assertRaises(ValueError):
            self.model.predict((0,1), (0,), 5)


if __name__ == '__main__':
    unittest.main()
