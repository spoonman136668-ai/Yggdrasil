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
