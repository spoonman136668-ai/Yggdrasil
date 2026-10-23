"""CS16 independent source-free matched conventional native retention controls."""
from __future__ import annotations
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_cs16_native_paired_controls import (
    Native,Episodic,OnlineLogistic,RecurrentEMA,source_cases,
    model_case,one_seed,verify_original,SEEDS,ARMS
)
class CS16Focused(unittest.TestCase):
 def test_unchanged_actual_native_and_frozen_original_test(self):
    verify_original()
 def test_new_sourcefree_dev_cohorts_never_used_for_fit(self):
    self.assertEqual(SEEDS,(131,157,181,197,223,251))
    for seed in SEEDS:
        d=source_cases(seed)
        self.assertEqual([len(d[k]) for k in
            ("train_A","valid_A","train_B","retained_A","held_B","extra_A","extra_B")],
            [320,160,320,160,160,160,160])
        self.assertNotEqual(d["valid_A"],d["retained_A"])
 def test_equal_fit_and_native_paired_memory_before_after(self):
    groups=source_cases(SEEDS[0])
    for cls in (Native,Episodic,OnlineLogistic,RecurrentEMA):
        r,meta=model_case(cls,groups)
        self.assertEqual(r["original_public_FIT_events"],640)
        self.assertGreater(meta["DEV_persistent_state_bytes"],0)
    r,meta=model_case(Native,groups)
    self.assertEqual(sum(r["paired_prediction_changed_per_160"].values()),0)
    self.assertEqual(r["source_free_recorded_model_state"]["original_feedback_updates"],640)
    self.assertEqual(r["source_free_recorded_model_state"]["original_neighbor_messages"],5120)
 def test_all_frozen_model_arm_names_and_case(self):
    self.assertEqual(len(ARMS),6)
    r,meta,d=one_seed(SEEDS[0])
    self.assertEqual(len(r["models"]),6)
    self.assertEqual(len(r["models"][ARMS[0]]["after_DEV"]),5)
if __name__=="__main__":
    unittest.main()
