"""WSP52 gradient-control engineering tests. SELFTEST only; no DEV/PRIMARY."""
import json
import math
import time
import unittest

from raw_temporal import (RawPhysicalRNN, WarmupThenDirect,
                          TrainedTemporalComparator, MAX_UPDATES,
                          PARAMETER_LIMIT)
from source import Observation, build_world
from fixture_harness import learn_observations, score_observations


class RawTemporalTests(unittest.TestCase):
    def setUp(self):
        self.world = build_world("SELFTEST", 9001, "identity")

    def test_true_analytic_gradient_matches_finite_difference(self):
        model = RawPhysicalRNN()
        row = self.world.phase_a[0]
        original_loss, deriv = model.loss_and_gradient(row)
        self.assertTrue(math.isfinite(original_loss))
        self.assertLess(model.parameter_count(), PARAMETER_LIMIT)
        self.assertEqual(model.parameter_count(), 632)
        for group, slot in (("bit", 0), ("recur", 7), ("init", 13), ("out", 8)):
            original = model.weights[group][slot]
            epsilon = 1e-6
            model.weights[group][slot] = original + epsilon
            positive = model.loss_and_gradient(row)[0]
            model.weights[group][slot] = original - epsilon
            negative = model.loss_and_gradient(row)[0]
            model.weights[group][slot] = original
            numeric = (positive - negative) / (2*epsilon)
            self.assertAlmostEqual(deriv[group][slot], numeric, places=6)

    def test_no_oracle_grammar_or_extra_environment_queries(self):
        w = self.world
        model = RawPhysicalRNN(seed="fixed-no-token-stream")
        initial = model.loss_and_gradient(w.phase_a[0])[0]
        model.train(w.phase_a, 64)
        self.assertEqual(model.updates, 64)
        self.assertGreater(model.parameter_count(), 0)
        self.assertNotEqual(initial, model.loss_and_gradient(w.phase_a[0])[0])
        for bad in (Observation((0,)*8,"01bad",(0,)*8),
                    Observation((0,)*8,"0"*15,(1,)*8,action_cost=0)):
            with self.assertRaises(ValueError):
                model.loss_and_gradient(bad)
        with self.assertRaises(ValueError):
            model.train(w.phase_a, MAX_UPDATES)

    def test_exact_64_then_grounded_writes_retention_and_restore(self):
        w = self.world
        arm = WarmupThenDirect()
        learn_observations(arm, w.phase_a)
        self.assertEqual(arm.actions, 36)
        self.assertIsNone(arm.predict(w.heldout_a[0].before,w.heldout_a[0].acoustic_bits))
        arm.seal_a()
        self.assertEqual(arm.gradient_steps,64)
        self.assertEqual(arm.writer.actions,36)
        self.assertGreater(arm.writer.numeric_weight_count(),0)
        phase_a = score_observations(arm,w.heldout_a)
        learn_observations(arm,w.phase_b)
        arm.finalize_b()
        phase_b = score_observations(arm,w.heldout_b)
        arm.use_phase("A")
        retained = score_observations(arm,w.heldout_a)
        self.assertEqual(arm.actions,42)
        self.assertEqual(arm.writer.actions,42)
        self.assertEqual(arm.gradient_steps,64)
        snap = arm.snapshot()
        clone = WarmupThenDirect.restore(snap)
        self.assertEqual(clone.snapshot(),snap)
        self.assertEqual(clone.capacity_bits(),arm.capacity_bits())
        for row in w.heldout_a[:10]:
            self.assertEqual(arm.predict(row.before,row.acoustic_bits),
                             clone.predict(row.before,row.acoustic_bits))
        with self.assertRaises(ValueError):
            WarmupThenDirect.restore(snap+" ")
        with self.assertRaises(ValueError):
            arm.observe(w.phase_b[0])
        print("WSP52_HYBRID_SELFTEST",json.dumps({"phase_a":phase_a.__dict__,
            "phase_b":phase_b.__dict__,"retained_a":retained.__dict__,
            "gradient_updates":arm.gradient_steps,"actions":arm.actions,
            "capacity_bits":arm.capacity_bits()},sort_keys=True),flush=True)

    def test_independently_trained_baseline_cold_restore_and_accounting(self):
        w = self.world
        arm = TrainedTemporalComparator()
        self.assertNotEqual(arm.model.seed,"warmup-64")
        t0=time.process_time()
        learn_observations(arm,w.phase_a)
        arm.seal_a()
        phase_a=score_observations(arm,w.heldout_a)
        learn_observations(arm,w.phase_b)
        arm.finalize_b()
        phase_b=score_observations(arm,w.heldout_b)
        arm.use_phase("A")
        retained=score_observations(arm,w.heldout_a)
        cpu_s=time.process_time()-t0
        self.assertEqual(arm.gradient_steps,arm.steps_a+arm.steps_b)
        self.assertGreater(arm.steps_a,0)
        self.assertGreater(arm.steps_b,0)
        self.assertLessEqual(arm.gradient_steps,20000)
        self.assertEqual(arm.actions,42)
        self.assertLessEqual(arm.model.parameter_count(),65536)
        snap=arm.snapshot()
        clone=TrainedTemporalComparator.restore(snap)
        self.assertEqual(clone.snapshot(),snap)
        for row in w.heldout_a[:10]:
            self.assertEqual(arm.predict(row.before,row.acoustic_bits),
                             clone.predict(row.before,row.acoustic_bits))
        with self.assertRaises(ValueError):
            TrainedTemporalComparator.restore(snap[:-1]+"x")
        print("WSP52_CONVENTIONAL_SELFTEST",json.dumps({"phase_a":phase_a.__dict__,
            "phase_b":phase_b.__dict__,"retained_a":retained.__dict__,
            "gradient_updates":arm.gradient_steps,"steps_a":arm.steps_a,
            "steps_b":arm.steps_b,"train_loss_a":arm.loss_a,
            "train_loss_b":arm.loss_b,"actions":arm.actions,
            "trainable_parameters":arm.model.parameter_count(),
            "capacity_bits":arm.capacity_bits(),"cpu_s":round(cpu_s,4)},sort_keys=True),flush=True)

if __name__ == "__main__":
    unittest.main()
