"""YNCA-06 focused analytic qualification, no protected science execution."""
import unittest
import qualify as q

class EarlyStopTests(unittest.TestCase):
    def test_frozen_boolean_function_space(self):
        self.assertEqual(len(q.LAWS), 64)
        self.assertEqual(len(set(q.LAWS)), 64)
        self.assertTrue(all(x[0] == 0 and x[7] == 1 for x in q.LAWS))

    def test_ipfc_eig_identical_paths(self):
        r=q.ipfc_gate()
        self.assertEqual(r['identical_IPFC_disagreement_and_EIG_paths'],64)
        self.assertEqual(r['remaining_laws_after_two_probes'],[16])
        self.assertEqual(r['distinct_paths'],[[1,2]])

    def test_ipfc_conditional_information(self):
        cs=list(q.LAWS)
        self.assertEqual(q.select_by(cs,'disagreement'),1)
        self.assertEqual(q.select_by(cs,'expected_information_gain_bits'),1)
        after=[rule for rule in cs if rule[1]==1]
        self.assertEqual(len(after),32)
        self.assertEqual(q.ipfc_scores(after)[1]['expected_information_gain_bits'],0)

    def test_scd_graph_cycle_not_hidden_state(self):
        a=q.scdr_gate()
        self.assertEqual(a['graph_cycle_rank'],1)
        self.assertFalse(a['hidden_state_needed_for_visible_cycle'])
        self.assertIn('NOT computed sheaf H1',a['scope'])

    def test_scd_noise_only_false_positive(self):
        x=q.scdr_gate()
        self.assertGreater(x['naive_ever_disagree_false_alarm'],0.99)
        self.assertEqual(x['calibrated_conflict_count_threshold'],16)
        self.assertLessEqual(x['calibrated_noise_null_false_alarm'],0.05)
        self.assertGreaterEqual(x['calibrated_alternating_parity_detection'],0.95)

    def test_crn_no_evidence_identity(self):
        x=q.crn_gate()
        self.assertAlmostEqual(x['best_possible_expected_context_accuracy_before_observation'],1/3,places=10)
        self.assertLess(x['bayes_vs_replicator_max_probability_deviation'],1e-12)

    def test_crn_dynamic_update_matched(self):
        weights=(1/3,1/3,1/3)
        for path in ((0,0,1,1),(2,1,2,0,0)):
            a=q.bayesian_context_update(weights,path)
            b=q.replicator_context_update(weights,path)
            self.assertAlmostEqual(sum(a),1)
            self.assertAlmostEqual(sum(b),1)
            self.assertTrue(all(abs(v-w)<1e-12 for v,w in zip(a,b)))

    def test_ltm_sparse_exact_baseline(self):
        x=q.ltm_gate()
        self.assertEqual(x['simple_sparse_direct_edit_count'],20)
        self.assertEqual(x['untouched_rule_error_after_direct_update'],0)
        self.assertEqual(x['changed_rule_error_after_direct_update'],0)
        self.assertFalse(x['measured_physical_energy'])

    def test_all_four_are_scoped_not_trained(self):
        r=q.qualify()
        self.assertEqual(set(r['gates']),{'IPFC','SCDR','CRN','LTM'})
        self.assertFalse(any(r['claims'].values()))
        self.assertFalse(r['qualification']['expensive_training_tuning_permitted_without_new_frozen_mechanism'])

if __name__=='__main__':
    unittest.main()
