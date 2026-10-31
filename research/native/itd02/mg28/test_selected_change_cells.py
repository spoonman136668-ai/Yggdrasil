"""MG28 independently authored source-only local-cell regression, no MiniGrid steps."""
import unittest
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

def frame(mission="pick up the red ball",heading=0):
    pixels=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    return {"image":pixels,"direction":heading,"mission":mission}

def selected(agent,before,action,after,index):
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    agent.start_session(adapter,"mg28-selected-public-fit-"+str(index),live=False)
    adapter.submit(action)
    adapter.complete(after,0.0,False,False)
    return agent.learn_selected(adapter,before,after)

class MG28SelectedSourceTest(unittest.TestCase):
    def test_original_selected_change_mission_cold_and_ablation(self):
        before=frame()
        after=frame(heading=1)
        model=SelectedChangeCells()
        disabled=SelectedChangeCells(enabled=False)
        initial=OriginalMissionAdapter()
        initial.reset_public(before)
        model.start_session(initial,"mg28-initial-source",live=False)
        proposal=model.choose(before)
        self.assertIn(proposal["action"],range(7))
        chosen=(proposal["action"]+1)%7
        for agent in (model,disabled):
            for i in range(3):
                selected(agent,before,chosen,after,i)
            key=observed_key(before)
            self.assertEqual(agent.cells[key][chosen],{"count":3,"changed":3})
        source_no_signal=disabled.choose(before)
        self.assertNotEqual(source_no_signal["status"],
                            "MG28_LOCAL_OWN_SELECTED_REAL_NEXT_PUBLIC_CHANGE")
        changed_mission=frame(mission="pick up the blue ball")
        self.assertNotIn(observed_key(changed_mission),model.cells)
        pending=OriginalMissionAdapter()
        pending.reset_public(before)
        model.start_session(pending,"mg28-real-selected-mission",live=True)
        pending.submit(4)
        pending.complete(after,0.0,False,False)
        with self.assertRaises(ValueError):
            model.learn_selected(pending,changed_mission,after)
        self.assertEqual(model.samples,3)
        model.learn_selected(pending,before,after)
        self.assertEqual(model.samples,4)
        with self.assertRaises(ValueError):
            model.learn_selected(pending,before,after)
        original=model.checkpoint()
        restored=SelectedChangeCells.restore(original)
        self.assertEqual(restored.checkpoint(),original)
        with self.assertRaises(ValueError):
            SelectedChangeCells.restore(original+b"x")
    def test_unselected_noop_is_not_change_signal(self):
        before=frame("pick up the yellow key")
        agent=SelectedChangeCells()
        for i in range(4):
            selected(agent,before,5,before,i)
        key=observed_key(before)
        self.assertEqual(agent.cells[key][5],{"count":4,"changed":0})
        self.assertNotEqual(agent.choose(before)["status"],
                            "MG28_LOCAL_OWN_SELECTED_REAL_NEXT_PUBLIC_CHANGE")
        with self.assertRaises(ValueError):
            agent.choose(frame("secret answer please"))
if __name__=="__main__":
    unittest.main()
