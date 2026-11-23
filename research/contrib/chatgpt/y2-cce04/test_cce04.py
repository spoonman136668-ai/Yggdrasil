"""CCE04 engineering-only fixtures. Do not use frozen primary trial seeds."""
import hashlib
import json
import random
import unittest
from cce04 import (CausalBeliefEcology, check_history, filter_history,
                   predict_future, templates, TRAIN_EPISODES, TRAIN_ACTIONS)


def synthetic_fixture():
    episodes = []
    for k in range(TRAIN_EPISODES):
        state = (k & 1)
        obs = [state]
        actions = []
        for t in range(TRAIN_ACTIONS):
            a = (t + (k % 3)) % 2
            state ^= a
            actions.append(a)
            obs.append(state)
        episodes.append((tuple(obs), tuple(actions)))
    return tuple(episodes)


class CCE04Tests(unittest.TestCase):
    def test_budgeted_candidate_and_stronger_comparator(self):
        self.assertEqual(36, len(templates(coarse=True)))
        self.assertEqual(432, len(templates(coarse=False)))
        self.assertEqual(108, len(templates(coarse=False, no_action=True)))

    def test_observed_only_data_contract(self):
        for obs, acts in [((True, 0), (1,)), ((1, 0), (2,)),
                          ((0, 0), ()), ((0,), (0,))]:
            with self.assertRaises(ValueError):
                check_history(obs, acts)
        check_history((0, 1, 0), (1, 1))

    def test_prior_and_intervention_have_consequences(self):
        h0 = (0,), ()
        hold = predict_future(*h0, (0,), ((0, 1), 0.2, 0.1))[0]
        toggle = predict_future(*h0, (1,), ((0, 1), 0.2, 0.1))[0]
        self.assertLess(hold, 0.5)
        self.assertGreater(toggle, 0.5)
        self.assertEqual((0.5, 0.5), predict_future((0,), (), (0, 1), None))

    def test_positive_fixture_selects_causal_action_role(self):
        learner = CausalBeliefEcology()
        learner.fit(synthetic_fixture())
        self.assertIsNotNone(learner.selected)
        self.assertEqual((0, 1), learner.selected[0])
        forecast = learner.predict((0, 0), (0,), (1, 1, 1))
        self.assertEqual(3, len(forecast))
        self.assertTrue(all(0 < p < 1 for p in forecast))

    def test_checkpoint_exact_cold_predictions(self):
        learner = CausalBeliefEcology()
        learner.fit(synthetic_fixture())
        packed = learner.snapshot()
        cold = CausalBeliefEcology.restore(packed)
        self.assertEqual(learner.selected, cold.selected)
        self.assertEqual(packed, cold.snapshot())
        for o in (0, 1):
            for a in (0, 1):
                self.assertEqual(learner.predict((o, o ^ a), (a,), (1, 1)),
                                 cold.predict((o, o ^ a), (a,), (1, 1)))

    def test_rejects_hash_tamper_and_forged_evidence(self):
        learner = CausalBeliefEcology()
        learner.fit(synthetic_fixture())
        original = learner.snapshot()
        tampered = bytearray(original)
        tampered[-1] ^= 1
        with self.assertRaises(ValueError):
            CausalBeliefEcology.restore(bytes(tampered))
        state = json.loads(original.split(b".", 2)[2])
        state["score"] += 1.0
        body = json.dumps(state, separators=(",", ":"), sort_keys=True).encode()
        forged = b"CCE04." + hashlib.sha256(body).hexdigest().encode() + b"." + body
        with self.assertRaises(ValueError):
            CausalBeliefEcology.restore(forged)

    def test_exact_train_budget_and_freeze(self):
        learner = CausalBeliefEcology()
        with self.assertRaises(ValueError):
            learner.fit(synthetic_fixture()[:-1])
        learner.fit(synthetic_fixture())
        with self.assertRaises(ValueError):
            learner.fit(synthetic_fixture())
        other = CausalBeliefEcology()
        with self.assertRaises(ValueError):
            other.predict((0,), (), (1,))

    def test_no_hidden_state_attribute_and_emission_condition(self):
        learner = CausalBeliefEcology()
        self.assertFalse(hasattr(learner, "hidden_state"))
        posterior, score = filter_history((1, 0), (1,), ((0, 1), 0.2, 0.1))
        self.assertGreater(posterior, 0)
        self.assertLess(posterior, 1)
        self.assertLess(score, 0)


if __name__ == "__main__":
    unittest.main()
