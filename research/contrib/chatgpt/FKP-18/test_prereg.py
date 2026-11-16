"""Prereg-first, source-only, isolated FKP-18 contribution contract."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parent


class FrozenExperimentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads((ROOT/"prereg.json").read_text("utf-8"))

    def test_exact_parent_and_predecessor_separation(self):
        p=self.contract
        self.assertEqual(p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(p["experiment_id"],"FKP-18-TOKENLESS-TEMPORAL-ELIGIBILITY-TRACES")
        self.assertEqual(p["exact_parent_sha"],
                         "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")
        self.assertIn(1109,[x.get("pr") for x in p["predecessor_evidence"]])
        self.assertIn(1113,[x.get("pr") for x in p["predecessor_evidence"]])

    def test_restricted_source_and_capacity_budget(self):
        frozen=self.contract["frozen_design"]
        self.assertEqual(frozen["slot_budget"],512)
        self.assertEqual(frozen["max_raw_learned_bytes"],65536)
        self.assertEqual(frozen["max_recent_eligibility_lag"],1)
        self.assertTrue(frozen["source_safe_only"])
        self.assertFalse(frozen["protected_source_first_use"])
        self.assertFalse(self.contract["authority"]["production_authority"])
        self.assertFalse(self.contract["authority"]["accepted_ref_mutation"])

    def test_no_protected_worlds_and_no_retroactive_science(self):
        guarded=self.contract["protected_original_worlds"]
        self.assertFalse(guarded["may_open"])
        self.assertEqual(guarded["fkp17_dev"],"978500..978531")
        self.assertEqual(guarded["fkp17_transfer"],"978600..978663")
        rules=self.contract["classification_rules"]
        self.assertIn("No SCIENTIFIC_PASS",rules["supported"])
        self.assertTrue(any("after measured result" in x for x in self.contract["prohibited_after_primary_run"]))

    def test_only_permitted_isolated_paths(self):
        self.assertEqual(self.contract["changed_paths"],[
            "research/contrib/chatgpt/FKP-18/**",
            ".ice/code-atlas.html",".ice/code-atlas.ice",".ice/code-atlas.json"])
        self.assertTrue((ROOT/"temporal_trace.py").exists())
        self.assertTrue((ROOT/"source_safe_witness.py").exists())
        self.assertTrue((ROOT/"run_source_safe_capacity.py").exists())


if __name__=="__main__":
    unittest.main()
