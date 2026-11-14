"""MD30 toy-only tests: public-information Bayesian control, never official data."""
import json
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bayesian_control import (
    ALL_ACTIONS, COUNT, LOCK, TRAIN_SEEDS, TOY_TRANSFER,
    BayesianGraphControl, build_hypotheses, paid_training_episodes)
from structural_catalog import synthetic_world, synthetic_pair


class MD30BayesianControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hypotheses = build_hypotheses()

    def test_capacity_universal_graph_grammar_without_hidden_catalog(self):
        self.assertEqual(len(self.hypotheses), COUNT)
        self.assertEqual(len(set(self.hypotheses)), COUNT)
        self.assertEqual(ALL_ACTIONS[:2], ((0, 1), (1, 1)))
        for sig in self.hypotheses:
            self.assertEqual(len(sig), 8)
            self.assertEqual(len(sig[0]), 6)
            self.assertIn((sig[0][5], sig[1][5]), ((1, 0), (0, 1)))

    def test_own_seed_ranges_are_disjoint_and_frozen(self):
        self.assertEqual((TRAIN_SEEDS[0], TRAIN_SEEDS[-1]), (3301, 3540))
        self.assertEqual((TOY_TRANSFER[0], TOY_TRANSFER[-1]), (5301, 5360))
        self.assertFalse(set(TRAIN_SEEDS) & set(TOY_TRANSFER))
        self.assertEqual(LOCK["bayes_training"]["em_rounds"], 3)
        for seed in (1080001, 2080001, 3080001, 4080001):
            with self.assertRaisesRegex(AssertionError, "FIRST_USE_FORBIDDEN"):
                synthetic_pair(seed, "braided")

    def test_physical_training_actions_and_explicit_custody(self):
        sessions, custody = paid_training_episodes()
        self.assertEqual(len(sessions), 240)
        self.assertEqual(custody["charged_steps"], 1920)
        self.assertEqual(len(custody["physical_sha256"]), 64)
        for pair in sessions:
            self.assertEqual(len(pair), 2)
            for rows in pair:
                self.assertEqual(len(rows), 4)
                self.assertEqual([x["action"]["kind"] for x in rows],
                                 ["diagnostic"] * 3 + ["actuator"])
                self.assertEqual({x["action"]["node"] for x in rows[:3]},
                                 {2, 3, 4})

    def test_posterior_requires_real_paid_public_receipt(self):
        model = BayesianGraphControl(self.hypotheses)
        world = synthetic_world(5301, "braided", rewire=True)
        obs = world.observe()
        action = model.choose(obs)
        self.assertIn(action["kind"], ("diagnostic", "actuator"))
        if action["kind"] == "diagnostic":
            self.assertIn(action["node"], (2, 3, 4))
        with self.assertRaisesRegex(AssertionError, "REQUIRE_CHARGED_PUBLIC_RECEIPT"):
            model.posterior_step(action, {"sensor_vector": [0] * 6})
        observation, _, _ = world.step(action)
        model.posterior_step(action, observation["charged_history"][-1])
        self.assertAlmostEqual(math.fsum(model.weights), 1.0, places=10)
        self.assertEqual(model.phase, int(action["kind"] == "actuator"))
        self.assertEqual(model.probes, int(action["kind"] == "diagnostic"))

    def test_cold_checkpoint_schema_and_invalid_weight_detection(self):
        a = BayesianGraphControl(self.hypotheses)
        b = BayesianGraphControl(self.hypotheses)
        self.assertEqual(a.checkpoint(), b.checkpoint())
        with self.assertRaisesRegex(AssertionError, "UNNORMALIZED_POSTERIOR"):
            a.set_prior((0.0,) * COUNT)
        with self.assertRaises(AssertionError):
            BayesianGraphControl(self.hypotheses[:-1])


if __name__ == "__main__":
    unittest.main()
