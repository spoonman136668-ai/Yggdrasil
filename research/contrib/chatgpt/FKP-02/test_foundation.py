"""Small focused foundation tests (source-only, unprotected, no model integration)."""
import importlib
import unittest

foundation = importlib.import_module("foundation")
source = importlib.import_module("source")


class FKP02FoundationTests(unittest.TestCase):
    def test_derive_only_from_real_observed_public_consequences(self):
        world = source.PublicCausalWorld(10000)
        history = tuple((a, world.observe(a))
                        for a in world.public_view().allowed_actions)
        self.assertEqual(len(history), 64)
        for effect in range(4):
            candidates = foundation.infer_pair_tables(history, effect)
            self.assertEqual(len(candidates), 1)
            a, b, table = candidates[0]
            self.assertIn(a, range(16))
            self.assertIn(b, range(16))
            self.assertIn(table, range(16))

    def test_mismatched_observations_do_not_fabricate_a_full_rule(self):
        world = source.PublicCausalWorld(10000)
        history = [(a, world.observe(a))
                   for a in world.public_view().allowed_actions]
        # One conflicting outcome at the exact same public input invalidates
        # the entire history (without ever consulting a hidden source label).
        corrupted = tuple(history[:-1] + [(history[0][0], history[0][1] ^ 1)])
        with self.assertRaises(ValueError):
            foundation.infer_pair_tables(corrupted, 0)  # 65 is wrong evidence length

    def test_uninformative_constant_records_do_not_misreport_unique_parents(self):
        history = tuple((i, 0) for i in range(64))
        candidates = foundation.infer_pair_tables(history, 0)
        self.assertEqual(candidates, ())

    def test_composer_does_not_hardcode_novel_gate_names(self):
        gates = (6, 7, 8, 14)  # independently discovered table IDs
        grammar, counts = foundation.compose_generic_programs(gates, 5)
        self.assertTrue(all(a <= b for a, b in zip(counts, counts[1:])))
        mux = sum(source.evaluate_gate(x, "mux3", (0, 1, 2)) << x
                  for x in range(8))
        majority = sum(source.evaluate_gate(x, "majority3", (0, 1, 2)) << x
                       for x in range(8))
        self.assertIn(mux, grammar)
        self.assertIn(majority, grammar)
        self.assertGreater(grammar[mux]["depth"], 0)
        self.assertGreater(grammar[majority]["depth"], 0)

    def test_no_source_private_operator_in_public_history(self):
        world = source.PublicCausalWorld(10001)
        view = world.public_view()
        self.assertEqual(set(view.__dataclass_fields__),
                         {"input_bits", "effect_bits", "allowed_actions",
                          "held_inputs"})
        history = tuple((a, world.observe(a))
                        for a in view.allowed_actions)
        self.assertEqual(len(history), 64)


if __name__ == "__main__":
    unittest.main()
