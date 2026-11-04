"""YGG-DB01 focused structural tests; not scientific training results."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).with_name("local_development.py")
spec = importlib.util.spec_from_file_location("ygg_db01_local", MODULE)
mod = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class DevelopmentTests(unittest.TestCase):
    def test_feedback_mapping_and_replay(self):
        beats = mod.feedback(1)
        noise = mod.feedback(0)
        self.assertEqual(beats, (1., 0., 0., 0.) * 4)
        self.assertEqual(noise, mod.feedback(0))
        self.assertNotEqual(beats, noise)
        self.assertGreater(len(set(noise)), 8)

    def test_reject_invalid_feedback(self):
        for value in (True, -1, 2, 0.5):
            with self.assertRaises(ValueError):
                mod.feedback(value)

    def test_locality_and_immutable_channel(self):
        model = mod.LocalDevelopment()
        state = tuple(tuple((0., 0.) for _ in range(4)) for _ in range(4))
        quiet = tuple(tuple(0. for _ in range(4)) for _ in range(4))
        signal = tuple(tuple(1. if (y, x) == (0, 0) else 0. for x in range(4)) for y in range(4))
        baseline = model.step(state, quiet)
        changed = model.step(state, signal)
        self.assertEqual(changed[0][0][1], 0.125)
        self.assertEqual(changed[3][3], baseline[3][3])
        self.assertTrue(all(changed[y][x][0] == 0. for y in range(4) for x in range(4)))
        self.assertEqual(model.step(state, signal), changed)

    def test_neighborhood_propagation(self):
        model = mod.LocalDevelopment()
        state = tuple(tuple((0., 1. if (y, x) == (0, 0) else 0.) for x in range(4)) for y in range(4))
        quiet = tuple(tuple(0. for _ in range(4)) for _ in range(4))
        next_state = model.step(state, quiet)
        self.assertGreater(next_state[0][1][1], 0.)
        self.assertEqual(next_state[3][3][1], 0.)


    def test_counterfactual_feedback_controls(self):
        for length in (4, 16, 17):
            for seed in (0, 1, 16, 17):
                for outcome in (0, 1):
                    self.assertEqual(
                        mod.feedback_control(outcome, "mapped", length, seed),
                        mod.feedback(outcome, length, seed))
                    self.assertEqual(
                        mod.feedback_control(outcome, "reversed", length, seed),
                        mod.feedback(1 - outcome, length, seed))
                    self.assertEqual(
                        mod.feedback_control(outcome, "no_feedback", length, seed),
                        (0.0,) * length)
                self.assertEqual(
                    mod.feedback_control(0, "sham", length, seed),
                    mod.feedback_control(1, "sham", length, seed))
                self.assertEqual(
                    mod.feedback_control(0, "sham", length, seed),
                    mod.feedback(seed & 1, length, seed))
        for bad in (True, 1, "unknown", None):
            with self.assertRaises(ValueError):
                mod.feedback_control(1, bad)
        for bad in (True, -1, 2, 0.5):
            with self.assertRaises(ValueError):
                mod.feedback_control(bad, "no_feedback")
        with self.assertRaises(ValueError):
            mod.feedback_control(1, "sham", length=3)
        with self.assertRaises(ValueError):
            mod.feedback_control(1, "reversed", seed=-1)

    def test_equal_frame_budget_local_channel_and_deterministic_replay(self):
        model = mod.LocalDevelopment()
        initial = tuple(tuple((0.0, 0.0) for _ in range(4)) for _ in range(4))
        def run(outcome, condition, seed=17):
            state = initial
            frames = mod.feedback_control(outcome, condition, length=16, seed=seed)
            for sample in frames:
                signal = tuple(tuple(sample if (y, x) == (1, 1) else 0.0
                                     for x in range(4)) for y in range(4))
                state = model.step(state, signal)
                self.assertEqual(len(state), 4)
                self.assertTrue(all(len(row) == 4 for row in state))
                self.assertTrue(all(cell[0] == 0.0 for row in state for cell in row))
            return state, len(frames)
        for condition in ("mapped", "reversed", "sham", "no_feedback"):
            for outcome in (0, 1):
                self.assertEqual(run(outcome, condition), run(outcome, condition))
                self.assertEqual(run(outcome, condition)[1], 16)
        self.assertEqual(run(0, "sham"), run(1, "sham"))
        self.assertEqual(run(0, "no_feedback"), run(1, "no_feedback"))
        self.assertEqual(run(1, "reversed"), run(0, "mapped"))
        self.assertEqual(run(0, "reversed"), run(1, "mapped"))

    def test_shape_and_signal_guards(self):
        model = mod.LocalDevelopment()
        state = tuple(tuple((0., 0.) for _ in range(4)) for _ in range(4))
        with self.assertRaises(ValueError):
            model.step(state, ((0.,),))
        with self.assertRaises(ValueError):
            mod.LocalDevelopment(channels=3)
        bad = tuple(tuple(2. for _ in range(4)) for _ in range(4))
        with self.assertRaises(ValueError):
            model.step(state, bad)


if __name__ == "__main__":
    unittest.main()
