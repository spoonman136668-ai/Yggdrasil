"""G42 synthetic interference trace: exact G40 replay, fixed budgets, no efficacy gate."""
import json
import unittest
from g38_native_learning import ROUNDS, FRAMES, GRADIENT_CALLS, CUES
from g40_adaptation import CONDITIONS, adapt
from g42_interference import CHECKPOINTS, SCHEMA, trace, build_report, report_json

class G42Interference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_checkpoint_coverage_and_no_hidden_budget_drift(self):
        self.assertEqual(CHECKPOINTS[0], 0)
        self.assertEqual(CHECKPOINTS[-1], ROUNDS)
        rows = self.report["rows"]
        self.assertEqual({(r["pretrained"], r["condition"]) for r in rows},
                         {(warm, cond) for warm in (False, True) for cond in CONDITIONS})
        for row in rows:
            with self.subTest(pretrained=row["pretrained"], condition=row["condition"]):
                cps = row["checkpoints"]
                self.assertEqual(tuple(x["rounds"] for x in cps), CHECKPOINTS)
                for x in cps:
                    n = x["rounds"] * len(CUES)
                    self.assertEqual(x["interactions"], n)
                    self.assertEqual(x["feedback_frames"], n * FRAMES)
                    self.assertEqual(x["gradient_calls"], n * GRADIENT_CALLS)
                    self.assertEqual(x["source_accuracy"] + x["target_accuracy"], 1.0)
                    self.assertGreaterEqual(x["weight_distance"], 0)
                self.assertEqual(cps[0]["weight_distance"], 0)

    def test_replay_exact_G40_endpoints(self):
        for warm in (False, True):
            for condition in CONDITIONS:
                with self.subTest(pretrained=warm, condition=condition):
                    t = trace(condition, warm)
                    g40 = adapt(condition, warm)
                    self.assertEqual(t.final_genome, g40.genome)
                    self.assertEqual(t.checkpoints[-1]["target_accuracy"],
                                     g40.target_after)
                    self.assertEqual(t.interactions, g40.interactions)
                    self.assertEqual(t.feedback_frames, g40.frames)
                    self.assertEqual(t.gradient_calls, g40.gradient_calls)

    def test_no_feedback_and_decoder_ablation_no_change(self):
        for row in self.report["rows"]:
            if row["condition"] in ("no_feedback", "decoder_ablation"):
                self.assertTrue(all(x["weight_distance"] == 0 for x in row["checkpoints"]))

    def test_scope_and_machine_readable_diagnostics(self):
        report = self.report
        self.assertEqual(report["schema"], SCHEMA)
        self.assertFalse(report["primary_execution_allowed"])
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        payload = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.assertEqual(json.loads(payload), json.loads(json.dumps(report)))
        self.assertEqual(json.loads(report_json()), json.loads(json.dumps(report)))
        print("YGG_G42_DEV_TRACE_JSON=" + payload, flush=True)

    def test_invalid_entry_points(self):
        for invalid in ("primary", "", None, 0):
            with self.assertRaises(ValueError):
                trace(invalid)
        with self.assertRaises(ValueError):
            trace("mapped", pretrained=1)

if __name__ == "__main__":
    unittest.main()
