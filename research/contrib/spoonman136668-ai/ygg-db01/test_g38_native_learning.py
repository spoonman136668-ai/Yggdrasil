"""G38 synthetic-only action/reward/control test; no original cohorts consumed."""
import json
from pathlib import Path
import unittest

from native_dg1a import DG1APrototype, seeded_genome, GENOME_PARAMETER_COUNT
from matched_feedback import matched_feedback
from g38_native_learning import (
    CONDITIONS, ROUNDS, FRAMES, GRADIENT_CALLS, CUES,
    action, perceived_valence, run_development, sensory,
)

class G38NativeLearning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {c: run_development(c)
                    for c in ("mapped", "reversed", "sham", "no_feedback")}

    def test_synthetic_action_learning_and_interpolated_cues(self):
        mapped = self.data["mapped"]
        self.assertEqual((mapped.baseline_score, mapped.post_train_score,
                          mapped.novel_magnitude_score), (0.5, 1.0, 1.0))
        self.assertNotEqual(mapped.genome, seeded_genome(17))
        self.assertEqual(mapped.genome.parameter_count, GENOME_PARAMETER_COUNT)

    def test_reversed_sham_and_no_feedback_controls(self):
        self.assertEqual(self.data["reversed"].novel_magnitude_score, 0.0)
        self.assertEqual(self.data["sham"].novel_magnitude_score, 0.5)
        self.assertEqual(self.data["no_feedback"].novel_magnitude_score, 0.5)
        self.assertEqual(self.data["no_feedback"].genome, seeded_genome(17))

    def test_equal_call_budgets_except_zero_energy(self):
        self.assertEqual(CONDITIONS, {"mapped", "reversed", "sham", "no_feedback"})
        for c, r in self.data.items():
            with self.subTest(condition=c):
                self.assertEqual(r.interactions, ROUNDS * len(CUES))
                self.assertEqual(r.feedback_frames, r.interactions * FRAMES)
                self.assertEqual(r.gradient_calls, r.interactions * GRADIENT_CALLS)
                self.assertEqual(r.cellular_step_calls,
                                 r.interactions * (FRAMES + 1) + 4)
                self.assertIn("SYNTHETIC_DEVELOPMENT_ONLY", r.evidence_class)

    def test_native_feedback_response_not_hidden_correct_answer(self):
        model, g = DG1APrototype(), seeded_genome(17)
        for outcome in (0, 1):
            for condition in ("mapped", "reversed", "sham"):
                wave = matched_feedback(outcome, condition, 16, 103)
                positive = (bool(103 & 1) if condition == "sham" else
                            not bool(outcome) if condition == "reversed"
                            else bool(outcome))
                self.assertEqual(perceived_valence(model, g, wave),
                                 1 if positive else -1)
        self.assertEqual(perceived_valence(model, g, (0.0,) * 16), 0)

    def test_invalid_sensory_and_control_fail_closed(self):
        model, g = DG1APrototype(), seeded_genome(17)
        for wave in ((1.0,) * 16, (0.0,) * 15,
                     (float("nan"),) * 16):
            with self.assertRaises(ValueError):
                perceived_valence(model, g, wave)
        for bad in (float("nan"), 1.1, True):
            with self.assertRaises(ValueError):
                sensory(bad)
        with self.assertRaises(ValueError):
            run_development("primary")
        self.assertIn(action(model, g, -0.5), (-1, 1))

    def test_original_admission_stays_no_go(self):
        here = Path(__file__).resolve().parent
        g35 = json.loads((here / "g35_candidate.json").read_text("utf-8"))
        g36 = json.loads((here / "g36_evidence_index.json").read_text("utf-8"))
        self.assertFalse(g35["authority"]["primary_execution_allowed"])
        self.assertFalse(g35["authority"]["protected_first_use_allowed"])
        self.assertEqual(g36["status"], "ORIGINALS_NOT_PROVIDED")
        self.assertFalse(g36["authority"]["primary_execution_allowed"])
        self.assertTrue(all(v is None for v in g36["records"].values()))

if __name__ == "__main__":
    unittest.main()
