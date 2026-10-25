"""O22-W bounded source-free tests, NOT simulated original MiniGrid science."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
from research.native.itd02.r1.native_policy import LocalCell
from research.optimizer_o22w.pair_models import (
    NativePairCells,FullNineRidgePairs,PAIRS,LEGAL,public,
    target,geometric_pair,select
)

def frame(blocked=False):
    return {"x":3,"y":4,"goal_x":7,"goal_y":7,"direction":0,"front_blocked":blocked}

class TestOriginalPairCausalInterface(unittest.TestCase):
    def test_original_R1_R3_unchanged(self):
        root=Path(__file__).resolve().parents[2]
        for f,sha in {
          "research/native/itd02/r1/native_policy.py":"3aa22b1e418a7f8cd9619c476f02b8c614917b16",
          "research/native/itd02/r3/navigator.py":"5348238f4ec2183bea29262659883391b5f429fd"
        }.items():
            d=(root/f).read_bytes().replace(b"\r\n",b"\n")
            self.assertEqual(hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d).hexdigest(),sha)
    def test_original_r1_cell_selected_pair_training(self):
        m=NativePairCells()
        self.assertIs(type(m.cells["02"][0][0]),LocalCell)
        before=m.predict(frame(),"02")
        for _ in range(6):
            m.learn(frame(),"02",{"progress":0.8,"blocked":True})
        self.assertNotEqual(m.predict(frame(),"02"),before)
        self.assertEqual(m.cells["02"][0][0].updates,6)
        self.assertEqual(m.cells["22"][0][0].updates,0)
        self.assertEqual(m.n,6)
    def test_all_nine_real_legal_alternatives_as_model_grammar(self):
        native=NativePairCells();conv=FullNineRidgePairs()
        for p in PAIRS:
            event={"progress":0.5 if p[-1]=="2" else 0.,
                   "blocked":p[0]=="0"}
            native.learn(frame(),p,event);conv.learn(frame(),p,event)
        conv.finalize()
        self.assertEqual(native.n,conv.n)
        self.assertEqual(native.n,9)
        self.assertEqual(set(native.counts),set(PAIRS))
        self.assertTrue(all(-1<=native.predict(frame(),p)[0]<=1
                            and 0<=conv.predict(frame(),p)[1]<=1 for p in PAIRS))
        with self.assertRaises(ValueError):conv.finalize()
    def test_excludes_direct_inverse_pair_without_changing_original_r3(self):
        m=NativePairCells()
        for p in PAIRS:
            m.learn(frame(),p,{"progress":1. if p in ("01","10") else 0.,"blocked":False})
        self.assertTrue(select(m,frame()) in LEGAL)
        self.assertNotIn(select(m,frame()),("01","10"))
        self.assertEqual(geometric_pair(frame()) in LEGAL,True)
    def test_illegal_hidden_map_or_unexecuted_labels_rejected(self):
        bad=dict(frame(),hidden_state="private-grid")
        with self.assertRaises(ValueError):public(bad)
        with self.assertRaises(ValueError):target({"progress":1.,"blocked":False,"unperformed_action":2})
        with self.assertRaises(ValueError):target({"progress":float("nan"),"blocked":False})
        with self.assertRaises(ValueError):NativePairCells().learn(frame(),"33",{"progress":0.,"blocked":False})
    def test_equal_input_choice_and_genuine_distinct_python_cold(self):
        for model in (NativePairCells(),FullNineRidgePairs()):
            for _ in range(2):
                for p in PAIRS:
                    model.learn(frame(),p,{"progress":0.5 if p.endswith("2") else -0.2,
                                           "blocked":p.startswith("0")})
            if isinstance(model,FullNineRidgePairs):model.finalize()
            cp=model.checkpoint()
            self.assertEqual(type(model).restore(cp).checkpoint(),cp)
            code=(
              "import sys,json;"
              "from research.optimizer_o22w.pair_models import NativePairCells,FullNineRidgePairs,PAIRS,select;"
              "d=json.loads(sys.stdin.buffer.read());"
              "m=globals()[d['class']].restore(d['blob'].encode());"
              "print(json.dumps({'n':m.n,'choice':select(m,d['state']),"
              "'pred':[m.predict(d['state'],p) for p in PAIRS]}))"
            )
            payload=json.dumps({"class":type(model).__name__,
                                "blob":cp.decode(),"state":frame()}).encode()
            r=subprocess.run([sys.executable,"-B","-c",code],input=payload,
                             capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stderr.decode())
            self.assertEqual(json.loads(r.stdout),{
              "n":model.n,"choice":select(model,frame()),
              "pred":[list(model.predict(frame(),p)) for p in PAIRS]})
            wire=json.loads(cp);wire["body"]["n"]+=1
            with self.assertRaises(ValueError):type(model).restore(json.dumps(wire).encode())
    def test_physical_original_branch_targets_remain_selected_only(self):
        m=NativePairCells()
        m.learn(frame(),"02",{"progress":0.5,"blocked":True})
        self.assertEqual(m.counts["02"],1)
        self.assertTrue(all(m.counts[p]==0 for p in PAIRS if p!="02"))

if __name__=="__main__":unittest.main(verbosity=2)
