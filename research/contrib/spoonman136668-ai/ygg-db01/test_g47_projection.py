"""G47 exact G46 baseline, fixed compute, controls and negative receipts."""
import json
import unittest
from native_dg1a import GENOME_PARAMETER_COUNT
from g46_optimization import PAIRS, STARTS, MODES, fit
from g47_projection import (ARMS, ROUNDS, UPDATES_PER_PAIR, SCHEMA,
                            run, build_report, report_json)

class G47ContextProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_unmodified_G46_four_round_baseline(self):
        for start in STARTS:
            for mode in MODES:
                with self.subTest(start=start, mode=mode):
                    old = fit("baseline", start, mode)
                    new = run("baseline", start, mode)
                    original = next(x for x in old.checkpoints if x["round"] == ROUNDS)
                    self.assertEqual(new.final_accuracy, original["accuracy"])
                    self.assertEqual(new.interpolation, original["interpolation"])
                    self.assertEqual(new.final_mse, original["supervised_mse"])

    def test_identical_gradient_budget_and_no_capacity_change(self):
        rows = self.report["rows"]
        self.assertEqual({(r["arm"], r["start"], r["context_mode"]) for r in rows},
                         {(a, s, m) for a in ARMS for s in STARTS for m in MODES})
        expected = ROUNDS * len(PAIRS) * UPDATES_PER_PAIR
        for row in rows:
            with self.subTest(row=row["arm"], start=row["start"], mode=row["context_mode"]):
                self.assertEqual(row["updates"], expected)
                self.assertEqual(row["gradient_evaluations"], 2 * expected)
                self.assertEqual(row["genome_parameters"], GENOME_PARAMETER_COUNT)
                self.assertLessEqual(row["projection_count"], row["negative_dot_count"])
                if row["arm"] == "baseline":
                    self.assertEqual(row["projection_count"], 0)
                for key in ("before_accuracy", "after_accuracy", "interpolation"):
                    self.assertIn(row[key], (0.0, 0.25, 0.5, 0.75, 1.0))
                self.assertGreaterEqual(row["after_mse"], 0)

    def test_context_hidden_is_information_theoretic_negative(self):
        for row in self.report["rows"]:
            if row["context_mode"] == "masked":
                self.assertEqual(row["after_accuracy"], 0.5)

    def test_receipt_scope_and_cross_platform_stability(self):
        report = self.report
        self.assertEqual(report["schema"], SCHEMA)
        self.assertFalse(report["primary_execution_allowed"])
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["native_reward_learning"], "UNVERIFIED")
        self.assertEqual(json.loads(report_json()), json.loads(json.dumps(report)))
        print("YGG_G47_DEV_PROJECTION_JSON=" + report_json(), flush=True)

    def test_invalid_entry_points(self):
        for bad in ("protected", "", None, 0):
            with self.assertRaises(ValueError):
                run(bad, "seeded", "visible")
            with self.assertRaises(ValueError):
                run("baseline", bad, "visible")
            with self.assertRaises(ValueError):
                run("baseline", "seeded", bad)

if __name__ == "__main__":
    unittest.main()
