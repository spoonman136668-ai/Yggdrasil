"""Engineering source and evaluator fixtures; no registered seed execution."""
import unittest
from num05 import canonical, digest, region
from numerical_source import EPISODES, FIXTURES, REGISTERED, RESERVED, fixture_world
from numerical_scoring import ARM_NAMES, score_arm_fixture, score_fixture_suite


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
            self.assertIsNone(a["peak_rss_bytes"])
            self.assertFalse(a["resource_qualification"])
            self.assertFalse(a["scientific_gain_verified"])
        self.assertEqual(out["registered_cohorts_consumed"],0)
        self.assertFalse(out["scientific_gain_verified"])
        self.assertFalse(out["source_owner_authenticated"])

    def test_null_fixture_uses_no_private_labels(self):
        rows,meta=fixture_world(620003)
        self.assertTrue(meta["null"])
        a=score_arm_fixture(620003,"candidate")
        self.assertEqual(a["witness_count"],448)
        self.assertTrue(a["cold_exact"])
        self.assertFalse(a["scientific_gain_verified"])

    def test_bad_parameter_and_unknown_arm(self):
        with self.assertRaises(ValueError):
            score_arm_fixture(620001,"two_bank_bayes",(.07,.04,.5))
        with self.assertRaises(ValueError):
            score_arm_fixture(620001,"fabricated_oracle")

if __name__=="__main__":
    unittest.main()
