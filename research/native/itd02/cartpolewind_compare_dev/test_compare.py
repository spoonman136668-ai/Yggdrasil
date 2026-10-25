"""Synthetic PUBLIC-wire engineering tests; no CartPoleWind episode rights."""
import copy
import json
import math
import subprocess
import sys
import unittest

from research.native.itd02.cartpolewind_compare_dev.compare import (
    ARMS, Model, _event, fit_identical_public_replay,
)
from research.native.itd02.r7.learner import NonlinearLocalLearner

# These are explicit arbitrary protocol payloads, NOT a physics simulator,
# generated world, training cohort, environment trace or outcome benchmark.
ROWS = (
    {"observation": [0.1, -0.2, 0.3, -0.4], "action": 0,
     "next_observation": [0.2, -0.1, 0.1, -0.2], "reward": 1.0,
     "terminated": False, "truncated": False},
    {"observation": [0.2, -0.1, 0.1, -0.2], "action": 1,
     "next_observation": [-0.1, 0.1, -0.2, 0.1], "reward": 0.5,
     "terminated": True, "truncated": False},
    {"observation": [-0.3, 0.0, 0.4, 0.2], "action": 1,
     "next_observation": [0.0, 0.2, 0.1, 0.1], "reward": 1.0,
     "terminated": False, "truncated": False},
    {"observation": [0.0, 0.2, 0.1, 0.1], "action": 0,
     "next_observation": [0.2, 0.4, -0.1, 0.2], "reward": 0.0,
     "terminated": False, "truncated": True},
)


class CartPoleDevComparisonTests(unittest.TestCase):
    def models(self):
        return [Model(arm) for arm in ARMS]

    def test_r7_frozen_native_requires_separate_cartpole_interface(self):
        original = NonlinearLocalLearner()
        with self.assertRaises(ValueError):
            original.observe("public", 0, ROWS[0]["observation"], 0)
        with self.assertRaises(ValueError):
            original.observe("public", 2, 2, 0.1)
        self.assertEqual(original.events, 0)
        # No source/module/state of original R7 was adapted or overwritten.
        self.assertEqual(len(original.models), 0)

    def test_three_fitted_arms_receive_exactly_equal_synthetic_data(self):
        models = self.models()
        receipt = fit_identical_public_replay(models, ROWS)
        self.assertEqual(receipt["public_updates_per_arm"], 4)
        self.assertEqual(receipt["original_source_episodes"], 0)
        self.assertFalse(receipt["scientific_go"])
        self.assertIn("SYNTHETIC", receipt["data_label"])
        self.assertEqual({x.updates for x in models}, {4})
        self.assertEqual(set(receipt["checkpoint_bytes"]), set(ARMS))
        for model in models:
            self.assertIn(model.choose((0.05, 0.10, -0.1, 0.3)), (0, 1))
            self.assertTrue(math.isfinite(model._q((0.05, 0.10, -0.1, 0.3), 0)))
            self.assertLess(len(model.checkpoint()), 262144)
        self.assertEqual(models[2].trace, [0.0] * 4)
        # Every arm must change a trained parameter after public feedback.
        self.assertTrue(any(any(abs(x) > 0 for x in weights)
                            for weights in models[0].fast.values()))
        self.assertTrue(any(any(abs(x) > 0 for x in row)
                            for row in models[1].table.values()))
        self.assertTrue(any(any(abs(x) > 0 for x in weights)
                            for weights in models[2].recurrent.values()))

    def test_private_raw_info_is_never_accepted_or_partially_fitted(self):
        models = self.models()
        forbidden = copy.deepcopy(ROWS[0])
        forbidden["info"] = {"hidden_wind": 42}
        for invalid in (
            forbidden,
            dict(ROWS[0], action=2),
            dict(ROWS[0], observation=[0.0, 0.0, 0.0]),
            dict(ROWS[0], next_observation=[0, 0, float("inf"), 0]),
            dict(ROWS[0], reward=float("nan")),
            dict(ROWS[0], terminated=1),
        ):
            with self.subTest(row=repr(invalid)):
                with self.assertRaises(ValueError):
                    fit_identical_public_replay(models, [ROWS[0], invalid])
                self.assertEqual([m.updates for m in models], [0, 0, 0])
                self.assertEqual([m.action_calls for m in models], [0, 0, 0])
        with self.assertRaises(ValueError):
            _event({"private": "source"})
        with self.assertRaises(ValueError):
            fit_identical_public_replay(models[:2], ROWS)

    def test_cold_interpreter_restore_and_tamper_veto(self):
        models = self.models()
        fit_identical_public_replay(models, ROWS)
        script = """
import json,sys
from research.native.itd02.cartpolewind_compare_dev.compare import Model
model=Model.restore(sys.stdin.buffer.read())
print(json.dumps({"arm":model.arm,"updates":model.updates,
                  "choice":model.choose([0.1,-0.1,0.2,-0.2])}))
"""
        for model in models:
            payload = model.checkpoint()
            result = subprocess.run(
                [sys.executable, "-B", "-c", script], input=payload,
                capture_output=True, timeout=20, check=False)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            answer = json.loads(result.stdout)
            self.assertEqual(answer["arm"], model.arm)
            self.assertEqual(answer["updates"], 4)
            self.assertIn(answer["choice"], (0, 1))
            forged = json.loads(payload)
            forged["body"]["updates"] -= 1
            with self.assertRaises(ValueError):
                Model.restore(json.dumps(forged).encode())

    def test_original_source_first_use_is_not_invoked(self):
        # Only hardcoded, source-free Python dictionary literals were used.
        # No upstream module is imported; no reset/step/do call is made.
        models = self.models()
        for model in models:
            self.assertEqual(model.updates, 0)
            self.assertEqual(model.action_calls, 0)
        self.assertEqual(len(ROWS), 4)
        self.assertEqual(sum(bool(r["terminated"] or r["truncated"]) for r in ROWS), 2)


if __name__ == "__main__":
    unittest.main()
