"""Focused development-only tests for YNCA-01; stdlib only."""
import unittest
import experiment as e

class YNCATests(unittest.TestCase):
    def test_world_seed_deterministic(self):
        self.assertEqual(e.sample_world(31001,"train"), e.sample_world(31001,"train"))
    def test_split_disjoint(self):
        spans=[set(range(*r)) for r in e.SEEDS.values()]
        for i in range(len(spans)):
            for j in range(i+1,len(spans)):
                self.assertFalse(spans[i]&spans[j])
    def test_intervention_natural_observations_distinct(self):
        _,obs,interv=e.sample_world(31001,"train")
        self.assertIn(len(obs),(90,110,120,140))
        self.assertIn(len(interv),(20,24,28,48))
        self.assertEqual(set(x for x,y in interv),{0,1})
    def test_expert_probability(self):
        _,obs,interv=e.sample_world(31001,"train")
        for p in e.predict_experts(obs,interv):
            self.assertGreaterEqual(p,0)
            self.assertLessEqual(p,1)
    def test_native_referee_normalized(self):
        model=e.train_referee(range(*e.SEEDS['train']))
        self.assertTrue(e.checks(model)['weights_normalized'])
    def test_shuffled_labels_perturb_reliability(self):
        rows=range(*e.SEEDS['train'])
        clean=e.train_referee(rows)
        shuffled=e.train_referee(rows,permuted_labels=True)
        self.assertNotEqual(clean['avg'],shuffled['avg'])
    def test_gate_width(self):
        self.assertEqual(e.GATE_HALF_WIDTH,0.2)

if __name__=='__main__':unittest.main()
