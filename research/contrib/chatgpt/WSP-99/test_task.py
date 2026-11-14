"""WSP99 structural and negative DEV fixtures only; no original-world use."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import FixtureWorld, auditor_delayed_witnesses, bits, EPISODE_LIMIT


class FixtureTests(unittest.TestCase):
    def test_reproducible(self):
        for i in range(8):
            a, b = FixtureWorld(i), FixtureWorld(i)
            self.assertEqual(a.reset(bits(19)), b.reset(bits(19)))
            for action in (0, 1, 2, 3):
                self.assertEqual(a.step(action), b.step(action))
            a.reset(bits(19))
            b.reset(bits(19))
            self.assertEqual(a.step(0), b.step(0))

    def test_hidden_action_effect_is_delayed_and_genuine(self):
        for i in range(8):
            w = auditor_delayed_witnesses(i)
            self.assertEqual(len(w), 2)
            self.assertEqual({item[0] for item in w}, {0, 1})

    def test_hidden_ablation_removes_effect(self):
        for i in range(8):
            self.assertEqual(auditor_delayed_witnesses(i, no_latches=True), ())

    def test_no_oracle_state_leaks(self):
        for i in range(8):
            model = FixtureWorld(i)
            self.assertEqual(len(model.reset(bits(17))), 6)
            record = model.step(0)
            self.assertEqual(set(record), {"observation", "reward"})
            self.assertEqual(len(record["observation"]), 6)
            self.assertIn(record["reward"], (0, 1))

    def test_original_worlds_blocked(self):
        for bad in (-1, 8, 99011, 99042, 99101, 99164, None, "0", True):
            with self.assertRaises(ValueError):
                FixtureWorld(bad)
        for seed in (99011, 99101):
            with self.assertRaises(PermissionError):
                FixtureWorld.original_world(seed)

    def test_bad_inputs_fail_closed(self):
        for bad in (None, 0, (0,) * 5, (0,) * 7,
                    (0, 0, 0, 0, 0, True), (0, 0, 0, 0, 0, 2)):
            with self.assertRaises(ValueError):
                FixtureWorld(0).reset(bad)
        world = FixtureWorld(0)
        for bad in (True, -1, 4, "2"):
            with self.assertRaises(ValueError):
                world.step(bad)

    def test_strict_episode_budget_and_reset(self):
        world = FixtureWorld(0)
        for _ in range(EPISODE_LIMIT):
            world.step(0)
        with self.assertRaises(ValueError):
            world.step(0)
        world.reset(bits(1))
        self.assertIn("observation", world.step(0))


if __name__ == "__main__":
    unittest.main()
