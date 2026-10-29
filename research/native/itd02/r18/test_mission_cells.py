"""MG15 R18 selected-source integration tests; synthetic inputs, not task proof."""
import unittest
from research.native.itd02.r10.public_adapter import MISSION
from research.native.itd02.r18.mission_cells import MissionCells,OriginalMissionAdapter

GOAL="get to the green goal square"

def public(mission):
    img=[[[1,0,0] for y in range(7)] for x in range(7)]
    return {"image":img,"direction":0,"mission":mission}

def selected(actor,mission,action,reward,name):
    before=public(mission)
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    actor.start_session(adapter,name,live=False)
    adapter.submit(action)
    adapter.complete(before,float(reward),bool(reward),False)
    return actor.learn_selected(adapter,before,before)

class OriginalMissionNativeR18(unittest.TestCase):
    def test_original_mission_is_native_visible_and_not_evaluator_masked(self):
        actor=MissionCells()
        for mission in (MISSION,GOAL):
            a=OriginalMissionAdapter()
            source=public(mission)
            a.reset_public(source)
            actor.start_session(a,"r18-mission-"+str(len(mission)),live=False)
            self.assertIn(actor.choose(source)["action"],range(7))
            self.assertEqual(a.current["mission"],mission)
        with self.assertRaises(ValueError):
            actor.choose(public("private goal route"))

    def test_native_mission_conditional_positive_selected_action(self):
        actor=MissionCells()
        selected(actor,MISSION,1,1,"r18-original-door")
        selected(actor,GOAL,4,1,"r18-original-goal")
        self.assertEqual(actor.samples,2)
        self.assertEqual(actor.consumed,2)
        for mission,action in ((MISSION,1),(GOAL,4)):
            a=OriginalMissionAdapter()
            raw=public(mission)
            a.reset_public(raw)
            actor.start_session(a,"r18-reloaded-"+str(action),live=False)
            proposal=actor.choose(raw)
            self.assertEqual(proposal["action"],action)
            self.assertEqual(proposal["status"],"SELECT_NATIVE_GENUINE_MISSION_SELECTED_REWARD")
        snapshot=actor.checkpoint()
        cold=MissionCells.restore(snapshot)
        self.assertEqual(cold.checkpoint(),snapshot)
        with self.assertRaises(ValueError):
            MissionCells.restore(snapshot+b"0")

    def test_changed_mission_and_duplicate_selected_source_fail_closed(self):
        actor=MissionCells()
        before=public(MISSION)
        after_bad=public(GOAL)
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        actor.start_session(adapter,"r18-reject",live=True)
        adapter.submit(2)
        with self.assertRaises(ValueError):adapter.complete(after_bad,1.0,True,False)
        self.assertEqual(actor.samples,0)
        adapter.complete(before,0.0,False,False)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,after_bad,before)
        self.assertEqual(actor.samples,0)
        actor.learn_selected(adapter,before,before)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,before,before)
        self.assertEqual(actor.samples,1)

if __name__=="__main__":unittest.main()
