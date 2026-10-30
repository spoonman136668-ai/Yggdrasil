import unittest
from research.native.itd02.mg37.source_bridge import SelectedProgressCells
from research.native.itd02.mg37.progress_cells import LocalProgressCells
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg23.selected_target_cells import observed_key

class MG49CheckpointTest(unittest.TestCase):
    def test_cold_roundtrip_context_isolation_and_tamper(self):
        model=SelectedProgressCells()
        red=observed_key(frame("pick up the red ball"))
        blue=observed_key(frame("pick up the blue ball"))
        cell=LocalProgressCells()
        for _ in range(5):
            cell.observe_selected(0,0)
            cell.observe_selected(1,1)
        model.cells[red]=cell
        raw=model.checkpoint()
        restored=SelectedProgressCells.restore(raw)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.cells[red].choose(0),(1,True))
        self.assertNotIn(blue,restored.cells)
        with self.assertRaises(ValueError):
            SelectedProgressCells.restore(raw+b"x")
        with self.assertRaises(ValueError):
            SelectedProgressCells.restore(raw.replace(b"MG49",b"MG48"))
    def test_reject_corrupt_reward(self):
        model=SelectedProgressCells()
        key=observed_key(frame())
        cell=LocalProgressCells()
        cell.count[0]=1
        cell.reward_sum[0]=2
        model.cells[key]=cell
        with self.assertRaises(ValueError):
            model.checkpoint()

if __name__=="__main__":
    unittest.main()
