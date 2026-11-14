"""Source-only AAI-01 negative, determinism, and nonleakage controls."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("aai01", Path(__file__).with_name("run.py"))
aai01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aai01)


class AAI01Tests(unittest.TestCase):
    def test_disjoint_frozen_cohorts(self):
        self.assertFalse(set(aai01.TRAIN) & set(aai01.DEV))
        self.assertFalse(set(aai01.DEV) & set(aai01.REVERSE))

    def test_world_determinism(self):
        self.assertEqual(aai01.world(2000, 96), aai01.world(2000, 96))

    def test_unrelated_knowledge_does_not_change_a_b(self):
        first, extra = aai01.world(2000, 0), aai01.world(2000, 96)
        self.assertEqual(first["a"], extra["a"])
        self.assertEqual(first["b"], extra["b"])
        self.assertEqual(len(extra["c"]), 96)

    def test_missing_relation_causes_abstention(self):
        w = aai01.world(2000)
        self.assertIsNone(aai01.compose({"a": w["a"], "b": None}, 0, 0))

    def test_untrained_gate_abstains(self):
        self.assertIsNone(aai01.choose([0.0, 0.0]))

    def test_source_target_changes_under_intervention(self):
        w = aai01.world(2000)
        target = aai01.compose(w, 0, 0)
        altered = {"a": w["a"][:], "b": w["b"][:]}
        altered["a"][0] = next(i for i in range(aai01.N) if altered["b"][i] != target)
        self.assertNotEqual(aai01.compose(altered, 0, 0), target)

    def test_conventional_control_reaches_frozen_target(self):
        w = aai01.world(1000)
        examples = [(w, x, aai01.compose(w, x, 0)) for x in w["sources"][:6]]
        weights, steps, loss, converged = aai01.train_logistic(examples)
        self.assertTrue(converged)
        self.assertLessEqual(loss, .01)
        self.assertGreater(weights[0], weights[1])
        self.assertLessEqual(steps, 500)


if __name__ == "__main__":
    unittest.main()
