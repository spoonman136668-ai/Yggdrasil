"""Mass CS15 source-free paired loss audit and original retention gate integrity."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_cs15_sourcefree_paired_r7_audit import (
    SEEDS,HISTORICAL,PROSPECTIVE_EXTRA,case_audit,exact_cohorts,audit,
    ORIGINAL_NATIVE_GIT_BLOB,ORIGINAL_TEST_GIT_BLOB,verify_source
)
class PairedOriginalR7(unittest.TestCase):
    def test_frozen_source_and_original_test_both_unedited(self):
        refs=verify_source()
        self.assertEqual(refs["original_native_Git_blob"],ORIGINAL_NATIVE_GIT_BLOB)
        self.assertEqual(refs["original_frozen_R7_test_Git_blob"],ORIGINAL_TEST_GIT_BLOB)
    def test_exact_original_generator_role_order_and_no_seed_reuse(self):
        self.assertEqual(SEEDS,(17,31,47,59,83,107))
        for seed in SEEDS:
            x=exact_cohorts(seed)
            self.assertEqual([len(y) for y in x],[320,160,320,160,160])
            self.assertTrue(all(z[0]=="A" for z in x[0]+x[1]+x[3]))
            self.assertTrue(all(z[0]=="B" for z in x[2]+x[4]))
    def test_identical_before_after_items_preserve_predictions(self):
        r=case_audit(31)
        self.assertEqual(r["ORIGINAL_UNPAIRED_different_valid_A_to_retained_A_loss"],.0625)
        self.assertEqual(r["PAIRED_same_valid_A_loss"],0)
        self.assertEqual(r["PAIRED_same_retained_A_loss"],0)
        self.assertEqual(r["identical_A_prediction_counts"]["valid_A_160"],160)
        self.assertEqual(r["identical_A_prediction_counts"]["retained_A_160"],160)
        self.assertTrue(r["original_full_checkpoint_changed_after_B_training"])
        self.assertNotEqual(r["original_A_before_B_checkpoint_SHA256"],
                            r["original_A_after_B_checkpoint_SHA256"])
    def test_frozen_historical_test_still_fails_and_extra_seed_audit_is_public(self):
        d=audit()
        self.assertIs(d["frozen_original_R7_historical_gates_pass"],False)
        self.assertEqual(d["original_R7_full_integration_promotion_gate"],"FAIL_UNCHANGED")
        self.assertEqual(d["paired_same_examples_all_6_seeds_exact_prediction_changes"],0)
        self.assertTrue(d["adversarial_A_label_inversion_any_prediction_change"])
        self.assertEqual(d["disposition"],
                         "PUBLIC_CS15_PAIRED_R7_MEASUREMENT_CONFOUND_CONFIRMED")
if __name__=="__main__":
    unittest.main()
