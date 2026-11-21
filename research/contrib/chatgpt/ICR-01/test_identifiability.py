"""ICR-01 proof and source-action safety tests; no real-world source."""
import unittest
from fractions import Fraction as F
from icr01_identifiability import (
    MODELS, observational_joint, observational_likelihood,
    intervention_outcome_one, identifiability_certificate)

class IdentifiabilityContracts(unittest.TestCase):
    def test_joint_models_equal_on_all_public_outcomes(self):
        for x in (0,1):
            for y in (0,1):
                self.assertEqual(observational_joint(MODELS[0],x,y),
                                 observational_joint(MODELS[1],x,y))
    def test_no_observational_tape_can_disambiguate(self):
        from itertools import product
        pairs=((0,0),(0,1),(1,0),(1,1))
        for length in range(0,5):
            for tape in product(pairs,repeat=length):
                self.assertEqual(observational_likelihood(MODELS[0],tape),
                                 observational_likelihood(MODELS[1],tape))
    def test_do_can_discriminate_but_is_charged(self):
        self.assertEqual(intervention_outcome_one(MODELS[0],"X",0),F(1,10))
        self.assertEqual(intervention_outcome_one(MODELS[1],"X",0),F(1,2))
        self.assertEqual(intervention_outcome_one(MODELS[0],"Y",0),F(1,2))
        self.assertEqual(intervention_outcome_one(MODELS[1],"Y",0),F(1,10))
        self.assertEqual(identifiability_certificate()["interventional_total_variation_gap"],"2/5")
    def test_no_information_when_variables_independent(self):
        for model in MODELS:
            self.assertEqual(intervention_outcome_one(model,"X",0,noise=F(1,2)),F(1,2))
        self.assertEqual(identifiability_certificate(noise=F(1,2))["interventional_total_variation_gap"],"0")
    def test_no_oracle_labels_in_model_interface_and_no_source_calls(self):
        with self.assertRaises(ValueError):observational_joint(MODELS[0],True,0)
        with self.assertRaises(ValueError):intervention_outcome_one(MODELS[0],"X",2)
        with self.assertRaises(ValueError):intervention_outcome_one("ORACLE","X",0)
        with self.assertRaises(ValueError):observational_likelihood(MODELS[0],[(0,1,2)])
        certificate=identifiability_certificate()
        self.assertFalse(certificate["source_first_use"])
        self.assertFalse(certificate["scientific_gain_verified"])
        self.assertEqual(certificate["source_observation_actions_consumed"],0)

if __name__=="__main__":unittest.main()
