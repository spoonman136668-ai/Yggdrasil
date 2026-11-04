"""G46 optimization diagnostic: replay exact baseline, all negative arms preserved."""
import json
import unittest

from native_dg1a import GENOME_PARAMETER_COUNT
from g45_representation import ROUNDS, UPDATES_PER_PAIR, supervised_fit
from g46_optimization import (ARMS, MODES, STARTS, INTERVALS, PAIRS, SCHEMA,
                              fit, build_report, report_json, cross_context_update_probe)


class G46OptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_g45_baseline_exact_model_and_scores(self):
        for start in STARTS:
            for mode in MODES:
                with self.subTest(start=start, mode=mode):
                    old, new = supervised_fit(start, mode), fit("baseline", start, mode)
                    self.assertEqual(new.genome, old.genome)
                    self.assertEqual(new.checkpoints[0]["accuracy"], old.before)
                    self.assertEqual(new.checkpoints[-1]["accuracy"], old.after)
                    self.assertEqual(new.checkpoints[-1]["interpolation"], old.interpolation)
                    self.assertEqual(new.updates, old.updates)

    def test_arms_budget_masked_control_and_loss_reporting(self):
        rows = self.report["rows"]
        self.assertEqual({(r["arm"], r["start"], r["context_mode"]) for r in rows},
                         {(a, s, m) for a in ARMS for s in STARTS for m in MODES})
        for row in rows:
            with self.subTest(arm=row["arm"], start=row["start"], mode=row["context_mode"]):
                self.assertEqual(row["updates"], ROUNDS * len(PAIRS) * UPDATES_PER_PAIR)
                self.assertEqual(row["genome_parameters"], GENOME_PARAMETER_COUNT)
                self.assertEqual(tuple(c["round"] for c in row["checkpoints"]), INTERVALS)
                for c in row["checkpoints"]:
                    self.assertEqual(c["updates"], c["round"] * len(PAIRS) * UPDATES_PER_PAIR)
                    self.assertGreaterEqual(c["supervised_mse"], 0)
                    self.assertLessEqual(c["accuracy"], 1.0)
                    if row["context_mode"] == "masked":
                        self.assertEqual(c["accuracy"], 0.5)
                        self.assertEqual(c["interpolation"], 0.5)

    def test_cross_context_gradient_diagnostic_complete_and_finite(self):
        probes = self.report["gradient_probes"]
        self.assertEqual(set(probes), set(STARTS))
        for start in STARTS:
            rows = probes[start]
            self.assertEqual({(r["context"], r["cue"]) for r in rows}, set(PAIRS))
            for r in rows:
                self.assertLess(abs(r["target_response_delta"]), 4.0)
                self.assertLess(abs(r["opposing_context_response_delta"]), 4.0)

    def test_scope_and_identical_machine_readable_report(self):
        r = self.report
        self.assertEqual(r["schema"], SCHEMA)
        self.assertFalse(r["primary_execution_allowed"])
        self.assertEqual(r["scientific_acceptance"], "NO_GO")
        self.assertEqual(r["native_reward_learning"], "UNVERIFIED")
        self.assertEqual(r["genuine_transfer"], "UNVERIFIED")
        self.assertEqual(json.loads(report_json()), json.loads(json.dumps(r)))
        print("YGG_G46_DEV_OPTIMIZATION_JSON=" + report_json(), flush=True)

    def test_invalid_inputs_fail_closed(self):
        for bad in ("primary", "", 0, None):
            with self.assertRaises(ValueError):
                fit(bad, "seeded", "visible")
            with self.assertRaises(ValueError):
                fit("baseline", bad, "visible")
            with self.assertRaises(ValueError):
                fit("baseline", "seeded", bad)


if __name__ == "__main__":
    unittest.main()
