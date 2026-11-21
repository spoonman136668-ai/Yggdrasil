"""KNOW20: frozen synthetic noisy action, provenance, retention, and controls."""
import json
import unittest

from noisy_regime_memory_dev import (
    TRAIN_A, TRAIN_B, HELD, SEEDS, STEPS, SOURCE_MODE, SCHEMA,
    public_source, optimal_private_action, private_noise,
    private_consequence, NativeSparseRegimeMemory,
    StationaryBeta, RollingBeta, ResetBeta, BayesianHMM,
    evaluate_world, proof, canonical, digest,
)


class Know20Tests(unittest.TestCase):
    def test_frozen_seeds_public_role_independence(self):
        self.assertEqual(TRAIN_A, (6011, 6121))
        self.assertEqual(TRAIN_B, (6247, 6337))
        self.assertEqual(HELD, (6451, 6581, 6703, 6823, 6947, 7069))
        self.assertEqual(len(set(SEEDS)), 10)
        self.assertTrue(set(SEEDS).isdisjoint({
            2111, 2221, 2333, 2441, 2551,
            3119, 3251, 3371, 3463, 3593}))
        for seed in SEEDS:
            public = public_source(seed)
            self.assertEqual(public["source_mode"], SOURCE_MODE)
            self.assertFalse(public["native_accepted"])
            self.assertNotIn("role", public)
            self.assertNotIn("noise", public)
            self.assertEqual(public_source(seed), public)

    def test_regime_truth_is_private_and_recurrent(self):
        for role in (0, 1):
            self.assertEqual([optimal_private_action(role, t)
                              for t in (0, 15, 16, 31, 32, 47)],
                             [role, role, role ^ 1, role ^ 1, role, role])
        with self.assertRaises(ValueError):
            optimal_private_action(True, 0)
        with self.assertRaises(ValueError):
            optimal_private_action(0, 48)

    def test_genuinely_variable_outcomes_from_same_public_action(self):
        scene = TRAIN_A[0]
        for a in (0, 1):
            observed = {private_consequence(scene, 0, t, a)
                        for t in range(STEPS)}
            self.assertEqual(observed, {0, 1})
        self.assertTrue(all(0.0 <= private_noise(scene, t) < 1.0
                            for t in range(STEPS)))

    def test_witnessed_outcome_changes_prediction(self):
        a = NativeSparseRegimeMemory()
        x = a.stage(TRAIN_A[0], 0, 0, 1)
        y = a.stage(TRAIN_A[0], 0, 0, 0)
        self.assertGreater(x.predict(TRAIN_A[0], 0), a.predict(TRAIN_A[0], 0))
        self.assertLess(y.predict(TRAIN_A[0], 0), a.predict(TRAIN_A[0], 0))
        self.assertNotEqual(x.checkpoint(), y.checkpoint())
        self.assertEqual(a.checkpoint(),
                         NativeSparseRegimeMemory().checkpoint())

    def test_disjoint_scene_retention_and_cold_restore(self):
        a = NativeSparseRegimeMemory()
        for t in range(8):
            a = a.stage(TRAIN_A[0], t, t % 2,
                        private_consequence(TRAIN_A[0], 0, t, t % 2))
        old = (a.predict(TRAIN_A[0], 0), a.predict(TRAIN_A[0], 1))
        before = a.checkpoint()
        b = a
        for t in range(8):
            b = b.stage(TRAIN_B[0], t, t % 2,
                        private_consequence(TRAIN_B[0], 1, t, t % 2))
        self.assertEqual(old,
                         (b.predict(TRAIN_A[0], 0), b.predict(TRAIN_A[0], 1)))
        self.assertEqual(before, a.checkpoint())
        raw = b.checkpoint()
        cold = NativeSparseRegimeMemory.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.predict(TRAIN_A[0], 0), old[0])
        self.assertEqual(cold.predict(TRAIN_A[0], 1), old[1])

    def test_canonical_checkpoint_source_forgery_and_replay(self):
        a = NativeSparseRegimeMemory().stage(TRAIN_A[0], 0, 0, 1)
        raw = a.checkpoint()
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_PIN"):
            NativeSparseRegimeMemory.restore(raw, "0" * 64)
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_REJECTED"):
            bad = raw.replace(b'"accepted_native":false',
                              b'"accepted_native":true')
            NativeSparseRegimeMemory.restore(bad, digest(bad))
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_REJECTED"):
            d = json.loads(raw)
            s = d["scenes"][0]
            s["slots"][0][0][1] = 9
            tampered = canonical(d)
            NativeSparseRegimeMemory.restore(tampered, digest(tampered))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY|CHECKPOINT_REJECTED"):
            duplicated = raw.replace(b'"schema":', b'"schema":"fake","schema":')
            NativeSparseRegimeMemory.restore(duplicated, digest(duplicated))
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_OUT_OF_ORDER"):
            a.stage(TRAIN_A[0], 0, 0, 1)
        with self.assertRaisesRegex(ValueError, "FORGED_SOURCE_MODE"):
            a.stage(TRAIN_A[0], 1, 1, 0, source_mode="owner_accepted")

    def test_strict_public_types(self):
        a = NativeSparseRegimeMemory()
        for bad in (True, -1, 2):
            with self.assertRaises(ValueError):
                a.stage(TRAIN_A[0], 0, bad, 1)
        for bad in (True, -1, 2):
            with self.assertRaises(ValueError):
                a.stage(TRAIN_A[0], 0, 0, bad)
        with self.assertRaises(ValueError):
            a.stage(TRAIN_A[0], 1, 0, 1)
        with self.assertRaises(ValueError):
            public_source(True)

    def test_controls_learn_only_from_observed_outcomes(self):
        classes = (StationaryBeta, RollingBeta, ResetBeta, BayesianHMM)
        for klass in classes:
            a, b = klass(), klass()
            p = a.predict(0)
            a.observe(0, 1)
            b.observe(0, 0)
            self.assertGreater(a.predict(0), b.predict(0))
            self.assertEqual(p, 0.5)
        rolling = RollingBeta()
        for i in range(20):
            rolling.observe(0, i % 2)
        self.assertEqual(len(rolling.history), 8)

    def test_equal_source_action_budget_and_oracle_ceiling(self):
        for scene in HELD[:2]:
            for role in (0, 1):
                for policy in ("native", "stationary_beta", "rolling_8",
                               "gated_reset", "bayes_hmm",
                               "seeded_random", "passive_zero", "truth_oracle"):
                    r = evaluate_world(scene, role, policy)
                    self.assertEqual(r["steps"], STEPS)
                    self.assertEqual(len(r["actions"]), STEPS)
                    self.assertGreaterEqual(r["wrong_actions"], 0)
                    self.assertEqual(r["wrong_actions"], 0
                                     if policy == "truth_oracle" else
                                     r["wrong_actions"])
                self.assertEqual(
                    evaluate_world(scene, role, "native"),
                    evaluate_world(scene, role, "native"))

    def test_one_frozen_trial_reports_all_controls_and_no_science_promotion(self):
        result = proof()
        self.assertEqual(result["prereg_commit"],
                         "1015bac86eecf675b3d563da1a5b64f4b8cacc5a")
        self.assertEqual(result["fit_witnessed_actions"], 192)
        self.assertEqual(result["fit_A_actions"], 96)
        self.assertEqual(result["fit_B_actions"], 96)
        self.assertEqual(result["old_A_prediction_drift"], 0)
        self.assertEqual(result["engineering_gate"], "PASS")
        self.assertEqual(result["scientific_gate"],
                         "NOT_QUALIFIED_SYNTHETIC_DEVELOPMENT_ONLY")
        self.assertFalse(result["protected_original_first_use"])
        self.assertTrue(result["no_accepted_model_or_training_owner_change"])
        self.assertEqual(set(result["held_policies"]), {
            "native", "stationary_beta", "rolling_8", "gated_reset",
            "bayes_hmm", "seeded_random", "passive_zero", "truth_oracle"})
        for row in result["held_policies"].values():
            self.assertEqual(row["worlds"], 12)
            self.assertEqual(row["witnessed_actions"], 576)
        self.assertEqual(result["held_policies"]["truth_oracle"]
                         ["expected_regret_per_action"], 0.0)
        self.assertIn(result["development_hypothesis"],
                      ("MECHANISM_SUPPORTED_DEVELOPMENT", "DEV_NO_GO_OR_MIXED"))


if __name__ == "__main__":
    unittest.main()
