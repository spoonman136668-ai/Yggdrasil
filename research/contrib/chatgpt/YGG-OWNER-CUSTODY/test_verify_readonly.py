"""Read-only negative controls for exact Yggdrasil native owner custody.

All fixture tests use the committed bounded public-source receipt only.
No science model imports, private credential inspection, training or disk
checkpoint traversal is performed.
"""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ygg_owner_checkpoint_readonly",HERE/"verify_readonly.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class OwnerCheckpointBoundary(unittest.TestCase):
    def setUp(self):
        self.baseline=M.load()

    def test_passes_source_only_evidence_without_owner_checkpoint(self):
        result=M.audit_offline(self.baseline)
        self.assertEqual(result["current_accepted_native_checkpoint"],"UNVERIFIED")
        self.assertEqual(result["scientific_qualification"],"UNVERIFIED")
        self.assertTrue(result["context_source_and_owner_bounded_read_verified"])
        self.assertEqual(result["deployment"],"NONE")
        self.assertEqual(result["new_science_seeds_consumed"],0)

    def test_exact_accepted_main_source_and_owner_protection_are_frozen(self):
        main=self.baseline["source_refs"]["accepted_main"]
        self.assertEqual(main["sha"],"5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")
        self.assertEqual(main["tree"],"180008502f6bdfe5a06c3d0d6f47f941dd01f20b")
        self.assertTrue(self.baseline["source_refs"]["active_native_research_branch"]["protected"])
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["accepted_main"]["sha"]="0"*40
        with self.assertRaisesRegex(M.CustodyError,"MAIN_ID"):M.audit_offline(c)

    def test_blocked_active_owner_state_is_not_training_success(self):
        self.assertEqual(self.baseline["source_refs"]["active_native_research_branch"]
                             ["live_research_state"]["status_classification"],"preregistered-blocked")
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["active_native_research_branch"]["live_research_state"]
            ["status_classification"]="scientific-pass"
        with self.assertRaisesRegex(M.CustodyError,"OWNER_BLOCK"):M.audit_offline(c)

    def test_successful_scheduled_runner_is_not_scientific_training(self):
        run=self.baseline["source_refs"]["research_only_controller"]["latest_observed_run"]
        self.assertEqual(run["job_result"],"success")
        self.assertFalse(run["native_model_training_advanced_by_this_run"])
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["research_only_controller"]["latest_observed_run"]
            ["log_verbatim_statuses"]=[]
        with self.assertRaisesRegex(M.CustodyError,"NO_MODEL_RUN"):M.audit_offline(c)

    def test_parallel_CAP03_has_real_history_but_no_accepted_promotion(self):
        cap=self.baseline["source_refs"]["parallel_CAP02_CAP03_research_checkpoint"]
        self.assertEqual(cap["continued_trained_source_episode_count_by_seed"],
                         {"14071":1118,"14072":1093})
        self.assertTrue(cap["direct_original_archive_retained_byte_exact"])
        self.assertFalse(cap["scientific_dev_go"])
        self.assertFalse(cap["accepted_owner_checkpoint"])
        self.assertFalse(cap["original_cross_os_checkpoint_sha_equal"])
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["parallel_CAP02_CAP03_research_checkpoint"]["scientific_dev_go"]=True
        with self.assertRaisesRegex(M.CustodyError,"CAP_SCIENCE"):M.audit_offline(c)

    def test_full_regression_green_not_science_positive(self):
        cap=self.baseline["source_refs"]["parallel_CAP02_CAP03_research_checkpoint"]
        self.assertEqual(cap["full_regression"]["run_id"],44520940169)
        self.assertFalse(cap["scientific_dev_go"])
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["parallel_CAP02_CAP03_research_checkpoint"]["full_regression"]["ubuntu_latest"]="failure"
        with self.assertRaisesRegex(M.CustodyError,"CAP_CI"):M.audit_offline(c)

    def test_historical_knowledge_image_is_not_owner_installed(self):
        k=self.baseline["source_refs"]["prior_factual_knowledge_image"]
        self.assertEqual(k["historical_records"],21343681)
        self.assertEqual(k["historical_predicates"],828)
        self.assertEqual(k["current_owner_installed"],"UNVERIFIED")
        c=copy.deepcopy(self.baseline)
        c["source_refs"]["prior_factual_knowledge_image"]["current_owner_installed"]="INSTALLED"
        with self.assertRaisesRegex(M.CustodyError,"KNOWLEDGE_INSTALL"):M.audit_offline(c)

    def test_missing_owner_checkpoint_and_authority_cannot_be_backfilled(self):
        keys=self.baseline["accepted_owner_checkpoint_requirements"]
        self.assertTrue(all(value is None for value in keys.values()))
        for k in ("trusted_owner_selected_identity","checkpoint_sha256",
                  "native_trained_checkpoint_path","stable_original_source_ledger_digest",
                  "accepted_runtime_integration_receipt"):
            c=copy.deepcopy(self.baseline)
            c["accepted_owner_checkpoint_requirements"][k]="invented"
            with self.assertRaisesRegex(M.CustodyError,"UNPROVEN_"):M.audit_offline(c)

    def test_audit_only_flag_rejects_hidden_execution_or_data_use(self):
        c=copy.deepcopy(self.baseline)
        c["this_gate"]["no_runner_dispatched"]=False
        with self.assertRaisesRegex(M.CustodyError,"NO_RUNNER_DISPATCHED"):M.audit_offline(c)
        c=copy.deepcopy(self.baseline)
        c["this_gate"]["no_new_scientific_source_consumed"]=False
        with self.assertRaisesRegex(M.CustodyError,"NO_NEW_SCIENTIFIC_SOURCE_CONSUMED"):M.audit_offline(c)

    def test_remote_verifier_denies_missing_auth_and_only_gets_pinned_metadata(self):
        with self.assertRaisesRegex(M.CustodyError,"REMOTE_TOKEN_UNAVAILABLE"):
            M.audit_online(self.baseline,"")
        # Do not invoke any actual GET during unit fixtures.
        with patch.object(M,"get_json") as mocked:
            mocked.return_value={}
            with self.assertRaises((KeyError,M.CustodyError)):
                M.audit_online(self.baseline,"dummy")
            self.assertEqual(mocked.call_count,1)
            args,_=mocked.call_args
            self.assertTrue(args[0].startswith("/branches/"))
            self.assertEqual(args[1],"dummy")

if __name__=="__main__":
    unittest.main()
