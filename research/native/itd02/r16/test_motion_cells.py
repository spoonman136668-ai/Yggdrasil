"""R16 original source-only native motion-evidence tests, no new world."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r16.motion_cells import MotionCells

def public(direction=0,held=False,scene=0):
    frame=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    if scene:frame[2][3]=[4,0,1]
    if held:frame[3][6]=[5,4,0]
    return {"image":frame,"direction":direction,"mission":MISSION}

def selected(model,original,action,after,name):
    adapter=DoorKeyPublicAdapter()
    adapter.reset_public(original)
    model.start_session(adapter,name,live=False)
    adapter.submit(action)
    adapter.complete(after,0.0,False,False)
    return model.learn_selected(adapter,original,after)

class TestNativeR16SelectedMotion(unittest.TestCase):
    def test_actual_source_same_heading_visual_effect_beats_camera_turn(self):
        actor=MotionCells()
        start=public(0);turn=public(1);progress=public(0,scene=1)
        selected(actor,start,0,turn,"r16-source-rotate")
        selected(actor,start,3,progress,"r16-source-scene-change")
        self.assertEqual(actor.samples,2)
        self.assertEqual(actor.local.samples,2)
        choice=actor.choose(start)
        self.assertEqual(choice["action"],3)
        self.assertEqual(choice["status"],"SELECT_NATIVE_LEARNED_SAME_HEADING_PUBLIC_EFFECT")
        raw=actor.checkpoint()
        restored=MotionCells.restore(raw)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.choose(start),choice)
        with self.assertRaises(ValueError):MotionCells.restore(raw+b"0")

    def test_original_source_with_no_progress_escapes_action_cycle(self):
        actor=MotionCells()
        before=public(0)
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(before)
        actor.start_session(adapter,"r16-native-unrewarded",live=True)
        chosen=[]
        for index in range(9):
            proposal=actor.choose(before)
            action=proposal["action"]
            chosen.append(action)
            adapter.submit(action)
            adapter.complete(before,0.0,False,False)
            actor.learn_selected(adapter,before,before)
        self.assertGreaterEqual(len(set(chosen)),4)
        self.assertEqual(actor.samples,9)
        self.assertEqual(actor.local.samples,9)

    def test_private_state_and_selected_feedback_error_fail_closed(self):
        actor=MotionCells()
        before=public()
        with self.assertRaises(ValueError):
            actor.choose(dict(before,global_agent_pos=[2,2]))
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(before)
        actor.start_session(adapter,"r16-reject")
        with self.assertRaises(ValueError):actor.learn_selected(adapter,before,before)
        adapter.submit(2)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,before,before)
        adapter.complete(before,0.0,False,False)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,public(direction=1),before)
        self.assertEqual(actor.samples,0)
        actor.learn_selected(adapter,before,before)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,before,before)
        self.assertEqual(actor.samples,1)

if __name__=="__main__":unittest.main()
