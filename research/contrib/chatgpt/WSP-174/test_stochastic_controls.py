"""WSP177 source-free scoring tests, no original chemistry simulator invocation."""
from __future__ import annotations

import ast
import math
from pathlib import Path
import unittest

from public_boundary import PublicEvidence
from stochastic_controls import (ConditionalDirichlet, descendant_brier,
                                 descendants, identity_forecast,
                                 uniform_forecast, validate_policy_input)

POSITIONS = ((0, 0), (0, 4), (4, 0), (4, 4), (2, 2))


def scene(colors):
    return tuple((x, y, color) for (x, y), color in zip(POSITIONS, colors))


def observed(action=10, changed=True):
    # Intervene on object2 (color0). Object3 changes 3->4 iff changed.
    current = scene((0, 1, 2, 3, 4))
    target = scene((0, 1, 0, 3, 4))
    next_state = scene((0, 1, 0, 4 if changed else 3, 4))
    reward = sum(x[2] == y[2] for x, y in zip(next_state, target)) / 5
    return PublicEvidence(current=current, goal=target, action=action,
                          next=next_state, reward=reward, done=False)


class StochasticScoringTests(unittest.TestCase):
    def test_subsequent_only_no_force_scoring(self):
        e = observed()
        self.assertEqual(descendants(0), (1, 2, 3, 4))
        self.assertEqual(descendants(10), (3, 4))
        self.assertEqual(descendants(24), ())
        self.assertEqual(identity_forecast(e.policy_input(), e.action).keys(), {3, 4})
        self.assertEqual(uniform_forecast(e.policy_input(), e.action).keys(), {3, 4})
        self.assertNotIn(2, identity_forecast(e.policy_input(), e.action))
        self.assertNotIn("next", e.policy_input())

    def test_exact_identity_uniform_brier(self):
        e = observed()
        self.assertEqual(descendant_brier(e, identity_forecast(e.policy_input(), e.action)), 1.0)
        self.assertAlmostEqual(descendant_brier(e, uniform_forecast(e.policy_input(), e.action)), 0.8)
        e2 = observed(changed=False)
        self.assertEqual(descendant_brier(e2, identity_forecast(e2.policy_input(), e2.action)), 0.0)

    def test_zero_downstream_does_not_count_as_perfect(self):
        e = PublicEvidence(current=scene((0, 1, 2, 3, 0)),
                           goal=scene((0, 1, 2, 3, 0)),
                           action=24, next=scene((0, 1, 2, 3, 4)),
                           reward=0.8, done=False)
        self.assertIsNone(descendant_brier(e, {}))
        self.assertEqual(identity_forecast(e.policy_input(), 24), {})
        with self.assertRaisesRegex(ValueError, "FORECAST_KEYS"):
            descendant_brier(e, {4: (1., 0., 0., 0., 0.)})

    def test_fitted_control_has_no_future_inputs(self):
        e = observed()
        c = ConditionalDirichlet()
        with self.assertRaisesRegex(ValueError, "NOT_FROZEN"):
            c.forecast(e.policy_input(), e.action)
        c.fit_observed(e)
        self.assertEqual(c.summary()["fit_records"], 1)
        self.assertEqual(c.summary()["fit_descendants"], 2)
        c.freeze()
        prior = c.forecast(e.policy_input(), e.action)
        self.assertEqual(prior[3], (1/6, 1/6, 1/6, 1/6, 2/6))
        self.assertEqual(prior[4], (1/6, 1/6, 1/6, 1/6, 2/6))
        self.assertLess(descendant_brier(e, prior), 0.8)
        with self.assertRaisesRegex(ValueError, "FIT_FROZEN"):
            c.fit_observed(e)
        self.assertEqual(c.summary()["fit_records"], 1)

    def test_fit_only_matches_exact_conditional_cells(self):
        e = observed()
        c = ConditionalDirichlet()
        c.fit_observed(e)
        c.fit_observed(observed(changed=False))
        c.freeze()
        prior = c.forecast(e.policy_input(), e.action)
        self.assertEqual(prior[3], (1/7, 1/7, 1/7, 2/7, 2/7))
        self.assertEqual(prior[4], (1/7, 1/7, 1/7, 1/7, 3/7))
        other = c.forecast(e.policy_input(), 5)
        self.assertEqual(other[2], (0.2,) * 5)
        self.assertEqual(c.summary()["conditional_cells"], 2)
        self.assertEqual(c.summary()["fit_descendants"], 4)

    def test_reject_forecast_leak_or_malformed_probs(self):
        e = observed()
        for p in ({}, {3: (0.2,) * 5, 4: (0.2,) * 5, 2: (0.2,) * 5},
                  {3: (0.2,) * 5}):
            with self.assertRaisesRegex(ValueError, "FORECAST_KEYS"):
                descendant_brier(e, p)
        for bad in ((1.0, 0., 0., 0.), (0.2,)*4+(float("nan"),),
                    (0.1,) * 5, (True, 0., 0., 0., 0.),
                    (float("inf"), 0., 0., 0., 0.), (1.1, -0.1, 0., 0., 0.)):
            with self.subTest(p=bad), self.assertRaises(ValueError):
                descendant_brier(e, {3: bad, 4: (0., 0., 0., 0., 1.)})

    def test_public_input_is_exact_and_cannot_use_future(self):
        e = observed()
        for bad in ({**e.policy_input(), "next": e.next},
                    {**e.policy_input(), "graph": [0]},
                    {"current": e.policy_input()["current"]}):
            with self.assertRaisesRegex(ValueError, "PUBLIC_POLICY_FIELDS"):
                validate_policy_input(bad, e.action)
        for a in (True, 25, -1, "10"):
            with self.assertRaisesRegex(ValueError, "ACTION"):
                validate_policy_input(e.policy_input(), a)
        moved = {"current": e.policy_input()["current"],
                 "goal": [list(x) for x in e.goal]}
        moved["goal"][0][0] = 1
        with self.assertRaisesRegex(ValueError, "GOAL_POSITIONS"):
            validate_policy_input(moved, e.action)

    def test_only_stdlib_and_public_boundary(self):
        content = Path(__file__).with_name("stochastic_controls.py").read_text("utf-8")
        tree = ast.parse(content)
        imports = {name.name.partition(".")[0] for n in ast.walk(tree)
                   if isinstance(n, ast.Import) for name in n.names}
        imports |= {n.module.partition(".")[0] for n in ast.walk(tree)
                    if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(imports & {"gym", "torch", "numpy", "causal_gym"})
        for banned in ("source_first_use_authority", "actor.execute",
                       "source_env.step", "source_env.reset", "protected_seed"):
            self.assertNotIn(banned, content)


if __name__ == "__main__":
    unittest.main()
