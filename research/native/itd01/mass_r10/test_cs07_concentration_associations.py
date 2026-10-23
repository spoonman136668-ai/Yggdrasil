"""CS07 pure public-model tests: no external POPGym source imported."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs07_concentration_associations import (
    PublicCardMemory, public_board, seed, CAPS,ARMS,FACE_DOWN, MAX_STEPS
)
class Guards(unittest.TestCase):
    def test_rank_board_validation(self):
        self.assertEqual(public_board([13]*52),[13]*52)
        with self.assertRaises(RuntimeError):public_board([0]*51)
        with self.assertRaises(RuntimeError):public_board([14]*52)
    def test_first_then_second_pair_legal(self):
        p=PublicCardMemory(52)
        first=p.choose([13]*52,0.,0)
        self.assertEqual(p.first,first)
        obs=[13]*52
        obs[first]=3
        second=p.choose(obs,0.,1)
        self.assertNotEqual(second,first)
        self.assertIsNone(p.first)
        obs[second]=4
        third=p.choose(obs,-.01,2)
        self.assertIn(first,p.cache)
        self.assertIn(second,p.cache)
        self.assertNotIn(third,p.matched)
    def test_capacity_and_erasure(self):
        p=PublicCardMemory(4,True)
        for i in range(10):p.remember(i,i%13)
        self.assertEqual(len(p.cache),4)
        self.assertNotIn(0,p.cache)
        self.assertEqual(list(p.cache),[6,7,8,9])
        z=PublicCardMemory(0)
        z.remember(1,3)
        self.assertEqual(len(z.cache),0)
    def test_split_ids(self):
        all_seeds={seed(role,r,i) for r in range(3)
                   for role,n in (("FIT",12),("VALID",8),("DEV",24))
                   for i in range(n)}
        self.assertEqual(len(all_seeds),132)
        self.assertEqual(CAPS,(0,4,16,52))
        self.assertEqual(len(ARMS),5)
        self.assertEqual(MAX_STEPS,104)
if __name__=="__main__":
    unittest.main()
