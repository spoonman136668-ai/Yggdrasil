"""R14 source-only selected-event regression, no original environment run."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter,MISSION
from research.native.itd02.r14.episodic_cells import EpisodicCells


def public(direction=0):
    frame=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    frame[3][5]=[5,4,0]
    return {"image":frame,"direction":direction,"mission":MISSION}


class R14SourceSelectedOnly(unittest.TestCase):
    def test_selected_nonself_evidence_beats_repeated_self_loop_and_restores(self):
        initial=public(0);moved=public(1)
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(initial)
        model=EpisodicCells()
        model.start_session(adapter,"r14-focused-original-public")
        first=model.propose(initial)
        self.assertIn(first["action"],range(7))
        self.assertEqual(first["status"],"SELECT_NATIVE_BASE_EXPLORATION")
        self.assertEqual(model.samples,0)
        adapter.submit(0)
        adapter.complete(initial,0.0,False,False)
        model.learn_selected(adapter)
        with self.assertRaises(ValueError):model.learn_selected(adapter)
        self.assertEqual(model.samples,1)
        adapter.submit(1)
        adapter.complete(moved,0.0,False,False)
        model.learn_selected(adapter)
        self.assertEqual(model.samples,2)
        result=model.propose(initial)
        self.assertEqual(result["action"],1)
        self.assertEqual(result["status"],"SELECT_NATIVE_LEARNED_PUBLIC_TRANSITION_NOVELTY")
        self.assertFalse(result["external_fallback"])
        blob=model.checkpoint()
        restored=EpisodicCells.restore(blob)
        self.assertEqual(restored.checkpoint(),blob)
        self.assertEqual(restored.propose(initial),result)
        with self.assertRaises(ValueError):EpisodicCells.restore(blob+b"0")
        with self.assertRaises(ValueError):EpisodicCells.restore(blob[:-1]+b"x")

    def test_original_positive_reward_stays_ahead_of_transition_novelty(self):
        adapter=DoorKeyPublicAdapter()
        unchanged=public(0);changed=public(1)
        adapter.reset_public(unchanged)
        agent=EpisodicCells()
        agent.start_session(adapter,"r14-original-reward-priority")
        adapter.submit(0)
        adapter.complete(unchanged,1.0,False,False)
        agent.learn_selected(adapter)
        adapter.submit(1)
        adapter.complete(changed,0.0,False,False)
        agent.learn_selected(adapter)
        chosen=agent.propose(unchanged)
        self.assertEqual(chosen["status"],"SELECT_NATIVE_OBSERVED_POSITIVE_REWARD")
        self.assertEqual(chosen["action"],0)
        self.assertEqual(agent.samples,2)

    def test_bad_public_and_unreturned_event_fail_without_updates(self):
        adapter=DoorKeyPublicAdapter()
        original=public()
        adapter.reset_public(original)
        model=EpisodicCells()
        model.start_session(adapter,"r14-strict-validation")
        with self.assertRaises(ValueError):
            model.propose(dict(original,private_agent_pos=[1,2]))
        with self.assertRaises(ValueError):
            model.propose(dict(original,mission="hidden target"))
        with self.assertRaises(ValueError):
            model.learn_selected(adapter)
        self.assertEqual(model.samples,0)
        self.assertEqual(model.native.samples,0)
        self.assertFalse(model.transitions)
        adapter.submit(2)
        with self.assertRaises(ValueError):model.learn_selected(adapter)
        self.assertEqual(model.samples,0)
        adapter.complete(original,0.0,False,False)
        model.learn_selected(adapter)
        self.assertEqual(model.samples,1)
        self.assertEqual(model.native.samples,1)


if __name__=="__main__": unittest.main()
