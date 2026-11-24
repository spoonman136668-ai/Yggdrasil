"""Fabricated engineering fixtures only; no scored scientific workload."""
import copy
import math
import unittest
from latent_density import LatentDensity


class LatentDensityTests(unittest.TestCase):
    def test_normalization_and_bounded_means(self):
        for k in (1, 2):
            m = LatentDensity(components=k)
            predictions = m.predict([1, -1, 0, 0.5])
            self.assertAlmostEqual(sum(p for p, _ in predictions), 1)
            self.assertTrue(all(p > 0 and all(abs(v) <= 1 for v in mu)
                                for p, mu in predictions))
            self.assertTrue(math.isfinite(m.nll([0]*4, [0]*2)))

    def test_read_only_and_preupdate_score(self):
        m = LatentDensity()
        before = copy.deepcopy(m.__dict__)
        nll = m.nll([0]*4, [1, -1])
        m.predict([0]*4)
        self.assertEqual(m.__dict__, before)
        self.assertEqual(m.observe([0]*4, [1,-1]), nll)
        self.assertNotEqual(m.__dict__, before)

    def test_negative_inputs_do_not_mutate(self):
        m = LatentDensity()
        before = copy.deepcopy(m.__dict__)
        for x,y in [([0]*3,[0]*2), ([0]*4,[float("nan"),0]),
                    ([2]*4,[0]*2), ([0]*4,[0]*3)]:
            with self.assertRaises(ValueError):
                m.observe(x,y)
            self.assertEqual(m.__dict__, before)

    def test_reproducible_updates(self):
        a,b = LatentDensity(seed=11), LatentDensity(seed=11)
        for m in (a,b):
            for _ in range(3):
                m.observe([0.5,0,0,1], [0.3,-0.2])
        self.assertEqual(a.__dict__, b.__dict__)

    def test_single_component_matches_gaussian(self):
        m = LatentDensity(components=1)
        x,y = [0]*4,[0.2,-0.4]
        p,mu = m.predict(x)[0]
        expected = 2*math.log(m.sigma*math.sqrt(2*math.pi))
        expected += sum((t-v)**2 for t,v in zip(y,mu))/(2*m.sigma**2)
        self.assertEqual(p, 1)
        self.assertAlmostEqual(m.nll(x,y), expected)

    def test_fixture_gradient_direction(self):
        for k in (1,2):
            m = LatentDensity(components=k)
            x,y = [0]*4,[0.7,-0.6]
            before = m.nll(x,y)
            m.observe(x,y)
            self.assertLess(m.nll(x,y), before)

    def test_config_rejected(self):
        for kw in ({"components":3}, {"context_dim":0},
                   {"sigma":0}, {"rate":float("nan")}):
            with self.assertRaises(ValueError):
                LatentDensity(**kw)


if __name__ == "__main__":
    unittest.main()
