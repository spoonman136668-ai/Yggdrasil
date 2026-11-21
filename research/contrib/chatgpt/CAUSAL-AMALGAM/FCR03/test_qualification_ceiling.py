"""FCR03 mathematical stop certificate: evidence and controls."""
import unittest
from fractions import Fraction
from qualification_ceiling import audit_ceiling, action_signatures

class QualificationCeilingTests(unittest.TestCase):
    def test_nontrivial_positive_control_for_contextual_actions(self):
        signatures=action_signatures(lambda c,a:0,lambda c,a:a^c)
        self.assertEqual(signatures, {'0':[0,1],'1':[1,0]})
        self.assertGreater(sum(max(v) for v in signatures.values()),
            max(sum(signatures[str(c)][i] for c in (0,1)) for i in (0,1)))

    def test_fcr03_action_equivalence_is_exact(self):
        evidence=audit_ceiling()
        self.assertEqual(evidence['action_distinguishability']['transition'],{'0':[0,0],'1':[1,1]})
        self.assertEqual(evidence['action_distinguishability']['reward'],{'0':[0],'1':[1]})
        self.assertTrue(evidence['same_action_information_per_context'])

    def test_prediction_clipping_floor_saturated(self):
        evidence=audit_ceiling()
        self.assertEqual(Fraction(evidence['deterministic_transition_brier_lower_bound']),Fraction(1,256))
        self.assertEqual(Fraction(evidence['original_c_candidate_transition_brier']),Fraction(1,256))
        self.assertEqual(Fraction(evidence['original_c_best_control_transition_brier']),Fraction(1,256))
        self.assertFalse(evidence['strict_transition_brier_gain_possible_under_same_clip'])

    def test_retrospective_only_no_science_promotion(self):
        evidence=audit_ceiling()
        self.assertEqual(evidence['new_trials'],0)
        self.assertEqual(evidence['new_seeds'],[])
        self.assertFalse(evidence['scientific_gain_verified'])
        self.assertEqual(evidence['regression_status'],'UNVERIFIED_TWO_OS')
        self.assertEqual(evidence['native_custody_status'],'UNVERIFIED')
        self.assertEqual(evidence['deployment'],'NONE')
        self.assertEqual(evidence['recombined_context_one_count'],310)

if __name__=='__main__':unittest.main()
