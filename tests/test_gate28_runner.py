"""Gate28 3-process A/B/R evaluator tests; reserved scientific seeds barred."""
import sys
import unittest
from pathlib import Path

HERE = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import runner
import world


class TestGate28Runner(unittest.TestCase):
    def test_public_preaction_context_and_intervention_independence(self):
        w = world.HiddenWorld(900011, diagnostic=True)
        for phase in ("B", "R"):
            for step in range(4):
                peek = w.public_context(phase, step)
                self.assertEqual(len(peek), 8)
                for action in world.ACTIONS:
                    self.assertEqual(w.feedback(phase, step, action).context, peek)

    def test_guard_rejects_primary_and_unapproved_seeds(self):
        for seed in (501000, 501047, 502001, 503023, -1, 999999, True):
            with self.assertRaisesRegex(ValueError, "PRIMARY_SEEDS_RESERVED"):
                runner.require_diagnostic(seed)
        runner.require_diagnostic(900011)

    def test_forced_equal_exposure_control_audit_diagnostic_only(self):
        # Three disjoint diagnostic worlds. Primary 501xxx/502xxx/503xxx
        # seed ranges must never enter this audit.
        records = []
        for seed, cohort in (
                (900071, "diagnostic_shifted"),
                (900072, "stationary"),
                (900073, "independent_noise")):
            with self.subTest(cohort=cohort):
                record = runner.compare_controls(seed, cohort)
                records.append(record)
                self.assertEqual(record["status"],
                                 "G28_EQUAL_EXPOSURE_CONTROL_DIAGNOSTIC_ONLY")
                self.assertEqual(record["cohort"], cohort)
                self.assertFalse(record["scientific_primary_scored"])
                self.assertFalse(record["original_world_first_use"])
                self.assertEqual(record["strongest_matched_control_adequacy"],
                                 "UNVERIFIED")
                self.assertEqual(record["phases"]["A"]["public_exposures"], 96)
                for phase in ("B", "R"):
                    summary = record["phases"][phase]
                    self.assertEqual(summary["public_exposures"], 64)
                    scores = summary["scores"]
                    self.assertEqual(set(scores), set(record["models"]))
                    self.assertGreater(
                        scores["full_reference_reward"]["checkpoint_bytes"],
                        16384)
                    self.assertGreater(
                        scores["full_reference_reward"]["peak_rule_work"],
                        8192)
                    for arm in record["models"]:
                        row = scores[arm]
                        self.assertTrue(0 <= row["equal_action_held_brier"] <= 1)
                        self.assertTrue(0 <= row["selected_held_reward"] <= 32)
                        if arm != "full_reference_reward":
                            self.assertLessEqual(row["checkpoint_bytes"], 16384)
                            self.assertLessEqual(row["peak_rule_work"], 8192)
                print("G28_DIAGNOSTIC_CONTROL_AUDIT",
                      __import__("json").dumps({
                          "cohort": cohort, "seed": seed,
                          "R": {arm: {
                              "brier": row["equal_action_held_brier"],
                              "reward": row["selected_held_reward"],
                              "bytes": row["checkpoint_bytes"],
                              "work": row["peak_rule_work"]}
                              for arm, row in record["phases"]["R"]["scores"].items()},
                          "science": "UNVERIFIED"},
                          sort_keys=True))

        import control_audit
        independent = control_audit.audit(records)
        self.assertEqual(independent["seed_count"], 3)
        self.assertFalse(independent["scientific_gain_verified"])
        self.assertEqual(independent["matched_control_adequacy"], "UNVERIFIED")

    def test_forced_exposure_parity_includes_every_model_control(self):
        baseline = {arm + ".forced": {"exposure_sha256": "a" * 64}
                    for arm in runner.MODEL_ARMS}
        self.assertEqual(runner.require_forced_parity(baseline), "a" * 64)
        for arm in runner.MODEL_ARMS:
            forged = {k: dict(v) for k, v in baseline.items()}
            forged[arm + ".forced"]["exposure_sha256"] = "b" * 64
            with self.subTest(arm=arm):
                with self.assertRaisesRegex(ValueError,
                                            "EQUAL_EXPOSURE_PARITY_FAIL"):
                    runner.require_forced_parity(forged)
        with self.assertRaisesRegex(ValueError,
                                    "EQUAL_EXPOSURE_PARITY_FAIL"):
            runner.require_forced_parity({})

    def test_true_cold_and_identical_forced_exposure(self):
        result = runner.diagnostic(900011)
        self.assertEqual(result["stages"], ["A", "B", "R"])
        self.assertEqual(result["distinct_processes"], 3)
        self.assertFalse(result["primary_scored"])
        self.assertEqual(result["status"], "G28_DIAGNOSTIC_COLD_PROCESS_PASS")
        self.assertEqual(result["science"], "NOT_RUN_NO_INDEPENDENTLY_QUALIFIED_STRONG_MATCHED_CONTROL")
        self.assertLessEqual(result["max_rule_work"], 8192)
        self.assertLessEqual(result["max_checkpoint_bytes"], 16384)
        self.assertNotEqual(result["forced_B_exposure_hash"],
                            result["forced_R_exposure_hash"])
