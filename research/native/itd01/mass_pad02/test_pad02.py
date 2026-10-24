"""PAD-02 focused SOURCE-FREE and non-protected synthetic controls."""
import ast
import itertools
import random
import unittest
from pathlib import Path

from research.native.itd01.mass_pad01 import run as old
from research.native.itd01.mass_pad02 import compare, source


class PAD02(unittest.TestCase):
    def fixture(self):
        # Hand-defined public dummy reward; never instantiates new original hidden role.
        rng = random.Random(123)
        rows = []
        prev = source.ZERO
        for _ in range(192):
            x = tuple(rng.randrange(2) for _ in range(6))
            a = rng.randrange(3)
            y = x[1] ^ x[4] if a == 0 else (x[0] & x[3] if a == 1 else prev[2] ^ x[5])
            rows.append((x, prev, a, y))
            prev = x
        return rows

    def test_frozen_source_roles_disjoint_from_pad01(self):
        self.assertEqual(source.BASE, 202610250000)
        self.assertEqual(source.FIT, 192)
        self.assertEqual(source.DEV, 128)
        self.assertEqual(source.FAMILIES, ("T", "L"))
        self.assertEqual(len({source.seed_for(f, r) for f in source.FAMILIES for r in source.REPLICAS}), 6)
        self.assertTrue(all(source.seed_for(f, r) > old.SEED_BASE + 11000
                            for f in source.FAMILIES for r in source.REPLICAS))

    def test_exact_matched_sparse_control_same_actions_without_oracle(self):
        rows = self.fixture()
        old_model = old.fit_sparse_pair([(x, a, y) for x, _, a, y in rows])
        control = compare.fit_conventional_sparse(rows, ("pair",))
        rng = random.Random(777)
        for _ in range(80):
            x = tuple(rng.randrange(2) for _ in range(6))
            prev = tuple(rng.randrange(2) for _ in range(6))
            legacy = max(range(3), key=lambda a: (old.predict_sparse(old_model, x, a), -a))
            matched = compare.choose_structural(control, x, prev)
            self.assertEqual(matched, legacy)

    def test_training_only_structural_model_can_fit_public_lag(self):
        rows = self.fixture()
        structural = compare.fit_conventional_sparse(rows, ("pair", "triple", "lag"))
        self.assertEqual(len(structural), 3)
        self.assertTrue(all(kind in ("pair","triple","lag") for kind, _, _ in structural))
        for x in itertools.product((0, 1), repeat=6):
            self.assertIn(compare.choose_structural(structural, x, source.ZERO), (0,1,2))

    def test_policy_source_module_is_not_imported_by_candidate_path(self):
        tree = ast.parse(Path(compare.__file__).read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "policy_run")
        imports = [n for n in ast.walk(fn) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertTrue(all("mass_pad02" not in ast.unparse(i) for i in imports))
        self.assertIn("LEARNER_IMPORTED_PRIVATE_SOURCE", Path(compare.__file__).read_text())

    def test_hidden_source_is_separate_from_candidate_implementation(self):
        tree = ast.parse(Path(source.__file__).read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.ImportFrom, ast.Import)):
                self.assertNotIn("mass_pad01", ast.unparse(node))
                self.assertNotIn("compare", ast.unparse(node))
        with self.assertRaises(ValueError):
            source.seed_for("NOT_A_FAMILY", 0)

    def test_fit_reward_requires_chosen_legal_action(self):
        # Pure non-role fixture seed. Not frozen experiment or protected seed.
        fixture_source = source.HiddenSource("L", -12345678)
        x = (0,1,0,1,0,1)
        with self.assertRaises(ValueError):
            fixture_source.step(x, 3)
        self.assertEqual(fixture_source.steps, 0)
        r = fixture_source.step(x, 0)
        self.assertIn(r, (0,1))
        self.assertEqual(fixture_source.previous, x)
        self.assertEqual(fixture_source.steps, 1)


if __name__ == "__main__":
    unittest.main()
