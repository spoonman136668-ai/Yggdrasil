"""Development-only symbolic fixtures; not registered WSP80 science."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).parent))
from independent_symbolic import IndependentConditionalSymbolic, _STATES


class IndependentControlTests(unittest.TestCase):
    def rows(self, kind):
        rows = []
        for x in sorted(_STATES):
            y = list(x)
            if kind == 'quartic':
                delta = x[0] & x[1] & x[2] & x[3]
            elif kind == 'complemented':
                delta = x[0] & x[1] & x[2] & (1 ^ x[3])
            else:
                delta = x[0] & x[1] & x[2]
            y[5] ^= delta
            rows.append((x, 0, tuple(y)))
        return rows

    def test_quartic_and_complemented_incompatibility(self):
        for kind in ('quartic', 'complemented'):
            rows = self.rows(kind)
            model = IndependentConditionalSymbolic(rows)
            self.assertIn((0, 5), model.incompatibilities)
            for s, a, expected in rows:
                self.assertEqual(model.predict(s, a), expected)

    def test_degree3_no_false_novelty(self):
        model = IndependentConditionalSymbolic(self.rows('degree3'))
        self.assertEqual(model.incompatibilities, [])

    def test_unobserved_action_abstains(self):
        model = IndependentConditionalSymbolic(self.rows('degree3'))
        self.assertIsNone(model.predict((0,) * 6, 1))

    def test_conflicting_public_observations_rejected(self):
        row = ((0,) * 6, 0, (0,) * 6)
        with self.assertRaises(ValueError):
            IndependentConditionalSymbolic([row, (row[0], 0, (1,) * 6)])

    def test_exact_replay_deterministic(self):
        rows = self.rows('quartic')
        a = IndependentConditionalSymbolic(rows)
        b = IndependentConditionalSymbolic(rows)
        self.assertEqual(a.incompatibilities, b.incompatibilities)
        for s in sorted(_STATES):
            for action in range(6):
                self.assertEqual(a.predict(s, action), b.predict(s, action))

    def test_paid_ledger_charge_and_continuity(self):
        zero = (0,) * 6
        event = lambda before, cost: SimpleNamespace(
            before=before, action=0, after=zero, action_cost=cost)
        ok = [event(zero, 1) for _ in range(144)]
        self.assertEqual(IndependentConditionalSymbolic.from_paid_ledger(ok).paid_actions, 144)
        with self.assertRaises(ValueError):
            IndependentConditionalSymbolic.from_paid_ledger(ok[:-1])
        wrong_cost = ok.copy()
        wrong_cost[4] = event(zero, 0)
        with self.assertRaises(ValueError):
            IndependentConditionalSymbolic.from_paid_ledger(wrong_cost)
        wrong_chain = ok.copy()
        wrong_chain[5] = event((1,) * 6, 1)
        with self.assertRaises(ValueError):
            IndependentConditionalSymbolic.from_paid_ledger(wrong_chain)

    def test_source_and_neural_imports_absent(self):
        source_text = Path(__file__).with_name('independent_symbolic.py').read_text()
        for forbidden in ('import source', 'from source', '_step_oracle',
                          'import structural_weights', 'from structural_weights'):
            self.assertNotIn(forbidden, source_text)


if __name__ == '__main__':
    unittest.main()
