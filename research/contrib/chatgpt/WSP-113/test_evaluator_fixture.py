"""Fabricated end-to-end WSP113 evaluator rehearsal.

All effects come from manually invented graph masks, never the original hidden
WSP113 evaluator. The substitute oracle module is injected BEFORE importing
the evaluator and replaced afterward.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from controls import independent_effect

HERE=Path(__file__).resolve().parent

def fabricated_train():
    return tuple(tuple((s,a,independent_effect(s,a,(w*7)%64))
                       for s in range(16) for a in range(8))
                 for w in range(128))

class TestSealedEvaluatorOnFabricatedEffects(unittest.TestCase):
    def test_full_rehearsal_without_original_oracle(self):
        module=types.ModuleType("oracle")
        module.training_observations=lambda seed="fixture":fabricated_train()
        module.graph_mask=lambda split,w,seed="fixture": (w*31+39)%64
        module.transfer_effect=lambda w,s,a,seed="fixture":independent_effect(
            s,a,(w*31+39)%64)
        old=sys.modules.get("oracle")
        try:
            sys.modules["oracle"]=module
            spec=importlib.util.spec_from_file_location("wsp113_fake_evaluator",HERE/"experiment.py")
            if spec is None or spec.loader is None:raise RuntimeError("missing evaluator")
            test=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test)
            test.WORLDS=2
            result=test.run()
        finally:
            if old is None:sys.modules.pop("oracle",None)
            else:sys.modules["oracle"]=old
        self.assertEqual(result["transfer_worlds"],2)
        self.assertEqual(result["cold_restored_worlds"],2)
        self.assertEqual(result["status"],"ORIGINAL_SYNTHETIC_DEV_NOT_INDEPENDENT_SCIENTIFIC_PASS")
        self.assertFalse(result["scientific_pass"])
        self.assertEqual(len(result["all_heldout_predictions_transcripts_sha256_before_oracle_scoring"]),64)
        self.assertEqual(result["scores"]["direct"]["total"],2*64)
        self.assertEqual(result["scores"]["bayesian"]["total"],2*64)
        self.assertEqual(result["scores"]["direct"]["trajectory_total"],16)
        self.assertEqual(result["new_independent_validation_cohorts_consumed"],0)
        self.assertTrue(result["tampered_native_memory_rejected"])

if __name__=="__main__":
    unittest.main()
