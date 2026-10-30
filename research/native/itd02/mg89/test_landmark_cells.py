"""MG89 source-only landmark correspondence, negative and cold-process tests."""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg89.landmark_cells import LandmarkLinkCells,patch_ids
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

def selected(agent,before,after,action):
    a=OriginalMissionAdapter()
    a.reset_public(before)
    agent.start_session(a,"mg89-original-selected-fixture",live=False)
    a.submit(action)
    a.complete(after,0.0,False,False)
    return agent.learn_selected(a,before,after)

class LandmarkSourceTest(unittest.TestCase):
    def make_view(self,mission="pick up the red ball"):
        x=frame(mission)
        x["image"][1][1]=[4,0,1]
        x["image"][2][1]=[5,0,0]
        return x

    def test_only_selected_public_landmarks_create_persistent_links(self):
        model=LandmarkLinkCells()
        view=self.make_view()
        self.assertTrue(patch_ids(view))
        self.assertEqual(model.choose(view)["action"],0)
        selected(model,view,view,0)
        self.assertEqual(model.samples,1)
        self.assertEqual(model.events[0]["count"],1)
        self.assertGreater(model.events[0]["novel"],0)
        self.assertGreater(model.events[0]["matched"],0)
        self.assertTrue(model.links)
        self.assertEqual(sum(model.events[i]["count"] for i in range(7)),1)
        self.assertEqual(len(model.landmarks),model.events[0]["novel"])

    def test_no_unselected_feedback_or_cross_mission(self):
        model=LandmarkLinkCells()
        before=self.make_view()
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"mg89-unselected",live=False)
        saved=model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn_selected(adapter,before,before)
        self.assertEqual(model.checkpoint(),saved)
        selected(model,before,before,0)
        other=self.make_view("pick up the blue ball")
        self.assertNotIn(__import__("research.native.itd02.r10.public_adapter",
                                  fromlist=["digest"]).digest(other),
                         model.parent.parent.cells)

    def test_source_cold_restore_in_independent_python_process(self):
        model=LandmarkLinkCells()
        view=self.make_view()
        selected(model,view,view,0)
        raw=model.checkpoint()
        self.assertEqual(LandmarkLinkCells.restore(raw).checkpoint(),raw)
        with self.assertRaises(ValueError):
            LandmarkLinkCells.restore(raw+b"!")
        with tempfile.TemporaryDirectory() as root:
            path=os.path.join(root,"checkpoint.bin")
            with open(path,"wb") as f:
                f.write(raw)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg89.landmark_cells import LandmarkLinkCells; "
                    "x=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert LandmarkLinkCells.restore(x).checkpoint()==x")
            subprocess.run([sys.executable,"-B","-c",script,path],
                           check=True,timeout=30)

    def test_no_semantic_goal_shortcut(self):
        model=LandmarkLinkCells()
        a=self.make_view()
        choice=model.choose(a)
        self.assertEqual(choice["status"],"MG89_SELECTED_PUBLIC_LANDMARK_LINKS")
        self.assertFalse(choice["external_fallback"])
        self.assertIn(choice["action"],range(7))

if __name__=="__main__":
    unittest.main()
