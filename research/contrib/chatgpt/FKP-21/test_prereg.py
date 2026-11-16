"""FKP-21 prospective source/evidence/authority lock tests."""
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent


class PreregisteredBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))

    def test_first_frozen_parent_exact_and_source_research_only(self):
        p=self.p
        self.assertEqual(p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(p["experiment_id"],
                         "FKP-21-OPEN-RULE-IDENTIFIABILITY-MICROFEEDBACK")
        self.assertEqual(p["exact_parent_sha"],
                         "a3f560435f8d23043b81438ec0e5d6b149ff0bec")
        self.assertTrue(p["prereg_first"])
        self.assertFalse(p["source"]["held_first_use_authorized"])

    def test_fixed_full_rank_split_and_adversarial_pair_budget(self):
        p=self.p["design"]
        self.assertEqual(p["train_patterns"],[3,4,5,6,8,9,10,11,12,13,14,15])
        self.assertEqual(p["unseen_first_probe_patterns"],[0,1,2,7])
        self.assertEqual(len(p["baseline_masks"]),8)
        self.assertEqual(p["expected"]["total_unseen_correct"],56)
        self.assertEqual(p["expected"]["min_unavoidable_errors"],8)
        self.assertEqual(p["bootstrap"]["draws"],10000)
        self.assertEqual(p["bootstrap"]["seed"],2121)
        self.assertTrue(p["no_postresult_tuning"])

    def test_protected_owner_first_use_stays_closed(self):
        p=self.p
        self.assertEqual(p["source"]["protected_dev"],"993500..993531")
        self.assertEqual(p["source"]["protected_transfer"],"993600..993663")
        self.assertTrue(p["source"]["prior_protected_sources_unopened"])
        a=p["authority"]
        self.assertTrue(a["research_only"])
        for key in ("protected_first_use","production_mutation","main_ref_update",
                    "private_runner_dispatch","scheduler_changes","merge_authority"):
            self.assertFalse(a[key])
        self.assertTrue(p["design"]["no_new_workflow_files"])

    def test_research_implementation_only_and_no_scientific_claim(self):
        for name in ("prereg.json","public_rule_source.py","rule_learning.py",
                     "run_public_feedback.py","test_rule_learning.py","README.md"):
            self.assertTrue((HERE/name).is_file())
        self.assertIn("UNVERIFIED",self.p["classification"]["scientific"])
        self.assertIn("INDEPENDENT_GF2_ELIMINATION",
                      self.p["design"]["comparators"])


if __name__=="__main__":
    unittest.main()
