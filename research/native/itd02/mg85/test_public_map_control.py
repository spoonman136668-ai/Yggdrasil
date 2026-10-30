"""MG85 source-only regression of CONVENTIONAL public-map positive control."""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg85.public_map_control import PublicMapControl,walkable
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

class PublicMapTest(unittest.TestCase):
    def start(self,agent,view):
        a=OriginalMissionAdapter()
        a.reset_public(view)
        agent.start_session(a,"mg85-fixture",live=False)
        return a

    def test_public_coordinates_and_wall_mask(self):
        agent=PublicMapControl()
        view=frame()
        view["image"][3][5]=[2,0,0]
        self.start(agent,view)
        self.assertEqual(agent.grid["1,0"],[2,0,0])
        self.assertFalse(walkable([2,0,0]))
        self.assertTrue(walkable([1,0,0]))
        self.assertFalse(walkable([4,0,2]))

    def test_original_selected_forward_odometry_and_checkpoint(self):
        agent=PublicMapControl()
        view=frame()
        adapter=self.start(agent,view)
        adapter.submit(2)
        adapter.complete(view,0.0,False,False)
        agent.learn_selected(adapter,view,view)
        self.assertEqual(agent.xy,(1,0))
        self.assertEqual(agent.samples,1)
        self.assertIn(agent.choose(view)["action"],range(7))
        blob=agent.checkpoint()
        self.assertEqual(PublicMapControl.restore(blob).checkpoint(),blob)
        with self.assertRaises(ValueError):
            PublicMapControl.restore(blob+b"broken")
        with tempfile.TemporaryDirectory() as tmp:
            p=os.path.join(tmp,"state.bin")
            with open(p,"wb") as f:f.write(blob)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg85.public_map_control import PublicMapControl; "
                    "s=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert PublicMapControl.restore(s).checkpoint()==s")
            subprocess.run([sys.executable,"-B","-c",script,p],timeout=30,check=True)

    def test_visible_goal_pickup_only_while_hands_free(self):
        agent=PublicMapControl()
        view=frame("pick up the red ball")
        view["image"][3][5]=[6,0,0]
        self.start(agent,view)
        self.assertEqual(agent.choose(view)["action"],3)
        self.assertEqual(agent.choose(view)["status"],"MG85_PUBLIC_MISSION_PICKUP")

    def test_unselected_observation_cannot_increment_samples(self):
        agent=PublicMapControl()
        before=frame()
        adapter=self.start(agent,before)
        blob=agent.checkpoint()
        with self.assertRaises(ValueError):
            agent.learn_selected(adapter,before,before)
        self.assertEqual(agent.checkpoint(),blob)

if __name__=="__main__":
    unittest.main()
