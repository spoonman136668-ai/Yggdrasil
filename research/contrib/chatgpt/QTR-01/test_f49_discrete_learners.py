"""F49 native, grammar Bayesian, exact Bayesian and query-boundary controls."""
import unittest
from unittest.mock import patch
import f49_worlds as w
import f49_discrete_learners as f


class TestF49Arms(unittest.TestCase):
    def test_frozen_seven_arm_contract_and_source_separation(self):
        p=w.freeze()
        self.assertEqual(set(p["arms"]), {
            "native","conventional_mlp","conventional_logistic",
            "exact_bank_bayes","compositional_bayes","random","uniform"})
        self.assertEqual(f.KINDS, ("native","compositional_bayes",
                                  "exact_bank_bayes","random","uniform"))
        self.assertEqual(f.PROPOSALS_PER_EVENT,1024)
        self.assertEqual(f.MAX_BUDGET,32)
        self.assertNotIn("target_ast", f.__dict__)
        self.assertNotIn("check_target_admission", f.__dict__)

    def test_grammar_public_updates_and_cold_repair(self):
        tr=(11,23,2)
        outcome=(0,1)
        for mode in (False,True):
            model=f.GrammarLearner(256,bayesian=mode)
            model.observe(tr,outcome)
            self.assertEqual(model.proposals,1024)
            self.assertEqual(len(model.history),1)
            first=model.probability((7,17,1))
            self.assertEqual(len(first),2)
            saved=model.cold_checkpoint()
            restored=f.GrammarLearner.restore(saved)
            self.assertEqual(restored.cold_checkpoint(),saved)
            self.assertEqual(restored.probability((7,17,1)),first)
            damaged=saved[:-1]+bytes((saved[-1]^1,))
            with self.assertRaises(f.ControlRejected):
                f.GrammarLearner.restore(damaged)

    def test_bounded_query_select_and_real_public_update(self):
        for kind in f.KINDS:
            arm=f.PublicArm(kind,256,163)
            idx,tr=arm.select()
            self.assertIn(tr,arm.queries)
            self.assertNotIn(idx,arm.used)
            with self.assertRaisesRegex(f.ControlRejected,"QUERY_STATE_INVALID"):
                arm.select()
            with self.assertRaisesRegex(f.ControlRejected,"UNAUTHORIZED_OR_REPLAYED"):
                arm.observe((idx+1)%256,(0,1))
            with self.assertRaisesRegex(f.ControlRejected,"INVALID_PUBLIC_OUTCOME_BITS"):
                arm.observe(idx,(True,0))
            self.assertEqual(arm.observed_bits,0)
            arm.observe(idx,(0,1))
            self.assertEqual(arm.observed_bits,2)
            self.assertEqual(len(arm.used),1)
            with self.assertRaises(f.ControlRejected):
                arm.observe(idx,(0,1))

    def test_no_protected_or_bad_sized_arm(self):
        for kind,size,seed in (("native",256,179),("native",128,163),
                               ("native",True,163),("bad",256,163),("native",256,True)):
            with self.assertRaises(f.ControlRejected):
                f.PublicArm(kind,size,seed)

    def test_exact_bayes_is_full_source_bank_noise_posterior(self):
        model=f.ExactBankBayes(256)
        self.assertEqual(len(model.rules),256)
        # No target outcomes: synthetic observation constructed from source index 3.
        tr=(9,45,3)
        truth=f._predict_rule(model.rules[3],tr)
        model.observe(tr,truth)
        self.assertEqual(len(model.mismatch),256)
        self.assertEqual(model.mismatch[3],0)
        self.assertEqual(model.prediction_accesses,512)
        self.assertTrue(all(0<=p<=1 for p in model.probability(tr)))

    def test_negative_malformed_and_tamper_rejected(self):
        g=f.GrammarLearner(256)
        before=g.cold_checkpoint()
        for tr, outcome in [((0,1,0),(0,0)),((2,2,1),(0,0)),
                            ((1,2,True),(0,0)),((1,2,0),(1,2)),
                            ((1,2,0),(False,1))]:
            with self.assertRaises(f.ControlRejected):
                g.observe(tr,outcome)
        self.assertEqual(g.cold_checkpoint(),before)

    def test_separated_clone_update_does_not_modify_original(self):
        g=f.GrammarLearner(256)
        orig=g.cold_checkpoint()
        clone=f.GrammarLearner.restore(orig)
        clone.observe((2,3,0),(0,1))
        self.assertNotEqual(clone.cold_checkpoint(),orig)
        self.assertEqual(g.cold_checkpoint(),orig)


if __name__=="__main__":
    unittest.main()
