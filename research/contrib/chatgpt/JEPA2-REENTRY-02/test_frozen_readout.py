"""Local source-free negative controls for frozen JEPA2-05 candidate ABI."""
import hashlib
import json
import math
import unittest

import numpy as np
from frozen_readout import FrozenHorizonReadout, _features


def fixture():
    n = lambda shape: np.zeros(shape, dtype=float).tolist()
    def head(kind, count):
        return {"kind": kind, "steps": 2, "windows": 1,
                "future_enc": n((count, 8)), "future_bias": n((8,)),
                "future_dec": n((8, count)), "future_dec_bias": n((count,)),
                "teacher_enc": n((count, 8)), "teacher_bias": n((8,)),
                "pred_enc": n((37, 16)), "pred_bias": n((16,)),
                "pred_latent": n((16, 8)), "pred_latent_bias": n((8,)),
                "readout": n((8, count)), "readout_bias": n((count,))}
    native = "{}"
    root = {"schema": "yggdrasil.jepa2-04.future-state-native-cumulative.v1",
            "native_ascii": native, "native_sha256": hashlib.sha256(native.encode()).hexdigest(),
            "sensory": head("sensors", 9), "reward": head("reward", 3)}
    return json.dumps(root, sort_keys=True, separators=(",", ":")).encode()


class FrozenReadoutTest(unittest.TestCase):
    def setUp(self):
        self.original = fixture()
        self.pin = hashlib.sha256(self.original).hexdigest()
        self.view = ((1, 0), (1, 1))
        self.plans = ((0, 1), (1, 0), (1, 1))

    def test_prediction_and_repeat_noninterference(self):
        before = bytes(self.original)
        r = FrozenHorizonReadout(self.original, self.pin)
        a = r.forecast(self.view, self.plans, ())
        b = r.forecast(self.view, self.plans, ())
        self.assertEqual(a, (0.5,) * 6)
        self.assertEqual(a, b)
        self.assertEqual(before, self.original)
        self.assertEqual(len(_features(self.view, self.plans, ())), 37)

    def test_nontrivial_logit_readout_and_precise_stage_order(self):
        data = json.loads(self.original)
        data["sensory"]["readout_bias"][1] = 2.0
        data["reward"]["readout_bias"][2] = -2.0
        raw = json.dumps(data).encode()
        readout = FrozenHorizonReadout(raw, hashlib.sha256(raw).hexdigest())
        forecast = readout.forecast(self.view, self.plans, ())
        self.assertAlmostEqual(forecast[0], 1 / (1 + math.exp(-2)))
        self.assertAlmostEqual(forecast[5], 1 / (1 + math.exp(2)))
        self.assertEqual(forecast[1:5], (0.5,) * 4)

    def test_history_order_and_immutable_parameters(self):
        row = ("id", ((1, 0), (0, 1)), 1, 0, 0, 1)
        features = _features(self.view, self.plans, (row,))
        self.assertEqual(features[9:16].tolist(), [1., -1., 1., 1., -1., -1., 1.])
        r = FrozenHorizonReadout(self.original, self.pin)
        self.assertFalse(r._weights["sensory"]["readout"].flags.writeable)

    def test_reject_nonpublic_actions_mismatch_and_missing_plan(self):
        r = FrozenHorizonReadout(self.original, self.pin)
        for views, plans, history in (
            (((1, 0), (0, 1)), self.plans, ()),
            (self.view, ((0, 1), (1, 0)), ()),
            (self.view, ((0, 1), (1, 0), (True, 1)), ()),
            (self.view, self.plans, [("id", "bad")]),
        ):
            with self.assertRaises(ValueError):
                r.forecast(views, plans, history)

    def test_reject_tamper_and_wrong_checkpoint_family(self):
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_PIN"):
            FrozenHorizonReadout(self.original + b" ", self.pin)
        wrong = json.loads(self.original)
        wrong["schema"] = "yggdrasil.ckad.native-causal-amalgam.v1"
        blob = json.dumps(wrong).encode()
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_SCHEMA"):
            FrozenHorizonReadout(blob, hashlib.sha256(blob).hexdigest())
        wrong = json.loads(self.original)
        wrong["sensory"]["pred_enc"][0][0] = 1000
        blob = json.dumps(wrong).encode()
        with self.assertRaisesRegex(ValueError, "NONFINITE_OR_BAD_SHAPE"):
            FrozenHorizonReadout(blob, hashlib.sha256(blob).hexdigest())
        wrong = json.loads(self.original)
        wrong["native_sha256"] = "0" * 64
        blob = json.dumps(wrong).encode()
        with self.assertRaisesRegex(ValueError, "PARENT_CUSTODY"):
            FrozenHorizonReadout(blob, hashlib.sha256(blob).hexdigest())


if __name__ == "__main__":
    unittest.main()
