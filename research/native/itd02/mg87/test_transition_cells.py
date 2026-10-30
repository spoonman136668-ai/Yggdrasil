"""MG87 source-only frozen native learning and baseline regressions.

Engineering fixtures do not establish original-world task performance.
"""
import os
import subprocess
import sys
import tempfile
import unittest

from research.native.itd02.mg87.transition_cells import PublicTransitionCells
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.r10.public_adapter import digest

def picked(agent,before,after,action,reward=0.0,terminal=False):
    a=OriginalMissionAdapter()
    a.reset_public(before)
    agent.start_session(a,"mg87-fixture-only",live=False)
    a.submit(action)
    a.complete(after,float(reward),terminal,False)
    return agent.learn_selected(a,before,after)

class PublicLearnTest(unittest.TestCase):
    def test_real_selected_successor_and_mission_separation(self):
        a=PublicTransitionCells("local")
        first=frame("pick up the red ball")
        second=frame("pick up the red ball",heading=1)
        self.assertEqual(a.choose(first)["action"],0)
        picked(a,first,second,0)
        row=a.cells[digest(first)][0]
        self.assertEqual(row["count"],1)
        self.assertEqual(row["next"],{digest(second):1})
        self.assertEqual(a.samples,1)
        self.assertNotIn(digest(frame("pick up the blue ball")),a.cells)
        self.assertEqual(a.choose(first)["action"],1)

    def test_reward_value_is_from_selected_original_feedback_only(self):
        a=PublicTransitionCells("td")
        before=frame()
        after=frame(heading=1)
        picked(a,before,after,0,reward=.8,terminal=True)
        self.assertEqual(a.cells[digest(before)][0]["q"],200)
        self.assertEqual(a.samples,1)
        self.assertEqual(a.choose(before)["action"],0)
        self.assertGreater(a.cells[digest(before)][0]["q"],0)

    def test_count_mode_cannot_use_next_effect_for_action_ranking(self):
        before=frame()
        after=frame(heading=1)
        a=PublicTransitionCells("count")
        b=PublicTransitionCells("local")
        for actor in (a,b):
            picked(actor,before,after,0)
            self.assertEqual(actor.samples,1)
            self.assertEqual(actor.choose(before)["action"],1)
            self.assertEqual(actor.cells[digest(before)][0]["next"],{digest(after):1})

    def test_unselected_source_rejected_without_learning(self):
        a=PublicTransitionCells("local")
        before=frame()
        original=OriginalMissionAdapter()
        original.reset_public(before)
        with self.assertRaises(ValueError):
            a.learn_selected(original,before,frame(heading=1))
        self.assertEqual(a.samples,0)
        self.assertEqual(a.cells,{})

    def test_exact_cold_process_and_tamper_reject(self):
        a=PublicTransitionCells("local")
        picked(a,frame(),frame(heading=1),0)
        wire=a.checkpoint()
        self.assertEqual(PublicTransitionCells.restore(wire).checkpoint(),wire)
        with self.assertRaises(ValueError):
            PublicTransitionCells.restore(wire+b"x")
        with tempfile.TemporaryDirectory() as root:
            path=os.path.join(root,"checkpoint.bin")
            with open(path,"wb") as f: f.write(wire)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg87.transition_cells import PublicTransitionCells; "
                    "b=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert PublicTransitionCells.restore(b).checkpoint()==b")
            subprocess.run([sys.executable,"-B","-c",script,path],
                           check=True,timeout=30)

if __name__=="__main__":
    unittest.main()
