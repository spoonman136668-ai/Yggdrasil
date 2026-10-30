import unittest
from research.native.itd02.mg37.progress_cells import LocalProgressCells

class MG37ProgressTest(unittest.TestCase):
    def test_reward_beats_observation_churn(self):
        m=LocalProgressCells()
        for _ in range(6):
            m.observe_selected(0,0)
            m.observe_selected(1,1)
        self.assertEqual(m.choose(0),(1,True))
        self.assertEqual(m.choose(1),(1,False))
    def test_negative_and_insufficient_evidence(self):
        m=LocalProgressCells()
        for _ in range(6):
            m.observe_selected(0,0)
        for _ in range(2):
            m.observe_selected(1,1)
        self.assertEqual(m.choose(0),(0,False))
        m.observe_selected(1,-1)
        self.assertEqual(m.choose(0),(0,False))
    def test_reject_non_public_reward(self):
        m=LocalProgressCells()
        with self.assertRaises(ValueError): m.observe_selected(2,float("nan"))
        with self.assertRaises(ValueError): m.observe_selected(2,3)
        with self.assertRaises(ValueError): m.choose(9)

if __name__=="__main__":
    unittest.main()
