"""G44 synthetic context experiment safeguards; negative result is allowed."""
import json
import unittest
from native_dg1a import DG1APrototype, GENOME_PARAMETER_COUNT
from g38_native_learning import run_development, FRAMES, GRADIENT_CALLS
from g44_context import (CONDITIONS, CONTEXT_MODES, CONTEXTS, CUES, ROUNDS,
                         context_state, chosen_action, run, build_report, report_json,
                         SCHEMA)


class G44ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_context_is_local_immutable_and_independent_of_cue(self):
        m = DG1APrototype()
        for context in CONTEXTS:
            visible = context_state(m, context, True)
            masked = context_state(m, context, False)
            self.assertEqual(visible[1][1][0], context)
            self.assertEqual(masked[1][1][0], 0.0)
            self.assertEqual(visible[1][1][1:], masked[1][1][1:])
            for y in range(4):
                for x in range(4):
                    if (y, x) != (1, 1):
                        self.assertEqual(visible[y][x], masked[y][x])

    def test_masked_context_cannot_separate_opposing_rules(self):
        m = DG1APrototype()
        genome = run_development("mapped").genome
        for cue in CUES:
            self.assertEqual(chosen_action(m, genome, cue, 1, False),
                             chosen_action(m, genome, cue, -1, False))
        for row in self.report["rows"]:
            if row["context_mode"] == "masked":
                self.assertEqual(row["joint_accuracy_after"], 0.5)

    def test_complete_balanced_budget_and_fixed_capacity(self):
        rows = self.report["rows"]
        self.assertEqual({(r["condition"], r["context_mode"]) for r in rows},
                         {(condition, mode) for condition in CONDITIONS
                          for mode in CONTEXT_MODES})
        for row in rows:
            with self.subTest(condition=row["condition"], mode=row["context_mode"]):
                n = ROUNDS * len(CUES) * len(CONTEXTS)
                self.assertEqual(row["interactions"], n)
                self.assertEqual(row["feedback_frames"], n * FRAMES)
                self.assertEqual(row["gradient_calls"], n * GRADIENT_CALLS)
                self.assertEqual(row["genome_parameters"], GENOME_PARAMETER_COUNT)
                for key in ("positive_before", "negative_before",
                            "positive_after", "negative_after"):
                    self.assertIn(row[key], (0.0, 0.5, 1.0))

    def test_no_feedback_preserves_pretrained_genome(self):
        original = run_development("mapped").genome
        for mode in CONTEXT_MODES:
            self.assertEqual(run("no_feedback", mode).genome, original)

    def test_repeatability_receipt_and_fail_closed_science(self):
        report = self.report
        self.assertEqual(report["schema"], SCHEMA)
        self.assertFalse(report["primary_execution_allowed"])
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        self.assertEqual(json.loads(report_json()), report)
        print("YGG_G44_DEV_CONTEXT_JSON=" + report_json(), flush=True)

    def test_invalid_conditions_and_context_rejected(self):
        for invalid in ("primary", "", None, 0):
            with self.assertRaises(ValueError):
                run(invalid, "visible")
            with self.assertRaises(ValueError):
                run("mapped", invalid)
        for invalid in (0, 2, 1.0, True):
            with self.assertRaises(ValueError):
                context_state(DG1APrototype(), invalid, True)
        with self.assertRaises(ValueError):
            context_state(DG1APrototype(), 1, 1)


if __name__ == "__main__":
    unittest.main()
