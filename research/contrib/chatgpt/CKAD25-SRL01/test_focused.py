"""Source-only unit tests; do not import real or consume held evaluator samples."""
import unittest
from fractions import Fraction as F
from yggdrasil.native_shared_fault_risk import (NativeSharedFaultRisk,
                                                 independent_beta_risks)
from dev_trial import (fitted,training_history,independent_exact_joint,
                       STATIONARY_SEEDS,NEGATIVE_SEEDS,world)

class FocusedContracts(unittest.TestCase):
    def test_prior_uniform_but_not_fixed_actual_hazard(self):
        history=(((0,0),(1,0)),)*3
        candidate=NativeSharedFaultRisk((0,1,2,3),history)
        self.assertEqual(sum(candidate.risks),1)
        self.assertEqual(len(candidate.posterior),16)
        self.assertEqual(sum(x[2] for x in candidate.posterior),1)
    def test_unknown_rate_fitted_no_hidden_input(self):
        history=(((0,1),(1,0)),((2,0),(3,0)),((0,1),(2,0)))
        model=NativeSharedFaultRisk((0,1,2,3),history)
        self.assertEqual(model.risks,independent_exact_joint(history))
        self.assertGreater(model.risk(0),model.risk(3))
    def test_exact_cold_persistent_source_history(self):
        receipt,forecasts,choices=fitted(STATIONARY_SEEDS[0])
        self.assertTrue(receipt['checkpoint_cold_parity'])
        self.assertEqual(choices['learned_shared_risk'],choices['independent_exact_joint_bayes'])
        self.assertEqual(forecasts['learned_shared_risk'],forecasts['independent_exact_joint_bayes'])
    def test_existing_beta_rule_independent(self):
        history=(((0,0),(1,0)),((0,1),(2,0)),((0,0),(3,1)))
        b=independent_beta_risks((0,1,2,3),history)
        self.assertEqual(b[0],F(2,5))
        self.assertEqual(b[3],F(2,3))
        self.assertEqual(b[1],F(1,3))
    def test_no_change_on_forecasts(self):
        history=training_history(STATIONARY_SEEDS[0],negative=False)
        candidate=NativeSharedFaultRisk((0,1,2,3),history)
        snapshot=candidate.checkpoint_fingerprint()
        for a in range(4):candidate.risk(a)
        candidate.select()
        self.assertEqual(snapshot,candidate.checkpoint_fingerprint())
    def test_admission_rejects_invalid_provenance(self):
        sample=(((0,0),(1,0)),)*3
        with self.assertRaises(ValueError):NativeSharedFaultRisk((0,1,1,3),sample)
        with self.assertRaises(ValueError):NativeSharedFaultRisk((0,1,2,3),sample[:2])
        with self.assertRaises(ValueError):NativeSharedFaultRisk((0,1,2,3),(((0,1),(1,1)),)*3)
        with self.assertRaises(ValueError):NativeSharedFaultRisk((0,1,2,3),(((0,True),(1,0)),)*3)
    def test_seed_split_nonreused_and_reproducible(self):
        self.assertEqual(len(set(STATIONARY_SEEDS)&set(NEGATIVE_SEEDS)),0)
        self.assertEqual(world(STATIONARY_SEEDS[0],10,negative=False),
                         world(STATIONARY_SEEDS[0],10,negative=False))
        self.assertEqual(len(training_history(STATIONARY_SEEDS[0],negative=False)),3)
    def test_exact_analytic_old_counterexample_retained(self):
        from yggdrasil.native_shared_fault_risk import independent_beta_risks
        history=(((2,0),(0,0)),((2,1),(1,0)),((1,0),(3,0)))
        p=NativeSharedFaultRisk((0,1,2,3),history)
        self.assertEqual(p.risks, independent_exact_joint(history))
        self.assertEqual(sum(p.risks),1)

if __name__=='__main__':unittest.main()
