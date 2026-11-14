"""Mechanical tests for AAI-03A only, not scientific acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aai03a", HERE / "run.py")
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


class AAI03A(unittest.TestCase):
    def test_exhaustive_identifiability(self):
        self.assertTrue(a.audit())

    def test_noise_support_normalization(self):
        for expected in range(8):
            total = sum(a.likelihood(y, expected) for y in range(8))
            self.assertAlmostEqual(total, 1.0)
            self.assertEqual(a.likelihood(expected, expected), .8)

    def test_source_leakage_cues(self):
        w = a.world(72000)
        other = dict(w, law=(w["law"] + 1) % 8)
        for i in range(a.DISTRACTORS):
            self.assertEqual(a.passive_event(w, i), a.passive_event(other, i))
        self.assertEqual(w["terminal_state"], other["terminal_state"])
        self.assertEqual(w["target"], other["target"])

    def test_matched_online_memory(self):
        w = a.world(72000)
        mem = []
        for i in range(a.PROBES):
            a.retain(mem, a.observe(w, i % 8, i % 4, i), "utility")
        for i in range(a.DISTRACTORS):
            a.retain(mem, a.passive_event(w, i), "utility")
        self.assertEqual(len(mem), 8)
        self.assertEqual(sum(e["kind"] == "do" for e in mem), 4)
        self.assertFalse(any("law" in e for e in mem))

    def test_exact_bayes_conditionals(self):
        w = a.world(72001)
        belief = [1 / 8] * 8
        state, action = a.choose_query(belief, w, "utility", 0)
        self.assertIn(state, range(8))
        self.assertIn(action, range(4))
        updated, mass = a.posterior_if(belief, w, state, action,
                                       a.observe(w, state, action, 0)["observed"])
        self.assertGreater(mass, 0)
        self.assertAlmostEqual(sum(updated), 1.0)

    def test_conventional_trained_restore(self):
        training = [a.world(s) for s in list(a.TRAIN)[:32]]
        model = a.train_table(training)
        self.assertEqual(len(model), 8)
        self.assertEqual(json.loads(json.dumps(model)), model)

    def test_frozen_budget_and_no_model_change(self):
        self.assertEqual(a.PROBES, 4)
        self.assertEqual(a.CAPACITY, 8)
        self.assertEqual(a.DISTRACTORS, 32)
        self.assertEqual(a.PREREG, "7f5b8b7150446a7b54a9fd9bc962cd584b2c92a6")
        w = a.world(72000)
        self.assertLessEqual(a.run_arm(w, "utility")["retained_do"], 8)
