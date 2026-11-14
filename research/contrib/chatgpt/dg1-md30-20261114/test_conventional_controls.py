"""Cross-platform bounded conventional RNN/RL preflight tests for MD30."""
import inspect
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bayesian_control import paid_training_episodes
from model_rl_control import EmpiricalModelBasedRL, state_key
from recurrent_control import RecurrentTrainer, RecurrentWorldControl, encode, prepare
from structural_catalog import synthetic_world


class ConventionalControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sessions, cls.receipt = paid_training_episodes()

    def test_common_physically_paid_training_and_disjoint_validation(self):
        self.assertEqual(self.receipt["charged_steps"], 1920)
        self.assertEqual(self.receipt["charged_episodes"], 240)
        self.assertEqual(len(self.sessions), 240)
        x, y = prepare(self.sessions)
        self.assertEqual(x.shape, (240, 8, 16))
        self.assertEqual(y.shape, (240, 8, 6))
        self.assertEqual(int(x.sum(axis=2).min()) >= 1, True)
        self.assertEqual(set(y.flatten().tolist()), {0.0, 1.0})

    def test_recurrent_trainable_dynamics_and_gradient(self):
        trainer = RecurrentTrainer()
        x, y = prepare(self.sessions)
        old = trainer.params["Wh"].copy()
        initial = trainer._loss(x[:16], y[:16])
        _ = trainer._train_batch(x[:16], y[:16])
        updated = trainer._loss(x[:16], y[:16])
        self.assertTrue(math.isfinite(updated))
        self.assertFalse((old == trainer.params["Wh"]).all())
        self.assertLess(updated, initial)

    def test_recurrent_fits_with_real_validation_holdout(self):
        trainer = RecurrentTrainer().fit(self.sessions)
        self.assertEqual(trainer.report["fit_episodes"], 192)
        self.assertEqual(trainer.report["validation_episodes"], 48)
        self.assertEqual(trainer.report["parameter_count"], 1766)
        self.assertTrue(math.isfinite(trainer.report["validation_bce"]))
        self.assertLess(trainer.report["validation_bce"], 0.70)
        self.assertGreaterEqual(trainer.report["epochs_executed"], 20)
        model = RecurrentWorldControl(trainer.params)
        world = synthetic_world(5301, "braided", rewire=True)
        before = world.observe()
        action = model.choose(before)
        self.assertIn(action["kind"], ("actuator", "diagnostic"))
        self.assertIn(action["node"], before["diagnostic_nodes"] if action["kind"] == "diagnostic" else (0, 1))
        with self.assertRaisesRegex(AssertionError, "UNCHARGED_UPDATE"):
            model.consume(before, action, {"charged_history": []})
        after, _, _ = world.step(action)
        model.consume(before, action, after)
        self.assertTrue(math.isfinite(float(model.h.sum())))
        self.assertEqual(trainer.checkpoint()["architecture"], [16, 32, 6])

    def test_empirical_rl_learns_only_paid_public_transitions(self):
        learner = EmpiricalModelBasedRL().fit(self.sessions)
        self.assertEqual(learner.fitted_steps, 1536)
        self.assertEqual(learner.metrics["fit_episodes"], 192)
        self.assertEqual(learner.metrics["validation_episodes"], 48)
        self.assertGreater(learner.metrics["fitted_local_state_action_cells"], 0)
        self.assertTrue(math.isfinite(learner.metrics["validation_categorical_logloss"]))
        p = learner.predict(0, (0, 0, 0, 0, 0, 0), 0)
        self.assertAlmostEqual(sum(prob for _, prob in p), 1.0, places=10)
        self.assertEqual(state_key((0, 0, 1, 0, 1, 0)), (1, 0, 1, 0))
        self.assertIn("local", learner.checkpoint())

    def test_both_controllers_use_public_actions_not_private_graph(self):
        for cls in (RecurrentWorldControl, EmpiricalModelBasedRL):
            code = inspect.getsource(cls)
            for forbidden in ("._graph", "._next_graph", "._roots", "fixture_graph(", "synthetic_pair("):
                self.assertNotIn(forbidden, code)
        learner = EmpiricalModelBasedRL().fit(self.sessions)
        world = synthetic_world(5302, "crossfork", rewire=True)
        count = 0
        while True:
            before = world.observe()
            if before["phase"] == "done":
                break
            action = learner.choose(before)
            self.assertIn(action["node"],
                          before["diagnostic_nodes"] if action["kind"] == "diagnostic" else (0, 1))
            after, _, done = world.step(action)
            self.assertEqual(after["charged_history"][-1]["action"], action)
            count += 1
            if done:
                break
        self.assertLessEqual(count, 8)
        self.assertLessEqual(sum(row["action"]["kind"] == "diagnostic" for row in world.receipt()["trace"]), 2)

    def test_fully_disallowed_official_scientific_seeds(self):
        for seed in (1080001, 2080001, 3080001, 4080001, 4080256):
            with self.assertRaisesRegex(AssertionError, "FIRST_USE_FORBIDDEN"):
                synthetic_world(seed, "doublecollider", rewire=True)


if __name__ == "__main__":
    unittest.main()
