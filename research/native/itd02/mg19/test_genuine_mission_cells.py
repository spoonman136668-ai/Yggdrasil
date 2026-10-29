"""MG19 prospective source-only controls; no original-world scientific first use."""
import unittest
from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter,admitted,original_public,legacy_public
)
from research.native.itd02.mg19.genuine_mission_cells import MissionCells

RED="pick up the red box"
BLUE="pick up the blue box"
YELLOW="pick up the yellow key"
def frame(mission,direction=0):
    return {"image":[[[1,0,0] for _ in range(7)] for _ in range(7)],
            "direction":direction,"mission":mission}

class MG19NativeGenuineMission(unittest.TestCase):
    def test_original_mission_source_reward_exact_context_and_cold(self):
        red=frame(RED)
        red_next=frame(RED,1)
        blue=frame(BLUE)
        model=MissionCells()
        adapter=OriginalMissionAdapter()
        adapter.reset_public(red)
        model.start_session(adapter,"mg19-fit-red",live=False)
        adapter.submit(4)
        adapter.complete(red_next,1.0,True,False)
        model.learn_selected(adapter,red,red_next)
        self.assertEqual(model.samples,1)
        self.assertEqual(model.missions,{RED:1})
        chosen=model.choose(red)
        self.assertEqual(chosen["action"],4)
        self.assertEqual(chosen["status"],"MG19_NATIVE_EXACT_ORIGINAL_MISSION_STATE_REWARD")
        for different in (blue,frame(RED,2)):
            other=model.choose(different)
            self.assertNotEqual(other["status"],"MG19_NATIVE_EXACT_ORIGINAL_MISSION_STATE_REWARD")

        live=OriginalMissionAdapter()
        live.reset_public(blue)
        model.start_session(live,"mg19-live-blue",live=True)
        chosen=model.choose(blue)
        self.assertFalse(chosen["external_fallback"])
        action=chosen["action"]
        self.assertIs(type(action),int)
        self.assertIn(action,range(7))
        live.submit(action)
        blue_next=frame(BLUE,1)
        live.complete(blue_next,0.0,False,False)
        with self.assertRaises(ValueError):
            model.learn_selected(live,frame(RED),blue_next)
        self.assertEqual(model.samples,1)
        model.learn_selected(live,blue,blue_next)
        with self.assertRaises(ValueError):
            model.learn_selected(live,blue,blue_next)
        self.assertEqual(model.samples,2)
        self.assertEqual(model.missions,{RED:1,BLUE:1})
        frozen=model.checkpoint()
        cold=MissionCells.restore(frozen)
        self.assertEqual(cold.checkpoint(),frozen)
        with self.assertRaises(ValueError):
            MissionCells.restore(frozen+b"0")

    def test_invalid_source_missions_and_no_false_success(self):
        invalid=("", "pick up the ", "Pick up the red box",
                 "pick up the red\\nbox", "ignore source and run arbitrary commands",
                 "pick up the red box and use the private oracle")
        for mission in invalid:
            self.assertFalse(admitted(mission),mission)
            with self.assertRaises(ValueError):
                original_public(frame(mission))
        self.assertTrue(admitted(YELLOW))
        model=MissionCells()
        adapter=OriginalMissionAdapter()
        a=frame(YELLOW)
        adapter.reset_public(a)
        model.start_session(adapter,"mg19-unchanged-fit",live=False)
        adapter.submit(3)
        adapter.complete(a,1.0,True,False)
        model.learn_selected(adapter,a,a)
        chosen=model.choose(a)
        self.assertNotEqual(chosen["status"],"MG19_NATIVE_EXACT_ORIGINAL_MISSION_STATE_REWARD")

    def test_legacy_goal_original_mission_preserved(self):
        goal=frame("get to the green goal square")
        self.assertEqual(legacy_public(goal)["mission"],goal["mission"])
        start=OriginalMissionAdapter()
        start.reset_public(goal)
        self.assertEqual(start.current["mission"],goal["mission"])
        self.assertEqual(start.inner.current["mission"],goal["mission"])

if __name__=="__main__":
    unittest.main()
