"""FKP-02 actual rule-selection interface and negative controls, DEV-only."""
import importlib
import unittest

source = importlib.import_module("source")
foundation = importlib.import_module("foundation")
learner = importlib.import_module("learner")


class FKP02LearnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar, cls.counts = foundation.compose_generic_programs(
            (6, 7, 8, 14), max_depth=5)
        cls.functions = learner.hypothesis_functions(cls.grammar)

    def test_three_input_requires_all_three_causal_parents(self):
        self.assertFalse(learner.truly_three_input(0))
        self.assertFalse(learner.truly_three_input(255))
        self.assertFalse(learner.truly_three_input(6))
        self.assertTrue(learner.truly_three_input(sum(
            source.evaluate_gate(state, "majority3", (0, 1, 2)) << state
            for state in range(8))))

    def test_fitted_program_reproduces_all_real_observed_consequences(self):
        w = source.PublicCausalWorld(200)
        xs = tuple(w.public_view().allowed_actions[:16])
        ys = tuple(w.observe(x) for x in xs)
        for use_prior in (True, False):
            with self.subTest(use_prior=use_prior):
                state = learner.fit(xs, ys, self.functions,
                                    use_learned_depth=use_prior)
                self.assertEqual(state["public_training_actions"], 16)
                self.assertEqual(len(state["programs"]), 4)
                self.assertGreater(state["programs_searched"], 0)
                self.assertTrue(all(count > 0 for count in
                                    state["compatible_hypotheses_per_effect"]))
                self.assertEqual(tuple(learner.predict(state, x) for x in xs), ys)
                restored, digest = learner.cold_roundtrip(state)
                self.assertEqual(restored, state)
                self.assertEqual(len(digest), 64)
                self.assertEqual(learner.predict(restored, 0),
                                 learner.predict(state, 0))

    def test_invalid_data_and_abstention(self):
        w = source.PublicCausalWorld(200)
        xs = tuple(w.public_view().allowed_actions[:16])
        ys = tuple(w.observe(x) for x in xs)
        with self.assertRaises(ValueError):
            learner.fit(xs[:-1], ys[:-1], self.functions)
        with self.assertRaises(ValueError):
            learner.fit(xs, ys, ())
        with self.assertRaises(ValueError):
            learner.fit(xs, ys[:-1] + (16,), self.functions)
        with self.assertRaises(ValueError):
            learner.fit(xs, ys, ((0, 255),))
        with self.assertRaises(ValueError):
            learner.predict({"schema": "invalid", "programs": []}, 0)
        with self.assertRaises(ValueError):
            learner.predict({"schema": "invalid", "programs": []}, -1)

    def test_learned_functions_cover_frozen_three_parent_held_effects(self):
        assert len(self.grammar) == 256
        for name in ("mux3", "majority3"):
            truth = sum(source.evaluate_gate(state, name, (0, 1, 2)) << state
                        for state in range(8))
            self.assertIn(truth, self.grammar)
            self.assertTrue(learner.truly_three_input(truth))
            self.assertIn((self.grammar[truth]["depth"], truth), self.functions)


if __name__ == "__main__":
    unittest.main()
