"""MG91 source-only positive return-to-go, independent trained controls, cold tests.

These artificial source-shaped fixtures validate algorithms only, NOT authentic
original MiniGrid task-learning or heldout performance.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg91.independent_linear import IndependentLinearControl
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.r10.public_adapter import digest
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

def shaped():
    a=frame("pick up the red ball")
    b=frame("pick up the red ball",heading=1)
    c=frame("pick up the red ball",heading=2)
    return [{"seed":24,"success":True,"steps":[
        {"before":a,"before_sha":digest(a),"after_sha":digest(b),"action":0,
         "reward":0.,"terminated":False},
        {"before":b,"before_sha":digest(b),"after_sha":digest(c),"action":1,
         "reward":0.8,"terminated":True}
    ]}]

class MG91Training(unittest.TestCase):
    def test_both_models_exact_same_source_training_manifest(self):
        examples=shaped()
        native=PublicRewardPrototypes()
        linear=IndependentLinearControl()
        native.fit(examples)
        linear.fit(examples)
        self.assertEqual(native.data_sha,linear.data_sha)
        self.assertEqual(native.training_count,2)
        self.assertEqual(linear.training_count,2)
        self.assertGreater(native.examples[0]["value"],0)
        self.assertEqual(native.choose(examples[0]["steps"][0]["before"])["action"],0)
        self.assertIn(linear.choose(examples[0]["steps"][0]["before"])["action"],range(7))
        self.assertNotEqual(native.choose(examples[0]["steps"][0]["before"])["status"],
                            linear.choose(examples[0]["steps"][0]["before"])["status"])

    def test_cold_checkpoint_in_independent_os_process(self):
        for cls in (PublicRewardPrototypes,IndependentLinearControl):
            actor=cls()
            actor.fit(shaped())
            wire=actor.checkpoint()
            self.assertEqual(cls.restore(wire).checkpoint(),wire)
            with self.assertRaises(ValueError):
                cls.restore(wire+b"tamper")
            with tempfile.TemporaryDirectory() as folder:
                path=os.path.join(folder,"policy.bin")
                with open(path,"wb") as f:f.write(wire)
                module=("native_prototypes" if cls is PublicRewardPrototypes
                        else "independent_linear")
                script=("import pathlib,sys; "
                        "from research.native.itd02.mg91."+module+
                        " import "+cls.__name__+"; "
                        "b=pathlib.Path(sys.argv[1]).read_bytes(); "
                        "assert "+cls.__name__+".restore(b).checkpoint()==b")
                subprocess.run([sys.executable,"-B","-c",script,path],
                               timeout=30,check=True)

    def test_unselected_heldout_does_not_modify_learned_weights(self):
        a=shaped()[0]["steps"][0]["before"]
        for cls in (PublicRewardPrototypes,IndependentLinearControl):
            policy=cls()
            policy.fit(shaped())
            before=policy.checkpoint()
            adapter=OriginalMissionAdapter()
            adapter.reset_public(a)
            policy.start_session(adapter,"mg91-selected-fixture",live=False)
            with self.assertRaises(ValueError):
                policy.observe_selected(adapter,a,a)
            self.assertEqual(policy.checkpoint(),before)
            adapter.submit(0)
            adapter.complete(a,0.,False,False)
            policy.observe_selected(adapter,a,a)
            self.assertEqual(policy.prev,0)
            self.assertEqual(policy.data_sha,cls.restore(before).data_sha)

    def test_fail_closed_on_false_positive_training_source(self):
        wrong=shaped()
        wrong[0]["steps"][-1]["reward"]=0.
        for cls in (PublicRewardPrototypes,IndependentLinearControl):
            with self.assertRaises(ValueError):
                cls().fit(wrong)

if __name__=="__main__":
    unittest.main()
