"""G40 development-only adaptation controls; no frozen original tasks used."""
import unittest
from native_dg1a import seeded_genome, GENOME_PARAMETER_COUNT
from g38_native_learning import run_development, ROUNDS, FRAMES, GRADIENT_CALLS, CUES
from g40_adaptation import CONDITIONS, adapt

class G40SyntheticAdaptation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.warm = {name: adapt(name) for name in CONDITIONS}
        cls.cold = {name: adapt(name, pretrained=False) for name in CONDITIONS}

    def test_paired_budget_and_fixed_capacity(self):
        expected = ROUNDS * len(CUES)
        for group in (self.warm, self.cold):
            for condition, result in group.items():
                with self.subTest(condition=condition, pretrained=result.pretrained):
                    self.assertEqual(result.interactions, expected)
                    self.assertEqual(result.frames, expected * FRAMES)
                    self.assertEqual(result.gradient_calls, expected * GRADIENT_CALLS)
                    self.assertEqual(result.genome.parameter_count, GENOME_PARAMETER_COUNT)
                    self.assertEqual(result.evidence_class,
                                     "SYNTHETIC_DEV_ADAPTATION_NOT_SCIENTIFIC_TRANSFER")

    def test_source_pretraining_and_target_reversal_before_adaptation(self):
        original = run_development("mapped").genome
        for result in self.warm.values():
            self.assertEqual(result.source_before + result.target_before, 1.0)
            self.assertEqual(result.source_before, 1.0)
        for result in self.cold.values():
            self.assertEqual(result.source_before + result.target_before, 1.0)
        self.assertNotEqual(original, seeded_genome(17))

    def test_all_control_scores_and_replay_are_well_formed(self):
        for group in (self.warm, self.cold):
            for condition, result in group.items():
                with self.subTest(condition=condition, pretrained=result.pretrained):
                    self.assertIn(result.target_after, (0.0, 0.5, 1.0))
                    self.assertEqual(result, adapt(condition, pretrained=result.pretrained))

    def test_decoder_ablation_and_zero_feedback_preserve_genome(self):
        self.assertEqual(self.cold["decoder_ablation"].genome, seeded_genome(17))
        self.assertEqual(self.cold["no_feedback"].genome, seeded_genome(17))
        self.assertEqual(self.warm["decoder_ablation"].genome, run_development("mapped").genome)
        self.assertEqual(self.warm["no_feedback"].genome, run_development("mapped").genome)

    def test_invalid_conditions_fail_closed(self):
        for name in ("primary", "", "protected", None):
            with self.assertRaises(ValueError):
                adapt(name)
        with self.assertRaises(ValueError):
            adapt("mapped", pretrained=1)

if __name__ == "__main__":
    unittest.main()
