"""O22-X source-only two-step autonomous belief rollout and cold-custody units."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
from research.native.itd02.r1.native_policy import LocalCell
from research.optimizer_o22x.transition_belief import (
    NativeCausalCells,ConventionalNineRidge,check_transition,
    one_step_belief,two_step_belief,choose,PAIRS,SAFE
)

def pub(x=2,y=3,direction=0,blocked=False):
    return {"x":x,"y":y,"goal_x":6,"goal_y":7,
            "direction":direction,"front_blocked":blocked}

def effect(s,a,blocked):
    d=s["direction"];o=dict(s,front_blocked=blocked)
    if a==0:o["direction"]=(d-1)%4
    elif a==1:o["direction"]=(d+1)%4
    elif not s["front_blocked"]:
        x,y=((1,0),(0,1),(-1,0),(0,-1))[d]
        o["x"]+=x;o["y"]+=y
    return o

class TruePublicBeliefTests(unittest.TestCase):
    def test_original_native_r1_r3_git_blob_identity(self):
        root=Path(__file__).resolve().parents[2]
        for fn,h in {
          "research/native/itd02/r1/native_policy.py":"3aa22b1e418a7f8cd9619c476f02b8c614917b16",
          "research/native/itd02/r3/navigator.py":"5348238f4ec2183bea29262659883391b5f429fd"
        }.items():
            raw=(root/fn).read_bytes().replace(b"\r\n",b"\n")
            self.assertEqual(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(),h)

    def test_original_cell_mutates_selected_source_outcome_only(self):
        m=NativeCausalCells()
        self.assertIs(type(m.cells["0"][0][0]),LocalCell)
        before=m.predict(pub(),0)
        for _ in range(5):m.learn(pub(),0,effect(pub(),0,True))
        self.assertGreater(m.predict(pub(),0)[0],before[0])
        self.assertEqual(m.cells["0"][0][0].updates,5)
        self.assertEqual(m.cells["2"][0][0].updates,0)
        self.assertEqual(m.cells["0"][1][0].updates,0)

    def test_original_moving_obstacle_sensor_blocked_can_move(self):
        b=pub(blocked=True)
        returned=dict(b,x=b["x"]+1,front_blocked=False)
        # The original Farama C35 source has this legally returned physics,
        # so NEVER assume a pre-action BLOCKED sensor guarantees no movement.
        self.assertEqual(check_transition(b,2,returned),(0,1))
        m=NativeCausalCells()
        m.learn(b,2,returned)
        self.assertEqual(m.events,1)
        self.assertTrue(m.predict(b,2)[1]>0.5)

    def test_two_step_belief_forecasts_own_intermediate_not_oracle(self):
        m=NativeCausalCells()
        for a in (0,1,2):
            m.learn(pub(),a,effect(pub(),a,False))
        first=one_step_belief(m,pub(),0)
        self.assertAlmostEqual(sum(w for w,_ in first),1.)
        self.assertTrue(all(s["direction"]==3 for _,s in first))
        self.assertTrue(all(s["x"]==2 and s["y"]==3 for _,s in first))
        ans=two_step_belief(m,pub(),"02")
        self.assertTrue(-1<=ans[0]<=1 and 0<=ans[1]<=1)
        self.assertAlmostEqual(ans[0],two_step_belief(m,pub(),"02")[0])
        self.assertIsInstance(choose(m,pub()),str)
        self.assertIn(choose(m,pub()),SAFE)

    def test_exact_all_nine_composition_and_full9_ridge_conventional(self):
        native=NativeCausalCells()
        conventional=ConventionalNineRidge()
        for _ in range(4):
            for a in (0,1,2):
                b=pub(direction=a,blocked=bool(a==1))
                n=effect(b,a,a==1)
                native.learn(b,a,n);conventional.learn(b,a,n)
        conventional.finalize()
        self.assertEqual(native.events,conventional.events)
        for p in PAIRS:
            r=two_step_belief(native,pub(),p)
            q=two_step_belief(conventional,pub(),p)
            self.assertTrue(all(isinstance(x,float) for x in r+q))
            self.assertTrue(-1<=r[0]<=1 and 0<=q[1]<=1)
        self.assertNotIn(choose(conventional,pub()),("01","10"))

    def test_privileged_fields_or_fabricated_original_action_rejected(self):
        s=dict(pub(),private_full_grid="forbidden")
        with self.assertRaises(ValueError):two_step_belief(NativeCausalCells(),s,"22")
        with self.assertRaises(ValueError):two_step_belief(NativeCausalCells(),pub(),"33")
        with self.assertRaises(ValueError):check_transition(pub(),5,pub())
        bad=pub(direction=1)
        with self.assertRaises(ValueError):check_transition(pub(),0,bad)

    def test_fresh_python_cold_exact_state_and_pair_policy(self):
        for model in (NativeCausalCells(),ConventionalNineRidge()):
            for _ in range(5):
                for a in (0,1,2):
                    before=pub(direction=a)
                    model.learn(before,a,effect(before,a,a==1))
            if isinstance(model,ConventionalNineRidge):model.finalize()
            cp=model.checkpoint()
            self.assertEqual(type(model).restore(cp).checkpoint(),cp)
            code=(
                "import json,sys;"
                "from research.optimizer_o22x.transition_belief import NativeCausalCells,ConventionalNineRidge,PAIRS,two_step_belief,choose;"
                "d=json.loads(sys.stdin.buffer.read());"
                "m=globals()[d['name']].restore(d['cp'].encode());"
                "print(json.dumps({'n':m.events,'out':[two_step_belief(m,d['state'],p) for p in PAIRS],"
                "'action':choose(m,d['state'])}))"
            )
            inp=json.dumps({"name":type(model).__name__,"cp":cp.decode(),"state":pub()}).encode()
            r=subprocess.run([sys.executable,"-B","-c",code],
                             input=inp,capture_output=True,timeout=25)
            self.assertEqual(r.returncode,0,r.stderr.decode())
            self.assertEqual(json.loads(r.stdout),{
                "n":15,"out":[list(two_step_belief(model,pub(),p)) for p in PAIRS],
                "action":choose(model,pub())})
            bad=json.loads(cp);bad["state"]["events"]+=1
            with self.assertRaises(ValueError):type(model).restore(json.dumps(bad).encode())

if __name__=="__main__":unittest.main(verbosity=2)
