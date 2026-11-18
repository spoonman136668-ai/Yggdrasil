"""WSP169: authenticated historical data stop-rule and hostile negatives.

Read-only Git blobs only. Never load original simulator source or held-world
row arrays, allocate a source seed, create a controller, or permit a do().
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
import unittest
from unittest.mock import patch

from admission_audit import (
    AUDIT_SCHEMA,EXPECTED_DTR_RUN,EXPECTED_BRIER_GAIN,EXPECTED_FROZEN_GAIN,
    PINNED,audit_historical_admission,load_pinned_records
)


class HistoricalSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=load_pinned_records()

    def test_frozen_original_denial_and_nonexperimental_result(self):
        o=audit_historical_admission(self.original)
        self.assertEqual(o["schema"],AUDIT_SCHEMA)
        self.assertEqual(o["classification"],"FIRST_USE_DENIED_HISTORICAL_READONLY")
        self.assertIs(o["first_use_execution_allowed"],False)
        self.assertIs(o["scientific_pass"],False)
        self.assertEqual(o["original_source_actions_this_gate"],0)
        for k in ("owner_signature_verified","independent_source_lease_verified",
                  "virgin_train_held_transfer_cohorts_verified",
                  "qualified_one_shot_actor_and_effect_journal_verified",
                  "same_law_MDP_new_seeds_count_as_unfamiliar"):
            self.assertIs(o[k],False,k)
        self.assertEqual(o["previously_consumed_original_dtr_episodes"],768)
        self.assertEqual(o["original_dtr_run"],EXPECTED_DTR_RUN)
        self.assertEqual(o["approved_but_unspent_conditional_source_action_ceiling"],13312)
        self.assertAlmostEqual(o["DTR_native_gain_over_MLE"],EXPECTED_BRIER_GAIN,places=12)
        self.assertAlmostEqual(o["DTR_frozen_required_gain"],EXPECTED_FROZEN_GAIN,places=12)
        self.assertLess(o["DTR_fraction_of_required_gain"],.02)
        self.assertEqual(o["DTR_native_pooled_Brier"],o["DTR_independent_same_fit_Brier"])
        self.assertEqual(o["CKAD20_passed_development_gates"],0)
        self.assertEqual(o["CKAD20_total_development_gates"],3)
        self.assertEqual(len(o["pinned_evidence"]),5)
        self.assertEqual(o["deployment"],"NONE")
        self.assertEqual(json.dumps(o,sort_keys=True),
                         json.dumps(audit_historical_admission(self.original),sort_keys=True))
        self.assertNotIn("CausalGym",sys.modules)
        self.assertNotIn("causal_gym",sys.modules)
        print("WSP169_SOURCEFIRSTUSE_DENIAL="+json.dumps(
            o,sort_keys=True,separators=(",",":")))

    def _reject(self,label,mutate):
        input_copy=copy.deepcopy(self.original)
        mutate(input_copy)
        with self.subTest(label=label):
            with self.assertRaisesRegex(ValueError,"WSP169_HISTORICAL_EVIDENCE_DRIFT"):
                audit_historical_admission(input_copy)

    def test_owner_spoofs_cannot_transform_old_evidence_to_permission(self):
        self._reject("old_owner_fake_signed",lambda r:r["cvh09"]["roster_denied"].__setitem__(
            "owner_signature_qualified",True))
        self._reject("fake_owner_lease",lambda r:r["cvh09"]["roster_denied"].__setitem__(
            "independent_owner_lease","invented"))
        self._reject("journal_claim",lambda r:r["cvh09"]["roster_denied"].__setitem__(
            "source_effect_journal_verified",True))
        self._reject("actor_claim",lambda r:r["cvh09"]["roster_denied"].__setitem__(
            "original_source_one_shot_runner_id","fake_actor"))
        self._reject("fake_virgin_train",lambda r:r["cvh09"]["roster_denied"].__setitem__(
            "train_seeds",[9999]))
        self._reject("fake_virgin_held",lambda r:r["cvh09"]["roster_denied"][
            "held_seeds_by_arm"]["native"].append(8888))
        self._reject("fake_virgin_transfer",lambda r:r["cvh09"]["roster_denied"][
            "transfer_seeds_by_arm"]["explorer"].append(7777))
        self._reject("recast_same_law",lambda r:r["cvh09"]["headroom"].__setitem__(
            "same_mdppch_seed_transfer_is_unfamiliar_family",True))
        self._reject("fake_owner_allowed",lambda r:r["cvh10"][
            "source_owner_firstuse_authority"].__setitem__(
            "first_use_execution_allowed",True))
        self._reject("new_source_reset",lambda r:r["cvh10"].__setitem__(
            "new_original_source_construct_reset_or_do_calls",1))
        self._reject("new_original_seed",lambda r:r["cvh10"].__setitem__(
            "original_source_seeds_reserved",10))

    def test_archived_dtr_reuse_control_and_reward_tamper_fail_closed(self):
        self._reject("claim_virgin_from_old",lambda r:r["wsp158"]["source"].__setitem__(
            "virgin",True))
        self._reject("inflate_old_gain",lambda r:r["wsp158"]["result"].__setitem__(
            "gain_over_MLE_absolute",.051))
        self._reject("change_threshold",lambda r:r["wsp158"]["result"].__setitem__(
            "frozen_minimum_gain_vs_MLE",.00001))
        self._reject("new_run_same_name",lambda r:r["ckad16"].__setitem__(
            "original_run",39932201243))
        self._reject("new_artifact_claim",lambda r:r["ckad16"].__setitem__(
            "original_artifact",12492506362))
        self._reject("original_archive_digest",lambda r:r["ckad16"].__setitem__(
            "original_zip_sha256","0"*64))
        self._reject("wrong_family_sha",lambda r:r["cvh10"].__setitem__(
            "original_source_commit","f"*40))
        self._reject("science_positive_from_history",lambda r:r["ckad20"].__setitem__(
            "scientific_pass",True))
        self._reject("CKAD_relabel_failed_dev",lambda r:r["ckad20"][
            "development_gates"].__setitem__("shift_reward_vs_all",True))
        self._reject("log_unspent_as_spent",lambda r:r["cvh09"].__setitem__(
            "physical_original_source_actions_executed",3))

    def test_missing_or_corrupted_pinned_git_source_denied_not_substituted(self):
        with patch("admission_audit._git",return_value=b"0"*40):
            with self.assertRaisesRegex(ValueError,"PINNED_BLOB_MISMATCH"):
                load_pinned_records()
        missing=copy.deepcopy(self.original)
        missing.pop("cvh10")
        with self.assertRaisesRegex(ValueError,"HISTORICAL_EVIDENCE_DRIFT"):
            audit_historical_admission(missing)
        wrong=copy.deepcopy(self.original)
        wrong["cvh10"]["schema"]="self-approved.lease.v999"
        with self.assertRaisesRegex(ValueError,"HISTORICAL_EVIDENCE_DRIFT"):
            audit_historical_admission(wrong)
        self.assertEqual(len(set(z[1:4] for z in PINNED)),5)

    def test_no_privileged_source_rows_or_authority_serialized(self):
        o=audit_historical_admission(self.original)
        wire=json.dumps(o,sort_keys=True,allow_nan=False).encode("ascii")
        self.assertLess(len(wire),3500)
        for name in ("raw_held_targets","private_wind","do_policy","source_cohort_seeds",
                     "owner_signed_lease","source_reset_info","secret_token"):
            self.assertNotIn(name,wire.decode("ascii"))
        allowed_keys={x[0] for x in PINNED}
        self.assertEqual(set(self.original),allowed_keys)
        self.assertEqual(o["original_source_actions_this_gate"],0)


if __name__=="__main__":
    unittest.main()
