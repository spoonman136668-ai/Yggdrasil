"""FKP-22 exact prereg-first authority and source-only experiment controls."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


class FrozenSourceSafeBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((ROOT/"prereg.json").read_text(encoding="utf-8"))

    def test_prereg_precedes_implementation_on_exact_predecessor(self):
        p=self.p
        self.assertEqual(p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(p["experiment_id"],
                         "FKP-22-ACTIVE-CONSEQUENCE-INTERVENTION-PRIOR-SHIFT")
        self.assertEqual(p["exact_parent_sha"],
                         "446e8c008bbab3ffbabeb755f3927a33bab90d0d")
        self.assertTrue(p["prereg_first"])
        self.assertTrue(p["no_postresult_tuning"])

    def test_support_eval_protected_source_cohorts_and_frozen_controls(self):
        p=self.p
        self.assertEqual(p["source"]["support_seeds"],"994000..994015")
        self.assertEqual(p["source"]["known_family_eval_seeds"],"994100..994115")
        self.assertEqual(p["source"]["prior_shift_eval_seeds"],"994200..994207")
        self.assertEqual(p["source"]["protected_dev"],"994500..994531")
        self.assertEqual(p["source"]["protected_transfer"],"994600..994663")
        self.assertFalse(p["source"]["source_held_first_use"])
        self.assertEqual(p["protocol"]["physical_action_count_total"],8704)
        self.assertEqual(p["protocol"]["bootstrap"]["resamples"],10000)
        self.assertEqual(p["protocol"]["bootstrap"]["seed"],2222)
        self.assertEqual(len(p["arms"]),5)
        self.assertEqual(p["learning"]["max_logical_learned_bytes"],65536)

    def test_fixed_expected_values_are_predictions_not_retunable_results(self):
        p=self.p["expected_source_safe"]
        self.assertEqual(p["known_candidate_correct"],32)
        self.assertEqual(p["known_bayes_correct"],32)
        self.assertEqual(p["known_fixed_correct"],16)
        self.assertEqual(p["known_random_correct"],22)
        self.assertEqual(p["known_no_support_correct"],16)
        self.assertEqual(p["shift_candidate_correct"],8)
        self.assertEqual(p["shift_bayes_correct"],8)
        self.assertIn("tie",p["claim"])

    def test_research_only_is_not_accepted_native_authority(self):
        p=self.p
        self.assertTrue(p["authority"]["research_only"])
        for key in ("protected_scientific_first_use","merge","main_ref_mutation",
                    "controller_or_scheduler_changes","private_runner"):
            self.assertFalse(p["authority"][key])
        self.assertTrue(p["no_new_workflow_file"])
        self.assertTrue(p["no_paid_api"])
        for required in ("public_active_source.py","active_policy.py",
                         "run_active_eval.py","test_active_policy.py",
                         "prereg.json","README.md"):
            self.assertTrue((ROOT/required).is_file())


if __name__=="__main__":
    unittest.main()
