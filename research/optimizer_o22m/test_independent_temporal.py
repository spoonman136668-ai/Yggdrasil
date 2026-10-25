"""Optimizer O22-M: matched independent conventional temporal controls (source-only)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.optimizer_o22l.observed_effect import PublicEffectProbe
from research.optimizer_o22m.independent_conventional import ConventionalTemporal

LOCKED = (4, 4, 2)
OPEN = (4, 4, 0)
KEY = (5, 4, 0)
CLEAR = (1, 0, 0)


def view(front=CLEAR,held=CLEAR,direction=0):
    a = [[[1,0,0] for _ in range(7)] for _ in range(7)]
    a[3][5]=list(front)
    a[3][6]=list(held)
    return {"image":a,"direction":direction,"mission":MISSION}


def train_pair(native,conv,index,before,action,after):
    for learner in (native,conv):
        o=DoorKeyPublicAdapter()
        o.reset_public(before)
        sid=f"frozen-source-public-fixture-{index}"
        if type(learner) is PublicEffectProbe:
            learner.start_session(o,sid)
        else:
            learner.start(o,sid)
        o.submit(action)
        o.complete(after,0.0,False,False)
        if type(learner) is PublicEffectProbe:
            learner.learn_selected(o)
        else:
            learner.learn(o)


class O22MControls(unittest.TestCase):
    def test_unchanged_owner_and_optimizer_source_blobs(self):
        root=Path(__file__).resolve().parents[2]
        originals={
            "research/native/itd02/r10/public_adapter.py":"3917d36ce9f86a2c1b998a0a2f93fb27674a9205",
            "research/native/itd02/r11/affordance_cells.py":"614c7dfb1b43f485009b70cb85e9b7b5119cafc2",
            "research/native/itd02/r12/outcome_choice.py":"2d19b28d6d4db1988ae908fe91be1a27ce4c1907"
        }
        for p,sha in originals.items():
            b=(root/p).read_bytes().replace(b"\r\n",b"\n")
            self.assertEqual(hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest(),sha)

    def test_valid_effect_baseline_complete_matched_prediction(self):
        native,conv=PublicEffectProbe(),ConventionalTemporal()
        b=view(front=LOCKED,held=KEY)
        for i in range(9):
            train_pair(native,conv,i,b,5,view(front=OPEN,held=KEY))
        for i in range(9,11):
            train_pair(native,conv,i,b,5,b)
        self.assertEqual(native.samples,conv.total)
        self.assertEqual(native.samples,11)
        for mode,scheme in (("active","blend"),("slow","lifetime"),("zero","disabled")):
            for a in range(7):
                n=native.predict(b,a,mode)
                c=conv.predict(b,a,scheme)
                self.assertEqual(n["status"]=="ABSTAIN",c is None)
                if c is not None:
                    self.assertEqual(n["samples"],c["sample_count"])
                    self.assertAlmostEqual(n["open_probability"],c["verified_open_probability"],places=12)
                    self.assertEqual(n["next_fronts"],[list(x) for x in c["next_public_fronts"]])
            native_action=native.choose(b,[0.4]*7,mode)["action"]
            baseline=conv.select(b,[0.4]*7,scheme)
            self.assertEqual(native_action,None if baseline is None else baseline["action"])
        self.assertIsNone(native.choose(b,[0.4]*7)["action"])
        self.assertEqual(native.choose(b,[0.4]*7,mode="slow")["action"],5)
        self.assertIsNone(conv.select(b,[0.4]*7,scheme="recent"))
        print("O22M_EQUAL_INFO_TEMPORAL_CONVENTIONAL_PARITY=PASS")

    def test_turn_observation_no_world_change_and_action_identity(self):
        n,c=PublicEffectProbe(),ConventionalTemporal()
        b=view(front=LOCKED)
        train_pair(n,c,0,b,1,view(front=OPEN,direction=1))
        self.assertIsNone(n.choose(b,[0.1]*7)["action"])
        self.assertIsNone(c.select(b,[0.1]*7))
        p=n.predict(b,1)
        q=c.predict(b,1)
        self.assertAlmostEqual(p["open_probability"],q["verified_open_probability"])
        self.assertEqual(p["next_fronts"],[list(OPEN)])
        self.assertEqual(p["next_fronts"],[list(v) for v in q["next_public_fronts"]])
        # A matched positive toggle is kept action-specific.
        train_pair(n,c,1,b,5,view(front=OPEN))
        self.assertEqual(n.choose(b,[0.1]*7)["action"],5)
        self.assertEqual(c.select(b,[0.1]*7)["action"],5)
        self.assertAlmostEqual(n.predict(b,1)["open_probability"],0)
        print("O22M_VIEW_VS_WORLD_AND_SELECTED_ACTION_IDENTITY=PASS")

    def test_full_next_state_alias_eliminated_both_arms(self):
        n,c=PublicEffectProbe(),ConventionalTemporal()
        b=view(front=(2,5,0))
        train_pair(n,c,0,b,0,view(front=CLEAR,direction=3))
        train_pair(n,c,1,b,0,view(front=LOCKED,direction=3))
        p=n.predict(b,0)
        q=c.predict(b,0)
        self.assertEqual(p["next_fronts"],[list(CLEAR),list(LOCKED)])
        self.assertEqual(q["next_public_fronts"],[CLEAR,LOCKED])
        self.assertEqual(p["samples"],q["sample_count"])
        self.assertEqual(len(p["probabilities"]),2)

    def test_sequence_history_and_current_action_provenance_fails_closed(self):
        n,c=PublicEffectProbe(),ConventionalTemporal()
        for model in (n,c):
            o=DoorKeyPublicAdapter()
            o.reset_public(view(front=LOCKED))
            if model is n:model.start_session(o,"session")
            else:model.start(o,"session")
            checkpoint=model.checkpoint()
            with self.assertRaises(ValueError):
                if model is n:model.learn_selected(o)
                else:model.learn(o)
            o.submit(5)
            with self.assertRaises(ValueError):
                if model is n:model.learn_selected(o)
                else:model.learn(o)
            self.assertEqual(checkpoint,model.checkpoint())
            o.complete(view(front=OPEN),0.0,False,False)
            if model is n:model.learn_selected(o)
            else:model.learn(o)
            saved=model.checkpoint()
            with self.assertRaises(ValueError):
                if model is n:model.learn_selected(o)
                else:model.learn(o)
            self.assertEqual(saved,model.checkpoint())

    def test_cold_restart_both_models_fully_informed(self):
        n,c=PublicEffectProbe(),ConventionalTemporal()
        before=view(front=LOCKED,held=KEY)
        train_pair(n,c,0,before,5,view(front=OPEN,held=KEY))
        a,b=n.checkpoint(),c.checkpoint()
        script=(
            "import json,sys;"
            "from research.optimizer_o22l.observed_effect import PublicEffectProbe;"
            "from research.optimizer_o22m.independent_conventional import ConventionalTemporal;"
            "from research.native.itd02.r10.public_adapter import MISSION;"
            "v=[[[1,0,0] for _ in range(7)] for _ in range(7)];"
            "v[3][5]=[4,4,2];v[3][6]=[5,4,0];"
            "o={'image':v,'direction':0,'mission':MISSION};"
            "data=json.loads(sys.stdin.buffer.read());"
            "n=PublicEffectProbe.restore(data['native'].encode());"
            "c=ConventionalTemporal.restore(data['conventional'].encode());"
            "print(json.dumps({'ns':n.samples,'cs':c.total,"
            "'na':n.choose(o,[0.1]*7)['action'],"
            "'ca':c.select(o,[0.1]*7)['action'],"
            "'np':n.predict(o,5)['open_probability'],"
            "'cp':c.predict(o,5)['verified_open_probability']}))"
        )
        result=subprocess.run([sys.executable,"-B","-c",script],
                    input=json.dumps({"native":a.decode(),"conventional":b.decode()}).encode(),
                    capture_output=True,timeout=25)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        self.assertEqual(json.loads(result.stdout),
            {"ns":1,"cs":1,"na":5,"ca":5,"np":1,"cp":1})
        bad=json.loads(b)
        bad["state"]["total"]=2
        with self.assertRaises(ValueError):
            ConventionalTemporal.restore(json.dumps(bad).encode())
        print("O22M_MATCHED_FULL_CONVENTIONAL_COLD_ACTION_RESTORE=PASS")


if __name__=="__main__":
    unittest.main(verbosity=2)
