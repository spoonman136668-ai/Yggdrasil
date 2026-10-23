"""CS06 no-source focused tests: algorithms only, no POPGym environment steps."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs06_popgym_retention import (
 RecurrentAlpha,ExactCounter,RecentEight,AlphaErasure,BlindedMarginal,
 seed,STEPS,SYMBOLS,ALPHAS,ARMS
)
class Tests(unittest.TestCase):
 def test_exact_counter_and_unforgotten_alpha(self):
    a=RecurrentAlpha(1)
    b=ExactCounter()
    for t,x in enumerate([0,1,1,2,3,1,0,12]):
        a.observe(x,t);b.observe(x,t)
    for i in range(13):self.assertEqual(a.act(i,7),b.act(i,7))
 def test_midway_reset_impairs_old_evidence(self):
    m=AlphaErasure(1)
    for t in range(110):m.observe(5 if t<104 else 1,t)
    self.assertEqual(m.act(5,109),0)
    self.assertEqual(m.act(1,109),6)
 def test_source_public_ids_disjoint(self):
    ids={seed(role,r,i) for role,n in (("FIT",16),("VALID",8),("DEV",16))
         for r in range(3) for i in range(n)}
    self.assertEqual(len(ids),120)
    self.assertEqual(STEPS,207);self.assertEqual(SYMBOLS,13)
    self.assertEqual(len(ALPHAS),5);self.assertEqual(len(ARMS),6)
 def test_nearest_observation_no_prefix_fallacy(self):
    z=RecentEight()
    for i in range(20):z.observe(2,i)
    self.assertEqual(z.act(2,19),8)
    b=BlindedMarginal({(3,0):4})
    self.assertEqual(b.act(3,2),4)
    self.assertEqual(b.act(3,90),0)
if __name__=="__main__":
 unittest.main()
