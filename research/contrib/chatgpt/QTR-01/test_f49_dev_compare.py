"""F49 DEV evaluator pre-first-use tests. All target bits use source fixture laws."""
import unittest
from unittest.mock import patch
import f49_dev_compare as d
import f49_worlds as world
import f49_discrete_learners as learners


class TestF49EvaluatorBoundary(unittest.TestCase):
    def test_open_development_seed_whitelist_and_protected_rejection(self):
        for bad in (179,181,True,172,-1,0):
            with self.assertRaises(d.ComparisonRejected):
                d.OutcomeService(256,bad,fixture_rule=world.leaf(0))
        for bank in (128,True,0):
            with self.assertRaises(d.ComparisonRejected):
                d.OutcomeService(bank,163,fixture_rule=world.leaf(0))
        self.assertEqual(d.CHECKPOINTS,(8,16,32))
        self.assertEqual(d.MAX_WORLDS,9)
        self.assertEqual(d.BASELINE_SHA,"e9714f125e73050cdac3114559f58b4b2f8e738b")

    def test_public_only_no_replayed_or_unregistered_interventions(self):
        # Explicit fixture bypasses target_ast. No DEV outcome observed.
        rule=world.source_bank(256)[0]
        with patch.object(world,"target_ast",side_effect=AssertionError("target-law leak")):
            oracle=d.OutcomeService(256,163,fixture_rule=rule)
            self.assertEqual(len(oracle.pool),256)
            self.assertEqual(len(oracle.evaluation),256)
            choice=7
            pool=oracle.pool
            self.assertEqual(oracle.answer("native",choice,pool[choice]),
                             oracle.answer("random",choice,pool[choice]))
            with self.assertRaises(d.ComparisonRejected):
                oracle.answer("native",choice,pool[choice])
            with self.assertRaises(d.ComparisonRejected):
                oracle.answer("native",choice,pool[choice-1])
            with self.assertRaises(d.ComparisonRejected):
                oracle.answer("invented",0,pool[0])
            with self.assertRaises(d.ComparisonRejected):
                oracle.answer("native",256,pool[0])
            self.assertEqual(len(oracle._calls["native"]),1)

    def test_clean_holdout_and_probability_rejection(self):
        oracle=d.OutcomeService(256,163,fixture_rule=world.leaf(0))
        def correct(tr):
            t=d.truth_from_rule(world.leaf(0),tr)
            return tuple(float(z) for z in t)
        good=oracle.evaluate_probabilities(correct)
        self.assertEqual(good["accuracy"],1)
        self.assertEqual(good["brier"],0)
        self.assertEqual(good["test_bits"],512)
        bad=oracle.evaluate_probabilities(lambda tr:(float("nan"),0.5)) if False else None
        with self.assertRaises(d.ComparisonRejected):
            oracle.evaluate_probabilities(lambda tr:(float("nan"),0.5))
        with self.assertRaises(d.ComparisonRejected):
            oracle.evaluate_probabilities(lambda tr:(1.5,0.5))

    def test_public_updates_only_and_accounting(self):
        oracle=d.OutcomeService(256,163,fixture_rule=world.source_bank(256)[2])
        arm=learners.PublicArm("native",256,163)
        with patch.object(world,"target_ast",side_effect=AssertionError("DEV target accessed")):
            index,_=arm.select()
            outcome=oracle.answer("native",index,arm.queries[index])
            arm.observe(index,outcome)
            self.assertEqual(arm.observed_bits,2)
            self.assertEqual(len(arm.used),1)
            with self.assertRaises(d.ComparisonRejected):
                oracle.answer("native",index,arm.queries[index])
        self.assertEqual(d.stats_for_arm("native",arm)["proposals"],1024)

    def test_frozen_classification_refuses_partial_or_fabricated_science(self):
        partial=d.classify([{"size":1024,"seed":163}])
        self.assertEqual(partial["classification"],"DEV_INCOMPLETE_NOT_SCIENTIFIC_PASS")
        self.assertFalse(partial["scientific_pass"])
        w=[]
        for bank in world.BANK_SIZES:
            for seed in world.SEEDS:
                arms={}
                for name in d.ALL_KINDS:
                    arms[name]={"checkpoints":{}}
                    for n in d.CHECKPOINTS:
                        value=.62 if name=="native" else .60
                        arms[name]["checkpoints"][str(n)]={
                            "accuracy":value,
                            "cold":{"cold_bit_exact":True,"corruption_rejected":True}}
                w.append({"size":bank,"seed":seed,"arms":arms})
        result=d.classify(w)
        self.assertEqual(result["classification"],"DEV_F49_NO_GO")
        self.assertFalse(result["scientific_pass"])
        # The preflight cannot award a DEV_GO without complete CPU/ablation audit.
        for each in w:
            each["arms"]["native"]["checkpoints"]["16"]["accuracy"]=.93
        new=d.classify(w)
        self.assertEqual(new["classification"],"DEV_F49_NUMERIC_GATE_PASS_NEEDS_COST_AND_ABLATION_AUDIT")
        self.assertFalse(new["scientific_pass"])

    def test_dev_run_requires_explicit_first_use(self):
        self.assertTrue(d.SCHEMA.endswith("frozen-development-results.v1"))
        self.assertEqual(len(d.CONTROL_KINDS),6)
        self.assertEqual(len(d.ABLATION_KINDS),3)
        self.assertFalse(set(d.ALL_KINDS).intersection({"target_ast","target_law"}))


if __name__=="__main__":
    unittest.main()
