"""O22-V public three-actually-selected-action value units, never a simulator."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r1.native_policy import LocalCell,PublicGrid,features
from research.optimizer_o22v.delayed_cells import DelayedNativeCells,FittedRidge9


def state(x=2,y=3,direction=1,blocked=False,goal_x=6,goal_y=6):
    return {"x":x,"y":y,"direction":direction,
            "front_blocked":blocked,"goal_x":goal_x,"goal_y":goal_y}


class O22VAuthenticSourceOnly(unittest.TestCase):
    def test_original_R1_R3_source_remains_byte_identical(self):
        root=Path(__file__).resolve().parents[2]
        pins={
          "research/native/itd02/r1/native_policy.py":
              "3aa22b1e418a7f8cd9619c476f02b8c614917b16",
          "research/native/itd02/r3/navigator.py":
              "5348238f4ec2183bea29262659883391b5f429fd"
        }
        for path,expected in pins.items():
            b=(root/path).read_bytes().replace(b"\r\n",b"\n")
            git=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
            self.assertEqual(git,expected)

    def test_true_original_native_LocalCell_plasticity(self):
        m=DelayedNativeCells()
        self.assertIs(type(m.cells["0"][0]),LocalCell)
        before=m.predict(state(),0)
        for _ in range(7):
            m.learn(state(),0,1.0)
        self.assertGreater(m.predict(state(),0),before)
        self.assertEqual(m.cells["0"][0].updates,7)
        self.assertEqual(m.cells["1"][0].updates,0)
        self.assertEqual(m.actions,{"0":7,"1":0,"2":0})

    def test_source_selected_three_action_credit_not_hidden_action(self):
        from research.optimizer_o22v.evaluate import actual_windows
        s0=state(x=2,y=3)
        s1=state(x=2,y=3,direction=0)
        s2=state(x=3,y=3,direction=0)
        s3=state(x=4,y=3,direction=0)
        rows=[
          {"family":"MiniGrid-Dynamic-Obstacles-8x8-v0","seed":47101,"step":0,
           "before":s0,"chosen_action":0,"returned_after":s1,
           "terminated":False,"truncated":False},
          {"family":"MiniGrid-Dynamic-Obstacles-8x8-v0","seed":47101,"step":1,
           "before":s1,"chosen_action":2,"returned_after":s2,
           "terminated":False,"truncated":False},
          {"family":"MiniGrid-Dynamic-Obstacles-8x8-v0","seed":47101,"step":2,
           "before":s2,"chosen_action":2,"returned_after":s3,
           "terminated":True,"truncated":False}
        ]
        got=actual_windows({("MiniGrid-Dynamic-Obstacles-8x8-v0",47101):rows})
        self.assertEqual(len(got),1)
        self.assertEqual(got[0]["observed_selected_sequence_progress"],2/3)
        self.assertEqual(got[0]["observed_three_ACTUALLY_SELECTED_actions"],[0,2,2])
        # Zero event possible after terminal; no unexecuted action target.

    def test_strong_full_nine_feature_conventional_equal_training(self):
        native=DelayedNativeCells()
        conventional=FittedRidge9(True)
        for i in range(24):
            action=i%3
            b=state(direction=i%4,blocked=bool(i%2))
            value=[1.,-1.,0.5][action]
            native.learn(b,action,value)
            conventional.learn(b,action,value)
        conventional.finalize()
        self.assertEqual(conventional.events,native.events)
        self.assertEqual(conventional.actions,native.actions)
        self.assertEqual(len(features(PublicGrid(2,3,6,6,1,False))),9)
        self.assertTrue(all(-1<=conventional.predict(state(),a)<=1
                            for a in (0,1,2)))
        with self.assertRaises(ValueError):
            conventional.finalize()

    def test_action_shuffling_changes_causal_proposal_only_as_hypothesis(self):
        native=DelayedNativeCells()
        shifted=DelayedNativeCells()
        for _ in range(9):
            native.learn(state(),0,0.8)
            native.learn(state(),1,-0.8)
            native.learn(state(),2,-0.2)
            shifted.learn(state(),1,0.8)
            shifted.learn(state(),0,-0.8)
            shifted.learn(state(),2,-0.2)
        self.assertNotEqual(native.propose(state()),shifted.propose(state()))
        self.assertIsNone(DelayedNativeCells().propose(state()))

    def test_cold_separate_os_python_process_exact_predictions(self):
        models=(DelayedNativeCells(),FittedRidge9(True),FittedRidge9(False))
        for m in models:
            for i in range(12):
                m.learn(state(direction=i%4),i%3,((i%5)-2)/5)
            if isinstance(m,FittedRidge9):m.finalize()
            cp=m.checkpoint()
            self.assertEqual(type(m).restore(cp).checkpoint(),cp)
            code=(
              "import json,sys;"
              "from research.optimizer_o22v.delayed_cells import DelayedNativeCells,FittedRidge9;"
              "m=globals()[sys.argv[1]].restore(sys.stdin.buffer.read());"
              "b={'x':2,'y':3,'direction':1,'goal_x':6,'goal_y':6,'front_blocked':False};"
              "print(json.dumps({'n':m.events,'prediction':[m.predict(b,a) for a in (0,1,2)],"
              "'proposal':m.propose(b)}))"
            )
            run=subprocess.run([sys.executable,"-B","-c",code,type(m).__name__],
                               input=cp,capture_output=True,timeout=20)
            self.assertEqual(run.returncode,0,run.stderr.decode())
            self.assertEqual(json.loads(run.stdout),{
                "n":12,"prediction":[m.predict(state(),a) for a in (0,1,2)],
                "proposal":m.propose(state())})
            bad=json.loads(cp)
            bad["body"]["events"]=15
            with self.assertRaises(ValueError):
                type(m).restore(json.dumps(bad).encode())

    def test_illegal_hidden_and_invalid_source_feedback_rejected(self):
        m=DelayedNativeCells()
        invalid=state()
        invalid["hidden_grid"]=42
        with self.assertRaises(ValueError):m.predict(invalid,0)
        with self.assertRaises(ValueError):m.learn(state(),5,1)
        with self.assertRaises(ValueError):m.learn(state(),0,float("nan"))
        with self.assertRaises(ValueError):m.learn(state(),0,5.)
        with self.assertRaises(ValueError):FittedRidge9().predict(state(),0)
        self.assertEqual(m.events,0)


if __name__=="__main__":
    unittest.main(verbosity=2)
