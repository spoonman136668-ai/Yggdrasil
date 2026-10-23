"""Source-free frozen structural checks for original POPGym relevance trial."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_cs18_popgym_relevance_screen import seed,K,ARMS,TYPES,CATS,actions
class CS18PreSource(unittest.TestCase):
 def test_original_source_role_seed_disjoint(self):
  ids=[seed(role,ti,r,i) for role in ("FIT","DEV") for ti in range(3)
       for r in (0,1) for i in range(32)]
  self.assertEqual(len(ids),len(set(ids)))
  self.assertEqual(len(ids),384)
 def test_memory_cap_and_exact_controls(self):
  self.assertEqual(K,3)
  self.assertEqual(len(ARMS),4)
  self.assertEqual(TYPES,("ranks","suits","colors"))
  self.assertEqual(CATS,(13,4,2))
  for n in CATS:
   self.assertEqual(actions(ARMS[0],n),tuple(range(n)))
   self.assertEqual(actions(ARMS[2],n),tuple(range(min(K,n))))
   self.assertEqual(actions(ARMS[3],n),())
if __name__=="__main__":unittest.main()
