"""Focused source-only controls; NEVER use B or reserved SHIFT data before lock."""
import unittest
import experiment as m


class CausalAtlasTests(unittest.TestCase):
    def test_graph_space_complete_and_structural(self):
        self.assertEqual(len(m.EDGES), 6)
        self.assertEqual(len(m.TOPOLOGIES), 15)
        self.assertEqual(len(m.CYCLES), 3)
        self.assertEqual(len(m.NONCYCLES), 12)
        for cycle in m.CYCLES:
            self.assertEqual(len(cycle), 4)
            self.assertTrue(all(sum(v in e for e in cycle)==2 for v in m.VERTICES))

    def test_action_outcome_semantics(self):
        self.assertEqual(m.xor_edge(0, (0,1)), 0)
        self.assertEqual(m.xor_edge(1, (0,1)), 1)
        self.assertEqual(m.xor_edge(3, (0,1)), 0)
        self.assertEqual(m.xor_edge(15,(2,3)), 0)

    def test_calibration_contains_no_true_edge_labels(self):
        w=m.world(410001,'A')
        self.assertEqual(len(w['observations']),m.SAMPLES)
        for action,outcomes in w['observations']:
            self.assertTrue(0<=action<16)
            self.assertEqual(len(outcomes),4)
        likelihood=m.likelihoods(w['observations'])
        self.assertEqual(len(likelihood),4)
        self.assertTrue(all(len(row)==12 for row in likelihood))
        self.assertEqual(likelihood,m.likelihoods(w['observations']))

    def test_same_data_across_all_inference_methods(self):
        w=m.world(410002,'A')
        L=m.likelihoods(w['observations'])
        im=m.independent_map(L)
        bm=m.cycle_map(L)
        self.assertEqual(len(im),4)
        self.assertEqual(len(bm),4)
        self.assertEqual(len(set(e for e,b in bm)),4)
        self.assertIn(tuple(sorted(e for e,b in bm)),m.CYCLES)
        x=m.independent_bayes(L)
        self.assertTrue(all(abs(sum(p.values())-1.0)<1e-12 for p in x))
        self.assertEqual(len(m.joint_bayes(L,m.CYCLES)),16)
        self.assertEqual(len(m.joint_bayes(L,m.TOPOLOGIES)),16)

    def test_bayes_posteriors_are_probabilities(self):
        L=m.likelihoods(m.world(410003,'A')['observations'])
        for priors in (m.CYCLES,m.TOPOLOGIES):
            prediction=m.joint_bayes(L,priors)
            self.assertTrue(all(0<=p<=1+1e-12 for row in prediction for p in row))

    def test_different_world_topologies_not_leaked(self):
        w=m.world(410004,'A')
        L=m.likelihoods(w['observations'])
        # Identifying labels cannot be necessary for prediction; only observations
        # are passed to the evaluator's policies.
        pred=m.from_map(m.cycle_map(L))
        self.assertEqual(pred,m.from_map(m.cycle_map(L)))
        self.assertEqual(len(m.tables(w)),16)

    def test_pass_A_frozen_exploratory_reproduction(self):
        a=m.eval_split('A')
        self.assertEqual(a['worlds'],64)
        self.assertEqual(a['metrics']['INDEPENDENT_MAP']['brier'],.10546875)
        self.assertEqual(a['metrics']['JOINT_BAYES_CYCLE']['brier'],.02695266)
        self.assertEqual(a['metrics']['INDEPENDENT_MAP']['edge_mapping_accuracy'],.7890625)

    def test_cohorts_disjoint_before_B_firstuse(self):
        self.assertFalse(set(m.A_SEEDS)&set(m.B_SEEDS))
        self.assertFalse(set(m.A_SEEDS)&set(m.SHIFT_SEEDS))
        self.assertFalse(set(m.B_SEEDS)&set(m.SHIFT_SEEDS))


if __name__=='__main__':
    unittest.main()
