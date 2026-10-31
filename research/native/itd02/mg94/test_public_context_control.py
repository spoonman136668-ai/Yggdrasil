"""MG94-AG focused leakage and frozen-policy checks."""
import unittest
from public_context_control import public_context,fit,evaluate
from frozen_routing_selector import TRAIN,HELDOUT

class TestPublicContext(unittest.TestCase):
    def test_prefix_only(self):
        self.assertEqual(public_context([0,1,0,0]),(0,1))
        self.assertEqual(public_context([0,1,1,1]),(0,1))
        with self.assertRaises(ValueError):
            public_context([1])
    def test_freeze_and_missing_context(self):
        trained=fit(TRAIN.values())
        before=dict(trained)
        result=evaluate()
        self.assertEqual(trained,before)
        self.assertEqual(len(result["heldout"]),len(HELDOUT))
        for item in result["heldout"].values():
            self.assertEqual(item["routed"],trained.get(tuple(item["public_prefix"]),False))
    def test_training_independent_of_heldout(self):
        baseline=fit(TRAIN.values())
        altered={k:[1-x for x in values] for k,values in HELDOUT.items()}
        self.assertEqual(baseline,fit(TRAIN.values()))
        self.assertEqual(len(altered),len(HELDOUT))

if __name__=="__main__":unittest.main()
