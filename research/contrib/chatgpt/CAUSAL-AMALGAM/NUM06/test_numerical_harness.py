"""Engineering source and evaluator fixtures; no registered seed execution."""
import unittest
from num05 import canonical, digest, region
from numerical_source import EPISODES, FIXTURES, REGISTERED, RESERVED, fixture_world
from numerical_scoring import (ARM_NAMES, score_arm_fixture, score_fixture_suite,
                               head_squared_errors, mean_head_errors, head_window_report)


class SourceHarnessTests(unittest.TestCase):
    def test_reserved_source_and_score_denied(self):
        self.assertEqual(sum(map(len,REGISTERED.values())),9)
        for seed in (*RESERVED,620999,True,"620001"):
            with self.assertRaisesRegex(ValueError,"FIXTURE_ONLY"):
                fixture_world(seed)
            with self.assertRaisesRegex(ValueError,"RESERVED_SCORING"):
                score_fixture_suite(seed)

    def test_source_shape_reproducibility_and_coverage(self):
        rows,meta=fixture_world(620001)
        again,_=fixture_world(620001)
        self.assertEqual(digest(canonical(rows)),digest(canonical(again)))
        self.assertEqual(len(rows),EPISODES)
        self.assertEqual(len({r["id"] for r in rows}),EPISODES)
        self.assertEqual({(r["action"],region(r["observation"])) for r in rows},
                         {(a,q) for a in range(5) for q in range(4)})
        self.assertTrue(any(r["action"]!=i%5 for i,r in enumerate(rows)))
        self.assertEqual(set(rows[0]),{"id","source_tag","observation","action",
                                      "successor","reward","terminated","truncated"})
        self.assertFalse(meta["source_owner_authenticated"])

    def test_exact_registry_and_fixture_separation(self):
        all_seeds=[s for group in REGISTERED.values() for s in group]
        self.assertEqual(len(all_seeds),len(set(all_seeds)))
        self.assertFalse(set(FIXTURES)&RESERVED)
        self.assertEqual(REGISTERED["held"],{620201:(145,305),620203:(165,325),620207:(177,337)})

    def test_matched_full_fixture_and_cold_recall_accounting(self):
        out=score_fixture_suite(620001)
        self.assertEqual(out["classification"],"FIXTURE_ONLY")
        self.assertEqual(len(out["arms"]),11)
        self.assertEqual(tuple(a["name"] for a in out["arms"]),ARM_NAMES)
        self.assertEqual(len({a["source_sha256"] for a in out["arms"]}),1)
        for a in out["arms"]:
            self.assertTrue(a["cold_exact"])
            self.assertEqual(a["late_count"],80)
            self.assertEqual(a["return_count"],111)
            self.assertAlmostEqual(a["pooled_mse"],(a["late_mse"]+a["return_mse"])/2)
            for scalar,head in (("full_mse","full_head_mse"),
                                ("late_mse","late_head_mse"),
                                ("return_mse","return_head_mse"),
                                ("pooled_mse","pooled_head_mse")):
                self.assertEqual(set(a[head]),{"delta_x","delta_y","reward"})
                self.assertAlmostEqual(a[scalar],sum(a[head].values())/3,places=12)
            self.assertIsNone(a["peak_rss_bytes"])
            self.assertFalse(a["resource_qualification"])
            self.assertFalse(a["scientific_gain_verified"])
        self.assertEqual(out["registered_cohorts_consumed"],0)
        self.assertFalse(out["head_diagnostics_only"]["per_head_acceptance_authorized"])
        self.assertFalse(out["scientific_gain_verified"])
        self.assertFalse(out["source_owner_authenticated"])

    def test_null_fixture_uses_no_private_labels(self):
        rows,meta=fixture_world(620003)
        self.assertTrue(meta["null"])
        a=score_arm_fixture(620003,"candidate")
        self.assertEqual(a["witness_count"],448)
        self.assertTrue(a["cold_exact"])
        self.assertFalse(a["scientific_gain_verified"])


    def test_three_head_masking_counterexample_diagnostic_only(self):
        baseline=mean_head_errors([[.20,.20,.10]])
        candidate=mean_head_errors([[.08,.08,.25]])
        base=sum(baseline.values())/3
        new=sum(candidate.values())/3
        self.assertGreaterEqual(base-new,.005)
        self.assertGreaterEqual((base-new)/base,.10)
        self.assertGreater(candidate["reward"],baseline["reward"])
        self.assertAlmostEqual(base-new,.03)
        self.assertFalse(candidate["reward"]<=baseline["reward"])
        # No acceptance decision is derived from aggregate gain alone.

    def test_head_errors_reject_incomplete_or_forged_data(self):
        for prediction,actual in (([0,1],[0,1,2]),
                                  ([0,0,float("nan")],[0,0,0]),
                                  ([False,0,0],[0,0,0])):
            with self.assertRaisesRegex(ValueError,"NUM06_HEAD_"):
                head_squared_errors(prediction,actual)
        for rows in ([],[[0,.1,float("inf")]],[[0,-.1,0]],[[0,0]]):
            with self.assertRaisesRegex(ValueError,"NUM06_HEAD_ERRORS_INVALID"):
                mean_head_errors(rows)
        with self.assertRaisesRegex(ValueError,"NUM06_HEAD_WINDOWS"):
            head_window_report([[0,0,0]]*447,145,305)

    def test_bad_parameter_and_unknown_arm(self):
        with self.assertRaises(ValueError):
            score_arm_fixture(620001,"two_bank_bayes",(.07,.04,.5))
        with self.assertRaises(ValueError):
            score_arm_fixture(620001,"fabricated_oracle")

if __name__=="__main__":
    unittest.main()
