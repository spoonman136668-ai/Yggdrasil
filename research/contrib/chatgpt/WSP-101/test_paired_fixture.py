"""Independent WSP101 task-validity tests: DEV pairs only, no learners."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paired_fixture import (
    DEV_CONTEXTS, STEPS, _PairOracle, digits4, observe_world,
    paired_delayed_witness, paired_passive_proof, passive_source, rank,
    source_sha256, validate_passive_source
)


class PairedFixtureTests(unittest.TestCase):
    def test_original_world_identities_fail_closed(self):
        for original in (-1, 8, 101011, 101026, 101101, 101132,
                         101201, 101216, 101301, 101332, None, True, "0"):
            for mode in (0, 1):
                with self.assertRaises(PermissionError):
                    observe_world(original, mode)
                with self.assertRaises(PermissionError):
                    passive_source(original, mode)
        for bad in (-1, 2, True, None, "0"):
            with self.assertRaises(ValueError):
                observe_world(0, bad)

    def test_passive_observations_are_byte_identical(self):
        for fid in DEV_CONTEXTS:
            first = passive_source(fid, 0)
            second = passive_source(fid, 1)
            self.assertEqual(first, second)
            self.assertEqual(source_sha256(first), source_sha256(second))
            proof = paired_passive_proof(fid)
            self.assertTrue(proof["same_source"])
            self.assertEqual(proof["episodes"], 16)
            self.assertEqual(proof["transitions_per_mode"], 64)
            self.assertEqual(proof["source_sha256"], source_sha256(first))
            self.assertTrue(validate_passive_source(first))
            self.assertEqual(first, passive_source(fid, 0))
            self.assertEqual(first, passive_source(fid, 1))

    def test_any_passive_sequence_is_mode_neutral_for_extra_starts(self):
        for fid in DEV_CONTEXTS:
            for start in range(32):
                initial = digits4((start * 113 + fid * 17) % 4096)
                left, right = observe_world(fid, 0), observe_world(fid, 1)
                self.assertEqual(left.reset(initial), right.reset(initial))
                for _ in range(STEPS):
                    self.assertEqual(left.step(0), right.step(0))

    def test_consequential_probe_has_one_step_delay(self):
        for fid in DEV_CONTEXTS:
            for start in range(32):
                initial = digits4((start * 127 + fid * 29) % 4096)
                w = paired_delayed_witness(fid, initial)
                self.assertTrue(w["immediate_equal"])
                self.assertTrue(w["delayed_visible_differs"])
                self.assertEqual(w["delayed_channel_difference_count"], 2)
                self.assertEqual(len(w["first_step_observations"]), 6)

    def test_no_latch_control_eliminates_delayed_mode_difference(self):
        for fid in DEV_CONTEXTS:
            trigger = 1 + rank(fid, "TRIGGER", 0) % 3
            for start in range(8):
                initial = digits4((start * 71 + fid * 19) % 4096)
                left = _PairOracle(fid, 0, no_latches=True)
                right = _PairOracle(fid, 1, no_latches=True)
                self.assertEqual(left.reset(initial), right.reset(initial))
                for action in (trigger, 0, 2, 1):
                    self.assertEqual(left.step(action), right.step(action))

    def test_public_interface_hides_labels_in_observation_records(self):
        o = observe_world(2, 1)
        self.assertEqual(set(o.__slots__), {"reset", "step"})
        self.assertFalse(hasattr(o, "mode"))
        self.assertFalse(hasattr(o, "trigger"))
        self.assertFalse(hasattr(o, "_program"))
        self.assertEqual(len(o.reset(digits4(42))), 6)
        r = o.step(1)
        self.assertEqual(set(r), {"observation", "reward"})
        self.assertTrue(all(type(x) is int and 0 <= x < 4 for x in r["observation"]))
        self.assertIn(r["reward"], (0, 1))
        source = passive_source(2, 1)
        self.assertIsInstance(source, tuple)
        self.assertTrue(all(type(row[1]) is int for ep in source for row in ep))

    def test_strict_reset_action_and_episode_budget(self):
        w = observe_world(0, 0)
        for bad in ((0,) * 5, (0,) * 7, (0,0,0,0,0,True),
                    (0,0,0,0,0,-1), None, 0):
            with self.assertRaises(ValueError):
                w.reset(bad)
        w.reset(digits4(0))
        for a in (True, -1, 4, None, "0"):
            with self.assertRaises(ValueError):
                w.step(a)
        for a in (0, 1, 2, 3):
            w.step(a)
        with self.assertRaises(ValueError):
            w.step(0)
        w.reset(digits4(3))
        self.assertEqual(set(w.step(0)), {"observation", "reward"})

    def test_passive_source_tamper_rejected(self):
        src = passive_source(0, 0)
        with self.assertRaises(ValueError):
            validate_passive_source(src[:-1])
        tampered = [list(ep) for ep in src]
        tampered[0][0] = (src[0][0][0], 3, src[0][0][2], src[0][0][3])
        with self.assertRaises(ValueError):
            validate_passive_source(tampered)
        tampered = [list(ep) for ep in src]
        tampered[0][1] = ((3,) * 6, 0, src[0][1][2], src[0][1][3])
        with self.assertRaises(ValueError):
            validate_passive_source(tampered)
        self.assertEqual(len(DEV_CONTEXTS), 8)


if __name__ == "__main__":
    unittest.main()
