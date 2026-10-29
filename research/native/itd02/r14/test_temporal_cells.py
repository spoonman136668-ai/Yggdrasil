"""R14 original selected R10 feedback and source-only cold temporal memory tests."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r14.temporal_cells import TemporalCells

def public():
    image=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    image[3][5]=[5,0,0]
    return {"image":image,"direction":1,"mission":MISSION}

class R14PublicTemporalTests(unittest.TestCase):
    def test_exact_original_selected_step_changes_temporal_action_and_cold_restore(self):
        source=public()
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(source)
        learner=PublicAffordanceCells()
        learner.start_session(adapter,"r14-authentic-selected-only-unit")
        memory=TemporalCells()
        first=memory.decide(learner,source)
        self.assertIn(first["action"],range(7))
        adapter.submit(first["action"])
        event=adapter.complete(source,0.0,False,False)
        learner.learn_selected(adapter)
        memory.learn_selected(source,first["action"],source,event)
        self.assertEqual(memory.steps,1)
        second=memory.decide(learner,source)
        self.assertNotEqual(first["action"],second["action"])
        cp=memory.checkpoint()
        self.assertEqual(TemporalCells.restore(cp).checkpoint(),cp)
        self.assertEqual(TemporalCells.restore(cp).decide(learner,source),second)
        with self.assertRaises(ValueError):
            TemporalCells.restore(cp+b"0")
        with self.assertRaises(ValueError):
            memory.learn_selected(source,second["action"],source,event)
        self.assertEqual(memory.steps,1)
    def test_private_observation_and_counterfactual_denied(self):
        learner=PublicAffordanceCells()
        memory=TemporalCells()
        source=public()
        with self.assertRaises(ValueError):
            memory.decide(learner,dict(source,private_agent_pos=[1,1]))
        with self.assertRaises(ValueError):
            memory.decide(learner,dict(source,mission="secret answer"))
        with self.assertRaises(ValueError):
            memory.learn_selected(source,7,source,{"action":7})
        self.assertEqual(memory.steps,0)

if __name__=="__main__":unittest.main()
