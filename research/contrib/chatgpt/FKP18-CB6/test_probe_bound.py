"""CB6 deterministic decision-theoretic scope checks; no CB5 source generation."""
import unittest
from itertools import permutations
from probe_bound import DirectExclusion, exhaustive_symmetric_worlds, exact_bayes_optimal_cost

class BoundTests(unittest.TestCase):
    def test_all_six_actual_identity_labels(self):
        rows=exhaustive_symmetric_worlds()
        self.assertEqual([r['probes'] for r in rows],[1,2,3,4,5,5])
        self.assertTrue(all(r['resolved']==r['hidden_evaluator_only'] for r in rows))
    def test_exact_optimal_uniform(self):
        cost,first=exact_bayes_optimal_cost((1,)*6,(1,)*6)
        self.assertAlmostEqual(cost,10/3)
        self.assertEqual(first,0)
    def test_last_inferred_without_a_sixth_paid_action(self):
        m=DirectExclusion(exactly_one=True)
        for j in range(5):
            self.assertEqual(m.next_probe(),j)
            m.observe(j,False)
        self.assertEqual(m.next_probe(),None)
        self.assertEqual(m.resolved,5)
        self.assertEqual(m.probes,5)
        self.assertEqual(len(m.raw_logical_bytes()),2)
    def test_cardinality_unknown_fails_closed(self):
        m=DirectExclusion(exactly_one=False)
        for j in range(5):m.observe(j,False)
        self.assertIsNone(m.resolved)
        self.assertEqual(m.next_probe(),5)
        m.observe(5,False)
        self.assertIsNone(m.resolved)
        self.assertIsNone(m.next_probe())
    def test_invalid_action_and_outcome_refuse_without_mutation(self):
        m=DirectExclusion(exactly_one=True)
        start=m.raw_logical_bytes()
        for channel,reversed in ((1,False),(0,0),(True,True),(-1,False)):
            with self.assertRaises(ValueError):m.observe(channel,reversed)
            self.assertEqual(start,m.raw_logical_bytes())
        m.observe(0,False)
        with self.assertRaises(ValueError):m.observe(0,False)
    def test_bayes_general_costs_and_priors(self):
        # Unit costs, skew posterior: best first test has high prior mass.
        cost,first=exact_bayes_optimal_cost((70,6,6,6,6,6),(1,)*6)
        self.assertEqual(first,0)
        self.assertLess(cost,10/3)
        # Explicit intervention costs must be considered by the exact comparator.
        cost2,first2=exact_bayes_optimal_cost((1,)*6,(100,1,1,1,1,1))
        self.assertNotEqual(first2,0)
        self.assertLess(cost2,100)
    def test_invalid_probability_or_cost(self):
        for ps,cs in [((1,)*5,(1,)*6),((0,1,1,1,1,1),(1,)*6),
                      ((1,)*6,(-1,1,1,1,1,1)),((float('nan'),1,1,1,1,1),(1,)*6)]:
            with self.assertRaises(ValueError):exact_bayes_optimal_cost(ps,cs)
    def test_no_original_scientific_first_use_or_generator(self):
        import inspect,probe_bound
        source=inspect.getsource(probe_bound)
        self.assertNotIn('import public_source',source)
        self.assertNotIn('PaidInterventionWorld(',source)

if __name__=='__main__':unittest.main()
