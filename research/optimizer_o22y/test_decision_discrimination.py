"""O22-Y source-public, world-group exclusion and real-action contrast units."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.optimizer_o22x.transition_belief import NativeCausalCells,ConventionalNineRidge,choose
from research.optimizer_o22w.pair_models import FullNineRidgePairs,select,geometric_pair,LEGAL as SAFE


def s(x=2,y=3,direction=0):
    return {"x":x,"y":y,"direction":direction,"goal_x":6,"goal_y":7,"front_blocked":False}


def after(b,a,blocked=False):
    v=dict(b,front_blocked=blocked)
    if a==0:v["direction"]=(b["direction"]-1)%4
    elif a==1:v["direction"]=(b["direction"]+1)%4
    elif a==2:
        step=((1,0),(0,1),(-1,0),(0,-1))[b["direction"]]
        v["x"]+=step[0];v["y"]+=step[1]
    return v


class SourceWorldDiscriminationControls(unittest.TestCase):
    def test_immutable_original_r1_r3_unchanged(self):
        root=Path(__file__).resolve().parents[2]
        for fn,pin in {
            "research/native/itd02/r1/native_policy.py":"3aa22b1e418a7f8cd9619c476f02b8c614917b16",
            "research/native/itd02/r3/navigator.py":"5348238f4ec2183bea29262659883391b5f429fd"
        }.items():
            blob=(root/fn).read_bytes().replace(b"\r\n",b"\n")
            git=hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()
            self.assertEqual(git,pin)

    def test_original_untrained_native_cannot_be_claimed_learned(self):
        m=NativeCausalCells()
        self.assertEqual(m.events,0)
        self.assertIn(choose(m,s()),SAFE)
        self.assertEqual(m.action_counts,{"0":0,"1":0,"2":0})

    def test_legal_real_selected_action_training_and_source_public_input_only(self):
        n=NativeCausalCells()
        c=ConventionalNineRidge()
        d=FullNineRidgePairs()
        for t in range(3):
            for a in (0,1,2):
                v=s(direction=a)
                n.learn(v,a,after(v,a))
                c.learn(v,a,after(v,a))
            for i in range(3):
                for j in range(3):
                    d.learn(s(direction=t),str(i)+str(j),
                            {"progress":0.5 if j==2 else 0.,"blocked":False})
        c.finalize();d.finalize()
        self.assertEqual(n.events,c.events)
        self.assertEqual(n.events,9)
        self.assertEqual(d.n,27)
        for x in (choose(n,s()),choose(c,s()),select(d,s()),geometric_pair(s())):
            self.assertIn(x,SAFE)

    def test_never_treat_equal_physical_pairs_as_mechanistic_advantage(self):
        trial={"native":"22","untrained":"12","ridge":"22"}
        physical={"22":0.5,"12":0.5}
        self.assertNotEqual(trial["native"],trial["untrained"])
        self.assertEqual(physical[trial["native"]]-physical[trial["untrained"]],0.)
        self.assertFalse(
            trial["native"]!=trial["untrained"] and
            trial["native"]!=trial["ridge"] and
            physical[trial["native"]]-physical[trial["untrained"]]>=0.5
        )

    def test_no_learner_gets_original_world_seed_as_public_input(self):
        illegal=dict(s(),source_seed=86101)
        for obj in (NativeCausalCells(),ConventionalNineRidge()):
            with self.assertRaises(ValueError):obj.predict(illegal,2)
        with self.assertRaises(ValueError):geometric_pair(illegal)

    def test_checkpoint_cold_native_and_fully_fitted_conventional(self):
        for model in (NativeCausalCells(),ConventionalNineRidge()):
            for _ in range(3):
                for a in (0,1,2):
                    b=s(direction=a)
                    model.learn(b,a,after(b,a))
            if isinstance(model,ConventionalNineRidge):model.finalize()
            cp=model.checkpoint()
            self.assertEqual(type(model).restore(cp).checkpoint(),cp)
            code=(
              "import json,sys;"
              "from research.optimizer_o22x.transition_belief import NativeCausalCells,ConventionalNineRidge,choose;"
              "x=json.loads(sys.stdin.buffer.read());"
              "m=globals()[x['class']].restore(x['checkpoint'].encode());"
              "print(json.dumps({'n':m.events,'choice':choose(m,x['state'])}))"
            )
            payload=json.dumps({"class":type(model).__name__,
                                "checkpoint":cp.decode(),"state":s()}).encode()
            r=subprocess.run([sys.executable,"-B","-c",code],
                             input=payload,capture_output=True,timeout=25)
            self.assertEqual(r.returncode,0,r.stderr.decode())
            self.assertEqual(json.loads(r.stdout),
                             {"n":model.events,"choice":choose(model,s())})
            bad=json.loads(cp);bad["state"]["events"]+=1
            with self.assertRaises(ValueError):
                type(model).restore(json.dumps(bad).encode())

    def test_original_FIT_check_role_not_train_or_positive_source(self):
        p=json.loads((Path(__file__).resolve().parent/"PREREG.json").read_text())
        self.assertEqual(p["source_C35"]["matched_fit_anchors"],31)
        self.assertEqual(p["governance"]["new_original_source_actions"],0)
        self.assertIn("ENTIRELY",p["role"])
        self.assertIn("NOT used",p["role"])
        self.assertTrue(p["governance"]["FORGE_FSA_83_protected_first_use_denied"])

if __name__=="__main__":
    unittest.main(verbosity=2)
