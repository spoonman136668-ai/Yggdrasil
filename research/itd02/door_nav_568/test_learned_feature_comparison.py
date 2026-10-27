"""Local feature-selection experiment: equal samples and explicit negatives."""
import unittest
from learned_feature_comparison_audit import run, trial
from local_feature_selector import LocalFeatureSelector
from local_feature_sufficiency_audit import conflicts
from specialization_scaling_audit import families

class LearnedFeatureComparisonTests(unittest.TestCase):
    def test_matched_budget_and_no_hidden_test_labels(self):
        rows=run()["experiments"]
        self.assertEqual(len(rows),18)
        for r in rows:
            self.assertEqual(r["actions"],2*r["count"])
            self.assertEqual(set(r["updates"].values()),{r["actions"]})
            self.assertLessEqual(r["native_records"],32)
            for policy in ("native","linear","tabular"):
                self.assertEqual(sum(r["trained"][policy].values()),r["count"])
                self.assertEqual(sum(r["heldout"][policy].values()),16-r["count"])
                self.assertGreaterEqual(r["cpu_ns"][policy],0)
            self.assertEqual(len(r["native_conflicts"]),4)

    def test_untrained_features_abstain_and_cap_enforced(self):
        local=LocalFeatureSelector()
        self.assertIsNone(local.predict((True,False,True,False)))
        with self.assertRaises(ValueError):
            local.observe((1,False,True,False),True)
        with self.assertRaises(ValueError):
            LocalFeatureSelector(cap=17)
        for bits,value in families(3):
            local.observe(bits,value)
        self.assertLessEqual(local.records(),32)

    def test_rule_is_fixture_only_not_model_argument(self):
        first=trial(3,8,"first_bit")
        parity=trial(3,8,"parity")
        self.assertEqual(first["actions"],parity["actions"])
        self.assertNotEqual(first["rule"],parity["rule"])
        self.assertEqual(first["updates"],parity["updates"])

    def test_alias_collision_diagnostic_is_observation_only(self):
        observed=conflicts(families(3)[:12])
        self.assertEqual(len(observed),4)
        self.assertTrue(all(item["distinct_features"]<=4 for item in observed))
        self.assertTrue(any(item["ambiguous_features"]>0 for item in observed))

    def test_current_local_feature_transfer_does_not_earn_promotion(self):
        rows=run()["experiments"]
        for rule in ("parity","first_bit"):
            group=[r for r in rows if r["rule"]==rule]
            linear=sum(r["heldout"]["linear"]["correct"] for r in group)
            native=sum(r["heldout"]["native"]["correct"] for r in group)
            wrong=sum(r["heldout"]["native"]["wrong"] for r in group)
            self.assertLess(native,linear)
            self.assertGreater(wrong,0)
