"""PSR engineering only: synthetic public fixtures, no CAL or PRIMARY seeds."""
import math
import random
import unittest
from calibration_psr import LearnedOperatorPSR, score_streaming_psr
from calibration_controls import validated


def fixture(seed, n=180):
    rng = random.Random(seed)
    observation = [rng.randrange(2), rng.randrange(2)]
    data = []
    for _ in range(n):
        action = rng.randrange(3)
        following = [observation[0] ^ int(action == 1 and rng.random() < .8),
                     observation[1] ^ int(action == 2 and rng.random() < .8)]
        data.append({'observation': observation[:], 'action': action,
                     'next_observation': following[:]})
        observation = following
    return tuple(data)


class OperatorControlFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = (fixture(997), fixture(998))
        cls.model = LearnedOperatorPSR(tests=6, depth=2).fit(cls.train)

    def test_trained_public_state_and_all_operators(self):
        m = self.model
        self.assertEqual(m.dim, 7)
        self.assertEqual(len(m.operators), 12)
        self.assertEqual(m.events, 360)
        self.assertEqual(sum(m.witnesses.values()), 360)
        self.assertEqual(len(m.new_state()), m.dim)
        self.assertTrue(all(len(row) == m.dim for op in m.operators.values() for row in op))
        self.assertFalse(hasattr(m, 'hidden_world_truth'))
        self.assertFalse(hasattr(m, 'counts'))

    def test_recurrent_update_and_probability_simplex(self):
        m = self.model
        s = m.new_state()
        for e in fixture(999, 35):
            p = m.forecast(s, e['action'])
            self.assertAlmostEqual(sum(p), 1)
            self.assertTrue(all(0 < x <= 1 and math.isfinite(x) for x in p))
            s = m.advance(s, e['action'], e['next_observation'])
            self.assertEqual(s[0], 1.0)
            self.assertTrue(all(0 <= x <= 1 for x in s))

    def test_streaming_equals_replay_prequential(self):
        m = self.model
        data = fixture(1001, 25)
        stream = score_streaming_psr(m, (data,))
        from calibration_controls import multichannel_brier
        replay = sum(multichannel_brier(m.predict(data[:t], e['action']),
                              e['next_observation']) for t,e in enumerate(data)) / len(data)
        self.assertAlmostEqual(stream, replay, places=13)

    def test_deterministic_training_and_operator_ablation(self):
        m = self.model
        same = LearnedOperatorPSR(tests=6, depth=2).fit(self.train)
        self.assertEqual(m.operators, same.operators)
        self.assertEqual(m.new_state(), same.new_state())
        # The forecast is computed from FITTED transition operators, not from
        # a prefix-table proxy retained at inference.
        changed = LearnedOperatorPSR(tests=6, depth=2).fit(self.train)
        changed.operators[1, 0] = tuple(tuple(0.0 for _ in row)
                                          for row in changed.operators[1, 0])
        self.assertNotEqual(m.forecast(m.new_state(), 1),
                            changed.forecast(changed.new_state(), 1))

    def test_reject_hidden_oracle_fields_and_invalid_actions(self):
        data = list(fixture(997))
        data[0] = dict(data[0], hidden_state=[1,0,1])
        with self.assertRaises(ValueError):
            LearnedOperatorPSR().fit((tuple(data),))
        with self.assertRaises(ValueError):
            self.model.forecast(self.model.new_state(), 99)
        with self.assertRaises(ValueError):
            self.model.advance(self.model.new_state(), 1, [2,0])

    def test_capacity_and_insufficient_training_fails_closed(self):
        with self.assertRaises(ValueError):
            LearnedOperatorPSR(tests=5)
        with self.assertRaises(ValueError):
            LearnedOperatorPSR(ridge=-1)
        with self.assertRaises(ValueError):
            LearnedOperatorPSR(tests=12).fit((fixture(1003, 7),))

    def test_frozen_public_only_holdout_scoring(self):
        data = fixture(999, 50)
        validated(data)
        score = score_streaming_psr(self.model, (data,))
        self.assertTrue(math.isfinite(score) and 0 <= score <= 1)
        bad = list(data)
        bad[-1] = dict(bad[-1], oracle_reward=1)
        with self.assertRaises(ValueError):
            score_streaming_psr(self.model, (tuple(bad),))


if __name__ == '__main__':
    unittest.main()
