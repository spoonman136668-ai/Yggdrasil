"""Source-free YNCA-03 invariant tests; safe before/after frozen heldout."""
import unittest
import experiment as e

class TestYNCA03(unittest.TestCase):
    def test_laws(self):
        self.assertEqual(e.truth("AND", 3), 1)
        self.assertEqual(e.truth("AND", 1), 0)
        self.assertEqual(e.truth("XOR", 1), 1)
        self.assertEqual(e.truth("XOR", 3), 0)
        self.assertEqual(e.truth("NOR", 0), 1)
    def test_seed_separation(self):
        spans = [set(range(*x)) for x in e.RANGES.values()]
        for i in range(len(spans)):
            for j in range(i+1,len(spans)):
                self.assertFalse(spans[i] & spans[j])
    def test_posterior_normalizes(self):
        p = e.posterior([(0,0),(3,1),(1,0),(2,1)])
        self.assertAlmostEqual(sum(p),1.0,places=12)
        self.assertTrue(all(0 <= v <= 1 for v in p))
    def test_do_data_reproducible_and_equal_cost(self):
        for action in range(4):
            vals=e.do_batch("XOR","train",210001,action)
            self.assertEqual(len(vals),4)
            self.assertEqual(vals,e.do_batch("XOR","train",210001,action))
    def test_posterior_update(self):
        prior=e.posterior([(0,0),(3,1)])
        updated=e.update(prior,1,(1,1,1,1))
        self.assertAlmostEqual(sum(updated),1,places=12)
        self.assertGreater(sum(abs(x-y) for x,y in zip(prior,updated)),0.001)
    def test_exact_bayes_policies_defined(self):
        prior=e.posterior([(0,0),(3,1)])
        for kind in ("bayes_eig","bayes_brier"):
            self.assertIn(e.exact_action(prior,kind),range(4))
    def test_learned_policy_cannot_read_truth(self):
        rows=[(0,0),(3,1),(1,1)]
        prior=e.posterior(rows)
        preds=e.expert_predictions(rows)
        key=e.observable_context(prior,preds)
        self.assertEqual(len(key),3)
    def test_brier_bounds(self):
        w=e.posterior([(0,0),(3,1)])
        self.assertTrue(0<=e.brier(w,"AND")<=1)
        self.assertTrue(0<=e.bayes_risk(w)<=0.25)

if __name__=="__main__":
    unittest.main()
