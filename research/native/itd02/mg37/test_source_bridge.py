import unittest
from research.native.itd02.mg37.source_bridge import SelectedProgressCells
from research.native.itd02.mg28.test_selected_change_cells import frame,selected
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

class MG38SelectedBridgeTest(unittest.TestCase):
    def test_source_only_reward_selection_and_parent(self):
        model=SelectedProgressCells()
        before=frame()
        after=frame(heading=1)
        for i in range(4):
            adapter=OriginalMissionAdapter()
            adapter.reset_public(before)
            model.start_session(adapter,"mg38-selected-"+str(i),live=False)
            adapter.submit(1)
            adapter.complete(after,1.0,False,False)
            model.learn_selected(adapter,before,after)
        self.assertEqual(model.progress.count[1],4)
        self.assertEqual(model.progress.reward_sum[1],4)
        self.assertEqual(model.parent.samples,4)
    def test_invalid_parent(self):
        with self.assertRaises(ValueError):
            SelectedProgressCells(parent=object())

if __name__=="__main__":
    unittest.main()
