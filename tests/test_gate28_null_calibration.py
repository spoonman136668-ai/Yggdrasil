"""Frozen Gate28-NC1 diagnostics: no primary-world or owner acceptance."""
import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import control_audit
import core
import dense_reference
import runner
import world


class TestGate28NullCalibration(unittest.TestCase):
    def test_frozen_preregistration_and_public_only_prequential_ratio(self):
        prereg = json.loads((HERE / "null_calibration_prereg.json").read_text())
        self.assertEqual(prereg["schema"],
                         "yggdrasil.gate28.null-mixture-diagnostic-prereg.v1")
        seeds = prereg["preregistered_fresh_diagnostic_seeds"]
        cohort_aliases = {"shifted": "diagnostic_shifted"}
        self.assertEqual({cohort_aliases.get(k, k): tuple(v)
                          for k, v in seeds.items()},
                         control_audit.NULL_FRESH_SEEDS)
        self.assertEqual(prereg["thresholds"]["noise_R_mean_brier_absolute_max"],
                         0.270)
        self.assertEqual(prereg["thresholds"][
            "shifted_mean_B_and_R_brier_degradation_vs_dense_max"], 0.015)
        self.assertEqual(prereg["thresholds"][
            "max_per_action_rule_evaluations"], 8192)

        source_world = world.HiddenWorld(900081, diagnostic=True)
        row = source_world.source(0)
        original = dense_reference.new("dense_causal_reward")
        null = dense_reference.new(dense_reference.NULL_ARM)
        forecast_before = dense_reference.predict(
            original, row.context, row.action, core.Work())
        self.assertEqual(null["null_evidence"], [])
        dense_reference.observe(original, row.context, row.intermediates,
                                row.action, row.consequence, core.Work())
        dense_reference.observe(null, row.context, row.intermediates,
                                row.action, row.consequence, core.Work())
        expected = round(math.log(2.0 * (
            forecast_before if row.consequence else 1.0 - forecast_before)), 9)
        self.assertEqual(null["null_evidence"], [expected])
        self.assertEqual(null["scores"], original["scores"])
        self.assertEqual(null["last_context"], original["last_context"])
        ctx = source_world.public_context("B", 0)
        self.assertEqual(dense_reference.choose(null, ctx, core.Work()),
                         dense_reference.choose(original, ctx, core.Work()))
        state = dense_reference.unpack(dense_reference.pack(null))
        self.assertEqual(state["null_evidence"], [expected])
        state["null_evidence"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "DENSE_NULL_PUBLIC_EVIDENCE"):
            dense_reference.pack(state)
        with self.assertRaisesRegex(ValueError,
                                    "G28_PRIMARY_SEEDS_RESERVED"):
            runner.require_diagnostic(501000)

    def test_frozen_nine_world_diagnostic_negative_is_not_a_ci_failure(self):
        # Nine new worlds are read exactly once by THIS frozen diagnostic.
        # A NO-GO is retained as a valid negative scientific outcome.
        records = []
        for cohort, seeds in control_audit.NULL_FRESH_SEEDS.items():
            for seed in seeds:
                result = runner.compare_controls(seed, cohort)
                self.assertEqual(result["seed"], seed)
                self.assertEqual(result["cohort"], cohort)
                self.assertFalse(result["scientific_primary_scored"])
                self.assertFalse(result["original_world_first_use"])
                self.assertEqual(
                    result["strongest_matched_control_adequacy"], "UNVERIFIED")
                for phase in ("B", "R"):
                    scores = result["phases"][phase]["scores"]
                    base = scores[control_audit.NULL_BASE]
                    calibrated = scores[control_audit.NULL_CANDIDATE]
                    self.assertLessEqual(calibrated["peak_rule_work"], 8192)
                    self.assertLessEqual(calibrated["checkpoint_bytes"], 16384)
                    self.assertEqual(base["selected_held_reward"],
                                     calibrated["selected_held_reward"])
                records.append(result)
        report = control_audit.audit_null_calibration(records)
        self.assertEqual(report["seed_count"], 9)
        self.assertEqual(report["classification"],
                         "NO_SCIENTIFIC_FIRST_USE_OR_PROMOTION")
        self.assertFalse(report["scientific_gain_verified"])
        self.assertFalse(report["source_primary_consumed"])
        self.assertEqual(report["matched_control_adequacy"], "UNVERIFIED")
        self.assertTrue(report["action_reward_exact_parity"])
        # This must not assert all scientific diagnostic thresholds pass.
        # A legitimate failure must be preserved, not CI-censored.
        self.assertIn(report["status"], (
            "G28_NULL_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE",
            "G28_NULL_DIAGNOSTIC_NO_GO"))
        print("G28_NULL_NINE_FRESH_DIAGNOSTIC",
              json.dumps(report, sort_keys=True))

    def test_independent_audit_rejects_missing_and_rogue_trials(self):
        with self.assertRaisesRegex(ValueError, "NULL_NINE_WORLDS"):
            control_audit.audit_null_calibration([])
        self.assertEqual(len({seed for ids in
                              control_audit.NULL_FRESH_SEEDS.values()
                              for seed in ids}), 9)
        self.assertTrue(all(900000 <= seed <= 909999 for group in
                            control_audit.NULL_FRESH_SEEDS.values()
                            for seed in group))
