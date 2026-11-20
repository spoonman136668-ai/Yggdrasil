"""Gate 23: preregistered source-free cross-view XOR/OR capacity controls.

Only isolated, newly constructed existing JEPA specialist instances are fitted.
No real source, owner checkpoint, canonical planner, or training controller runs.
The contract was committed independently in cross_view_interaction_freeze.md.
"""
from collections import defaultdict
from fractions import Fraction
from math import isclose, log
import unittest

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import (
    TemporalLatentSpecialist, _features as temporal_features,
)

EXTRAS = (0, 0, 0)
PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))


def tape(law):
    if law not in ("xor", "or"):
        raise ValueError("GATE23_LAW")
    result = []
    for rep in range(4):
        for a, b in PAIRS:
            current_views = ((0, a), (0, b))
            y = (a ^ b) if law == "xor" else (a | b)
            result.append((f"source-free-gate23/{law}/{rep}/{a}/{b}",
                           current_views, y))
    return tuple(result)


def fit(law):
    action = ActionLatentSpecialist("reward")
    temporal = TemporalLatentSpecialist("reward")
    prior = []
    for identifier, views, y in tape(law):
        action.observe(views, EXTRAS, y)
        # Only previously witnessed synthetic public events enter history.
        temporal.observe(views, EXTRAS, tuple(prior), y)
        prior.append((identifier, views, 0, 0, 0, y))
    return action, temporal, tuple(prior)


def predictions(head, history=()):
    result = {}
    for a, b in PAIRS:
        views = ((0, a), (0, b))
        if isinstance(head, ActionLatentSpecialist):
            result[(a, b)] = head.probability(views, *EXTRAS)
        else:
            result[(a, b)] = head.probability(views, EXTRAS, history)
    return result


def pair_public_frequency(rows):
    cells = defaultdict(lambda: [0, 0])
    for _, views, y in rows:
        cells[(views[0][1], views[1][1])][y] += 1
    return {(a, b): Fraction(cells[(a, b)][1] + 1,
                             sum(cells[(a, b)]) + 2)
            for a, b in PAIRS}


def raw_per_view_logits(head, history=()):
    if isinstance(head, ActionLatentSpecialist):
        xs = head._input(((0, 0), (0, 1)), EXTRAS)
    else:
        xs = temporal_features(((0, 0), (0, 1)), EXTRAS,
                               history, "reward")
    return tuple(
        head._forward(x)[1][0] - head._forward(x)[1][1] for x in xs
    )


class Gate23CrossViewInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xor = fit("xor")
        cls.or_heads = fit("or")

    def test_precommitted_balanced_16_witnesses_and_public_only_tape(self):
        for law, expected in (("xor", (0, 1, 1, 0)),
                              ("or", (0, 1, 1, 1))):
            rows = tape(law)
            self.assertEqual(len(rows), 16)
            self.assertEqual(len({identifier for identifier, _, _ in rows}),
                             16)
            for idx, pair in enumerate(PAIRS):
                matching = [(v, y) for _, v, y in rows
                            if (v[0][1], v[1][1]) == pair]
                self.assertEqual(len(matching), 4)
                self.assertEqual({y for _, y in matching}, {expected[idx]})
                for v, _ in matching:
                    self.assertEqual(v, ((0, pair[0]), (0, pair[1])))
        with self.assertRaisesRegex(ValueError, "GATE23_LAW"):
            tape("unfrozen")

    def test_exact_pair_frequency_control_same_observations(self):
        for law in ("xor", "or"):
            rows = tape(law)
            probs = pair_public_frequency(rows)
            brier = sum(
                (probs[(views[0][1], views[1][1])] - y)**2
                for _, views, y in rows
            ) / len(rows)
            accuracy = sum(
                (probs[(views[0][1], views[1][1])] > Fraction(1, 2)) == y
                for _, views, y in rows
            ) / len(rows)
            self.assertEqual(brier, Fraction(1, 36))
            self.assertEqual(accuracy, 1.0)
            self.assertEqual(set(probs), set(PAIRS))

    def test_actual_unmodified_action_and_temporal_heads_are_additive(self):
        for law, (action, temporal, full_prior) in (
            ("xor", self.xor), ("or", self.or_heads)
        ):
            for model in (ActionLatentSpecialist("reward"), action,
                          TemporalLatentSpecialist("reward"), temporal):
                histories = ((), full_prior) if isinstance(
                    model, TemporalLatentSpecialist) else ((),)
                for history in histories:
                    with self.subTest(law=law, model=type(model).__name__,
                                      fitted=model.steps > 0,
                                      history=len(history)):
                        probs = predictions(model, history)
                        self.assertEqual(probs[(0, 1)], probs[(1, 0)])
                        self.assertTrue(all(0 < p < 1 for p in probs.values()))
                        logits = {pair: log(p / (1 - p))
                                  for pair, p in probs.items()}
                        self.assertTrue(isclose(
                            2 * logits[(0, 1)],
                            logits[(0, 0)] + logits[(1, 1)],
                            rel_tol=0, abs_tol=1e-9
                        ))
                        first, second = raw_per_view_logits(model, history)
                        # The actual two-view logit is score(first)+score(second).
                        self.assertTrue(isclose(
                            logits[(0, 0)], 2 * first,
                            rel_tol=0, abs_tol=1e-9
                        ))
                        self.assertTrue(isclose(
                            logits[(1, 1)], 2 * second,
                            rel_tol=0, abs_tol=1e-9
                        ))

    def test_xor_prediction_ceiling_for_both_actual_fitted_heads(self):
        action, temporal, prior = self.xor
        for model, history in ((action, ()), (temporal, ()),
                               (temporal, prior)):
            probs = predictions(model, history)
            correct = sum(int(probs[(a, b)] > 0.5) == (a ^ b)
                          for a, b in PAIRS)
            # This is a hard expressivity ceiling, not measured source science.
            self.assertLessEqual(correct, 3)
            self.assertEqual(probs[(0, 1)], probs[(1, 0)])

    def test_or_negative_control_is_mathematically_realizable(self):
        # Shared-view logits -1 and +3: matched/mixed pair logits -2,2,6
        # respectively before the monotone sigmoid. A separate interaction
        # term is NOT structurally required for this symmetric OR law.
        f = {0: -1, 1: 3}
        additive = {(a, b): f[a] + f[b] for a, b in PAIRS}
        self.assertEqual([int(additive[pair] > 0) for pair in PAIRS],
                         [0, 1, 1, 1])
        self.assertEqual(additive[(0, 1)], additive[(1, 0)])
        self.assertEqual(2 * additive[(0, 1)],
                         additive[(0, 0)] + additive[(1, 1)])

    def test_isolated_training_budget_without_owner_state(self):
        for action, temporal, prior in (self.xor, self.or_heads):
            self.assertEqual(action.steps, 48)
            self.assertEqual(temporal.steps, 48)
            self.assertEqual(len(prior), 16)
            for index, (identifier, views, x1, s2, x2, label) in enumerate(prior):
                self.assertTrue(identifier.startswith("source-free-gate23/"))
                self.assertEqual((x1, s2, x2), EXTRAS)
                self.assertIn(label, (0, 1))
                self.assertEqual(len(views), 2)
                self.assertIn(identifier.split("/")[2], ("0", "1", "2", "3"))
        # No original external source or owner's checkpoint was loaded.


if __name__ == "__main__":
    unittest.main()
