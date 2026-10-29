import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter,MISSION
from research.native.itd02.r16.selected_novelty import NativeNovelty
def frame():
    image=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    return {"image":image,"direction":1,"mission":MISSION}
class TestR16OriginalSelectedPublicNovelty(unittest.TestCase):
    def test_seven_distinct_real_public_actions_and_cold_restore(self):
        v=frame();adapter=DoorKeyPublicAdapter();adapter.reset_public(v)
        native=NativeNovelty();native.start_session(adapter,"r16-original-public",live=True)
        chosen=[]
        for i in range(7):
            option=native.choose(v)
            self.assertEqual(option["status"],"SELECT_NATIVE_UNTRIED_PUBLIC_STATE_ACTION")
            a=option["action"];self.assertNotIn(a,chosen);chosen.append(a)
            adapter.submit(a)
            adapter.complete(v,0.0,False,False)
            native.learn_selected(adapter,v,v)
        self.assertEqual(len(set(chosen)),7)
        self.assertEqual(native.samples,7)
        self.assertEqual(native.steps,7)
        decision=native.choose(v)
        self.assertEqual(decision["status"],"SELECT_NATIVE_OBSERVED_PUBLIC_NOVELTY")
        cp=native.checkpoint()
        cold=NativeNovelty.restore(cp)
        self.assertEqual(cold.checkpoint(),cp)
        # An authenticated restored source session must produce the same public action.
        self.assertEqual(cold.choose(v),decision)
        with self.assertRaises(ValueError):NativeNovelty.restore(cp+b"0")
    def test_reject_unreturned_or_private_source(self):
        v=frame();adapter=DoorKeyPublicAdapter();adapter.reset_public(v)
        n=NativeNovelty();n.start_session(adapter,"r16-bad",live=True)
        with self.assertRaises(ValueError):n.learn_selected(adapter,v,v)
        with self.assertRaises(ValueError):n.choose(dict(v,private_pose=[1,2]))
        self.assertEqual(n.samples,0)
        self.assertEqual(n.steps,0)
if __name__=="__main__":unittest.main()
