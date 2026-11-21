"""CAP04 V2 source-only clock shortcut. No science/registered generator use."""
from __future__ import annotations

from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / "research/contrib/chatgpt/YGG-CAP04/clock_only_negative_control.py"
spec = importlib.util.spec_from_file_location("cap04_clock_only", SCRIPT)
clock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clock)


class ClockOnlyNegativeTests(unittest.TestCase):
    def test_original_source_and_unchanged_science_prereg(self):
        source = clock.source_guard()
        self.assertEqual(clock.git_blob_sha(clock.SOURCE_FILE.read_bytes()),
                         clock.SOURCE_GIT_BLOB)
        self.assertEqual(clock.git_blob_sha((clock.HERE/"prereg.json").read_bytes()),
                         clock.PREREG_GIT_BLOB)
        self.assertEqual(source.SCHEMA, "yggdrasil.cap04.prospective-source.v2")
        self.assertEqual(source.BOUNDARIES, (0, 32, 72, 96))
        for seed in source.REGISTERED:
            with self.subTest(seed=seed), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.generate_registered(seed)

    def test_clock_learns_16_public_actions_then_predicts_80_previous(self):
        r = clock.census()
        self.assertEqual(r["results"]["n"], 80)
        self.assertEqual(r["early_public_actions_fit"], 16)
        self.assertEqual(r["results"]["correct"]["clock16"], 80)
        self.assertEqual(r["results"]["correct"]["current_action_only"], 35)
        self.assertEqual(r["results"]["correct"]["clock4"], 35)
        self.assertEqual(r["results"]["correct"]["clock16_shifted"], 5)
        self.assertEqual(r["conclusion"], "CAP04_CLOCK_ALIAS_CONFIRMED")
        self.assertFalse(r["native_history_gain_verified"])
        self.assertFalse(r["scientific_gain_verified"])
        self.assertFalse(r["protected_first_use"])
        self.assertEqual(r["source_episodes_generated"], 0)
        self.assertEqual(r["registered_source_actions"], 0)
        self.assertEqual(r["learner_training_steps"], 0)

    def test_all_3_frozen_windows_and_negative_controls(self):
        r = clock.census()
        expected = {
            "familiar_continuation": (16, 7, 7, 1),
            "unfamiliar": (40, 18, 16, 2),
            "return": (24, 10, 12, 2),
        }
        self.assertEqual(set(r["results"]["phases"]), set(expected))
        for name, (count, current, mod4, shifted) in expected.items():
            row = r["results"]["phases"][name]
            self.assertEqual(row["n"], count)
            self.assertEqual(row["correct"], {
                "clock16": count,
                "current_action_only": current,
                "clock4": mod4,
                "clock16_shifted": shifted,
            })

    def test_current_action_alone_does_not_identify_predecessor(self):
        source = clock.source_guard()
        actions = tuple(source.action_at(t) for t in range(96))
        self.assertEqual(len(set(actions)), 4)
        self.assertEqual(Counter(actions), Counter({a: 24 for a in source.ACTIONS}))
        previous = {a: set() for a in source.ACTIONS}
        for t in range(16, 96):
            previous[actions[t]].add(actions[t-1])
        self.assertGreaterEqual(min(map(len, previous.values())), 2)
        self.assertTrue(all(actions[t] == actions[t % 16] for t in range(96)))
        self.assertTrue(all(set(actions[t:t+4]) == set(source.ACTIONS)
                            for t in range(0, 96, 4)))

    def test_source_sha_tamper_fails_before_schedule_use(self):
        original = clock.SOURCE_FILE
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory)/"prospective_source.py"
            altered.write_bytes(original.read_bytes() + b"\n# forged")
            try:
                clock.SOURCE_FILE = altered
                with self.assertRaisesRegex(ValueError, "ORIGINAL_SOURCE_DRIFT"):
                    clock.census()
            finally:
                clock.SOURCE_FILE = original

    def test_original_bytes_stay_immutable_and_bad_fit_rejected(self):
        a = clock.SOURCE_FILE.read_bytes()
        b = (clock.HERE/"prereg.json").read_bytes()
        source = clock.source_guard()
        actions = tuple(source.action_at(t) for t in range(96))
        for stop in (1, 97, False, 1.0):
            with self.subTest(stop=stop), self.assertRaisesRegex(
                    ValueError, "INVALID_FIT_WINDOW"):
                clock.action_majority(actions, stop=stop)
        self.assertEqual(a, clock.SOURCE_FILE.read_bytes())
        self.assertEqual(b, (clock.HERE/"prereg.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
