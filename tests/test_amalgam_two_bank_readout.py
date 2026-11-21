"""G33 source-free interface and causal-ordering negative tests."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location("g33_bank", HERE / "two_bank_readout.py")
G33 = module_from_spec(SPEC)
SPEC.loader.exec_module(G33)

VIEWS = ((0, 0), (0, 1))
PREFIX = (("old", VIEWS, 0, 1, 0, 1),)
SUFFIX = (("new1", VIEWS, 0, 0, 0, 0),
          ("new2", VIEWS, 1, 1, 0, 1),
          ("new3", VIEWS, 0, 0, 1, 0))


class TwoBankTests(unittest.TestCase):
    def setUp(self):
        self.heads = (ActionLatentSpecialist("transition"),
                      ActionLatentSpecialist("reward"),
                      TemporalLatentSpecialist("transition"),
                      TemporalLatentSpecialist("reward"))

    def test_anchor_preserved_and_adaptive_changes(self):
        before = G33._bank_bytes(self.heads)
        r = G33._replay(self.heads, PREFIX, SUFFIX)
        self.assertEqual(G33._bank_bytes(self.heads), before)
        self.assertEqual(r["initial_head_sha256"], r["anchor_head_sha256"])
        self.assertNotEqual(r["anchor_head_sha256"], r["adaptive_head_sha256"])
        self.assertEqual(r["forecast_count"], 24)
        self.assertEqual(r["adaptive_head_updates"], 12)
        self.assertEqual(r["source_actions"], 0)
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["official_checkpoint_restore_supported"])

    def test_deterministic_recompute_not_owner_cold_claim(self):
        first = G33._replay(self.heads, PREFIX, SUFFIX)
        second = G33._replay(tuple(h.clone() for h in self.heads), PREFIX, SUFFIX)
        self.assertEqual(first, second)
        self.assertEqual(first["trace"][0]["adaptive_weight_before"], .5)
        for row in first["trace"]:
            w = row["adaptive_weight_before"]
            self.assertEqual(row["routed"], G33._mix(row["anchor"], row["adaptive"], w))
            self.assertEqual(row["equal"], G33._mix(row["anchor"], row["adaptive"], .5))

    def test_current_outcomes_cannot_route_current_prediction(self):
        changed = SUFFIX[:1] + (("new2", VIEWS, 1, 0, 0, 0),) + SUFFIX[2:]
        a = G33._replay(self.heads, PREFIX, SUFFIX)["trace"]
        b = G33._replay(self.heads, PREFIX, changed)["trace"]
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1]["adaptive_weight_before"], b[1]["adaptive_weight_before"])
        for name in ("anchor", "adaptive", "equal", "routed"):
            for i in (0, 2):
                self.assertEqual(a[1][name][i], b[1][name][i])
        # Actual observed stage-two state may affect reward forecasts.
        changed_reward = SUFFIX[:1] + (("new2", VIEWS, 1, 1, 0, 0),) + SUFFIX[2:]
        c = G33._replay(self.heads, PREFIX, changed_reward)["trace"]
        for name in ("anchor", "adaptive", "equal", "routed"):
            self.assertEqual(a[1][name], c[1][name])

    def test_renaming_identifiers_cannot_change_predictions(self):
        renamed = tuple(("renamed-"+row[0], *row[1:]) for row in SUFFIX)
        self.assertEqual(G33._replay(self.heads, PREFIX, SUFFIX)["trace"],
                         G33._replay(self.heads, PREFIX, renamed)["trace"])

    def test_router_direction_and_indistinguishability(self):
        p = (.8,) * 4
        q = (.2,) * 4
        self.assertEqual(G33._advance_router(0., p, p, (1,)*4), 0.)
        self.assertGreater(G33._advance_router(0., q, p, (1,)*4), 0.)
        self.assertLess(G33._advance_router(0., p, q, (1,)*4), 0.)
        self.assertEqual(G33._advance_router(8., q, p, (1,)*4), 8.)
        with self.assertRaisesRegex(ValueError, "G33_ROUTER_INPUT"):
            G33._advance_router(0., (float("nan"),)*4, p, (1,)*4)

    def test_fail_closed_duplicate_invalid_order_and_non_native(self):
        with self.assertRaisesRegex(ValueError, "G33_EVENT_IDENTITY"):
            G33._replay(self.heads, PREFIX, PREFIX)
        with self.assertRaisesRegex(ValueError, "G33_HEAD_IDENTITY"):
            G33._replay(self.heads[::-1], PREFIX, SUFFIX)
        with self.assertRaisesRegex(ValueError, "G33_EVENT_IDENTITY"):
            G33._replay(self.heads, PREFIX, (("bad", VIEWS, True, 0, 0, 0),))
        with self.assertRaisesRegex(ValueError, "G33_LEDGER_BOUNDS"):
            G33._replay(self.heads, PREFIX, ())
        with self.assertRaisesRegex(ValueError, "G33_NATIVE_REQUIRED"):
            G33.audit_admitted_prefix(None, None, anchor_sha256="", descendant_sha256="")


    def test_switching_is_opt_in_and_preserves_all_original_arms(self):
        import copy
        old = G33._replay(self.heads, PREFIX, SUFFIX)
        new = G33._replay(self.heads, PREFIX, SUFFIX, switching=True)
        self.assertEqual(G33._replay(self.heads, PREFIX, SUFFIX, switching=False), old)
        projected = copy.deepcopy(new)
        self.assertEqual(projected.pop("switching_hazard"), 1 / 32)
        self.assertEqual(projected.pop("additional_router_updates"), len(SUFFIX))
        self.assertEqual(projected.pop("additional_mixture_scalar_predictions"), 4 * len(SUFFIX))
        for row in projected["trace"]:
            self.assertTrue(0 < row.pop("switching_adaptive_weight_before") < 1)
            row.pop("switching")
            row.pop("switching_log_odds_after")
            row["brier"].pop("switching")
        self.assertEqual(projected, old)
        self.assertEqual(new, G33._replay(self.heads, PREFIX, SUFFIX, switching=True))
        with self.assertRaisesRegex(ValueError, "G33_SWITCH_FLAG"):
            G33._replay(self.heads, PREFIX, SUFFIX, switching=1)

    def test_switching_uses_only_prior_evidence(self):
        changed = SUFFIX[:1] + (("new2", VIEWS, 1, 0, 0, 0),) + SUFFIX[2:]
        ref = G33._replay(self.heads, PREFIX, SUFFIX, switching=True)["trace"]
        alt = G33._replay(self.heads, PREFIX, changed, switching=True)["trace"]
        self.assertEqual(ref[0], alt[0])
        self.assertEqual(ref[0]["switching_adaptive_weight_before"], .5)
        self.assertEqual(ref[1]["switching_adaptive_weight_before"],
                         alt[1]["switching_adaptive_weight_before"])
        for i in (0, 2):
            self.assertEqual(ref[1]["switching"][i], alt[1]["switching"][i])
        self.assertEqual(ref[2]["switching_adaptive_weight_before"],
                         G33._switch_prior(ref[1]["switching_log_odds_after"]))
        for row in ref:
            self.assertEqual(row["switching"],
                             G33._mix(row["anchor"], row["adaptive"],
                                      row["switching_adaptive_weight_before"]))

    def test_frozen_router_return_and_stable_cost(self):
        from math import exp, log
        def run(a, b, initial, labels, switching):
            odds = initial
            weights, losses = [], []
            for y in labels:
                p = G33._switch_prior(odds) if switching else 1 / (1 + exp(-odds))
                weights.append(p)
                losses.append((G33._mix((a,)*4, (b,)*4, p)[0] - y)**2)
                z = log(p/(1-p)) if switching else odds
                odds = G33._advance_router(z, (a,)*4, (b,)*4, (y,)*4)
            weights.append(G33._switch_prior(odds) if switching else 1 / (1 + exp(-odds)))
            return weights, losses
        c, lc = run(.6, .4, 8., [1]*32, False)
        s, ls = run(.6, .4, 8., [1]*32, True)
        self.assertEqual(next(i for i, p in enumerate(c) if p <= .5), 20)
        self.assertEqual(next(i for i, p in enumerate(s) if p <= .5), 7)
        self.assertLess(sum(ls), sum(lc))
        _, lc = run(.6, .4, 0., [0]*64+[1]+[0]*31, False)
        s, ls = run(.6, .4, 0., [0]*64+[1]+[0]*31, True)
        self.assertLessEqual((sum(ls[:64])-sum(lc[:64]))/64, .02)
        self.assertGreater(s[65], .5)
        w, losses = run(.5, .5, 0., [0,1]*32, True)
        self.assertEqual(w, [.5]*65)
        self.assertEqual(losses, [.25]*64)
        _, lc = run(.6, .4, 8., [0]*32, False)
        _, ls = run(.6, .4, 8., [0]*32, True)
        self.assertLessEqual((sum(ls)-sum(lc))/32, .02)
        for bad in (True, None, float("nan"), float("inf"), 8.1, -8.1):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "G33_SWITCH_ODDS"):
                    G33._switch_prior(bad)


if __name__ == "__main__":
    unittest.main()
