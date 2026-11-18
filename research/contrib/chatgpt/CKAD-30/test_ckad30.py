"""CKAD30 pre-primary negative/control and contract checks; NEVER scores the primary cohort."""
import importlib.util
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

P = Path(__file__).with_name("campaign.py")
spec = importlib.util.spec_from_file_location("ckad30_campaign_frozen", P)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CKAD30FrozenTests(unittest.TestCase):
    def test_complete_grammar(self):
        self.assertEqual(10, len(c.PAIRS))
        self.assertEqual(45, len(c.PAIR_CHOICES))
        self.assertEqual(2880, 2 * 32 * len(c.PAIR_CHOICES))
        self.assertTrue(set(c.PILOT).isdisjoint(c.PRIMARY))
        for name in c.GRAPHS:
            for bits in __import__("itertools").product((0, 1), repeat=3):
                self.assertIn(c.composition(name, bits), (0, 1))

    def test_exact_law_consistency_for_public_fixture(self):
        law = (1, 19, 2, 8)
        rows = [[x & 15, x >> 4, c.effect(law, x)] for x in (0, 1, 3, 8, 17, 25)]
        compatible = c.posterior(rows)
        self.assertIn(law, compatible)
        self.assertTrue(all(0 <= c.bayes_prob(compatible, x) <= 1 for x in range(32)))

    def test_native_cold_source_ledger_without_hidden_generator(self):
        m = c.learner()
        rows = [[x & 15, x >> 4, (x & 3).bit_count() & 1] for x in range(16)]
        m = c.observe(m, 19001, 0, rows)
        blob = m.checkpoint()
        restored = NativeCumulativeLearner.restore(blob, digest(blob))
        self.assertEqual(blob, restored.checkpoint())
        self.assertEqual({tuple(x) for x in rows},
                         {tuple(x) for x in restored._rows(0)})

    def test_screen_requires_both_custody_and_real_improvement(self):
        def mk(seed, n, repaired, a, b):
            return {"seed":seed,
                    "metrics":{"native_original":{"brier":n},
                               "native_sparse_repair":{"brier":repaired}},
                    "coverage":{"native_original":a,"native_sparse_repair":b},
                    "old_primitive_retention_exact":True,
                    "cold_restore_exact":True,"local_quarantine_exact":True}
        one = mk(9101, .35, .30, .20, .45)
        two = mk(9102, .30, .30, .10, .10)
        self.assertTrue(c.screen([one, two]))
        self.assertFalse(c.screen([two | {"seed":9101}, two]))
        self.assertFalse(c.screen([one | {"cold_restore_exact":False}, two]))

    def test_primary_requires_explicit_source_and_receipt_guard(self):
        self.assertNotIn(707, c.PILOT)
        self.assertNotIn(808, c.PILOT)
        self.assertNotIn(909, c.PILOT)
        self.assertEqual((707, 808, 909), c.PRIMARY)


if __name__ == "__main__":
    unittest.main()
