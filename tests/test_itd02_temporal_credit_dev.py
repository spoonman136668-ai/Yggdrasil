"""Temporal-credit source-free tests; never original Shuttle episodes."""
import json
import subprocess
import sys
import unittest

from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, NativeRingMemoryDev
from yggdrasil.itd02_temporal_credit_dev import (
    GAMMA, LAMBDA, TRACE_CAP, TemporalCreditRingDev,
)


def force_action(model, action):
    """Deterministic engineering fixture to choose one legal action."""
    for row in model.memory.heads:
        row[:] = [0.0, 0.0, 0.0]
    model.memory.heads[ACTIONS.index(action)][0] = 3.0


def two_step_training(reward):
    model = TemporalCreditRingDev()
    force_action(model, "Backup")
    model.advance("LRV")
    first = model.choose()
    assert first == "Backup"
    model.feedback(first, 0.0, terminal=False)
    before_delayed_credit = [row[:] for row in model.memory.heads]
    # This fixture represents the next chosen action, not a simulator.
    model.memory.heads[ACTIONS.index("TurnAround")][0] = 3.1
    model.advance("Nothing")
    second = model.choose()
    assert second == "TurnAround"
    model.feedback(second, reward, terminal=True)
    return model, before_delayed_credit


class TemporalCreditDevTests(unittest.TestCase):
    def test_frozen_constants_and_bounded_trace_state(self):
        self.assertAlmostEqual(GAMMA, 0.95)
        self.assertAlmostEqual(LAMBDA, 0.80)
        self.assertLessEqual(abs(TemporalCreditRingDev().eligibility[0][0]), TRACE_CAP)
        self.assertEqual(len(ACTIONS), 3)

    def test_terminal_reward_credits_an_earlier_selected_action(self):
        positive, positive_before = two_step_training(4.0)
        negative, negative_before = two_step_training(-4.0)
        backup = ACTIONS.index("Backup")
        # Backup's earlier, nonterminal head must receive the direction of
        # the later terminal reward, beyond its value before that event.
        p_delta = positive.memory.heads[backup][0] - positive_before[backup][0]
        n_delta = negative.memory.heads[backup][0] - negative_before[backup][0]
        self.assertGreater(p_delta, 0.0)
        self.assertLess(n_delta, 0.0)
        self.assertGreater(p_delta - n_delta, 0.1)
        # The episode boundary clears transient eligibility after applying it.
        self.assertEqual(positive.eligibility, [[0.0] * 3 for _ in ACTIONS])
        self.assertEqual(negative.eligibility, [[0.0] * 3 for _ in ACTIONS])
        self.assertEqual(positive.events, 2)

    def test_trace_decays_and_respects_bound(self):
        model = TemporalCreditRingDev()
        force_action(model, "Backup")
        for i in range(20):
            model.advance("LRV" if i % 2 == 0 else "Nothing")
            action = model.choose()
            if i == 19:
                model.feedback(action, 0.0, terminal=True)
            else:
                model.feedback(action, 0.0, terminal=False)
        self.assertTrue(all(abs(v) <= TRACE_CAP for row in model.eligibility for v in row))
        # terminal cleared the trace, so test its bounded live value via a
        # continuing episode with multiple nonterminal actions.
        force_action(model, "Backup")
        for i in range(3):
            model.advance("MRV")
            action = model.choose()
            model.feedback(action, 0.0, terminal=False)
        self.assertTrue(any(v != 0 for row in model.eligibility for v in row))
        for row in model.eligibility:
            for value in row:
                self.assertLessEqual(abs(value), TRACE_CAP)

    def test_mismatch_and_bad_reward_do_not_change_pending_state(self):
        model = TemporalCreditRingDev()
        model.advance("LRV")
        action = model.choose()
        before = model.checkpoint()
        with self.assertRaisesRegex(ValueError, "MISMATCH"):
            model.feedback("Backup" if action != "Backup" else "GoForward", 10.0)
        self.assertEqual(model.checkpoint(), before)
        with self.assertRaises(ValueError):
            model.feedback(action, float("nan"))
        self.assertEqual(model.checkpoint(), before)
        model.feedback(action, 0.0, terminal=True)

    def test_checkpoint_restores_trace_and_pending_action_across_process(self):
        model = TemporalCreditRingDev()
        force_action(model, "Backup")
        model.advance("LRV")
        action = model.choose()
        model.feedback(action, 0.0, terminal=False)
        model.memory.heads[ACTIONS.index("TurnAround")][0] = 3.1
        model.advance("Nothing")
        selected = model.choose()
        saved = model.checkpoint()
        restored = TemporalCreditRingDev.restore(saved)
        self.assertEqual(restored._selected_action, selected)
        self.assertEqual(restored.eligibility, model.eligibility)
        self.assertEqual(restored.memory.parameter_sha256(), model.memory.parameter_sha256())
        script = """
import json,sys
from yggdrasil.itd02_temporal_credit_dev import TemporalCreditRingDev
m=TemporalCreditRingDev.restore(sys.stdin.buffer.read())
action=m._selected_action
m.feedback(action, 4.0, terminal=True)
print(json.dumps({"events":m.events,"sha":m.parameter_sha256(),"trace":m.eligibility}))
"""
        cp = subprocess.run([sys.executable, "-B", "-c", script], input=saved,
                            capture_output=True, timeout=15, check=True)
        result = json.loads(cp.stdout)
        self.assertEqual(result["events"], 2)
        self.assertEqual(result["trace"], [[0.0] * 3 for _ in ACTIONS])
        self.assertLess(len(saved), 16384)

    def test_frozen_evaluation_observes_but_never_fits(self):
        model = TemporalCreditRingDev()
        model.advance("LRV")
        action = model.choose()
        model.feedback(action, 1.0, terminal=True)
        digest = model.parameter_sha256()
        model.start_frozen_evaluation(digest)
        model.advance("Nothing")
        action = model.choose()
        before = model.memory.parameter_sha256()
        model.feedback(action, 10.0, learning=False, terminal=True)
        self.assertEqual(model.memory.parameter_sha256(), before)
        self.assertEqual(model.parameter_sha256(), digest)

    def test_no_privileged_observation_or_reward_schema_added(self):
        model = TemporalCreditRingDev()
        for value in ("hidden_state", "u_wind", None, {"info": "private"}):
            with self.assertRaises(ValueError):
                model.advance(value)
        model.advance("LRV")
        action = model.choose()
        with self.assertRaises(ValueError):
            model.feedback(action, float("inf"))
        self.assertEqual(model.events, 0)
        model.feedback(action, 0.0, terminal=True)


if __name__ == "__main__":
    unittest.main()
