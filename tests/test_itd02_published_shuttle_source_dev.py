"""Development tests: ORIGINAL publisher bytes inspected, but never stepped.

Tests that exercise a source action use patched source-FREE toy arrays only.
They cannot create first-use original science or consume a protected cohort.
"""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from yggdrasil.itd02_published_shuttle_source_dev import (
    ACTIONS, OBSERVATIONS, ORIGINAL_PUBLISHER_SHA256,
    PublishedShuttleOwnerDev, SourcePreflightDenied,
    read_original_published_model,
)
from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev


def artificial_source_free_model():
    # Explicit toy unit fixture, NEVER the actual publisher task.
    o = [(1.0, 0., 0., 0., 0.) for _ in range(8)]
    o[7] = (0., 0., 1., 0., 0.)
    t = tuple(tuple(1. if x == i else 0. for x in range(8))
              for i in range(8))
    return {
        "initial": (0., 0., 0., 0., 0., 0., 0., 1.),
        "transitions": {a: t for a in ACTIONS},
        "observations": tuple(o),
        "rewards": {},
    }


class PublishedSourceIdentityTests(unittest.TestCase):
    def test_exact_publisher_public_source_parse_only(self):
        source = os.environ.get("ITD02_PUBLISHED_SOURCE_PATH")
        if not source:
            self.skipTest("Authentic publisher bytes available only in owner CI preflight")
        raw = Path(source).read_bytes()
        model = read_original_published_model(raw)
        self.assertEqual(model["source_sha256"], ORIGINAL_PUBLISHER_SHA256)
        self.assertFalse(model["scientific_first_use"])
        self.assertEqual(tuple(model["transitions"]), ACTIONS)
        self.assertEqual(len(model["observations"]), 8)
        self.assertEqual(len(model["observations"][0]), 5)
        self.assertEqual(model["initial"][7], 1.)
        self.assertEqual(model["rewards"][("Backup", 3, 0)], 10)
        self.assertEqual(model["rewards"][("GoForward", 6, 6)], -3)
        self.assertEqual(OBSERVATIONS, (
            "LRV", "MRV", "docked_MRV", "Nothing", "docked_LRV"))
        with self.assertRaisesRegex(SourcePreflightDenied, "PUBLISHER_IDENTITY"):
            read_original_published_model(raw[:-1] + bytes([raw[-1] ^ 1])
                                         if len(raw) else b"bad")

    def test_rejects_unpinned_or_modified_original(self):
        for altered in (b"", b"fake POMDP", bytes(2281)):
            with self.assertRaises(SourcePreflightDenied):
                read_original_published_model(altered)

    @patch("yggdrasil.itd02_published_shuttle_source_dev.read_original_published_model",
           return_value=artificial_source_free_model())
    def test_source_owner_unit_fixture_public_wire_and_budget(self, _):
        src = PublishedShuttleOwnerDev(
            b"toy-fixture-only", seed=4, episode_steps=1,
            development_role="OWNER_AUTHORIZED_PUBLIC_FIT_ONLY")
        self.assertEqual(src.reset_public(), "docked_MRV")
        after, reward, terminal, truncated = src.step_public("TurnAround")
        self.assertEqual((after, reward, terminal, truncated),
                         ("docked_MRV", 0, False, True))
        self.assertEqual(src.source_receipt["steps"], 1)
        self.assertFalse(src.source_receipt["protected_first_use"])
        with self.assertRaisesRegex(SourcePreflightDenied, "SOURCE_RESET_NOT_AT_BOUNDARY"):
            src.reset_public()
        with self.assertRaisesRegex(SourcePreflightDenied, "PUBLIC_STEP_INVALID"):
            src.step_public("GoForward")

    @patch("yggdrasil.itd02_published_shuttle_source_dev.read_original_published_model",
           return_value=artificial_source_free_model())
    def test_source_owner_role_and_budget_are_not_optional(self, _):
        with self.assertRaisesRegex(SourcePreflightDenied, "FIT_ROLE"):
            PublishedShuttleOwnerDev(
                b"toy", seed=4, episode_steps=2, development_role="HOLDOUT")
        with self.assertRaisesRegex(SourcePreflightDenied, "INTERACTION_BUDGET"):
            PublishedShuttleOwnerDev(
                b"toy", seed=4, episode_steps=999999,
                development_role="OWNER_AUTHORIZED_PUBLIC_FIT_ONLY")

    def test_native_driver_preserves_truncation_not_forged_terminal(self):
        # This fixture supplies only a developer-authored legal public outcome.
        # It does NOT call published source state or RNG.
        class PublicTruncationFixture:
            resets = 0
            steps = 0
            def reset_public(self):
                self.resets += 1
                return "docked_MRV"
            def step_public(self, action):
                self.steps += 1
                self.last_action = action
                return ("Nothing", 0, False, True)
        f = PublicTruncationFixture()
        session = NativeTrainingSessionDev(max_steps=1)
        result = session.run_episode(f)
        self.assertFalse(result["terminal"])
        self.assertTrue(result["truncated"])
        self.assertEqual(result["steps"], 1)
        self.assertEqual(session.model.transitions, 1)
        self.assertEqual(f.steps, 1)
        self.assertGreater(len(result["checkpoint"]), 0)

    def test_conflicting_terminal_and_truncation_rejected_without_retry(self):
        class InvalidPublicEnd:
            def __init__(self):
                self.reset_calls = 0
                self.steps = 0
            def reset_public(self):
                self.reset_calls += 1
                return "docked_MRV"
            def step_public(self, action):
                self.steps += 1
                return ("Nothing", 0, True, True)
        source = InvalidPublicEnd()
        session = NativeTrainingSessionDev(max_steps=1)
        with self.assertRaisesRegex(ValueError, "CONFLICTING_SOURCE_END"):
            session.run_episode(source)
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(source)
        self.assertEqual(source.steps, 1)
        self.assertEqual(source.reset_calls, 1)


if __name__ == "__main__":
    unittest.main()
