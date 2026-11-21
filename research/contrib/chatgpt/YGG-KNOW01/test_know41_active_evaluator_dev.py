"""KNOW41 prospective budget, simulator and controls — injected MOCK only.

Never calls a private FIT/HELD source, never tests using frozen FIT/HELD seeds.
"""
import unittest
from know41_active_evaluator_dev import (
    ARMS, PHASES, GreedyLookup, StatelessPolicy, compute_verdict,
    create_tape, expected_net_regret, fit_selection, hidden_world_uniform,
    run_world, v2,
)
from know41_active_identifiability_dev import expected_milli


def mock_u(seed, t, c):
    # Never import private_source or use a protected/held seed.
    return ((seed * 17 + t * 13 + c * 7) % 997 + .5) / 997.0


class Know41EvaluatorMockOnly(unittest.TestCase):
    def test_v2_replaces_inconsistent_arm_action_budget_before_first_use(self):
        p = v2()
        self.assertEqual(p["replacement_exogenous_source"]
                         ["max_total_new_source_uniforms"], 9216)
        self.assertEqual(p["source_gate"]["private_sampler_default"], "DENY")
        with self.assertRaisesRegex(ValueError, "SOURCE_FIRST_USE_NOT_AUTHORIZED"):
            hidden_world_uniform(41101, 0, 0)
        self.assertEqual(set(ARMS), {"candidate", "bayesian", "bandit", "lookup",
                                     "passive", "random", "no_memory"})

    def test_exact_exogenous_reuse_all_arms_and_cold(self):
        tape = create_tape(990101, mock_u)
        self.assertEqual(len(tape), 256)
        fit = {"candidate_hazard": 1 / 32,
               "bayesian_hazard": 1 / 32, "bayesian_bonus": 1.0}
        treatment = run_world(990101, tape, fit, fork_theta=1)
        sham = run_world(990101, tape, fit, fork_theta=1, sham=True)
        self.assertEqual(treatment["world_unique_exogenous_draws"], 256)
        self.assertEqual(sham["world_unique_exogenous_draws"], 256)
        self.assertTrue(treatment["candidate_a_preserved"])
        self.assertTrue(sham["candidate_a_preserved"])
        self.assertEqual(set(treatment["regret"]), set(PHASES))
        self.assertEqual(set(treatment["action1_counts"]), set(ARMS))
        self.assertEqual(treatment["action1_counts"]["passive"], 0)
        self.assertGreater(treatment["action1_counts"]["random"], 0)
        self.assertGreater(treatment["action1_counts"]["candidate"], 0)
        self.assertTrue(all(0 <= n <= 256 for n in treatment["action1_counts"].values()))
        self.assertTrue(all(n < 4096 for n in treatment["max_checkpoint_bytes"].values()))
        self.assertEqual(treatment["regret"]["A_first"]["passive"],
                         sham["regret"]["A_first"]["passive"])

    def test_fit_selection_uses_same_tape_and_enumerates_strong_controls(self):
        seen = []
        def witnessed(seed, t, c):
            seen.append((seed, t, c))
            return mock_u(seed, t, c)
        f = fit_selection([990201, 990211], witnessed)
        self.assertEqual(len(seen), 2 * 256)
        self.assertEqual(len(set(seen)), len(seen))
        self.assertEqual(f["unique_fit_exogenous_draws"], 512)
        self.assertEqual(len(f["fit_scores"]), 15)
        self.assertEqual(set(f["selected"]),
                         {"candidate_hazard","bayesian_hazard","bayesian_bonus"})
        self.assertTrue(all(x["regret"] >= 0 for x in f["fit_scores"]))

    def test_scorer_never_needs_counterfactual_sample(self):
        self.assertAlmostEqual(expected_net_regret("CHAIN", 0, 0, 0), 0)
        self.assertAlmostEqual(expected_net_regret("CHAIN", 1, 0, 0), .15)
        self.assertEqual(expected_milli("CHAIN", 0, 0, 0), 350)
        self.assertEqual(expected_milli("CHAIN", 1, 1, 0), 550)
        self.assertEqual(expected_milli("FORK", 1, 1, 0), 350)
        with self.assertRaisesRegex(ValueError, "TAPE_TYPE"):
            create_tape(990312, lambda seed,t,c: "bad" if t==128 else mock_u(seed,t,c))


    def test_cold_policy_type_and_prospective_next_action(self):
        # A greedy lookup may not turn into an exploring bandit on cold restore.
        m = GreedyLookup()
        for t in range(64):
            c = t % 8
            a = m.choose(t, c)
            m.observe(t, c, a, int((t + c) % 3 == 0))
        saved = m.checkpoint()
        cold = GreedyLookup.cold(saved)
        self.assertIs(type(cold), GreedyLookup)
        self.assertEqual(type(m), type(cold))
        self.assertEqual(m.choose(64, 0), cold.choose(64, 0))
        self.assertEqual(cold.checkpoint(), m.checkpoint())

    def test_held_receipts_reject_foreign_or_duplicate_mock_worlds(self):
        # Pure injected mock, NOT frozen held source or evaluation.
        fit = {"candidate_hazard": 1 / 32,
               "bayesian_hazard": 1 / 32, "bayesian_bonus": 1.0}
        mock = run_world(990401, create_tape(990401, mock_u), fit)
        self.assertEqual(mock["cold_boundary_checks"], 4 * len(ARMS))
        with self.assertRaisesRegex(ValueError, "HELD_CUSTODY"):
            compute_verdict([mock] * 24)
        # Additional invalid fake metadata cannot be accepted as a completed trial.
        mock["cold_boundary_checks"] = 0
        with self.assertRaisesRegex(ValueError, "HELD_CUSTODY"):
            compute_verdict([mock] * 24)

    def test_malformed_scientific_held_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HELD_WORLD_COUNT"):
            compute_verdict([])


if __name__ == "__main__":
    unittest.main()
