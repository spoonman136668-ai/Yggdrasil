import unittest
from research.native.itd02.mg37.source_bridge import SelectedProgressCells
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg37.progress_cells import LocalProgressCells

class MG43NoCrossContextLeak(unittest.TestCase):
    def test_context_reward_isolation(self):
        model=SelectedProgressCells()
        red=frame("pick up the red ball")
        blue=frame("pick up the blue ball")
        key_red=observed_key(red)
        key_blue=observed_key(blue)
        self.assertNotEqual(key_red,key_blue)
        cell=LocalProgressCells()
        for _ in range(5):
            cell.observe_selected(0,0)
            cell.observe_selected(1,1)
        model.cells[key_red]=cell
        self.assertEqual(model.cells[key_red].choose(0),(1,True))
        self.assertNotIn(key_blue,model.cells)
        self.assertEqual(LocalProgressCells().choose(0),(0,False))
    def test_reject_unscoped_prior_evidence(self):
        legacy=LocalProgressCells()
        legacy.observe_selected(0,1)
        with self.assertRaises(ValueError):
            SelectedProgressCells(progress=legacy)

if __name__=="__main__":
    unittest.main()
