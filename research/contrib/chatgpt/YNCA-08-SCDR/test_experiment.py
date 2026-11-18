"""Focused training-only and Pass-A checks for a true constant-F2 cellular sheaf."""
import unittest
import experiment as m

class FormalSheafTests(unittest.TestCase):
    def test_bounded_coboundary_operator_and_H1(self):
        h=m.cohomology()
        self.assertEqual(h['d0_rank'],2)
        self.assertEqual(h['H1_dimension'],1)
        self.assertEqual(len(h['nontrivial_cohomology_class_representatives']),4)
        for a in range(2):
            for b in range(2):
                for c in range(2):
                    self.assertEqual(m.defect(m.delta((a,b,c))),0)

    def test_obstruction_invariant_under_all_vertex_gauges(self):
        base=(1,1,1)
        for a in range(2):
            for b in range(2):
                for c in range(2):
                    change=m.delta((a,b,c))
                    representative=tuple(x^y for x,y in zip(base,change))
                    self.assertEqual(m.defect(representative),1)

    def test_contextual_obstruction_not_equated_with_hidden_cause(self):
        h=m.cohomology()
        self.assertEqual(h['C0_cardinality'],8)
        self.assertEqual(h['C1_cardinality'],8)
        self.assertEqual(set(h['nontrivial_cohomology_class_representatives']),{
            (1,0,0),(0,1,0),(0,0,1),(1,1,1)})

    def test_first_pass_reproduces_only_consumed_a(self):
        result=m.eval_one('A',m.train())
        self.assertEqual(result['worlds'],96)
        self.assertEqual(result['verdict'],'DEVELOPMENT_NO_GO')
        self.assertAlmostEqual(result['metrics']['SCDR_A']['brier'],.18642489)
        self.assertAlmostEqual(result['metrics']['BAYES_ORACLE']['brier'],.12761882)

    def test_equal_input_budget_no_hidden_state_prediction_input(self):
        model=m.train()
        rows=m.sample_world(300001,'train')
        s=m.filter_sheaf(rows,model['tau_unsupervised'],True)
        changed=[(1-h,obs) for h,obs in rows]
        self.assertEqual(s,m.filter_sheaf(changed,model['tau_unsupervised'],True))
        self.assertEqual(len(s),m.LENGTH)
        self.assertEqual(len(m.filter_raw_hmm(rows,model)),m.LENGTH)

    def test_unsupervised_switch_rate_uses_observations_only(self):
        model=m.train()
        self.assertTrue(0 <= model['tau_unsupervised'] < .49)
        self.assertTrue(0 <= model['tau_supervised'] < .49)
        self.assertEqual(model['train_worlds'],160)
        self.assertTrue(set(range(*m.A)).isdisjoint(range(*m.B)))
        self.assertTrue(set(range(*m.A)).isdisjoint(range(*m.TRAIN)))
        self.assertTrue(set(range(*m.NULL)).isdisjoint(range(*m.B)))

if __name__=='__main__': unittest.main()
