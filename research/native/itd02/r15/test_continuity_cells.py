"""Focused R15 native original public selected consequence tests. No simulator."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r15.continuity_cells import NativeContinuity

def view(direction=0,held=True):
    image=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    if held:image[3][6]=[5,4,0]
    return {"image":image,"direction":direction,"mission":MISSION}

def experience(model,session,before,action,after,live=True):
    source=DoorKeyPublicAdapter()
    source.reset_public(before)
    model.start_session(source,session,live=live)
    source.submit(action)
    source.complete(after,0.0,False,False)
    return model.learn_selected(source,before,after)

class TestR15SourceContinuity(unittest.TestCase):
    def test_new_native_exploration_then_selected_object_retention(self):
        native=NativeContinuity()
        held=view();dropped=view(held=False);moved=view(direction=1)
        source=DoorKeyPublicAdapter()
        source.reset_public(held)
        native.start_session(source,"r15-zero-evidence",live=True)
        decision=native.choose(held)
        self.assertIn(decision["action"],range(7))
        self.assertFalse(decision["external_fallback"])
        self.assertEqual(decision["status"],"SELECT_NATIVE_UNKNOWN_PUBLIC_ACTION")
        source.submit(0)
        source.complete(dropped,0.0,False,False)
        native.learn_selected(source,held,dropped)
        with self.assertRaises(ValueError):native.learn_selected(source,held,dropped)
        experience(native,"r15-new-session",held,1,moved)
        self.assertEqual(native.samples,2)
        self.assertEqual(native.local.samples,2)
        decision=native.choose(held)
        self.assertEqual(decision["action"],1)
        self.assertEqual(decision["status"],"SELECT_NATIVE_LEARNED_PUBLIC_OBJECT_CONTINUITY")
        blob=native.checkpoint()
        cold=NativeContinuity.restore(blob)
        self.assertEqual(cold.checkpoint(),blob)
        self.assertEqual(cold.choose(held),decision)
        with self.assertRaises(ValueError):NativeContinuity.restore(blob+b"0")

    def test_untrusted_public_mismatch_must_not_mutate(self):
        model=NativeContinuity()
        before=view()
        private=dict(before,agent_pos=[2,2])
        with self.assertRaises(ValueError):model.choose(private)
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"r15-invalid-source")
        with self.assertRaises(ValueError):model.learn_selected(adapter,before,before)
        adapter.submit(2)
        with self.assertRaises(ValueError):model.learn_selected(adapter,before,before)
        adapter.complete(before,0.0,False,False)
        with self.assertRaises(ValueError):model.learn_selected(adapter,view(direction=1),before)
        self.assertEqual(model.samples,0)
        self.assertEqual(model.local.samples,0)
        self.assertEqual(model.memory,{})
        model.learn_selected(adapter,before,before)
        self.assertEqual(model.samples,1)

if __name__=="__main__":unittest.main()
