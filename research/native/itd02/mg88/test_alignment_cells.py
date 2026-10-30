"""MG88 independent source-free fixtures; NOT original-world learning evidence."""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg88.alignment_cells import PublicAlignmentCells,public_alignment
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.r10.public_adapter import digest

def submit_selected(model,before,after,action,reward=0.0):
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    model.start_session(adapter,"mg88-authentic-public-fixture",live=False)
    adapter.submit(action)
    adapter.complete(after,float(reward),False,False)
    return model.learn_selected(adapter,before,after)

class MG88PublicAlignmentTest(unittest.TestCase):
    def test_source_selected_learner_maintains_action_alignment_counts(self):
        agent=PublicAlignmentCells()
        before=frame()
        self.assertEqual(agent.choose(before)["action"],0)
        after=frame(heading=1)
        submit_selected(agent,before,after,0)
        self.assertEqual(agent.samples,1)
        self.assertEqual(agent.events[0]["count"],1)
        self.assertEqual(agent.events[0]["turns"],1)
        self.assertEqual(agent.parent.cells[digest(before)][0]["count"],1)
        self.assertEqual(agent.choose(before)["action"],1)

    def test_same_visible_frame_is_zero_shift_only(self):
        before=frame()
        self.assertEqual(public_alignment(before,before),(0,0))
        agent=PublicAlignmentCells()
        submit_selected(agent,before,before,2)
        self.assertEqual(agent.events[2]["shift"],{"0,0":1})
        self.assertEqual(agent.events[2]["unresolved"],0)

    def test_unselected_does_not_create_action_event(self):
        model=PublicAlignmentCells()
        before=frame()
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"mg88-unselected",live=False)
        wire=model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn_selected(adapter,before,frame(heading=1))
        self.assertEqual(wire,model.checkpoint())

    def test_mission_isolation_and_checked_cold_process(self):
        model=PublicAlignmentCells()
        before=frame("pick up the red ball")
        other=frame("pick up the blue ball")
        submit_selected(model,before,frame("pick up the red ball",heading=1),0)
        self.assertNotIn(digest(other),model.parent.cells)
        wire=model.checkpoint()
        self.assertEqual(PublicAlignmentCells.restore(wire).checkpoint(),wire)
        with self.assertRaises(ValueError):
            PublicAlignmentCells.restore(wire+b"x")
        with tempfile.TemporaryDirectory() as temp:
            p=os.path.join(temp,"model.bin")
            with open(p,"wb") as f:f.write(wire)
            cmd=("import pathlib,sys; "
                 "from research.native.itd02.mg88.alignment_cells import PublicAlignmentCells; "
                 "v=pathlib.Path(sys.argv[1]).read_bytes(); "
                 "assert PublicAlignmentCells.restore(v).checkpoint()==v")
            subprocess.run([sys.executable,"-B","-c",cmd,p],check=True,timeout=30)

if __name__=="__main__":
    unittest.main()
