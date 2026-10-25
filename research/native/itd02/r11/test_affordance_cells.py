"""R11 source-only selected-public-effect learning, no original-world simulation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r10.public_adapter import (
    ACTION_NAMES, DoorKeyPublicAdapter, MISSION, digest,
)
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells


def view(front=(1, 0, 0), held=(1, 0, 0), direction=0):
    image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
    image[3][5] = list(front)
    image[3][6] = list(held)
    return {"image": image, "direction": direction, "mission": MISSION}


LOCKED = (4, 4, 2)
OPENED = (4, 4, 0)
YELLOW_KEY = (5, 4, 0)


def experience(learner, session, before, action, after, reward=0.0, terminated=False):
    source = DoorKeyPublicAdapter()
    source.reset_public(before)
    learner.start_session(source, session)
    source.submit(action)
    event = source.complete(after, reward, terminated, False)
    assert learner.learn_selected(source)["examples_here"] >= 1
    return event, source


def original_git_blob(path):
    b = Path(path).read_bytes().replace(b"\r\n", b"\n")
    if b"\r" in b:
        raise ValueError("UNCANONICAL_CR_SOURCE")
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


class ConventionalCountControl:
    """Independent conventional conditional-action count estimator. Same public info."""
    def __init__(self):
        self.table = {}
    @staticmethod
    def features(event):
        front, held = event["front_before"], event["carried_before"]
        return (tuple(front), tuple(held[:2]) if held else None, event["action"])
    @staticmethod
    def effects(event):
        a,b = event["front_before"],event["front_after"]
        return (a != b, a[0] == b[0] == 4 and a[2] != b[2],
                event["carried_before"] != event["carried_after"],
                event["heading_before"] != event["heading_after"],
                event["reward"] > 0, event["terminated"], event["truncated"])
    def fit(self, event):
        key = self.features(event)
        label = self.effects(event)
        hist = self.table.setdefault(key,{})
        hist[label] = hist.get(label,0) + 1
    def predict(self, observation, action):
        front = observation["image"][3][5]
        carried = observation["image"][3][6]
        held = tuple(carried[:2]) if carried[0] in (5,6,7) else None
        rows = self.table.get((tuple(front),held,action))
        if rows is None:
            return None
        return min(rows,key=lambda label:(-rows[label],label))


def as_tuple(pred):
    return (pred["front_changed"],pred["visible_door_state_changed"],
            pred["carrying_changed"],pred["heading_changed"],
            pred["positive_reward"],pred["terminated"],pred["truncated"])


class R11NativeSourceOnly(unittest.TestCase):
    def test_immutable_upstream_native_source_identity(self):
        root = Path(__file__).resolve().parents[1]
        expected = {"r7/learner.py":"204ecd993b954b23e66d6d1e8b3568e7c93183c5",
                    "r8/revision.py":"346fb9eb7462208a6cbd28cfb51716c22e5ec857",
                    "r9/evidence_cells.py":"66ec3befe92e2d2c2b7116217354a40f59e659d7",
                    "r10/public_adapter.py":"3917d36ce9f86a2c1b998a0a2f93fb27674a9205"}
        for path, sha in expected.items():
            self.assertEqual(original_git_blob(root/path),sha)

    def test_learns_selected_public_key_pickup_and_unseen_orientation(self):
        model=PublicAffordanceCells()
        before=view(front=YELLOW_KEY)
        after=view(front=(1,0,0),held=YELLOW_KEY)
        self.assertEqual(model.predict(before,3)["status"],"ABSTAIN_UNOBSERVED")
        experience(model,"public-key-one",before,3,after)
        new_dir=view(front=YELLOW_KEY,direction=3)
        q=model.predict(new_dir,3)
        self.assertEqual(q["status"],"LEARNED_PUBLIC_CONSEQUENCE")
        self.assertTrue(q["predicted"]["carrying_changed"])
        self.assertTrue(q["predicted"]["front_changed"])
        self.assertEqual(q["confidence"],1.0)
        self.assertEqual(model.predict(new_dir,5)["status"],"ABSTAIN_UNOBSERVED")
        self.assertEqual(model.samples,1)

    def test_toggling_conditioned_on_visible_key_and_door_state(self):
        model=PublicAffordanceCells()
        no_key=view(front=LOCKED)
        with_key=view(front=LOCKED,held=YELLOW_KEY)
        opened=view(front=OPENED,held=YELLOW_KEY)
        experience(model,"door-no-key",no_key,5,no_key)
        experience(model,"door-key",with_key,5,opened)
        absent=model.predict(view(front=LOCKED,direction=2),5)["predicted"]
        present=model.predict(view(front=LOCKED,held=YELLOW_KEY,direction=3),5)["predicted"]
        self.assertFalse(absent["front_changed"])
        self.assertTrue(present["front_changed"])
        self.assertTrue(present["visible_door_state_changed"])
        self.assertFalse(present["carrying_changed"])
        self.assertEqual(model.predict(view(front=OPENED,held=YELLOW_KEY),5)["status"],"ABSTAIN_UNOBSERVED")
        self.assertEqual(model.samples,2)

    def test_seven_actions_and_reward_are_separate_public_outcomes(self):
        model=PublicAffordanceCells()
        for action in range(7):
            before=view()
            after=view(direction=3) if action==0 else (view(direction=1) if action==1 else view())
            reward=.8 if action==2 else 0.0
            terminal=action==2
            experience(model,f"legal-{action}",before,action,after,reward,terminal)
            q=model.predict(view(direction=2),action)
            self.assertEqual(q["status"],"LEARNED_PUBLIC_CONSEQUENCE")
            self.assertEqual(q["predicted"]["heading_changed"],action in (0,1))
            self.assertEqual(q["predicted"]["positive_reward"],action==2)
            self.assertEqual(q["predicted"]["terminated"],action==2)
        self.assertEqual(model.samples,7)

    def test_exact_parity_with_independently_fit_conventional(self):
        native=PublicAffordanceCells()
        conventional=ConventionalCountControl()
        examples=[
          (view(front=YELLOW_KEY),3,view(front=(1,0,0),held=YELLOW_KEY)),
          (view(front=LOCKED),5,view(front=LOCKED)),
          (view(front=LOCKED,held=YELLOW_KEY),5,view(front=OPENED,held=YELLOW_KEY)),
          (view(front=LOCKED,held=YELLOW_KEY),2,view(front=LOCKED,held=YELLOW_KEY)),
          (view(front=YELLOW_KEY),0,view(front=YELLOW_KEY,direction=3)),
          (view(front=YELLOW_KEY),1,view(front=YELLOW_KEY,direction=1)),
        ]
        for i,(before,action,after) in enumerate(examples):
            event,_=experience(native,f"train-{i}",before,action,after)
            conventional.fit(event)
        total=0
        for front in (YELLOW_KEY,LOCKED,OPENED,(2,5,0),(1,0,0)):
            for held in ((1,0,0),YELLOW_KEY):
                for direction in range(4):
                    for action in range(7):
                        obs=view(front=front,held=held,direction=direction)
                        p=native.predict(obs,action)
                        b=conventional.predict(obs,action)
                        self.assertEqual(None if b is None else as_tuple(p["predicted"]),b)
                        self.assertEqual(p["status"]=="ABSTAIN_UNOBSERVED",b is None)
                        total+=1
        self.assertEqual(total,280)
        self.assertEqual(native.samples,len(examples))

    def test_selected_effect_cursor_no_duplicate_and_atomicity(self):
        native=PublicAffordanceCells()
        source=DoorKeyPublicAdapter()
        source.reset_public(view(front=YELLOW_KEY))
        native.start_session(source,"session-one")
        cp=native.checkpoint()
        with self.assertRaises(ValueError):native.learn_selected(source)
        self.assertEqual(native.checkpoint(),cp)
        source.submit(3)
        with self.assertRaises(ValueError):native.learn_selected(source)
        self.assertEqual(native.checkpoint(),cp)
        source.complete(view(front=(1,0,0),held=YELLOW_KEY),0,False,False)
        native.learn_selected(source)
        checkpoint=native.checkpoint()
        with self.assertRaises(ValueError):native.learn_selected(source)
        self.assertEqual(native.checkpoint(),checkpoint)
        source.submit(5)
        source.complete(view(front=LOCKED,held=YELLOW_KEY),0,False,False)
        native.learn_selected(source)
        self.assertEqual(native.samples,2)
        with self.assertRaises(ValueError):native.start_session(source,"new-session")
        self.assertEqual(native.samples,2)

    def test_validation_rejects_hidden_cues_and_illegal_actions(self):
        model=PublicAffordanceCells()
        good=view(front=LOCKED)
        for action in (-1,7,"pickup",True,1.0):
            with self.assertRaises(ValueError):model.predict(good,action)
        for hidden in ("agent_pos","full_grid","carrying","door_locked"):
            obs=copy.deepcopy(good)
            obs[hidden]=[1,2,3]
            with self.assertRaises(ValueError):model.predict(obs,5)
        self.assertEqual(model.samples,0)
        bridge=DoorKeyPublicAdapter()
        bridge.reset_public(good)
        with self.assertRaises(ValueError):model.start_session(bridge,"")
        self.assertEqual(model.session,None)

    def test_exact_os_cold_retention_and_invalid_checkpoints(self):
        model=PublicAffordanceCells()
        before=view(front=LOCKED,held=YELLOW_KEY)
        after=view(front=OPENED,held=YELLOW_KEY)
        event,adapter=experience(model,"cold-episode",before,5,after)
        raw=model.checkpoint()
        self.assertEqual(PublicAffordanceCells.restore(raw).checkpoint(),raw)
        script = ("import json,sys;from research.native.itd02.r11.affordance_cells import PublicAffordanceCells;"
                  "from research.native.itd02.r10.public_adapter import MISSION;"
                  "x=PublicAffordanceCells.restore(sys.stdin.buffer.read());"
                  "v=[[[1,0,0] for _ in range(7)] for _ in range(7)];v[3][5]=[4,4,2];v[3][6]=[5,4,0];"
                  "r=x.predict({'image':v,'direction':2,'mission':MISSION},5);"
                  "print(json.dumps({'samples':x.samples,'cursor':x.cursor,'status':r['status'],"
                  "'opened':r['predicted']['visible_door_state_changed']}))")
        p=subprocess.run([sys.executable,"-B","-c",script],input=raw,capture_output=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(json.loads(p.stdout),{"samples":1,"cursor":1,
                                               "status":"LEARNED_PUBLIC_CONSEQUENCE","opened":True})
        bad=json.loads(raw)
        bad["state"]["samples"]=200
        with self.assertRaises(ValueError):PublicAffordanceCells.restore(json.dumps(bad).encode())
        bad=json.loads(raw)
        bad["state"]["counts"]["4:4:2:5:4:5"]={"128":1}
        bad["sha256"]=digest(bad["state"])
        with self.assertRaises(ValueError):PublicAffordanceCells.restore(json.dumps(bad).encode())

if __name__ == "__main__":
    unittest.main()
