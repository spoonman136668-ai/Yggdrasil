import unittest
from research.native.itd02.mg40.task_cells import (
    TaskCell,SelectedTaskCells,selected_task_effect
)
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.mg28.test_selected_change_cells import frame

def front(public,code):
    public["image"][3][5]=list(code)
    return public

def selected(model,before,action,after,ordinal):
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    model.start_session(adapter,"nr-m1q-public-source-"+str(ordinal),live=False)
    adapter.submit(action)
    adapter.complete(after,0.0,False,False)
    model.learn_selected(adapter,before,after)
    with unittest.TestCase().assertRaises(ValueError):
        model.learn_selected(adapter,before,after)

class TestLocalNativeTaskEffects(unittest.TestCase):
    def test_original_public_door_open_not_view_churn(self):
        b=front(frame("pick up the red key"),(4,2,2))
        n=front(frame("pick up the red key"),(4,2,0))
        self.assertTrue(selected_task_effect(b,5,n))
        self.assertFalse(selected_task_effect(n,5,b))
        shifted=front(frame("pick up the red key",heading=1),(4,2,0))
        self.assertFalse(selected_task_effect(b,0,shifted))

    def test_exact_selected_target_pickup(self):
        b=front(frame("pick up the yellow ball"),(6,4,0))
        n=frame("pick up the yellow ball")
        self.assertTrue(selected_task_effect(b,3,n))
        wrong=front(frame("pick up the yellow ball"),(6,0,0))
        self.assertFalse(selected_task_effect(wrong,3,n))

    def test_policy_requires_matched_observation_support(self):
        cell=TaskCell()
        for _ in range(3):cell.record(0,False)
        cell.record(5,True)
        self.assertEqual(cell.propose(0),(0,False))
        cell.record(5,True)
        self.assertEqual(cell.propose(0),(5,True))
        with self.assertRaises(ValueError):cell.propose(9)

    def test_actual_source_ledger_and_cold_checkpoint(self):
        model=SelectedTaskCells(enabled=True)
        b=front(frame("pick up the red key"),(4,2,2))
        n=front(frame("pick up the red key"),(4,2,0))
        for i in range(2):
            selected(model,b,5,n,i)
        self.assertEqual(len(model.cells),1)
        cell=next(iter(model.cells.values()))
        self.assertEqual(cell.count[5],2)
        self.assertEqual(cell.effect[5],2)
        saved=model.checkpoint()
        restored=SelectedTaskCells.restore(saved)
        self.assertEqual(saved,restored.checkpoint())
        with self.assertRaises(ValueError):
            SelectedTaskCells.restore(saved+b"x")

    def test_disabled_variant_keeps_original_parent_decision(self):
        model=SelectedTaskCells(enabled=False)
        b=frame("pick up the red ball")
        adapter=OriginalMissionAdapter()
        adapter.reset_public(b)
        model.start_session(adapter,"nr-m1q-native-no-action",live=False)
        choice=model.choose(b)
        self.assertIn(choice["action"],range(7))
        self.assertNotEqual(choice["status"],"NRM1Q_LOCAL_REAL_PUBLIC_TASK_EFFECT")

if __name__=="__main__":unittest.main()
