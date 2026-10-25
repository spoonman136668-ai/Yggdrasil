"""O22-L: authored public source-schema unit certificates, zero original episodes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r12.outcome_choice import select_public_action
from research.optimizer_o22l.observed_effect import PublicEffectProbe

LOCKED = (4, 4, 2)
OPENED = (4, 4, 0)
KEY = (5, 4, 0)
EMPTY = (1, 0, 0)
WALL = (2, 5, 0)


def view(front=EMPTY, held=EMPTY, direction=0):
    pixels = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
    pixels[3][5] = list(front)
    pixels[3][6] = list(held)
    return {"image": pixels, "direction": direction, "mission": MISSION}


def fit_one(learner, sid, before, action, after):
    owner = DoorKeyPublicAdapter()
    owner.reset_public(before)
    learner.start_session(owner, sid)
    owner.submit(action)
    event = owner.complete(after, 0.0, False, False)
    learned = learner.learn_selected(owner)
    return owner, event, learned


class O22LSourceOnlyTests(unittest.TestCase):
    def test_unchanged_original_source_pins(self):
        root = Path(__file__).resolve().parents[2]
        expected = {
            "r10/public_adapter.py": "3917d36ce9f86a2c1b998a0a2f93fb27674a9205",
            "r11/affordance_cells.py": "614c7dfb1b43f485009b70cb85e9b7b5119cafc2",
            "r12/outcome_choice.py": "2d19b28d6d4db1988ae908fe91be1a27ce4c1907",
        }
        for path, expected_blob in expected.items():
            raw = (root / "research/native/itd02" / path).read_bytes()
            self.assertNotIn(b"\r", raw)
            actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            self.assertEqual(actual, expected_blob)

    def test_original_view_world_alias_and_guarded_non_attribution(self):
        before = view(front=LOCKED, direction=0)
        after = view(front=OPENED, direction=1)
        original = PublicAffordanceCells()
        _, ev, _ = fit_one(original, "original-turn", before, 1, after)
        self.assertFalse(ev["visible_door_opened"])
        old = select_public_action(original, before, "visible_door_state_changed",
                                   costs=[0.1] * 7)
        self.assertEqual(old["action"], 1)
        bounded = PublicEffectProbe()
        _, _, new = fit_one(bounded, "guarded-turn", before, 1, after)
        self.assertEqual(new["attribution"], "CHANGED_VIEW_NOT_WORLD_EFFECT")
        self.assertIsNone(bounded.choose(before, [0.1] * 7)["action"])
        print("O22L_ORIGINAL_R12_VIEW_TO_WORLD_ALIAS_REPRODUCED=PASS")
        print("O22L_GUARDED_VIEW_WORLD_ATTRIBUTION=PASS")

    def test_verified_toggle_keeps_selected_effect(self):
        model = PublicEffectProbe()
        before = view(front=LOCKED, held=KEY)
        after = view(front=OPENED, held=KEY)
        _, event, updated = fit_one(model, "verified-toggle", before, 5, after)
        self.assertTrue(event["visible_door_opened"])
        self.assertEqual(updated["attribution"], "R10_WITNESSED_VISIBLE_OPEN")
        result = model.choose(before, costs=[0.1] * 7)
        self.assertEqual(result["action"], 5)
        self.assertEqual(result["probability"], 1)

    def test_distinct_next_public_fronts_are_not_aliased(self):
        model = PublicEffectProbe()
        before = view(front=WALL, direction=0)
        fit_one(model, "next-empty", before, 0, view(front=EMPTY, direction=3))
        fit_one(model, "next-door", before, 0, view(front=LOCKED, direction=3))
        p = model.predict(before, 0)
        self.assertEqual(p["samples"], 2)
        self.assertEqual(p["next_fronts"], [list(EMPTY), list(LOCKED)])
        self.assertEqual(len(p["probabilities"]), 2)

    def test_selected_effect_revision_and_frozen_slow_zero_ablations(self):
        model = PublicEffectProbe()
        before = view(front=LOCKED, held=KEY)
        for i in range(9):
            fit_one(model, "stable-" + str(i), before, 5, view(front=OPENED, held=KEY))
        frozen = PublicEffectProbe.restore(model.checkpoint())
        for i in range(2):
            fit_one(model, "changed-" + str(i), before, 5, before)
        costs = [0.4] * 7
        self.assertEqual(frozen.choose(before, costs)["action"], 5)
        self.assertIsNone(model.choose(before, costs)["action"])
        self.assertEqual(model.choose(before, costs, mode="slow")["action"], 5)
        self.assertIsNone(model.choose(before, costs, mode="zero")["action"])
        self.assertLess(model.predict(before, 5)["open_probability"], 0.4)
        self.assertGreater(model.predict(before, 5, mode="slow")["open_probability"], 0.8)
        print("O22L_FAST_FROZEN_SLOW_ZERO_DECISION_SEPARATION=PASS")

    def test_unreturned_duplicate_hidden_state_rejected(self):
        model = PublicEffectProbe()
        owner = DoorKeyPublicAdapter()
        owner.reset_public(view(front=LOCKED, held=KEY))
        model.start_session(owner, "new")
        snapshot = model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn_selected(owner)
        owner.submit(5)
        with self.assertRaises(ValueError):
            model.learn_selected(owner)
        self.assertEqual(model.checkpoint(), snapshot)
        owner.complete(view(front=OPENED, held=KEY), 0.0, False, False)
        model.learn_selected(owner)
        observed = model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn_selected(owner)
        self.assertEqual(model.checkpoint(), observed)
        hidden = view(front=LOCKED)
        hidden["agent_pos"] = [2, 3]
        with self.assertRaises(ValueError):
            model.choose(hidden)

    def test_true_fresh_python_cold_prediction_and_action(self):
        model = PublicEffectProbe()
        before = view(front=LOCKED, held=KEY)
        fit_one(model, "before-restart", before, 5, view(front=OPENED, held=KEY))
        data = model.checkpoint()
        self.assertEqual(PublicEffectProbe.restore(data).checkpoint(), data)
        program = (
            "import json,sys;"
            "from research.optimizer_o22l.observed_effect import PublicEffectProbe;"
            "from research.native.itd02.r10.public_adapter import MISSION;"
            "m=PublicEffectProbe.restore(sys.stdin.buffer.read());"
            "a=[[[1,0,0] for _ in range(7)] for _ in range(7)];"
            "a[3][5]=[4,4,2];a[3][6]=[5,4,0];"
            "o={'image':a,'direction':0,'mission':MISSION};"
            "p=m.predict(o,5);c=m.choose(o,[0.1]*7);"
            "print(json.dumps({'samples':m.samples,'action':c['action'],"
            "'door':p['open_probability']}))"
        )
        result = subprocess.run([sys.executable, "-B", "-c", program],
                                input=data, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(json.loads(result.stdout), {"samples": 1, "action": 5, "door": 1.0})
        bad = json.loads(data)
        bad["state"]["samples"] += 1
        with self.assertRaises(ValueError):
            PublicEffectProbe.restore(json.dumps(bad).encode())
        print("O22L_OS_COLD_PREDICTION_AND_ACTION_PARITY=PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
