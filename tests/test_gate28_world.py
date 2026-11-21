"""Gate28 generator diagnostics; no primary seed or scoring."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import world


class TestGate28World(unittest.TestCase):
    def test_contract_counts(self):
        self.assertEqual({k: len(v) for k, v in world.SEED_COHORTS.items()},
                         {"shifted": 48, "stationary": 24, "independent_noise": 24})
        self.assertEqual(len(world.ACTIONS), 13)
        self.assertEqual(world.PHASE_LENGTHS, {"A": 96, "B": 64, "R": 64})
        with self.assertRaisesRegex(ValueError, "NONPRIMARY_SEED"):
            world.HiddenWorld(900001)

    def test_diagnostic_only(self):
        self.assertFalse(world.validate_diagnostic()["primary_consumed"])

    def test_replay_and_do(self):
        a, b = (world.HiddenWorld(900002, diagnostic=True) for _ in range(2))
        for phase in ("B", "R"):
            for t in range(6):
                for action in world.ACTIONS:
                    x = a.feedback(phase, t, action)
                    self.assertEqual(x, b.feedback(phase, t, action))
                    self.assertEqual(len(x.context), 8)
                    self.assertEqual(len(x.intermediates), 6)
                    self.assertTrue(set(x.context + x.intermediates +
                                        (x.consequence,)) <= {0, 1})
                    if action < 12:
                        self.assertEqual(x.intermediates[action // 2], action % 2)

    def test_held_contexts_separate(self):
        w = world.HiddenWorld(900003, diagnostic=True)
        seen = {w.source(i).context for i in range(96)}
        for phase in ("B", "R"):
            seen.update(w.feedback(phase, t, 12).context for t in range(64))
        held = {w.held_context(phase, t)
                for phase in ("B", "R") for t in range(32)}
        self.assertEqual(len(held), 64)
        self.assertTrue(seen.isdisjoint(held))

    def test_rules_shift_then_return(self):
        w = world.HiddenWorld(900004, diagnostic=True)
        self.assertEqual([w._layer(p) for p in ("A", "B", "R")],
                         ["A", "B", "A"])

    def test_held_lag_uses_public_last_context(self):
        # The hidden phase's lag parent must be an observation the policy
        # already received, not a private withheld context unknown to it.
        w = world.HiddenWorld(900009, diagnostic=True)
        for phase in ("B", "R"):
            last_public = w.public_context(phase, 63)
            for step in (0, 13, 31):
                self.assertEqual(w._previous_context(phase, step, held=True),
                                 last_public)
                self.assertEqual(w.held_query(phase, step, 12).context,
                                 w.held_context(phase, step))
        rule = w._rules["B"][2]
        self.assertEqual(rule.kind, "lag_xor")
        row = w.held_query("B", 0, 12)
        cells = row.context + row.intermediates
        expected = (w.public_context("B", 63)[rule.parents[0] % 8] ^
                    cells[rule.parents[1]] ^ rule.invert)
        self.assertEqual(row.intermediates[2], expected)

    def test_invalid_input_rejected(self):
        w = world.HiddenWorld(900005, diagnostic=True)
        for action in (-1, 13, 300):
            with self.assertRaisesRegex(ValueError, "INVALID_ACTION"):
                w.feedback("B", 0, action)
        with self.assertRaisesRegex(ValueError, "INVALID_HELD_PHASE"):
            w.held_query("A", 0, 12)
        with self.assertRaisesRegex(ValueError, "INVALID_PHASE_STEP"):
            w.feedback("B", 64, 12)
