"""MG83 source-only engineering negative and cold-process regressions."""
import os
import subprocess
import sys
import tempfile
import unittest

from research.native.itd02.mg83.revisit_cells import RevisitGuard
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

class MG83NativeRevisitTest(unittest.TestCase):
    def prime(self, agent, before):
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        agent.start_session(adapter,"mg83-prime",live=False)

    def selected(self, agent, before, action, after, n):
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        agent.start_session(adapter,"mg83-selected-"+str(n),live=False)
        adapter.submit(action)
        adapter.complete(after,0.0,False,False)
        agent.learn_selected(adapter,before,after)

    def test_repeated_identical_public_successor_triggers_probe(self):
        native=RevisitGuard()
        before=frame()
        after=frame(heading=1)
        self.prime(native,before)
        parent_action=native.parent.choose(before)["action"]
        for i in range(2):
            self.selected(native,before,parent_action,after,i)
        self.assertEqual(native.samples,2)
        self.assertEqual(native.parent.choose(before)["action"],parent_action)
        proposed=native.choose(before)
        self.assertNotEqual(proposed["action"],parent_action)
        self.assertEqual(proposed["status"],
                         "MG83_REVISITED_ORIGINAL_PUBLIC_CONSEQUENCE_ESCAPE")
        self.assertFalse(proposed["external_fallback"])

    def test_distinct_public_successor_not_falsely_a_revisit(self):
        native=RevisitGuard()
        before=frame()
        self.prime(native,before)
        action=native.parent.choose(before)["action"]
        self.selected(native,before,action,frame(heading=1),1)
        self.selected(native,before,action,frame(heading=2),2)
        self.assertEqual(native.choose(before)["action"],native.parent.choose(before)["action"])
        self.assertEqual(len(native.cells[observed_key(before)][action]["successors"]),2)

    def test_mission_isolation_exact_cold_restore(self):
        red=frame("pick up the red ball")
        blue=frame("pick up the blue ball")
        native=RevisitGuard()
        self.prime(native,red)
        action=native.parent.choose(red)["action"]
        self.selected(native,red,action,frame("pick up the red ball",heading=1),1)
        self.assertNotIn(observed_key(blue),native.cells)
        checkpoint=native.checkpoint()
        restored=RevisitGuard.restore(checkpoint)
        self.assertEqual(restored.checkpoint(),checkpoint)
        with self.assertRaises(ValueError):
            RevisitGuard.restore(checkpoint+b"x")
        with tempfile.TemporaryDirectory() as tmp:
            path=os.path.join(tmp,"native.bin")
            with open(path,"wb") as f: f.write(checkpoint)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg83.revisit_cells import RevisitGuard; "
                    "b=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert RevisitGuard.restore(b).checkpoint()==b")
            subprocess.run([sys.executable,"-B","-c",script,path],check=True,timeout=30)

    def test_unselected_action_cannot_create_effect(self):
        native=RevisitGuard()
        before=frame()
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        native.start_session(adapter,"mg83-unselected",live=False)
        saved=native.checkpoint()
        with self.assertRaises(ValueError):
            native.learn_selected(adapter,before,frame(heading=1))
        self.assertEqual(saved,native.checkpoint())

if __name__=="__main__":
    unittest.main()
