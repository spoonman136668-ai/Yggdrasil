"""Source-free independent CS10 learned-fit and provenance role guards."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs10_original_rewarded_cross_episode import (
    OnlineLocal,BatchCov,RawEpisodic,InventoryBlind,Rotated,ExitOnly,
    fit_models,MAP_KEYS,FIT_N,VALID_N,DEV_N,ARMS,SOURCE_MAP_CELLS,native_seed
)
def synthetic():
    # Unit-test shaped public check/sign and actual-looking reward labels only.
    # NEVER used as evaluation or substitute environment.
    ans=[]
    coords=[0,4,8,12,16]
    for ep in range(64):
        bits=[((ep>>(i%5))&1)*2-1 for i in range(5)]
        rew=[0]*20
        for i,p in enumerate(coords):rew[p]=bits[i]
        ans.append({"checks":bits,"reward10":rew})
    return ans
class Tests(unittest.TestCase):
    def test_candidate_equals_batch_and_episodic_on_exact_fit(self):
        m,rec=fit_models(synthetic())
        self.assertEqual(m[ARMS[0]].weights,m[ARMS[1]].weights)
        self.assertEqual(m[ARMS[0]].mapping(),m[ARMS[1]].mapping())
        self.assertEqual(m[ARMS[0]].mapping(),m[ARMS[2]].mapping())
        self.assertEqual(len(m[ARMS[0]].mapping()),5)
        self.assertEqual(len(set(m[ARMS[0]].mapping())),5)
    def test_erasure_permutation_has_no_training(self):
        m,_=fit_models(synthetic())
        orig=m[ARMS[0]].mapping()
        erase=m[ARMS[3]].mapping()
        self.assertEqual(erase,tuple(orig[(i+1)%5] for i in range(5)))
        self.assertNotEqual(erase,orig)
        self.assertEqual(m[ARMS[5]].mapping(),())
    def test_frozen_source_roles_disjoint(self):
        allset={native_seed(role,mapidx,i)
          for mapidx in range(len(MAP_KEYS))
          for role,n in (("FIT",FIT_N),("VALID",VALID_N),("DEV",DEV_N))
          for i in range(n)}
        self.assertEqual(len(allset),2*(FIT_N+VALID_N+DEV_N))
        self.assertNotIn(1600400,allset)
        self.assertEqual(len(SOURCE_MAP_CELLS),20)
        self.assertEqual(len(ARMS),6)
if __name__=="__main__":
 unittest.main()
