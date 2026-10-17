"""Non-admitting F100/CKB provenance guard contracts; no research cohorts."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("f100_source_custody_under_test",
                                             HERE/"source_custody_preflight.py")
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)


def base_policy():
    # Pure mock: NEVER treated as an attested Git object in these tests.
    return {
        "schema":M.CKB_POLICY_SCHEMA,
        "policy_state":M.CKB_POLICY_STATE,
        "birth_cutoff_utc":M.CKB_EPOCH,
        "selection_excludes_unseen_outcomes":True,
        "scope":("publicly-available immutable GitHub source-file discovery; "
                 "new filename does not prove independently new content"),
        "approved_public_repositories":["nodejs/node","python/cpython"],
        "source_prefix_budgets":{"code":41453,"structured":14365,
                                 "technical_prose":1454},
        **{k:False for k in M.FLAGS},
    }


class CustodyGateTests(unittest.TestCase):
    def test_missing_cross_lane_ledger_and_origin_blocks_first_use(self):
        result=M.assess_policy(base_policy())
        self.assertEqual(result["classification"],
                         "F100_SOURCE_CUSTODY_NOT_QUALIFIED")
        self.assertIn("incomplete_cross_lane_historical_exclusion_ledger",
                      result["missing_or_not_qualified"])
        self.assertIn("prospective_content_origin_not_independent",
                      result["missing_or_not_qualified"])
        self.assertFalse(result["source_first_use_allowed"])
        self.assertFalse(result["scientifically_accepted"])

    def test_even_self_asserted_all_green_is_never_admission(self):
        p=base_policy()
        p["global_historical_source_ledger_complete"]=True
        p["prospective_input_independence_established"]=True
        p["frozen_experiment"]=True
        x=M.assess_policy(p)
        self.assertEqual(x["classification"],
                         "F100_SOURCE_CUSTODY_NOT_QUALIFIED")
        self.assertEqual(x["approved_f100_guard_graphs"],0)
        self.assertFalse(x["source_first_use_allowed"])
        self.assertIn("F100_FIRST_USE_WITNESS_ABSENT_FROM_CKB_SOURCE_DISCOVERY_POLICY",
                      x["missing_or_not_qualified"])

    def test_disallow_claimed_dispatch(self):
        for forbidden in ("dispatch","ready_research","accepted_ref_mutation"):
            p=base_policy()
            p[forbidden]=True
            with self.subTest(forbidden=forbidden):
                with self.assertRaisesRegex(M.PreflightBlocked,
                                            "AUTHORITY_CONTRADICTION"):
                    M.assess_policy(p)

    def test_missing_or_bad_flags_are_not_defaulted(self):
        for key in M.FLAGS:
            for bad in (None,0,"false"):
                p=base_policy()
                p[key]=bad
                with self.subTest(key=key,bad=bad):
                    with self.assertRaises(M.PreflightBlocked):
                        M.assess_policy(p)

    def test_schema_state_epoch_rejected(self):
        for key in ("schema","policy_state","birth_cutoff_utc"):
            p=base_policy()
            p[key]="altered"
            with self.subTest(field=key):
                with self.assertRaises(M.PreflightBlocked):
                    M.assess_policy(p)

    def test_source_selection_can_never_be_future_outcome_based(self):
        p=base_policy()
        p["selection_excludes_unseen_outcomes"]=False
        with self.assertRaises(M.PreflightBlocked):
            M.assess_policy(p)

    def test_unapproved_budget_and_duplicate_repos_rejected(self):
        x=base_policy()
        x["source_prefix_budgets"]["code"]=41454
        with self.assertRaises(M.PreflightBlocked):
            M.assess_policy(x)
        x=base_policy()
        x["approved_public_repositories"].append("nodejs/node")
        with self.assertRaises(M.PreflightBlocked):
            M.assess_policy(x)

    def test_arbitrary_fake_policy_bytes_cannot_be_admitted(self):
        raw=json.dumps(base_policy(),sort_keys=True).encode()
        self.assertNotEqual(M.git_blob_sha(raw), M.CKB_POLICY_BLOB)
        with self.assertRaisesRegex(M.PreflightBlocked,"GIT_OBJECT_DRIFT"):
            M.policy_from_pinned_bytes(raw)

    def test_policy_bytes_size_bound(self):
        with self.assertRaises(M.PreflightBlocked):
            M.policy_from_pinned_bytes(b"")
        with self.assertRaises(M.PreflightBlocked):
            M.policy_from_pinned_bytes(b"x"*(M.POLICY_BYTES_MAX+1))

    def test_exact_frozen_f100_provenance_and_no_science_claim(self):
        x=M.assess_policy(base_policy())
        self.assertEqual(x["frozen_f100_r2_prereg_commit"],
                         "17e27350e295a47fb224d69c237c802c9997861c")
        self.assertEqual(x["f100_source_blob"],
                         "14066ad4f36e09e77134e7d5e192fcacf94b5810")
        self.assertEqual(x["f100_source_qualification_run"],39015811146)
        for flag in ("prospective_experiment_dispatched",
                     "prospective_outcomes_accessed","protected_cohorts_accessed",
                     "scientifically_accepted","optimizer_promoted",
                     "CKB_controller_mutated","accepted_ref_mutated",
                     "Codex_invoked"):
            self.assertFalse(x[flag])

if __name__=="__main__":
    unittest.main()
