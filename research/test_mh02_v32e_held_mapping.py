"""Pre-registered MH02 source-free controls; do not promote DEV scores to science."""
import json
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from research import mh02_v32e_held_mapping_audit as mh
from research import itd02_v32c_world_reversal_audit as v32c


class MH02Tests(unittest.TestCase):
    def test_original_source_and_new_mapping_disjointness(self):
        mh.source_guard()
        self.assertEqual(len(mh.MAPS), 2)
        self.assertEqual(len(mh.SEEDS), 5)
        self.assertTrue(set(mh.SEEDS).isdisjoint(v32c.SEEDS))
        self.assertEqual(sum(a != b for a, b in zip(mh.A, mh.MAPS["D"])), 3)
        self.assertEqual(sum(a != b for a, b in zip(mh.A, mh.MAPS["E"])), 4)

    def test_balanced_public_schedule_exact(self):
        for seed in mh.SEEDS:
            for phase in mh.PHASES:
                events = mh.schedule(seed, phase)
                self.assertEqual(len(events), 240)
                self.assertEqual(len(set(events)), 240)
                self.assertEqual(mh.schedule(seed, phase), events)
                for chunk in range(20):
                    part = events[12*chunk:12*(chunk+1)]
                    self.assertEqual({(c,a) for c,a,_ in part},
                                     {(c,a) for c in range(4) for a in range(3)})
        with self.assertRaises(ValueError):
            mh.schedule(11, "a")

    def test_public_feedback_and_nulls_are_independently_balanced(self):
        for seed in mh.SEEDS:
            shuffled = mh.shuffled_null(seed)
            for cue in range(4):
                for action in range(3):
                    vals = shuffled[(cue,action)]
                    self.assertEqual(len(vals), 20)
                    self.assertEqual(vals.count(1.), 10)
                    self.assertEqual(vals.count(-1.), 10)
                    alternating = [mh.outcome(mh.MAPS["D"], cue, action, r, null="alternating")
                                   for r in range(20)]
                    self.assertEqual(alternating.count(1.), 10)
                    self.assertEqual(alternating.count(-1.), 10)

    def test_recency_source_only_and_held_mapping_learning(self):
        for label, target in mh.MAPS.items():
            d = mh.recency_arm(mh.SEEDS[0], target)
            self.assertGreaterEqual(d["stages"]["a240"]["a"], .75)
            self.assertEqual(d["stages"]["x60"]["x"], 1.0)
            self.assertEqual(d["stages"]["x240"]["x"], 1.0)
            self.assertEqual(d["stages"]["return_a240"]["a"], 1.0)
            self.assertLessEqual(d["checkpoint_bytes"], 2264)
            self.assertEqual(d["stages"]["return_a240"]["updates"], 720)

    def test_recency_rejects_invalid_events_atomically(self):
        model = mh.Recency()
        b = model.checkpoint()
        for args in ((4,0,1.),(1,3,1.),(1,0,0.),(True,0,1.)):
            with self.assertRaises(ValueError):
                model.learn(*args)
            self.assertEqual(model.checkpoint(), b)

    def test_native_integrity_and_cold_tamper_fails(self):
        api = mh.v32e.API
        h = api.new()
        try:
            api.layout(h)
            raw = api.checkpoint(h)
            stage = mh.native_readout(api,h,mh.MAPS["D"])
            self.assertEqual(stage["checkpoint"],raw)
            self.assertEqual(stage["checkpoint_bytes"],2264)
            with tempfile.TemporaryDirectory() as temp:
                file = pathlib.Path(temp)/"s.bin"
                file.write_bytes(raw)
                mh.verify_cold("v32e",stage,mh.MAPS["D"])
                tampered = bytearray(raw)
                tampered[40] ^= 1
                self.assertLess(api.restore(h,bytes(tampered)),0)
                self.assertEqual(api.checkpoint(h),raw)
        finally:
            api.free(h)


if __name__ == "__main__":
    unittest.main()
