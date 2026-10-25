"""Strict source-only paired-score tests. All rewards are literal fake metrics.

No original Causal-Gymnasium source or episode is imported or run.
"""
import copy
import json
import unittest
import sys
from research.native.itd02.cartpolewind_compare_dev.score_contract import (
    ARMS, SCHEMA, score_untrusted_public_report,
)


def literal_accounting_fixture():
    # Synthetic report values exercise accounting only, not reward physics.
    report = {
        "schema": SCHEMA,
        "source_kind": "SYNTHETIC_ACCOUNTING_FIXTURES",
        "stage": "DEV",
        "fit_source_sha256": "f" * 64,
        "fit_updates_per_arm": {arm: 4 for arm in ARMS},
        "paired_trial_budget": 2,
        "rows": [],
    }
    examples = {"native": [11, 13], "tabular": [9, 10],
                "recurrent": [10, 9]}
    for arm in ARMS:
        for i, score in enumerate(examples[arm]):
            report["rows"].append({
                "arm": arm,
                "trial_id": f"synthetic-trial-{i}",
                "paired_cohort_sha256": str(i+1) * 64,
                "return_total": float(score),
                "episode_length": 10+i,
                "terminated": True,
                "truncated": False,
                "action_calls": 10+i,
                "train_weight_sha256": {"native": "a", "tabular": "b",
                                         "recurrent": "c"}[arm]*64,
                "eval_weight_sha256": {"native": "a", "tabular": "b",
                                        "recurrent": "c"}[arm]*64,
                "cpu_ns": 1000000*(i+1),
                "peak_rss_bytes": 10000,
                "checkpoint_bytes": 2500
            })
    return report


class PairedSourceOnlyAccountingTests(unittest.TestCase):
    def test_matched_public_scoring_and_no_science_claim(self):
        report = literal_accounting_fixture()
        got = score_untrusted_public_report(report)
        self.assertEqual(got["per_arm"]["native"]["paired_trials_reported"], 2)
        self.assertEqual(got["per_arm"]["native"]["action_calls_reported"], 21)
        self.assertAlmostEqual(got["per_arm"]["native"]["mean_return_reported"], 12)
        self.assertAlmostEqual(got["mean_paired_return_differences_reported"]
                               ["native_minus_tabular"], 2.5)
        self.assertAlmostEqual(got["mean_paired_return_differences_reported"]
                               ["native_minus_recurrent"], 2.5)
        self.assertFalse(got["scientific_go"])
        self.assertFalse(got["real_fsa_signed_witness_verified"])
        self.assertEqual(got["original_source_episodes_authenticated"], 0)
        self.assertEqual(got["report_sha256"],
                         score_untrusted_public_report(report)["report_sha256"])
        self.assertNotIn("causal_gym.envs.cartpole_wind", sys.modules)

    def test_invalid_and_extra_privileged_fields_are_denied(self):
        baseline = literal_accounting_fixture()
        cases = []
        for key, value in [
            ("info", {"current_wind": 0.01}),
            ("get_graph", "hidden"),
            ("ctf_do", 1),
        ]:
            report = copy.deepcopy(baseline)
            report["rows"][0][key] = value
            cases.append(report)
        mutations = [
            ("fit_updates_per_arm", {"native": 4, "tabular": 4, "recurrent": 3}),
            ("source_kind", "REAL_ORIGINAL_VERIFIED"),
            ("paired_trial_budget", 3),
            ("fit_source_sha256", "1" * 64),
        ]
        for key, value in mutations:
            report = copy.deepcopy(baseline)
            report[key] = value
            cases.append(report)
        for row_key, value in [
            ("return_total", float("nan")),
            ("episode_length", 201),
            ("action_calls", 9),
            ("peak_rss_bytes", -1),
            ("cpu_ns", -1),
            ("checkpoint_bytes", 400000),
            ("terminated", 1),
            ("eval_weight_sha256", "9"*64),
        ]:
            report = copy.deepcopy(baseline)
            report["rows"][0][row_key] = value
            cases.append(report)
        for case in cases:
            with self.subTest(change=repr(case)[:250]):
                with self.assertRaises(ValueError):
                    score_untrusted_public_report(case)
        self.assertEqual(baseline, literal_accounting_fixture())

    def test_pair_completeness_and_source_cohort_reuse_denied(self):
        report = literal_accounting_fixture()
        report["rows"][-1]["trial_id"] = "synthetic-trial-0"
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)
        report = literal_accounting_fixture()
        report["rows"][1]["paired_cohort_sha256"] = "1"*64
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)
        report = literal_accounting_fixture()
        report["rows"][4]["paired_cohort_sha256"] = "5"*64
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)
        report = literal_accounting_fixture()
        report["rows"][4]["trial_id"] = "not-matched"
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)

    def test_no_online_weight_updates_between_scored_trials(self):
        report = literal_accounting_fixture()
        report["rows"][1]["train_weight_sha256"] = "d"*64
        report["rows"][1]["eval_weight_sha256"] = "d"*64
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)

    def test_falsely_authenticated_run_cannot_enter_scoring(self):
        report = literal_accounting_fixture()
        report["source_kind"] = "FSA_AUTHORIZED_ORIGINAL"
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)
        report = literal_accounting_fixture()
        report["rows"][0]["source_owner_permit"] = "user-made-receipt"
        with self.assertRaises(ValueError):
            score_untrusted_public_report(report)


if __name__ == "__main__":
    unittest.main()
