"""Read-only FCR03 action-identifiability negative controls."""
import copy
import json
import unittest

from audit_identifiability import audit,check_custody,separation_table,phase_coverage

class AuditContracts(unittest.TestCase):
    def test_full_original_trial_hash_and_scope(self):
        original=check_custody()
        self.assertEqual(original['classification'],'DEV_NO_GO')
        self.assertEqual(original['total_events'],2944)
    def test_action_independence_exact(self):
        table=separation_table()
        self.assertEqual(table['0']['transition_model_separation'],0)
        self.assertEqual(table['0']['reward_model_separation_given_public_s2'],0)
        self.assertEqual(table['1']['transition_model_separation'],1)
        self.assertEqual(table['1']['reward_model_separation_given_public_s2'],1)
        self.assertTrue(all(not v['information_gain_dependent_on_x1_or_x2'] for v in table.values()))
        self.assertTrue(all(v['public_outcome_combinations_checked']==10 for v in table.values()))
    def test_every_phase_has_informative_context(self):
        coverage=phase_coverage()
        self.assertEqual(len(coverage),5)
        self.assertEqual(sum(v['total'] for v in coverage.values()),2944)
        self.assertTrue(all(min(v['per_seed'].values())>0 for v in coverage.values()))
    def test_no_new_trial_or_science_claim(self):
        receipt=audit()
        self.assertFalse(receipt['new_experiment_consumed'])
        self.assertFalse(receipt['safety']['original_world_first_use'])
        self.assertFalse(receipt['safety']['scientific_gain_verified'])
        self.assertGreater(receipt['recombined_reward_Brier_delta_vs_strongest_control'],0)
        self.assertGreater(receipt['return_transition_Brier_delta_vs_strongest_control'],0.020)

if __name__=='__main__': unittest.main()
