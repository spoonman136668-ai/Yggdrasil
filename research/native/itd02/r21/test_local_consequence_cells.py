"""R21 evidence tests: real selected public consequences, not navigation simulation."""
import unittest
from research.native.itd02.r10.public_adapter import MISSION
from research.native.itd02.r18.mission_cells import OriginalMissionAdapter
from research.native.itd02.r21.local_consequence_cells import LocalConsequenceCells,context

GOAL="get to the green goal square"
def view(mission=MISSION,direction=0,far=1,near=1):
    image=[[[1,0,0] for j in range(7)] for i in range(7)]
    image[0][0]=[far,0,0]
    image[3][5]=[near,0,0]
    return {"image":image,"direction":direction,"mission":mission}
def learn(agent,before,action,after,reward=0,terminal=False,live=False):
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    agent.start_session(adapter,"r21-selected-source-"+str(agent.samples),live=live)
    adapter.submit(action)
    adapter.complete(after,float(reward),bool(terminal),False)
    return agent.learn_selected(adapter,before,after)

class R21LocalOriginalEvidenceTests(unittest.TestCase):
    def test_distinct_full_source_state_shares_observed_local_consequence(self):
        actor=LocalConsequenceCells()
        a=view(far=1)
        after=view(far=2)
        novel=view(direction=3,far=7)
        self.assertNotEqual(a,novel)
        self.assertEqual(context(a),context(novel))
        for _ in range(2):learn(actor,a,5,after)
        self.assertEqual(actor.local[context(a)][5]["changed"],2)
        self.assertEqual(actor.samples,2)
        chosen=actor.choose(novel)
        self.assertIn(chosen["action"],range(7))
        cold=LocalConsequenceCells.restore(actor.checkpoint())
        self.assertEqual(cold.checkpoint(),actor.checkpoint())
        self.assertEqual(cold.choose(novel),chosen)
        with self.assertRaises(ValueError):
            LocalConsequenceCells.restore(actor.checkpoint()+b"0")
    def test_different_public_local_cell_or_mission_cannot_inherit(self):
        actor=LocalConsequenceCells()
        a=view(mission=GOAL)
        after=view(mission=GOAL,far=2)
        for _ in range(2):learn(actor,a,4,after)
        for candidate in (view(mission=GOAL,near=6,direction=1),
                          view(mission=MISSION,direction=1)):
            adapter=OriginalMissionAdapter()
            adapter.reset_public(candidate)
            actor.start_session(adapter,"r21-independent-negative-source",live=False)
            chosen=actor.choose(candidate)
            baseline=actor.parent.choose(candidate)
            self.assertEqual(chosen["action"],baseline["action"])
            self.assertEqual(chosen["status"],baseline["status"])
    def test_headings_no_effects_and_changed_mission_fail_closed(self):
        actor=LocalConsequenceCells();a=view(mission=GOAL)
        turned=view(mission=GOAL,direction=1)
        for _ in range(2):
            learn(actor,a,1,turned)
            learn(actor,a,2,a)
        row=actor.local[context(a)]
        self.assertEqual(row[1]["changed"],0)
        self.assertEqual(row[1]["no_effect"],0)
        self.assertEqual(row[2]["no_effect"],2)
        fresh=OriginalMissionAdapter();fresh.reset_public(a)
        actor.start_session(fresh,"r21-no-effect-fallback",live=False)
        chosen=actor.choose(a);baseline=actor.parent.choose(a)
        self.assertEqual(chosen["action"],baseline["action"])
        self.assertEqual(chosen["status"],baseline["status"])
        before=actor.samples
        live=OriginalMissionAdapter();live.reset_public(a)
        actor.start_session(live,"r21-true-selected-feedback",live=True)
        live.submit(6)
        with self.assertRaises(ValueError):
            live.complete(view(mission=MISSION),1.0,True,False)
        self.assertEqual(actor.samples,before)
        live.complete(a,0.0,False,False)
        with self.assertRaises(ValueError):
            actor.learn_selected(live,view(mission=MISSION),a)
        self.assertEqual(actor.samples,before)
        actor.learn_selected(live,a,a)
        with self.assertRaises(ValueError):actor.learn_selected(live,a,a)
        self.assertEqual(actor.samples,before+1)

if __name__=="__main__":unittest.main()
