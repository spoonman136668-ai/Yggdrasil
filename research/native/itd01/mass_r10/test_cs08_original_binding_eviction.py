"""CS08 source-free bounded cache and eviction decision tests."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs08_original_binding_eviction import MemoryWithEviction, FIT_POLICIES, K, role_seed

class Test(unittest.TestCase):
 def test_all_strategies_bounded_and_actually_evict(self):
    for mode in FIT_POLICIES:
        p=MemoryWithEviction(K,mode)
        for i in range(8):
            p.decisions=i
            p.remember(i,i%13)
        self.assertEqual(len(p.cache),4)
        self.assertEqual(p.peak_cache,4)
        self.assertEqual(p.total_evictions,4)
        self.assertIsNotNone(p.first_eviction_step)
        self.assertEqual(len(p.index_seen),8)
        self.assertEqual(sum(p.rank_seen),8)
 def test_common_source_free_public_board(self):
    p=MemoryWithEviction(4,"fifo")
    first=p.choose([13]*52,0.0,0)
    frame=[13]*52;frame[first]=3
    second=p.choose(frame,0.0,1)
    self.assertNotEqual(first,second)
    frame[second]=2
    p.choose(frame,-.01,2)
    self.assertGreater(len(p.cache),0)
 def test_identifiers_and_control_menu(self):
    ids={role_seed(role,r,i) for role,n in (("FIT",16),("VALID",8),("DEV",32))
         for r in range(3) for i in range(n)}
    self.assertEqual(len(ids),3*(16+8+32))
    self.assertEqual(len(FIT_POLICIES),5)
    self.assertEqual(K,4)
if __name__=="__main__":unittest.main()
