import unittest
from fractions import Fraction as F
from audit import (HOT,COLD,posterior,bayes_risk,native_beta_risk,
                   choose_two,expected_detection,analyse,likelihood)

class RiskVarianceContracts(unittest.TestCase):
    def test_no_mapping_prior_indifferent(self):
        self.assertEqual(posterior(())[0],(F(1,4),)*4)
        self.assertEqual(bayes_risk(()),(F(1,4),)*4)
        self.assertEqual(choose_two(native_beta_risk(())),choose_two(bayes_risk(())))
    def test_positive_evidence_same_choice(self):
        history=((2,1),)
        self.assertEqual(choose_two(native_beta_risk(history)),choose_two(bayes_risk(history)))
    def test_contradictory_witnesses_reveal_variance(self):
        history=((2,0),(2,1))
        self.assertEqual(posterior(history)[1],F(5,48))
        self.assertEqual(posterior(history)[0],(F(11,60),F(11,60),F(9,20),F(11,60)))
        self.assertEqual(native_beta_risk(history),(F(1,2),)*4)
        self.assertEqual(bayes_risk(history),(F(37,180),F(37,180),F(23,60),F(37,180)))
        self.assertEqual(choose_two(native_beta_risk(history)),(0,1))
        self.assertEqual(choose_two(bayes_risk(history)),(2,0))
        self.assertEqual(expected_detection(bayes_risk(history),(2,0))-expected_detection(bayes_risk(history),(0,1)),F(8,45))
    def test_exhaustive_no_negative_bayes_regret(self):
        data=analyse()
        self.assertEqual(data['length_two_histories_enumerated'],64)
        self.assertEqual(data['length_two_histories_strict_bayes_gain_count']+data['length_two_histories_ties_count'],64)
        self.assertTrue(all(F(v['expected_detection_gain'])>0 for v in data['strict_gain_examples']))
    def test_strict_public_validation(self):
        with self.assertRaises(ValueError):likelihood(1,2,True)
        with self.assertRaises(ValueError):likelihood(1,4,1)
    def test_scope_and_honesty(self):
        data=analyse()
        self.assertEqual(data['actual_new_source_actions'],0)
        self.assertFalse(data['scientific_gain_verified'])
        self.assertEqual(data['native_full_runner_test'],'NOT_RUN')
        self.assertFalse(data['accepted_model_changed'])

if __name__ == '__main__':unittest.main()
