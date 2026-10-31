"""MG94-AH actual held-out mutation and frozen-policy leakage tests.

Source-free engineering tests. Does not qualify original-world transfer.
"""
import unittest
from unittest.mock import patch
import public_context_control as cc
from frozen_routing_selector import TRAIN, HELDOUT

class FrozenContextTests(unittest.TestCase):
    def test_heldout_mutation_cannot_change_fit(self):
        baseline=cc.fit(TRAIN.values())
        flipped={k:[1-v for v in sequence] for k,sequence in HELDOUT.items()}
        with patch.object(cc, "HELDOUT", flipped):
            self.assertEqual(cc.fit(TRAIN.values()),baseline)
            out=cc.evaluate()
            self.assertEqual(len(out["heldout"]),len(flipped))
            self.assertEqual(out["frozen_policy"],{str(k):v for k,v in baseline.items()})

    def test_prefix_disjointness_is_not_independent_transfer(self):
        train_prefixes={cc.public_context(v) for v in TRAIN.values()}
        held_prefixes={cc.public_context(v) for v in HELDOUT.values()}
        # Deliberate context overlap is explicit, not a new-world claim.
        self.assertTrue(train_prefixes.intersection(held_prefixes))

    def test_missing_prefix_fails_closed(self):
        fitted=cc.fit(TRAIN.values())
        self.assertFalse(fitted.get((0,0),False))
        self.assertFalse(fitted.get((1,1),False))

if __name__=="__main__":unittest.main()
