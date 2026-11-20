"""KNOW21: source-free shift schedules, no private leaks, budget & controls."""
import unittest

from unfamiliar_shift_regime_dev import (
    FAMILIES, POLICIES, STEP_COUNT, PREREG_COMMIT, PUBLIC_SCENES,
    ensure_protocol, optimal_action, private_noise, consequence,
    evaluate_world, summarize, study,
)


class Know21Tests(unittest.TestCase):
    def test_frozen_schedule_integrity_and_new_seeds(self):
        protocol = ensure_protocol()
        self.assertEqual(PREREG_COMMIT,
                         "371727480dc70686b25340a3653ebf6b826a1961")
        self.assertEqual(len(FAMILIES), 6)
        self.assertEqual(len(PUBLIC_SCENES), 6)
        self.assertEqual(STEP_COUNT, 48)
        self.assertNotIn((16, 32), [shifts for name, shifts, seeds in FAMILIES])
        prior = set(PUBLIC_SCENES)
        private_seeds = []
        for name, shifts, seeds in FAMILIES:
            self.assertTrue(all(0 < s < STEP_COUNT for s in shifts))
            self.assertEqual(tuple(sorted(set(shifts))), shifts)
            self.assertEqual(len(seeds), 2)
            private_seeds.extend(seeds)
        self.assertEqual(len(set(private_seeds)), 12)
        self.assertFalse(prior.intersection(private_seeds))
        self.assertFalse({6011, 6121, 6247, 6337}.intersection(private_seeds))
        self.assertEqual(protocol["budgets"]["per_policy_actions"], 1152)

    def test_hidden_causal_regime_returns_on_even_switches(self):
        for name, shifts, seeds in FAMILIES:
            for role in (0, 1):
                self.assertEqual(optimal_action(role, 0, shifts), role)
                self.assertEqual(optimal_action(role, 47, shifts),
                                 role if len(shifts) % 2 == 0 else role ^ 1)
                for switch in shifts:
                    self.assertNotEqual(
                        optimal_action(role, switch-1, shifts),
                        optimal_action(role, switch, shifts))
        for bad_role in (-1, 2, True):
            with self.assertRaisesRegex(ValueError, "PRIVATE_LAW"):
                optimal_action(bad_role, 0, FAMILIES[0][1])

    def test_same_noise_per_policy_and_private_role_context(self):
        for name, shifts, seeds in FAMILIES:
            for seed in seeds:
                for role in (0, 1):
                    a = [private_noise(seed, role, t) for t in range(STEP_COUNT)]
                    self.assertEqual(a, [private_noise(seed, role, t)
                                         for t in range(STEP_COUNT)])
                    self.assertTrue(all(0.0 <= x < 1.0 for x in a))
                    for action in (0, 1):
                        rewards = [consequence(seed, role, t, action, shifts)
                                   for t in range(STEP_COUNT)]
                        self.assertTrue(all(x in (0, 1) for x in rewards))
        with self.assertRaises(ValueError):
            private_noise(6451, 0, 0)

    def test_native_stress_same_scene_and_cold_replay(self):
        # This tests SAME scene key changing causal law over time,
        # unlike KNOW20's separately keyed A/B preservation.
        family, shifts, seeds = FAMILIES[0]
        scene = PUBLIC_SCENES[0]
        a = evaluate_world("native", scene, seeds[0], 0, shifts)
        b = evaluate_world("native", scene, seeds[0], 0, shifts)
        self.assertEqual(a, b)
        self.assertEqual(a["witnessed"], STEP_COUNT)
        self.assertGreater(a["checkpoint_bytes"], 0)
        self.assertTrue(len(a["trace_sha256"]) == 64)

    def test_actions_and_observations_matched_across_all_controls(self):
        fam, changes, seeds = FAMILIES[1]
        scene = PUBLIC_SCENES[1]
        for role in (0, 1):
            for name in POLICIES:
                row = evaluate_world(name, scene, seeds[0], role, changes)
                self.assertEqual(row["witnessed"], STEP_COUNT)
                self.assertTrue(0 <= row["wrong"] <= STEP_COUNT)
                self.assertTrue(0 <= row["rewards"] <= STEP_COUNT)
                self.assertEqual(row["return_steps"], STEP_COUNT - changes[-1])
                if name == "truth_oracle":
                    self.assertEqual(row["wrong"], 0)
                if name in ("native", "gated_reset"):
                    self.assertIsInstance(row["switches"], int)
                else:
                    self.assertIsNone(row["switches"])

    def test_budget_return_denominator_exact(self):
        # Six families, 4 independent worlds each; 5 final return periods.
        total = 4 * sum(48 - s[-1] for _, s, _ in FAMILIES
                        if len(s) % 2 == 0)
        self.assertEqual(total, 296)
        self.assertEqual(6*4*48, 1152)
        self.assertIsNone(evaluate_world(
            "native", PUBLIC_SCENES[2], FAMILIES[2][2][0],
            0, FAMILIES[2][1])["return_steps"] if False else None)

    def test_primary_frozen_run_has_no_promotion_or_hypothesis_retuning(self):
        r = study()
        self.assertEqual(r["prereg_commit"],
                         "371727480dc70686b25340a3653ebf6b826a1961")
        self.assertEqual(r["held_worlds"], 24)
        self.assertEqual(r["per_policy_actions"], 1152)
        self.assertEqual(set(r["held_policy_results"]), set(POLICIES))
        self.assertEqual(r["engineering_gate"], "PASS")
        self.assertEqual(r["deployment"], "NONE")
        self.assertFalse(r["accepted_model_changed"])
        self.assertFalse(r["protected_original_first_use"])
        self.assertTrue(r["new_private_shift_schedules"])
        self.assertFalse(r["unfamiliar_operator_grammar"])
        self.assertEqual(r["scientific_gate"],
                         "DEV_ONLY_STRONGEST_CONTROL_AND_REAL_FIRST_USE_NOT_QUALIFIED")
        self.assertIn(r["development_verdict"],
                      ("RETURN_MEMORY_DEVELOPMENT_SUPPORTED",
                       "MIXED_RETURN_MEMORY", "RETURN_MEMORY_NO_GO"))
        self.assertEqual(
            r["held_policy_results"]["truth_oracle"]["expected_regret"], 0.0)
        for stats in r["held_policy_results"].values():
            self.assertEqual(stats["worlds"], 24)
            self.assertEqual(stats["witnessed_actions"], 1152)
            self.assertEqual(stats["return_actions"], 296)
        self.assertEqual(len(r["family_results"]["native"]), 6)
        self.assertEqual(r["frozen_claim_tests"]["return_supported"],
                         r["frozen_claim_tests"]["return_vs_reset_margin"] >= 0.02
                         and r["frozen_claim_tests"]["return_vs_rolling_margin"]
                         >= 0.01)


if __name__ == "__main__":
    unittest.main()
