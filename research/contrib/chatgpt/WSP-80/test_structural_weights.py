"""Developer unit fixtures ONLY: not physically charged scientific results."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'wsp80_structural', Path(__file__).with_name('structural_weights.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class StructuralWeightUnitTests(unittest.TestCase):
    def test_quartic_cannot_fit_degree3_on_complete_developer_truth_table(self):
        rows = {}
        for s in m.STATES:
            y = list(s)
            y[5] ^= s[0] & s[1] & s[2] & s[3]
            rows[s] = tuple(y)
        self.assertEqual(m._survivors(rows, m.LOW)[5], ())
        self.assertTrue(m._survivors(rows, m.HIGH)[5])

        # Synthetic fixture injection, NOT accepted as physically charged learning.
        model = m.PaidStructuralWeightEditor()
        model._rows[0] = rows
        model.charges = 144
        diag = model.compile()
        self.assertIn((0, 5), diag['paid_incompatible_action_outputs'])
        self.assertEqual(diag['expanded_action_channels'], 1)
        self.assertEqual(diag['learned_numerical_relu_features'], 267)
        frozen = m.PaidStructuralWeightEditor.restore(model.snapshot())
        for s, truth in rows.items():
            self.assertEqual(frozen.predict(s, 0), truth)
            self.assertEqual(frozen.predict(s, 0, force=True), truth)
        self.assertIsNone(frozen._rows)
        self.assertTrue(diag['numeric_parameters'] > 0)

    def test_cubic_consistent_control_has_no_false_expansion(self):
        rows = {}
        for s in m.STATES:
            y = list(s)
            y[5] ^= s[0] & s[1] & s[2]
            rows[s] = tuple(y)
        model = m.PaidStructuralWeightEditor()
        model._rows[0] = rows
        model.charges = 144
        diag = model.compile()
        self.assertEqual(diag['paid_incompatible_action_outputs'], ())
        self.assertEqual(diag['expanded_action_channels'], 0)
        frozen = m.PaidStructuralWeightEditor.restore(model.snapshot())
        for s, truth in rows.items():
            self.assertEqual(frozen.predict(s, 0), truth)

    def test_paid_continuity_budget_and_snapshot_tamper(self):
        model = m.PaidStructuralWeightEditor()
        with self.assertRaises(ValueError):
            model.charge((1,) * 6, 0, (1,) * 6)
        for _ in range(144):
            model.charge(model.current, 0, model.current)
        diag = model.compile()
        self.assertEqual(diag['paid_incompatible_action_outputs'], ())
        blob = model.snapshot()
        with self.assertRaises(ValueError):
            m.PaidStructuralWeightEditor.restore(blob.replace('wsp80', 'spoof'))
        model.charge(model.current, 0, model.current)
        with self.assertRaises(ValueError):
            model.snapshot()
        with self.assertRaises(ValueError):
            model.compile()
        for _ in range(239):
            model.charge(model.current, 0, model.current)
        model.compile()
        with self.assertRaises(ValueError):
            model.charge(model.current, 0, model.current)
        self.assertEqual(m.PaidStructuralWeightEditor.restore(model.snapshot()).charges, 384)


if __name__ == '__main__':
    unittest.main()
