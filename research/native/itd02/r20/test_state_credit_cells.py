"""MG16 R20 native source-only tests: exact public reward never globalizes."""
import unittest
from research.native.itd02.r10.public_adapter import MISSION
from research.native.itd02.r18.mission_cells import OriginalMissionAdapter,projected
from research.native.itd02.r20.state_credit_cells import StateCreditCells

GOAL="get to the green goal square"
def public(mission,direction=0):
    img=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    return {"image":img,"direction":direction,"mission":mission}
def session(actor,p,name,live=False):
    a=OriginalMissionAdapter();a.reset_public(p)
    actor.start_session(a,name,live=live)
    return a
def selected(actor,adapter,before,action,after,reward=0,terminal=False):
    adapter.submit(action)
    adapter.complete(after,float(reward),bool(terminal),False)
    return actor.learn_selected(adapter,before,after)

class R20ExactSourceCredit(unittest.TestCase):
    def test_positive_is_from_exact_source_context_not_mission_global(self):
        agent=StateCreditCells()
        a=public(MISSION,0);after=public(MISSION,1)
        s=session(agent,a,"r20-initial",live=False)
        selected(agent,s,a,2,after,1,True)
        self.assertEqual(agent.samples,1)
        other=public(MISSION,2)
        goal=public(GOAL,0)
        for target in (other,goal):
            session(agent,target,"r20-source-reset-"+str(target["direction"])+target["mission"],live=False)
            outcome=agent.choose(target)
            baseline=agent.parent.parent.choose(projected(target))
            self.assertEqual(outcome["action"],baseline["action"])
            self.assertEqual(outcome["status"],baseline["status"])
            self.assertFalse(outcome["external_fallback"])
        session(agent,a,"r20-source-exact",live=False)
        reward=agent.choose(a)
        self.assertEqual(reward["action"],2)
        self.assertEqual(reward["status"],"SELECT_NATIVE_EXACT_PUBLIC_REWARDED_SOURCE")
        snapshot=agent.checkpoint()
        cold=StateCreditCells.restore(snapshot)
        self.assertEqual(cold.checkpoint(),snapshot)
        with self.assertRaises(ValueError):StateCreditCells.restore(snapshot+b"0")
    def test_unchanged_public_positive_does_not_override(self):
        agent=StateCreditCells();p=public(GOAL)
        s=session(agent,p,"r20-public-unchanged")
        selected(agent,s,p,2,p,1,True)
        session(agent,p,"r20-public-unchanged-again")
        choice=agent.choose(p)
        original=agent.parent.parent.choose(projected(p))
        self.assertEqual(choice["action"],original["action"])
        self.assertEqual(choice["status"],original["status"])
    def test_mission_change_and_duplicate_selected_event_rejected(self):
        agent=StateCreditCells();p=public(MISSION);bad=public(GOAL)
        a=session(agent,p,"r20-original-selected",live=True)
        a.submit(1)
        with self.assertRaises(ValueError):a.complete(bad,1.0,True,False)
        self.assertEqual(agent.samples,0)
        a.complete(p,0.0,False,False)
        with self.assertRaises(ValueError):agent.learn_selected(a,bad,p)
        self.assertEqual(agent.samples,0)
        agent.learn_selected(a,p,p)
        with self.assertRaises(ValueError):agent.learn_selected(a,p,p)
        self.assertEqual(agent.samples,1)

if __name__=="__main__":unittest.main()
