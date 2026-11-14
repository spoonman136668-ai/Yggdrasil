"""WSP88 public fixture and negative controls; no reserved DEV cohort consumption."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from world import make_world, OLD, NEW
from weights import DirectWeights, LiteralLookup, features, WIDTH
from experiment import classify, single_world, FIXTURE_SEEDS, RESERVED_DEV_SEEDS


class GroundingStructuralTests(unittest.TestCase):
    def test_isolated_cohorts_and_paid_action_source(self):
        self.assertTrue(set(FIXTURE_SEEDS).isdisjoint(RESERVED_DEV_SEEDS))
        w = make_world(FIXTURE_SEEDS[0])
        self.assertEqual((len(w.train_a), len(w.train_b), len(w.eval_a), len(w.eval_b)),
                         (108, 9, 108, 36))
        self.assertTrue(set(w.train_a).isdisjoint(w.eval_a))
        self.assertTrue(set(w.train_b).isdisjoint(w.eval_b))
        self.assertTrue(set(w.train_a).isdisjoint(w.train_b))
        self.assertEqual(len(OLD), 3)
        self.assertEqual(len(NEW), 3)
        for utterance in w.train_a + w.train_b:
            self.assertEqual(sum(w.probe(utterance, i) for i in range(3)), 1)
        with self.assertRaises(ValueError):
            w.probe(w.eval_a[0], 0)

    def test_raw_character_feature_invariants(self):
        self.assertEqual(features("Please RAISE the gate."),
                         features("please raise the gate."))
        self.assertNotEqual(features("Please raise the gate."),
                            features("Please lower the gate."))
        self.assertTrue(all(0 <= idx < WIDTH for idx, _ in features("hello")))
        with self.assertRaises(ValueError):
            features("")

    def test_intervention_edit_and_negative_control(self):
        model = DirectWeights()
        lookup = LiteralLookup()
        phrase = "Please hoist the panel."
        self.assertIsNone(model.predict(phrase))
        for action in range(3):
            success = action == 1
            model.observe(phrase, action, success)
            lookup.observe(phrase, action, success)
        self.assertEqual(model.scores(phrase).index(max(model.scores(phrase))), 1)
        self.assertEqual(lookup.predict(phrase), 1)
        self.assertIsNone(lookup.predict("Kindly hoist this panel for me."))

    def test_cold_snapshot_and_corruption_rejected(self):
        model = DirectWeights()
        for a in range(3):
            model.observe("Kindly lower the gate.", a, a == 2)
        snap = model.snapshot()
        restored = DirectWeights.restore(snap)
        self.assertEqual(model.weights, restored.weights)
        bad = json.loads(snap)
        bad["payload"]["weights"][2][17] = 123.0
        with self.assertRaises(ValueError):
            DirectWeights.restore(json.dumps(bad))
        with self.assertRaises(ValueError):
            model.observe("test", 3, True)

    def test_public_fixture_frozen_comparison(self):
        rows = [single_world(seed) for seed in FIXTURE_SEEDS]
        result = classify(rows, dev=False)
        print("WSP88_PUBLIC_FIXTURE=" + json.dumps({
            "classification": result["classification"],
            "checks": result["checks"],
            "stageA_correct": result["stageA_correct"],
            "stageA_total": result["stageA_total"],
            "stageB_correct": result["stageB_correct"],
            "stageB_total": result["stageB_total"],
            "retained_correct": result["retained_correct"],
            "retained_total": result["retained_total"],
            "unknown_confident": [r["unknown_confident"] for r in rows],
            "fixture_stageA_errors": [r["fixture_stageA_errors"] for r in rows],
            "fixture_stageB_errors": [r["fixture_stageB_errors"] for r in rows],
            "softmax_training": [
                (r["trained_softmax_train_correct"], r["trained_softmax_train_total"])
                for r in rows
            ],
        }, sort_keys=True), flush=True)
        self.assertEqual(result["classification"], "FIXTURE_FEASIBLE")


if __name__ == "__main__":
    unittest.main()
