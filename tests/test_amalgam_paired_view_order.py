"""Source-free, pre-frozen view-role alias audit of existing JEPA specialists.

Reuses only previously disclosed 16 synthetic Gate20 witness rows. This
never accesses protected source, host-owner checkpoint, or native trainer.
"""
from collections import defaultdict
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

PATH = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/CAUSAL-AMALGAM" /
        "projection_disjoint_factor_audit.py")
SPEC = spec_from_file_location("ordered_view_gate21_fixture", PATH)
FIXTURE = module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)


def views(n):
    return ((0, n), (0, 1 - n))


def fit_heads(rows):
    action_t = ActionLatentSpecialist("transition")
    action_y = ActionLatentSpecialist("reward")
    temporal_t = TemporalLatentSpecialist("transition")
    temporal_y = TemporalLatentSpecialist("reward")
    prior = []
    for identifier, current_views, row in rows:
        x1, s2, x2, y = (row["x1"], row["s2"], row["x2"], row["y"])
        # A witnessed label is given only to the active source-free
        # development heads after this row is disclosed.
        action_t.observe(current_views, (x1,), s2)
        action_y.observe(current_views, (x1, s2, x2), y)
        temporal_t.observe(current_views, (x1,), tuple(prior), s2)
        temporal_y.observe(current_views, (x1, s2, x2), tuple(prior), y)
        prior.append((identifier, current_views, x1, s2, x2, y))
    return action_t, action_y, temporal_t, temporal_y, tuple(prior)


def public_frequency(rows):
    """Independent, equal-data, role-sensitive Laplace-1 conventional fit."""
    cells = defaultdict(lambda: [0, 0])
    for _, current_views, row in rows:
        cells[(current_views[0][1], row["x2"])][row["y"]] += 1
    return {
        (n, a): Fraction(cells[(n, a)][1] + 1,
                         sum(cells[(n, a)]) + 2)
        for n in (0, 1) for a in (0, 1)
    }


class PairedViewOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = tuple(FIXTURE.witness_records(disjoint=True))
        cls.same_law_rows = tuple(FIXTURE.witness_records(disjoint=False))
        cls.heads = fit_heads(cls.rows)
        cls.prior = cls.heads[-1]

    def test_disclosed_rows_only_and_public_ordered_role(self):
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(len({identifier for identifier, _, _ in self.rows}), 16)
        for _, current_views, row in self.rows:
            self.assertEqual(current_views, views(current_views[0][1]))
            self.assertEqual(row["y"],
                             int(row["x2"] == current_views[0][1]))
            self.assertEqual(set(row), {"s1", "x1", "s2", "x2", "y"})

    def test_both_action_heads_invariant_pre_and_post_training(self):
        for kind, extras in (
            ("transition", ((0,), (1,))),
            ("reward", ((0, 0, 0), (0, 0, 1),
                        (1, 0, 0), (1, 0, 1))),
        ):
            for head in (ActionLatentSpecialist(kind),
                         self.heads[0 if kind == "transition" else 1]):
                for actions in extras:
                    with self.subTest(kind=kind, extras=actions,
                                      steps=head.steps):
                        self.assertEqual(
                            head.probability(views(0), *actions),
                            head.probability(views(1), *actions))

    def test_both_temporal_heads_invariant_for_same_public_history(self):
        for kind, extras in (
            ("transition", ((0,), (1,))),
            ("reward", ((0, 0, 0), (0, 0, 1),
                        (1, 0, 0), (1, 0, 1))),
        ):
            for head in (TemporalLatentSpecialist(kind),
                         self.heads[2 if kind == "transition" else 3]):
                for prior in ((), self.prior):
                    for actions in extras:
                        with self.subTest(kind=kind, extras=actions,
                                          prior_len=len(prior),
                                          steps=head.steps):
                            self.assertEqual(
                                head.probability(views(0), actions, prior),
                                head.probability(views(1), actions, prior))

    def test_swapping_observed_view_order_cannot_change_single_update(self):
        for kind, actions, label in (
            ("transition", (1,), 0),
            ("reward", (1, 0, 1), 1),
        ):
            a, b = ActionLatentSpecialist(kind), ActionLatentSpecialist(kind)
            a.observe(views(0), actions, label)
            b.observe(views(1), actions, label)
            self.assertEqual(a.as_data(), b.as_data())
            ta, tb = TemporalLatentSpecialist(kind), TemporalLatentSpecialist(kind)
            ta.observe(views(0), actions, self.prior, label)
            tb.observe(views(1), actions, self.prior, label)
            self.assertEqual(ta.data(), tb.data())

    def test_mathematical_brier_floor_on_role_dependent_pairs(self):
        for head in (self.heads[1],):
            for x1 in (0, 1):
                for x2 in (0, 1):
                    args = (x1, 0, x2)
                    p0 = head.probability(views(0), *args)
                    p1 = head.probability(views(1), *args)
                    self.assertEqual(p0, p1)
                    loss = ((p0 - int(x2 == 0)) ** 2 +
                            (p1 - int(x2 == 1)) ** 2) / 2
                    self.assertGreaterEqual(loss + 1e-12, .25)
                    self.assertAlmostEqual(
                        loss, .25 + (p0 - .5) ** 2, places=12)

    def test_equal_information_order_aware_conventional_control(self):
        probs = public_frequency(self.rows)
        actions = [int(probs[(n, 1)] > probs[(n, 0)])
                   for n in (0, 1)]
        self.assertEqual(actions, [0, 1])
        self.assertEqual(
            sum(int(actions[n] == n) for n in (0, 1)) / 2, 1.0)
        mean_brier = sum(
            (probs[(current_views[0][1], row["x2"])] - row["y"]) ** 2
            for _, current_views, row in self.rows
        ) / len(self.rows)
        self.assertEqual(mean_brier, Fraction(1, 36))

    def test_nuisance_independent_control_has_no_order_requirement(self):
        probs = public_frequency(self.same_law_rows)
        actions = [int(probs[(n, 1)] > probs[(n, 0)])
                   for n in (0, 1)]
        self.assertEqual(actions, [0, 0])
        self.assertEqual(
            sum(int(actions[n] == 0) for n in (0, 1)) / 2, 1.0)

    def test_fitted_development_heads_do_not_touch_owner_state(self):
        for head in self.heads[:4]:
            self.assertEqual(head.steps, 16 * 3)
        self.assertEqual(len(self.prior), 16)
        # These newly initialized ephemeral fixture heads are NOT restored
        # from, or connected to, any owner-controlled trained state.
        self.assertTrue(all(identifier in
                            {record[0] for record in self.rows}
                            for identifier, *_ in self.prior))


if __name__ == "__main__":
    unittest.main()
