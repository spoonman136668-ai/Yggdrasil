"""Native public-history coverage selection and compatibility checks."""
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

def witness(model, index, context, first, state, second):
    views = ((context, 0), (context, 1))
    row = {"s1": context, "x1": first, "s2": state, "x2": second, "y": index & 1}
    return model.observe(digest(canonical(["ckad24-coverage-unit", index])), views, row)

def initial():
    model = NativeEpisodeExperience()
    for index in range(8):
        model = witness(model, index, 0, 1, 0, 1)
    return model

class CoverageRegression(unittest.TestCase):
    def test_less_observed_action_at_both_decisions_and_read_only(self):
        model = initial().begin_stream()
        raw = model.checkpoint()
        self.assertEqual(model.coverage_explore((0, 1)), 0)
        self.assertEqual(model.coverage_explore((0, 1), 1, 0), 0)
        self.assertEqual(model.coverage_explore((1, 1)), model.context_explore((1, 1)))
        self.assertEqual(raw, model.checkpoint())

    def test_window_is_total_rows_not_last_matching_rows(self):
        model = initial().begin_stream()
        for index in range(8, 40):
            model = witness(model, index, 1, 0, 1, 0)
        self.assertEqual(model.coverage_explore((0, 0)), model.context_explore((0, 0)))
        self.assertEqual(model.coverage_explore((1, 0)), 1)
        self.assertEqual(model.coverage_explore((1, 0), 0, 1), 1)

    def test_public_history_validation_and_stream_requirement(self):
        with self.assertRaises(ValueError):
            initial().coverage_explore((0, 0))
        model = initial().begin_stream()
        for args in (((0, 0), 0), ((0, 0), 0, 2), ((0, 0), True, 0), ([0, 0],)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                model.coverage_explore(*args)

    def test_restored_existing_stream_continues_identically(self):
        model = initial().begin_stream()
        for index in range(8, 24):
            model = witness(model, index, index & 1, (index // 2) & 1,
                            (index // 3) & 1, (index // 4) & 1)
        raw = model.checkpoint()
        restored = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(restored.checkpoint(), raw)
        for view in ((0, 0), (1, 1)):
            self.assertEqual(model.coverage_explore(view), restored.coverage_explore(view))
        self.assertEqual(witness(model, 24, 0, 0, 0, 1).checkpoint(),
                         witness(restored, 24, 0, 0, 0, 1).checkpoint())

if __name__ == "__main__":
    unittest.main()
