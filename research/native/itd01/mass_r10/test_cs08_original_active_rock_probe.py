"""CS08 isolated unit tests: pure source-law math, no source episodes."""
import math,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs08_original_active_rock_probe import (
    Posterior,POSITIONS,HYPOTHESES,K,Q,ARMS,BLOCKS,CHECKS_TOTAL,choose,entropy
)
class TestLaw(unittest.TestCase):
    def test_exact_prior_and_source_law_shape(self):
        m=Posterior()
        self.assertEqual(K,40)
        self.assertEqual(len(POSITIONS),20)
        self.assertEqual(len(HYPOTHESES),40)
        self.assertEqual(len(Q),20)
        self.assertAlmostEqual(sum(m.p),1)
        self.assertAlmostEqual(entropy(m.marginal()),math.log(20),places=10)
    def test_exact_source_probability_at_identity(self):
        i=0;loc=POSITIONS[i]
        self.assertEqual(Q[i][2*i],0.0)
        self.assertEqual(Q[i][2*i+1],1.0)
    def test_observation_updating_uses_only_public_sign(self):
        p=Posterior();p.update(0,1)
        self.assertEqual(p.updates,1)
        self.assertAlmostEqual(sum(p.p),1,places=10)
        self.assertGreater(p.p[1],p.p[0])
        self.assertTrue(all(math.isfinite(x) for x in p.p))
    def test_adaptive_is_legal_and_deterministic(self):
        import random
        x=Posterior();current=(1,1)
        a=choose(ARMS[0],0,x,current,random.Random(1))
        b=choose(ARMS[0],0,x,current,random.Random(999))
        self.assertEqual(a,b)
        self.assertIn(a,range(20))
        self.assertGreaterEqual(x.coordinate_information(a),-1e-10)
        self.assertEqual(choose(ARMS[1],4,x,current,random.Random(0)),4)
        self.assertEqual(BLOCKS,20)
        self.assertEqual(CHECKS_TOTAL,160)
if __name__=="__main__":
    unittest.main()
