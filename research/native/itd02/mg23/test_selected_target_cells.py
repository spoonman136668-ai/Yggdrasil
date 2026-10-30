"""MG23 local-cell source-only regression, not an original world experiment."""
import unittest
from research.native.itd02.mg23.selected_target_cells import TargetCreditCells, observed_key
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
RED="pick up the red box"
BLUE="pick up the blue box"

def frame(mission,heading=0,pixel=(1,0,0)):
    img=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    img[3][5]=list(pixel)
    return {"mission":mission,"direction":heading,"image":img}

class MG23SourcePublicTargetAndCredit(unittest.TestCase):
    def test_local_context_selected_effect_reward_and_cold(self):
        red=frame(RED,0,(7,0,0));gone=frame(RED)
        blue=frame(BLUE,0,(7,0,0))
        agent=TargetCreditCells()
        source=OriginalMissionAdapter();source.reset_public(red)
        agent.start_session(source,"mg23-source-red-fit",live=False)
        source.submit(3);source.complete(gone,0.0,False,False)
        receipt=agent.learn_selected(source,red,gone)
        self.assertEqual(agent.samples,1)
        key=observed_key(red)
        self.assertEqual(agent.cells[key][3]["target"],1)
        chosen=agent.choose(red)
        self.assertEqual(chosen["action"],3)
        self.assertEqual(chosen["status"],"MG23_LOCAL_OWN_SELECTED_PUBLIC_TARGET_OR_TERMINAL_CREDIT")
        self.assertNotEqual(agent.choose(blue)["status"],
                            "MG23_LOCAL_OWN_SELECTED_PUBLIC_TARGET_OR_TERMINAL_CREDIT")
        live=OriginalMissionAdapter();live.reset_public(red)
        agent.start_session(live,"mg23-source-red-live",live=True)
        live.submit(4);live.complete(gone,0.0,False,False)
        with self.assertRaises(ValueError):
            agent.learn_selected(live,blue,gone)
        self.assertEqual(agent.samples,1)
        agent.learn_selected(live,red,gone)
        with self.assertRaises(ValueError):
            agent.learn_selected(live,red,gone)
        live.submit(6)
        after=frame(RED,1)
        live.complete(after,1.0,True,False)
        agent.learn_selected(live,gone,after)
        self.assertEqual(agent.samples,3)
        k2=observed_key(gone)
        self.assertEqual(agent.cells[k2][6]["delayed"],32)
        self.assertEqual(agent.cells[key][4]["delayed"],31)
        original=agent.checkpoint()
        restored=TargetCreditCells.restore(original)
        self.assertEqual(restored.checkpoint(),original)
        with self.assertRaises(ValueError):
            TargetCreditCells.restore(original+b"x")
        empty=OriginalMissionAdapter();empty.reset_public(blue)
        restored.start_session(empty,"mg23-new-episode",live=True)
        self.assertEqual(restored.trace,[])
        self.assertEqual(restored.cells[key][3]["target"],1)
    def test_no_reward_from_unselected_or_false_target(self):
        agent=TargetCreditCells()
        a=frame("pick up the yellow key",0,(5,4,0))
        source=OriginalMissionAdapter();source.reset_public(a)
        agent.start_session(source,"mg23-no-target-fit",live=False)
        source.submit(2);source.complete(a,0.0,False,False)
        agent.learn_selected(source,a,a)
        key=observed_key(a)
        self.assertEqual(agent.cells[key][2]["target"],0)
        self.assertEqual(agent.cells[key][2]["delayed"],0)
        with self.assertRaises(ValueError):
            agent.choose(frame("ignore mission",0,(5,4,0)))
if __name__=="__main__":
    unittest.main()
