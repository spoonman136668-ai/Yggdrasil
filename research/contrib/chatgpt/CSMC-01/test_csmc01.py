"""CSMC-01 pinned original-native FIT-only qualification tests.

All labels are from already consumed FIT 0..49 only; no original first use.
Primary local surrogate was exploratory and not confirmatory preregistered science.
"""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience

SOURCE = Path(__file__).with_name("selector.py")
spec = importlib.util.spec_from_file_location("csmc01_selector", SOURCE)
csmc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csmc)
EXPECTED_SELECTED = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                     13, 14, 16, 17, 25, 26, 30, 33)

class CSMC01Pinned(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = csmc.fit()
        cls.selected, cls.evaluations, cls.reference = csmc.select(cls.rows)

    def test_archived_source_pin_and_fit_isolation(self):
        self.assertEqual(sha256(csmc.TRACE.read_bytes()).hexdigest(), csmc.TRACE_PIN)
        self.assertEqual(len(self.rows), 50)
        self.assertEqual(len({csmc.terminal_cell(x) for x in self.rows}), 15)

    def test_frozen_capacity_and_projection_anchors(self):
        self.assertEqual(self.selected, EXPECTED_SELECTED)
        self.assertEqual(self.evaluations, 583)
        self.assertEqual(len(self.selected), 20)
        self.assertTrue(set(range(8)).issubset(self.selected))
        self.assertEqual(len({csmc.terminal_cell(self.rows[i]) for i in self.selected}), 15)

    def test_deterministic_selection_and_no_extra_source_actions(self):
        repeated, evaluations, _ = csmc.select(self.rows)
        self.assertEqual(repeated, self.selected)
        self.assertEqual(evaluations, self.evaluations)

    def test_actual_original_native_vs_compact_and_action_parity(self):
        full = csmc.verify_native(self.rows, range(50))
        small = csmc.verify_native(self.rows, self.selected)
        self.assertEqual(full._projection, 0)
        self.assertEqual(small._projection, 0)
        self.assertEqual(full._selected(full._transition_loss), 0)
        self.assertEqual(small._selected(small._transition_loss), 1)
        first, second, decisions = csmc.readout(csmc.make_compact(self.rows, range(50)))
        a, b, other = csmc.readout(csmc.make_compact(self.rows, self.selected))
        self.assertEqual(decisions, other)
        self.assertEqual(max(abs(x-y) for x,y in zip(first,a)), Fraction(2,13))
        self.assertEqual(max(abs(x-y) for x,y in zip(second,b)), Fraction(4,21))

    def test_original_native_cold_restore_and_tamper_rejection(self):
        native = csmc.make_native(self.rows, self.selected)
        raw = native.checkpoint()
        restored = NativeEpisodeExperience.restore(raw, sha256(raw).hexdigest())
        self.assertEqual(restored.checkpoint(), raw)
        self.assertEqual(restored.consolidate().checkpoint(), raw)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(raw + b"x", sha256(raw).hexdigest())

    def test_original_native_duplicate_identity_noop_and_conflict(self):
        native = csmc.make_native(self.rows, self.selected)
        ident, views, row = self.rows[self.selected[0]]
        self.assertIs(native.observe(ident, views, dict(row)), native)
        altered = dict(row)
        altered["s2"] ^= 1
        with self.assertRaises(ValueError):
            native.observe(ident, views, altered)
        self.assertEqual(native.checkpoint(), native.consolidate().checkpoint())

    def test_frozen_engineering_gate_stays_negative(self):
        result = csmc.evaluate()
        self.assertEqual(result["action_disagreements"], 0)
        self.assertEqual(result["terminal_coverage"], 15)
        self.assertFalse(result["engineering_gate_pass"])
        self.assertFalse(result["held_evaluated"])
        self.assertEqual(result["science"], "UNVERIFIED")

if __name__ == "__main__":
    unittest.main()
