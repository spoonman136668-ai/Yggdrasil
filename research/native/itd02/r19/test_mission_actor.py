"""R19 source-only integration regression and true-mission preservation, no env."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r17.successor_cells import SuccessorCells
from research.native.itd02.r19.mission_actor import MissionActor

def public(mission=MISSION,front=1):
    p={"image":[[[1,0,0] for _ in range(7)] for _ in range(7)],
       "direction":0,"mission":mission}
    p["image"][3][5]=[front,0,0]
    return p

class R19ActorIntegrationTest(unittest.TestCase):
    def test_legacy_native_doorkey_exact_original_selection_and_checkpoint(self):
        p=public()
        a=MissionActor()
        a.begin(p)
        baseline=SuccessorCells()
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(p)
        baseline.start_session(adapter,"r19-original-doorkey",live=True)
        original=baseline.choose(p)
        integrated=a.choose()
        self.assertEqual(integrated["action"],original["action"])
        self.assertEqual(integrated["reason"],original["status"])
        self.assertEqual(a.original.checkpoint(),baseline.checkpoint())
        self.assertEqual(a.mode,"ORIGINAL_DOORKEY_UNCHANGED")
        self.assertEqual(a.boundary.current["mission"],MISSION)
        action=integrated["action"]
        a.commit(action)
        adapter.submit(action)
        after=public(front=4)
        adapter.complete(after,0.0,False,False)
        baseline.learn_selected(adapter,p,after)
        r=a.feedback(action,after,0.0)
        self.assertEqual(a.original.checkpoint(),baseline.checkpoint())
        self.assertIsNotNone(r["legacy_receipt"])
        self.assertEqual(a.boundary.current["mission"],MISSION)

    def test_original_unlock_mission_enters_separate_native_actor_without_spoofing(self):
        unlock=public("open the door")
        a=MissionActor()
        a.begin(unlock)
        self.assertEqual(a.mode,"NATIVE_NEW_MISSION_PUBLIC_SELECTED")
        self.assertIsNone(a.legacy)
        before_original=a.original.checkpoint()
        choice=a.choose()
        self.assertIn(choice["action"],range(7))
        self.assertEqual(choice["mode"],a.mode)
        self.assertEqual(a.boundary.current["mission"],"open the door")
        a.commit(choice["action"])
        after=public("open the door",front=4)
        receipt=a.feedback(choice["action"],after,0.0)
        self.assertEqual(receipt["public_receipt"]["action"],choice["action"])
        self.assertIsNone(receipt["legacy_receipt"])
        self.assertEqual(a.original.checkpoint(),before_original)
        self.assertEqual(a.boundary.events[0]["public_after"]["mission"],"open the door")
        self.assertEqual(sum(a.counts),1)
        snap=a.checkpoint()
        b=MissionActor.restore(snap)
        self.assertEqual(b.checkpoint(),snap)
        self.assertEqual(b.choose(),a.choose())

    def test_new_goal_only_mission_cold_restore_and_true_terminal(self):
        a=MissionActor();a.begin(public("get to the green goal square"))
        q=a.choose();a.commit(q["action"])
        with self.assertRaises(ValueError):
            a.feedback(7,public("get to the green goal square"),0)
        self.assertEqual(len(a.boundary.events),0)
        with self.assertRaises(ValueError):
            a.feedback(q["action"],public("open the door"),0)
        self.assertEqual(len(a.boundary.events),0)
        receipt=a.feedback(q["action"],public("get to the green goal square"),1.0,True)
        self.assertEqual(receipt["public_receipt"]["terminated"],True)
        with self.assertRaises(ValueError):a.choose()
        cold=MissionActor.restore(a.checkpoint())
        self.assertTrue(cold.boundary.finished)
        with self.assertRaises(ValueError):cold.choose()

    def test_source_private_fields_rejected_before_action(self):
        a=MissionActor()
        p=public("open the door");p["agent_pos"]=[1,2]
        with self.assertRaises(ValueError):a.begin(p)
        self.assertIsNone(a.mode)
        q=MissionActor();q.begin(public("open the door"))
        self.assertEqual(q.original.samples,0)
        with self.assertRaises(ValueError):q.commit(True)
        with self.assertRaises(ValueError):q.commit(-1)
        snap=q.checkpoint()
        with self.assertRaises(ValueError):MissionActor.restore(snap+b"x")
        self.assertEqual(MissionActor.restore(snap).checkpoint(),snap)

if __name__=="__main__":unittest.main()
