"""Equal-event TD(lambda) control parity tests; source-free engineering only."""
import json
import subprocess
import sys
import unittest

from yggdrasil.itd02_local_ring_memory_dev import ACTIONS
from yggdrasil.itd02_temporal_credit_dev import TemporalCreditRingDev
from yggdrasil.itd02_conventional_td_lambda_dev import ConventionalTDLambdaControlDev

def force_native_action(model, action):
    # Deterministic policy fixture makes both models receive the same selected
    # action sequence. It is not a learner-performance or environment test.
    for row in model.memory.heads:
        row[:] = [0.0, 0.0, 0.0]
    model.memory.heads[ACTIONS.index(action)][0] = 3.0

class MatchedTDLambdaControlTests(unittest.TestCase):
    def test_same_legal_public_event_stream_reaches_both_models(self):
        native = TemporalCreditRingDev()
        control = ConventionalTDLambdaControlDev()
        events = [
            ("LRV", "Backup", 0.0, "MRV", False),
            ("Nothing", "TurnAround", 0.0, "docked_MRV", False),
            ("MRV", "GoForward", 4.0, "docked_LRV", True),
            ("docked_LRV", "Backup", 0.0, "Nothing", False),
            ("Nothing", "GoForward", -2.0, "LRV", True),
        ]
        for observation, action, reward, nxt, terminal in events:
            force_native_action(native, action)
            native.advance(observation)
            chosen = native.choose()
            self.assertEqual(chosen, action)
            control.advance(observation)
            # Explicit event stream supplies identical chosen action and result.
            native.feedback(chosen, reward, terminal=terminal)
            control.feedback(action, reward, next_observation=nxt, terminal=terminal)
        self.assertEqual(native.events, control.events)
        self.assertEqual(native.events, len(events))
        self.assertEqual(len(events), 5)
        self.assertNotEqual(native.parameter_sha256(), control.parameter_sha256())

    def test_tabular_control_assigns_terminal_td_error_to_prior_action(self):
        control = ConventionalTDLambdaControlDev()
        control.advance("LRV")
        control.feedback("Backup", 0.0, next_observation="Nothing", terminal=False)
        prior = control.q.get("LRV|Backup", 0.0)
        control.advance("Nothing")
        control.feedback("TurnAround", 4.0, terminal=True)
        self.assertGreater(control.q["LRV|Backup"], prior)
        self.assertEqual(control.events, 2)
        self.assertEqual(control.traces, {})

    def test_bad_events_leave_pending_and_values_unchanged(self):
        control = ConventionalTDLambdaControlDev()
        control.advance("LRV")
        before = control.checkpoint()
        with self.assertRaisesRegex(ValueError, "NEXT_PUBLIC_OBSERVATION_REQUIRED"):
            control.feedback("Backup", 0.0, terminal=False)
        self.assertEqual(control.checkpoint(), before)
        with self.assertRaisesRegex(ValueError, "INVALID_PUBLIC_REWARD_OR_FLAGS"):
            control.feedback("Backup", float("nan"), next_observation="Nothing")
        self.assertEqual(control.checkpoint(), before)
        control.feedback("Backup", 0.0, next_observation="Nothing")

    def test_cold_restart_and_frozen_observation_only(self):
        control = ConventionalTDLambdaControlDev()
        control.advance("LRV")
        control.feedback("Backup", 0.0, next_observation="Nothing")
        control.advance("Nothing")
        saved = control.checkpoint()
        restored = ConventionalTDLambdaControlDev.restore(saved)
        self.assertEqual(restored.q, control.q)
        self.assertEqual(restored.traces, control.traces)
        self.assertEqual(restored.pending, "Nothing")
        digest = restored.parameter_sha256()
        restored.pending = None
        restored.start_frozen_evaluation(digest)
        restored.advance("MRV")
        restored.feedback("GoForward", 100.0, next_observation="LRV", learning=False, terminal=True)
        self.assertEqual(restored.parameter_sha256(), digest)
        self.assertEqual(restored.events, 1)

    def test_corrupt_checkpoint_rejected(self):
        control = ConventionalTDLambdaControlDev()
        control.advance("LRV")
        raw = control.checkpoint()
        bad = json.loads(raw)
        bad["body"]["q"]["LRV|Backup"] = 999.0
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_CONTROL_CHECKPOINT"):
            ConventionalTDLambdaControlDev.restore(json.dumps(bad).encode())

if __name__ == "__main__":
    unittest.main()
