"""MG86 public-only model-based conventional control custody, no MiniGrid steps."""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg86.public_map_repair import RepairedMapControl
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.mg82.test_effect_cells import MG82PublicEffectTest

def started(model,ob):
    a=OriginalMissionAdapter()
    a.reset_public(ob)
    model.start_session(a,"mg86-original-source-fixture",live=False)
    return a

def selected(model,before,action,after):
    a=OriginalMissionAdapter()
    a.reset_public(before)
    a.submit(action)
    a.complete(after,0.0,False,False)
    model.learn_selected(a,before,after)

class MG86Control(unittest.TestCase):
    def test_locked_door_and_matching_selected_key(self):
        ob=frame("pick up the blue ball")
        ob["image"][3][5]=[5,1,0]
        model=RepairedMapControl()
        started(model,ob)
        self.assertEqual(model.choose(ob)["action"],3)
        after=frame("pick up the blue ball")
        selected(model,ob,3,after)
        self.assertEqual(model.carrying,5)
        self.assertEqual(model.key_color,1)
        locked=frame("pick up the blue ball")
        locked["image"][3][5]=[4,1,2]
        self.assertEqual(model.choose(locked)["action"],5)
        other=frame("pick up the blue ball")
        other["image"][3][5]=[4,0,2]
        self.assertNotEqual(model.choose(other)["action"],5)

    def test_key_drop_only_after_opened_with_known_target_and_no_repickup(self):
        ob=frame("pick up the blue ball")
        model=RepairedMapControl()
        started(model,ob)
        model.carrying=5
        model.key_color=0
        model.opened=1
        model.grid["2,1"]=[6,2,0]
        self.assertEqual(model.choose(ob)["action"],4)
        after=frame("pick up the blue ball")
        after["image"][3][5]=[5,0,0]
        selected(model,ob,4,after)
        self.assertTrue(model.deposited_key)
        self.assertIsNone(model.carrying)
        # A dropped key is not immediately reacquired without a new
        # publicly observed locked door.
        self.assertNotEqual(model.choose(after)["action"],3)
        self.assertLess(model.samples,2)

    def test_blocked_original_forward_cannot_phantom_move(self):
        before=frame()
        before["image"][3][5]=[2,0,0]
        model=RepairedMapControl()
        started(model,before)
        previous=model.xy
        selected(model,before,2,before)
        self.assertEqual(model.xy,previous)
        self.assertEqual(model.movement_failures,1)

    def test_cold_process_canonical_and_corrupt_rejected(self):
        model=RepairedMapControl()
        ob=frame()
        started(model,ob)
        selected(model,ob,0,frame(heading=3))
        blob=model.checkpoint()
        self.assertEqual(RepairedMapControl.restore(blob).checkpoint(),blob)
        with self.assertRaises(ValueError):
            RepairedMapControl.restore(blob+b"x")
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,"mem.bin")
            with open(path,"wb") as f:f.write(blob)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg86.public_map_repair import RepairedMapControl; "
                    "b=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert RepairedMapControl.restore(b).checkpoint()==b")
            subprocess.run([sys.executable,"-B","-c",script,path],timeout=30,check=True)

    def test_unselected_feedback_does_not_change_memory(self):
        ob=frame()
        model=RepairedMapControl()
        a=started(model,ob)
        saved=model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn_selected(a,ob,ob)
        self.assertEqual(saved,model.checkpoint())

if __name__=="__main__":
    unittest.main()
