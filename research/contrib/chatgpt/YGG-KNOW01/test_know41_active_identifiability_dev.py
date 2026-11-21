"""KNOW41 mock-only tests: do not open private FIT/HELD consequences."""
import unittest
from know41_active_identifiability_dev import (
    ChosenActionTable, expected_milli, key, protocol
)

class Know41MockOnly(unittest.TestCase):
    def test_prospective_protocol_seal(self):
        p = protocol()
        self.assertTrue(p["seed_custody"]["primary_first_use"].startswith("NONE;"))
        seeds = (p["seed_custody"]["fit"] + p["seed_custody"]["held_fork_theta0"] +
                 p["seed_custody"]["held_fork_theta1"])
        self.assertEqual(len(set(seeds)), 36)
        self.assertFalse(p["authority"]["native_training"])
        self.assertEqual(p["budgets"]["maximum_held_source_actions"], 6144)

    def test_passive_worlds_exactly_indistinguishable(self):
        self.assertEqual({key(c, a) for c in range(8) for a in (0, 1)}, set(range(16)))
        for c in range(8):
            self.assertEqual({expected_milli(g, c, 0, theta)
                              for g in ("CHAIN", "FORK") for theta in (0, 1)}, {350})
            self.assertTrue({expected_milli(g, c, 1, theta)
                             for g in ("CHAIN", "FORK") for theta in (0, 1)}
                            <= {150, 350, 550})
        distinguishing = [c for c in range(8)
                          if expected_milli("FORK", c, 1, 0) !=
                          expected_milli("FORK", c, 1, 1)]
        self.assertEqual(len(distinguishing), 4)
        self.assertTrue(all(expected_milli("FORK", c, 1, 0) !=
                            expected_milli("FORK", c, 1, 1) for c in distinguishing))

    def test_active_witness_only_and_cold_restoration(self):
        m = ChosenActionTable()
        actions = []
        for t in range(256):
            c = t % 8
            a = m.choose(t, c)
            with self.assertRaisesRegex(ValueError, "UNWITNESSED_ACTION"):
                m.observe(t, c, 1 - a, 0)
            # Explicit injected MOCK, not a new source-family consequence.
            y = int((7 * t + 3 * c + a) % 11 < 5)
            m.observe(t, c, a, y)
            actions.append(a)
            if (t + 1) % 64 == 0:
                frozen = m.checkpoint()
                self.assertLess(len(frozen), 4096)
                restored = ChosenActionTable.cold(frozen)
                self.assertEqual(restored.checkpoint(), frozen)
                self.assertEqual([restored.prob(c, a) for c in range(8) for a in (0, 1)],
                                 [m.prob(c, a) for c in range(8) for a in (0, 1)])
                m = restored
        self.assertEqual(m.received, 256)
        self.assertEqual(sum(m.n), 256)
        self.assertGreater(sum(actions), 0)
        self.assertLess(sum(actions), 256)

    def test_strict_inputs_and_corrupt_checkpoint(self):
        m = ChosenActionTable()
        for c, a in ((True, 0), (0, True), (8, 0)):
            with self.assertRaisesRegex(ValueError, "KEY"):
                key(c, a)
        with self.assertRaisesRegex(ValueError, "CHOOSE"):
            m.choose(1, 0)
        a = m.choose(0, 0)
        with self.assertRaisesRegex(ValueError, "CHOOSE"):
            m.choose(0, 0)
        m.observe(0, 0, a, 1)
        frozen = m.checkpoint()
        for bad in ('{"n":[]}', frozen.replace('"received":1', '"received":2'),
                    '{"n":[],"n":[]}'):
            with self.assertRaises(ValueError):
                ChosenActionTable.cold(bad)

if __name__ == "__main__":
    unittest.main()
