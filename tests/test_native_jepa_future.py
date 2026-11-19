"""YGG-JEPA2-04 focused native future-state learner invariants.

Development source only. Do not use scientific first-use or hidden regime data.
"""
import importlib.util
import json
from pathlib import Path
import unittest
import numpy as np

from yggdrasil.native_context_basis import digest
from yggdrasil.native_jepa_future import (
    FutureStateHead, NativeFutureStateLearner, DirectLogistic,
    targets, primary_truth, public_observed, observed_features, DIM, UPDATES,
)
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research/contrib/chatgpt/YGG-JEPA2-04"
PRIOR = ROOT / "research/contrib/chatgpt/YGG-JEPA2-03"


def source():
    spec = importlib.util.spec_from_file_location(
        "jepa4_unit_source", HERE / "source.py")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class FutureStateTest(unittest.TestCase):
    def test_new_causal_source_is_public_and_sequential(self):
        data = source()
        cases = []
        for seed in data.SEEDS:
            for world in data.WORLDS:
                events = data.generate(seed, world)
                self.assertEqual(len(events), 120)
                self.assertEqual(events, data.generate(seed, world))
                self.assertEqual(len({e["source_id"] for e in events}), 120)
                cases.append(events[0]["source_id"])
                for i, e in enumerate(events):
                    self.assertEqual(e["actions"], data.announced_plan(seed, world, i))
                    self.assertEqual(e["row"]["s2"], e["post"][1])
                    self.assertEqual(len(e["post"]), 3)
                    self.assertTrue(all(x in (0, 1) for x in e["post"]))
                    if i < len(events) - 1:
                        self.assertEqual(
                            e["post"],
                            (events[i+1]["views"][0][0],
                             events[i+1]["views"][0][1],
                             events[i+1]["views"][1][1]))
        self.assertEqual(len(set(cases)), 4)

    def test_future_state_target_and_delayed_learning_are_separate(self):
        rows = source().generate(95413, 0)
        window = rows[:3]
        view = rows[0]["views"]
        acts = tuple(x["actions"] for x in window)
        x = observed_features(view, acts, ())
        self.assertEqual(x.shape, (DIM,))
        s, r = targets(window)
        self.assertEqual(s.shape, (9,))
        self.assertEqual(r.shape, (3,))
        self.assertEqual(primary_truth(window).shape, (6,))
        sensory = FutureStateHead("sensors")
        reward = FutureStateHead("reward")
        p0, r0 = sensory.predict(x).copy(), reward.predict(x).copy()
        state0 = sensory.checkpoint()
        target0 = sensory.teacher_enc.copy()
        sensory.learn(x, s)
        reward.learn(x, r)
        self.assertEqual(sensory.steps, UPDATES)
        self.assertEqual(reward.steps, UPDATES)
        self.assertNotEqual(sensory.checkpoint(), state0)
        self.assertFalse(np.array_equal(target0, sensory.teacher_enc))
        self.assertFalse(np.allclose(p0, sensory.predict(x), atol=1e-14))
        self.assertFalse(np.allclose(r0, reward.predict(x), atol=1e-14))
        restored = FutureStateHead.restore(sensory.checkpoint())
        np.testing.assert_allclose(restored.predict(x), sensory.predict(x),
                                   atol=0, rtol=0)

    def test_no_future_consequence_label_in_forecast_features(self):
        data = source().generate(95413, 1)
        plan = tuple(x["actions"] for x in data[:3])
        x = observed_features(data[0]["views"], plan, ())
        future_changed = [dict(x) for x in data[:3]]
        for q in future_changed:
            q["post"] = tuple(1-z for z in q["post"])
            q["row"] = dict(q["row"])
            q["row"]["s2"] ^= 1
            q["row"]["y"] ^= 1
        altered = observed_features(data[0]["views"], plan, ())
        np.testing.assert_array_equal(x, altered)
        head = FutureStateHead("reward")
        self.assertEqual(head.predict(x).tolist(), head.predict(altered).tolist())
        # Only after a complete 3-event observation can different target data
        # produce a different update.
        original = FutureStateHead("reward")
        original.learn(x, targets(data[:3])[1])
        head.learn(x, targets(future_changed)[1])
        self.assertFalse(np.array_equal(original.readout, head.readout))

    def test_trained_direct_control_uses_same_public_feature_dimension(self):
        events = source().generate(95429, 0)
        v = events[0]["views"]
        x = observed_features(v, tuple(e["actions"] for e in events[:3]), ())
        d = DirectLogistic()
        before = d.predict(x).copy()
        sensory, reward = targets(events[:3])
        d.learn(x, np.concatenate((sensory, reward)))
        self.assertEqual(d.steps, UPDATES)
        self.assertFalse(np.allclose(before, d.predict(x), atol=1e-15))
        self.assertTrue(np.isfinite(d.predict(x)).all())

    def test_original_cumulative_native_and_old_heads_remain_cold_restorable(self):
        path = PRIOR / "seed-14071-state.json"
        d = json.loads(path.read_bytes())
        raw = d["state_ascii"].encode("ascii")
        self.assertEqual(digest(raw), d["state_sha256"])
        older = NativeTemporalMultiLearner.restore(raw, digest(raw))
        model = NativeFutureStateLearner(older)
        original = older.checkpoint()
        raw2 = model.checkpoint()
        copy = NativeFutureStateLearner.restore(raw2, digest(raw2))
        self.assertEqual(copy.original.checkpoint(), original)
        self.assertEqual(copy.checkpoint(), raw2)
        self.assertEqual(copy.sensory.windows, 0)
        self.assertEqual(copy.reward.windows, 0)

    def test_fail_closed_on_public_shapes_and_corrupt_checkpoint(self):
        model = FutureStateHead("sensors")
        with self.assertRaises(ValueError):
            model.learn(np.zeros(DIM), np.ones(3))
        with self.assertRaises(ValueError):
            model.predict(np.zeros(DIM + 1))
        with self.assertRaises(ValueError):
            public_observed(((0, 1), (0, 2)))
        with self.assertRaises(ValueError):
            FutureStateHead.restore({**model.checkpoint(), "steps": 999})
        with self.assertRaises(ValueError):
            FutureStateHead.restore({**model.checkpoint(), "new_field": True})


if __name__ == "__main__":
    unittest.main()

