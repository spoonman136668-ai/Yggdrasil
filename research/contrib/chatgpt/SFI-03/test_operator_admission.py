"""SFI-03 frozen PUBLIC source / candidate custody and negative controls."""
import ast
import importlib.util
from pathlib import Path
import unittest
from collections import namedtuple

import operator_induction as model
import public_source as source
import run_public_dev as harness


class AdmissionTests(unittest.TestCase):
    def test_only_thirtytwo_new_public_world_seeds(self):
        self.assertEqual(source.WORLD_SEEDS, tuple(range(880300, 880332)))
        for invalid in (True, -1, 0, 32, 978500, 978531, 978600, 978663):
            with self.assertRaises(PermissionError):
                source.PublicWorld(invalid)
        self.assertEqual(len(source.exploration(880300)), 24)

    def test_source_is_deterministic_and_public_schema_exact(self):
        a, b = source.PublicWorld(880300), source.PublicWorld(880300)
        tape = source.exploration(880300)
        for act in tape:
            x, y = a.step(act), b.step(act)
            self.assertEqual(x, y)
            self.assertEqual(x._fields, model.STEP_FIELDS)
            self.assertFalse(hasattr(x, "_family"))
            self.assertFalse(hasattr(x, "_shift"))
            self.assertFalse(hasattr(x, "oracle_future"))
            self.assertLessEqual(len(x.history), 16)
            self.assertEqual(len(x.before), 8)
            self.assertEqual(len(x.after), 8)

    def test_exact_two_step_credit_and_public_continuity(self):
        world = source.PublicWorld(880300)
        tape = source.exploration(880300)
        for index, act in enumerate(tape):
            row = world.step(act)
            credit, receipt = model._public(row)
            self.assertTrue(receipt)
            if index < 3:
                self.assertEqual(row.reward, 0.)
                self.assertIsNone(credit)
            elif credit:
                previous, older, c, eligible, positive = credit
                self.assertEqual(positive, eligible == source.target(
                    world._family, world._shift, previous, older, c))
            if row.history:
                self.assertEqual(row.history[-1].after, row.before)
            self.assertEqual(world.state, row.after)

    def test_generic_bank_covers_all_four_source_families(self):
        for family in range(4):
            for shift in range(8):
                for p, q, ctx in ((0,0,0),(1,3,1),(4,7,0),(6,2,1)):
                    expected = source.target(family, shift, p, q, ctx)
                    self.assertIn(expected, model._predictions(p, q, ctx))

    def test_two_independent_generic_interpreters_agree(self):
        for p, q, ctx in ((0,0,0),(1,3,1),(7,5,0),(3,4,1)):
            lookup = model._predictions(p, q, ctx)
            for i in range(model.PROGRAMS):
                self.assertEqual(lookup[i], model.IndependentExactBoolean._evaluate(i, p, q, ctx))

    def test_same_public_evidence_same_hypotheses_and_choices(self):
        one, two = model.DirectMicrofeedbackExpansion(), model.IndependentExactBoolean()
        world = source.PublicWorld(880301)
        for act in source.exploration(880301):
            row = world.step(act)
            one.observe_public(row)
            two.observe_public(row)
            self.assertEqual(one.hypotheses, two.hypotheses)
            self.assertEqual(one.choose_public(world.state, world.public_history()),
                             two.choose_public(world.state, world.public_history()))
        self.assertEqual(one.rows, 24)
        self.assertEqual(one.learned_bytes, 32768)
        self.assertEqual(two.learned_bytes, 65536)

    def test_private_fields_and_budget_reject_without_mutation(self):
        one = model.DirectMicrofeedbackExpansion()
        src = source.PublicWorld(880300)
        row = src.step(0)
        Extra = namedtuple("Extra", model.STEP_FIELDS + ("oracle",))
        before = one.receipt()
        for bad in (Extra(*row, [1.]*8), row._replace(action=True),
                    row._replace(after=(0,)*7),
                    row._replace(reward=float("nan"))):
            with self.assertRaises(ValueError):
                one.observe_public(bad)
            self.assertEqual(before, one.receipt())
        for _ in range(model.MAX_WORLD_ROWS):
            one.observe_public(row)
        frozen = one.receipt()
        with self.assertRaises(ValueError):
            one.observe_public(row)
        self.assertEqual(frozen, one.receipt())

    def test_no_source_generator_import_or_source_private_access_in_learner(self):
        path = Path(model.__file__)
        tree = ast.parse(path.read_text("utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(x.name for x in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add(node.module)
        self.assertNotIn("public_source", names)
        self.assertNotIn("source_audit", names)
        self.assertFalse(hasattr(model.DirectMicrofeedbackExpansion(), "_family"))
        self.assertFalse(hasattr(model.DirectMicrofeedbackExpansion(), "_shift"))


if __name__ == "__main__":
    unittest.main()
