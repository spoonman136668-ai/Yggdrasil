"""FKP-17 public fixture source-safe tests. No original held source is opened."""
import ast
import importlib
import json
from pathlib import Path
import unittest

import source_fixture as src


class PublicFixtureTests(unittest.TestCase):
    def test_frozen_cohorts_and_denied_held_worlds(self):
        self.assertEqual((len(src.FOUNDATION), len(src.TRAIN),
                          len(src.VALIDATION)), (128, 64, 16))
        for seed in (978500, 978531, 978600, 978663, 976500,
                     975100, -1, 978164):
            with self.subTest(seed=seed):
                with self.assertRaises(PermissionError):
                    src.cohort(seed)
                with self.assertRaises(PermissionError):
                    src.collect_public(seed, (0,))
                with self.assertRaises(PermissionError):
                    src.public_actions(seed, 1)
        for invalid in (True, False, 978100.0, "978100"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    src.cohort(invalid)
        with self.assertRaises(TypeError):
            src.collect_public(978100, (0,), allow_dev=True)

    def test_public_source_is_reproducible(self):
        actions = src.public_actions(src.TRAIN[0], 40)
        first = src.collect_public(src.TRAIN[0], actions)
        second = src.collect_public(src.TRAIN[0], actions)
        self.assertEqual(first, second)
        self.assertEqual(src.public_digest(first), src.public_digest(second))
        self.assertEqual(len(first), 40)
        self.assertEqual(first[0].history, ())
        self.assertEqual(len(first[-1].history), 16)
        self.assertEqual(first[-1].history[-1].after, first[-2].after)

    def test_source_visible_only_no_future_or_law_fields(self):
        actions = (0, 1, 2, 3, 4, 5, 6, 7) * 3
        rows = src.collect_public(src.VALIDATION[1], actions)
        self.assertEqual(src.PublicStep._fields,
                         ("before", "action", "after", "reward",
                          "done", "history"))
        self.assertEqual(src.PublicTransition._fields,
                         ("before", "action", "reward", "after",
                          "done"))
        for n, row in enumerate(rows):
            with self.subTest(index=n):
                self.assertIs(type(row), src.PublicStep)
                self.assertEqual(row.action, actions[n])
                self.assertEqual(len(row.before), 8)
                self.assertEqual(len(row.after), 8)
                self.assertTrue(all(type(v) is int and 0 <= v <= 15
                                    for v in row.before + row.after))
                self.assertTrue(-1.0 <= row.reward <= 1.0)
                self.assertIs(type(row.done), bool)
                self.assertEqual(len(row.history), min(n, 16))
                self.assertFalse(any(key in row._fields for key in
                                     ("law", "oracle", "private_info",
                                      "future_returns", "source_mode")))
                if n:
                    self.assertEqual(row.before, rows[n - 1].after)
                    self.assertEqual(row.history[-1].after, row.before)
                for j, earlier in enumerate(row.history):
                    self.assertLess(j, 16)
                    self.assertIs(type(earlier), src.PublicTransition)

    def test_actual_action_changes_observable_consequences(self):
        seed = src.TRAIN[2]
        consequences = [src.collect_public(seed, (arm,))[0]
                        for arm in range(8)]
        self.assertGreater(len({r.after for r in consequences}), 1)
        self.assertEqual(len({r.before for r in consequences}), 1)
        self.assertTrue(all(r.action == n
                            for n, r in enumerate(consequences)))
        # This is source feasibility only, NOT scored candidate action value.

    def test_action_type_range_and_length_rejected(self):
        for bad in ([-1], [8], [True], [0.0], (0.0,), (True,), (-1,), (8,)):
            with self.subTest(actions=bad):
                with self.assertRaises(ValueError):
                    src.collect_public(src.TRAIN[0], bad)
        with self.assertRaises(ValueError):
            src.collect_public(src.TRAIN[0], (0,) * 257)
        for bad_length in (-1, 257, True, 1.0):
            with self.assertRaises(ValueError):
                src.public_actions(src.TRAIN[0], bad_length)

    def test_public_fact_digest_rejects_private_or_tampered_type(self):
        rows = src.collect_public(src.TRAIN[3], (1, 2, 3))
        with self.assertRaises(ValueError):
            src.public_digest(({"law": "hidden"},))
        with self.assertRaises(ValueError):
            src.public_digest((tuple(rows[0]),))
        # A public outcome is hashed, not a privileged latent law.
        changed = rows[0]._replace(reward=rows[0].reward + .125)
        self.assertNotEqual(src.public_digest((rows[0],)),
                            src.public_digest((changed,)))

    def test_foundation_full_32768_records(self):
        all_rows = list(src.foundation_facts())
        self.assertEqual(len(all_rows), 32768)
        self.assertEqual(all_rows[0][:2], (979100, 0))
        self.assertEqual(all_rows[-1][:2], (979227, 255))
        self.assertEqual(len({s for s, _, _ in all_rows}), 128)
        self.assertEqual(len({(s, idx) for s, idx, _ in all_rows}), 32768)
        self.assertTrue(all(type(r) is src.PublicStep for _, _, r in all_rows))

    def test_public_session_only_exposes_actual_chosen_action(self):
        seed = src.TRAIN[7]
        tape = src.public_actions(seed, 24)
        session = src.PublicSession(seed)
        rows = []
        for step, action in enumerate(tape):
            before = session.current_public
            row = session.apply_public(action)
            self.assertEqual(row.before, before)
            self.assertEqual(row.action, action)
            self.assertEqual(row.history, tuple(
                src.PublicTransition(x.before, x.action, x.reward, x.after, x.done)
                for x in rows[-16:]))
            rows.append(row)
            self.assertEqual(session.current_public, row.after)
            self.assertEqual(session.observed_steps, step + 1)
        # Match the original source-safe physical transition stream exactly.
        self.assertEqual(tuple(rows), src.collect_public(seed, tape))
        for _ in range(16):
            session.apply_public(0)
        with self.assertRaises(ValueError):
            session.apply_public(0)

    def test_session_denies_unseen_and_forbidden_source(self):
        for seed in (978500, 978531, 978600, 978663, 976500,
                     src.FOUNDATION[0], -1):
            with self.assertRaises(PermissionError):
                src.PublicSession(seed)
        s = src.PublicSession(src.VALIDATION[2])
        for invalid in (-1, 8, True, 0.0, "0"):
            prior = s.current_public
            with self.assertRaises(ValueError):
                s.apply_public(invalid)
            self.assertEqual(s.current_public, prior)
            self.assertEqual(s.observed_steps, 0)

    def test_no_nonfixture_module_imports_private_evaluator(self):
        root = Path(__file__).parent
        for path in root.glob("*.py"):
            # Fixtures may import their source; production learner modules
            # must never import a simulator or its private law state.
            # The sole source-safe training entrypoint may import its public
            # evaluator to assemble already-committed observations. Learned
            # policies must NOT import source_fixture or an evaluator.
            if path.name in ("source_fixture.py", "qualify_public_recurrent.py", "run_public_onpolicy.py", "run_train_matrix.py") or path.name.startswith("test_"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn("source_fixture", alias.name,
                                         "learner may not import fixture evaluator")
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn("source_fixture", node.module or "",
                                     "learner may not import fixture evaluator")
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "import_module" and node.args:
                        first = node.args[0]
                        if isinstance(first, ast.Constant):
                            self.assertNotIn("source_fixture", str(first.value),
                                             "no dynamic private evaluator import")


if __name__ == "__main__":
    unittest.main()
