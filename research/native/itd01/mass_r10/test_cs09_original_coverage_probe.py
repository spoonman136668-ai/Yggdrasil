"""Source-free CS09 frozen-policy and common-posterior tests."""
import pathlib,random,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs09_original_coverage_probe import (
    new_coverage_choice,select,POLICIES,POSITIONS,Posterior,mdist,BLOCKS,
    CHECKS,MAP_KEYS,RESET_SEEDS,
)
class Coverage(unittest.TestCase):
    def test_first_ten_are_distinct_and_legal(self):
        counts=[0]*20
        p=Posterior()
        loc=(2,1)
        picks=[]
        for block in range(10):
            i=new_coverage_choice(block,p,loc,counts)
            self.assertIn(i,range(20))
            self.assertEqual(counts[i],0)
            picks.append(i);counts[i]+=1
            loc=POSITIONS[i]
        self.assertEqual(len(set(picks)),10)
    def test_remaining_blocks_cap_two(self):
        p=Posterior();counts=[0]*20;loc=(2,1)
        for b in range(20):
            i=new_coverage_choice(b,p,loc,counts)
            counts[i]+=1;loc=POSITIONS[i]
            self.assertLessEqual(max(counts),2)
        self.assertEqual(sum(counts),20)
        self.assertGreaterEqual(sum(x>0 for x in counts),10)
    def test_observation_and_source_law_only(self):
        p=Posterior()
        choices=[select(k,0,p,(1,1),[0]*20,random.Random(17)) for k in POLICIES]
        self.assertEqual(len(choices),4)
        self.assertTrue(all(0<=i<20 for i in choices))
        self.assertEqual(BLOCKS,20)
        self.assertEqual(CHECKS,160)
        self.assertEqual(len(MAP_KEYS),3)
        self.assertEqual(len(RESET_SEEDS),4)
        self.assertEqual(mdist((0,0),(4,3)),7)
if __name__=="__main__":
    unittest.main()
