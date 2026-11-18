"""CKAD18 frozen independent sidecar development checks."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ckad18_campaign', HERE / 'campaign.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CKAD18Tests(unittest.TestCase):
    def test_enumeration_and_private_law(self):
        self.assertEqual(len(mod.PAIRS), 6)
        self.assertEqual(len(mod.RULES), 48)
        for h in mod.RULES:
            self.assertTrue(all(mod.law(h, x) in (0, 1) for x in range(16)))

    def test_frozen_training_and_explicit_held_pair(self):
        for seed in mod.SEEDS:
            for fam in (0, 1):
                for held in range(6):
                    tr = mod.trained(seed, fam, held)
                    self.assertEqual(len(tr), 5)
                    self.assertTrue(all(len(t) == 6 and len({x for x, _ in t}) == 6 for t in tr))
                    self.assertEqual(mod.trained(seed, fam, held), tr)
                    pairs = [p for p in range(6) if p != held]
                    self.assertNotIn(held, pairs)

    def test_restore_and_tamper(self):
        raw = mod.checkpoint(mod.trained(101, 0, 0))
        restored = mod.restore(raw, mod.sha(raw))
        self.assertEqual(restored, mod.family_posterior(mod.trained(101, 0, 0)))
        with self.assertRaises(ValueError):
            mod.restore(raw[:-1] + b'!', mod.sha(raw))

    def test_matched_exact_bayes_and_no_hidden_labels(self):
        tasks = mod.trained(101, 0, 0)
        prior = mod.family_posterior(tasks)
        self.assertTrue(all(len(row) == 2 for t in tasks for row in t))
        hidden = mod.world(101, 0, 0, 0)
        observations = []
        for x in (1, 2, 5, 9):
            for q in range(16):
                self.assertAlmostEqual(mod.forecast(prior, observations, q),
                                       mod.exact_control(prior, observations, q), places=12)
            observations.append((x, mod.law(hidden, x)))


if __name__ == '__main__':
    unittest.main()
