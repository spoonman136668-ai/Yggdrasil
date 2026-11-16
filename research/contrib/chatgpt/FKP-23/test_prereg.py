"""FKP-23 original frozen-first parent, real actions and authority fences."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


class FrozenCausalRepairPrereg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((ROOT/"prereg.json").read_text("utf-8"))

    def test_original_first_frozen_prereg_and_fkp22_parent(self):
        p=self.p
        self.assertEqual(p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(p["experiment_id"],
                         "FKP-23-CONTRADICTION-GATED-PRIOR-REPAIR-RETENTION")
        self.assertTrue(p["prereg_first"])
        self.assertEqual(p["exact_parent_sha"],
                         "65801e5777c9d399cdd49d919bcd4428d3cad951")
        self.assertFalse(p["science"]["scientific_pass"])

    def test_unconsumed_train_split_and_reproducible_critical_thresholds(self):
        x=self.p
        s=x["source"]
        self.assertEqual(s["support_seeds"],"995000..995015")
        self.assertEqual(s["update_seeds"],"995100..995107")
        self.assertEqual(s["shift_eval_seeds"],"995200..995215")
        self.assertEqual(s["return_eval_seeds"],"995300..995315")
        self.assertEqual(s["protected_dev"],"995500..995531")
        self.assertEqual(s["protected_transfer"],"995600..995663")
        self.assertTrue(s["predecessor_protected_unopened"])
        d=x["primary_design"]
        self.assertEqual(d["limits"]["full_physical_action_count"],11776)
        self.assertEqual(d["bootstrap"]["draws"],10000)
        self.assertEqual(d["bootstrap"]["seed"],2323)
        self.assertEqual(d["prereg_expected"]["candidate_shift"],16)
        self.assertEqual(d["prereg_expected"]["candidate_return"],16)
        self.assertEqual(d["prereg_expected"]["frozen_shift"],12)
        self.assertEqual(d["prereg_expected"]["recent_return"],12)
        self.assertEqual(len(d["all_arms"]),5)
        self.assertIn("NO_MEMORY",d["all_arms"])

    def test_no_replay_or_post_result_tuning_and_accepted_main_mutation(self):
        x=self.p
        self.assertTrue(x["engineering"]["no_new_workflow_file"])
        self.assertTrue(x["engineering"]["no_scheduled_tasks"])
        self.assertTrue(x["engineering"]["no_paid_api"])
        self.assertTrue(x["engineering"]["inherited_fkp18_through_fkp22"])
        self.assertFalse(x["authority"]["accepted_main_mutation"])
        self.assertFalse(x["authority"]["merge"])
        self.assertFalse(x["authority"]["protected_first_use"])
        self.assertFalse(x["authority"]["controller_scheduler"])
        self.assertFalse(x["authority"]["private_runner"])
        self.assertFalse(x["authority"]["deploy"])
        self.assertIn("No revision",x["primary_design"]["postresult"])

    def test_source_safe_custody_precedes_artifact_audit_and_prereg_file_exists(self):
        x=self.p
        self.assertIn("before",x["engineering"]["proof_archive"])
        for name in ("prereg.json","public_repair_source.py","prior_repair.py",
                     "run_repair.py","test_prior_repair.py",
                     "test_prereg.py","README.md"):
            self.assertTrue((ROOT/name).is_file())


if __name__=="__main__":
    unittest.main()
