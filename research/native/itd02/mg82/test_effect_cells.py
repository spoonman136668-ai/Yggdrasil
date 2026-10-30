"""MG82 independent source-free regressions. NOT original-world science."""
import os
import subprocess
import sys
import tempfile
import unittest

from research.native.itd02.mg82.effect_cells import PublicEffectCells
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.mg23.selected_target_cells import observed_key

class MG82PublicEffectTest(unittest.TestCase):
    def train(self, model, before, action, after, index):
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"mg82-public-selected-"+str(index),live=False)
        adapter.submit(action)
        adapter.complete(after,0.0,False,False)
        model.learn_selected(adapter,before,after)

    def test_zero_effect_stalling_triggers_empirical_alternative(self):
        agent=PublicEffectCells(mode="effect")
        before=frame()
        parent_action=agent.parent.choose(before)["action"]
        for n in range(2):
            self.train(agent,before,parent_action,before,n)
        proposal=agent.choose(before)
        self.assertEqual(agent.samples,2)
        self.assertEqual(agent.cells[observed_key(before)][parent_action],
                         {"count":2,"changed":0})
        self.assertNotEqual(proposal["action"],parent_action)
        self.assertEqual(proposal["status"],"MG82_SELECTED_PUBLIC_EFFECT_EXPLORE")
        self.assertFalse(proposal["external_fallback"])

    def test_count_only_explores_but_effect_holds_observed_change(self):
        before=frame()
        after=frame(heading=1)
        actors=[PublicEffectCells(mode=m) for m in ("effect","count")]
        native=actors[0].parent.choose(before)["action"]
        for agent in actors:
            for i in range(2):
                self.train(agent,before,native,after,i)
        self.assertEqual(actors[0].choose(before)["action"],native)
        self.assertNotEqual(actors[1].choose(before)["action"],native)
        self.assertEqual(actors[1].choose(before)["status"],"MG82_COUNT_ONLY_EXPLORE")
        self.assertEqual(actors[1].cells[observed_key(before)][native]["changed"],2)

    def test_no_cross_mission_memory_and_corrupt_cold_reject(self):
        red=frame("pick up the red ball")
        blue=frame("pick up the blue ball")
        agent=PublicEffectCells()
        action=agent.parent.choose(red)["action"]
        self.train(agent,red,action,red,1)
        self.assertNotEqual(observed_key(red),observed_key(blue))
        self.assertEqual(agent.choose(blue)["action"],agent.parent.choose(blue)["action"])
        snapshot=agent.checkpoint()
        self.assertEqual(PublicEffectCells.restore(snapshot).checkpoint(),snapshot)
        with self.assertRaises(ValueError):
            PublicEffectCells.restore(snapshot+b"x")
        with tempfile.TemporaryDirectory() as root:
            path=os.path.join(root,"checkpoint.bin")
            with open(path,"wb") as target: target.write(snapshot)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg82.effect_cells import PublicEffectCells; "
                    "p=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert PublicEffectCells.restore(p).checkpoint()==p")
            subprocess.run([sys.executable,"-B","-c",script,path],
                           check=True,timeout=30)

    def test_unselected_feedback_rejected_without_mutation(self):
        agent=PublicEffectCells()
        before=frame()
        after=frame(heading=1)
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        agent.start_session(adapter,"mg82-negative",live=False)
        before_ck=agent.checkpoint()
        with self.assertRaises(ValueError):
            agent.learn_selected(adapter,before,after)
        self.assertEqual(agent.checkpoint(),before_ck)

if __name__=="__main__": unittest.main()
