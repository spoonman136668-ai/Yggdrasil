"""CS09 focused source-free original model priority/paired statistics tests."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs09_paired_original_eviction import (
 ProspectiveMemory,MENU,COMPARE,seed,paired_bootstrap,N,ARMS
)
class CS09Pure(unittest.TestCase):
 def test_binding_cache_priority_modes(self):
    for mode in (*MENU,"fifo","lru"):
        m=ProspectiveMemory(4,mode)
        for i in range(11):
            m.decisions=i
            m.remember(i,i%13)
        self.assertEqual(m.total_evictions,7)
        self.assertEqual(m.peak_cache,4)
        self.assertEqual(len(m.cache),4)
 def test_full_conventional_cache_sufficient(self):
    m=ProspectiveMemory(52,"lru")
    for i in range(13):
        m.decisions=i
        m.remember(i,i)
    self.assertEqual(m.total_evictions,0)
    self.assertEqual(m.peak_cache,13)
 def test_paired_ci_deterministic_and_seed_matched(self):
    def sample(k):
        return {"per_seed_original_outcomes":[
            {"seed":i,"reward_sum":(1 if k else 0)+i*.01}
            for i in range(48)]}
    a=paired_bootstrap(sample(1),sample(0),0,0)
    b=paired_bootstrap(sample(1),sample(0),0,0)
    self.assertEqual(a,b)
    self.assertGreater(a["paired_95_percentile_lower"],.99)
    self.assertEqual(len(a["per_seed_reward_deltas"]),48)
 def test_split_unique_ids_and_arm_count(self):
    ids={seed(role,r,i) for role,num in N.items() for r in range(3) for i in range(num)}
    self.assertEqual(len(ids),3*(20+12+48))
    self.assertEqual(len(MENU),6)
    self.assertEqual(len(ARMS),6)
    self.assertEqual(len(COMPARE),6)
if __name__=="__main__":
 unittest.main()
