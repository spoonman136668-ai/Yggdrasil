"""G43 bounded plasticity checks; negative results are recorded, never hidden."""
import json
import unittest
from native_dg1a import seeded_genome, GENOME_PARAMETER_COUNT
from g38_native_learning import run_development, ROUNDS, CUES, FRAMES, GRADIENT_CALLS
from g40_adaptation import adapt
from g43_plasticity import (ARMS, CONDITIONS, MIX, SCHEMA, mix_genomes,
                           run, build_report, report_json)

class G43PlasticityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_unmodified_baseline_exact_G40(self):
        for cond in CONDITIONS:
            with self.subTest(cond=cond):
                ours = run("baseline", cond)
                old = adapt(cond, pretrained=True)
                self.assertEqual(ours.genome, old.genome)
                self.assertEqual(ours.target_after, old.target_after)
                self.assertEqual(ours.source_before, old.source_before)
                self.assertEqual(ours.target_before, old.target_before)

    def test_frozen_arms_and_matched_adaptation_budgets(self):
        rows = self.report["rows"]
        self.assertEqual(set(ARMS), set(MIX))
        self.assertEqual(len(rows), len(ARMS) * len(CONDITIONS))
        self.assertEqual({(x["arm"], x["condition"]) for x in rows},
                         {(a, c) for a in ARMS for c in CONDITIONS})
        for r in rows:
            with self.subTest(arm=r["arm"], condition=r["condition"]):
                self.assertEqual(r["interactions"], ROUNDS * len(CUES))
                self.assertEqual(r["feedback_frames"], r["interactions"] * FRAMES)
                self.assertEqual(r["gradient_calls"],
                                 r["interactions"] * GRADIENT_CALLS)
                for key in ("source_before", "target_before", "source_after", "target_after"):
                    self.assertIn(r[key], (0.0, 0.5, 1.0))
                self.assertEqual(r["source_before"] + r["target_before"], 1.0)
                self.assertEqual(r["source_after"] + r["target_after"], 1.0)

    def test_no_feedback_preserves_initial_intervention_weights(self):
        original = run_development("mapped").genome
        for arm in ARMS:
            with self.subTest(arm=arm):
                expected = mix_genomes(original, seeded_genome(17), MIX[arm])
                result = run(arm, "no_feedback")
                self.assertEqual(result.genome, expected)
                self.assertEqual(result.genome.parameter_count, GENOME_PARAMETER_COUNT)

    def test_scope_receipt_and_determinism(self):
        report = self.report
        self.assertEqual(report["schema"], SCHEMA)
        self.assertFalse(report["primary_execution_allowed"])
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        self.assertIn(report["diagnostic_verdict"], (
            "DEV_INTERVENTION_IMPROVES_TARGET_WITH_PRE_ADAPTATION_SOURCE_RETENTION",
            "NO_QUALIFYING_DEVELOPMENT_IMPROVEMENT"))
        self.assertEqual(json.loads(report_json()), report)
        print("YGG_G43_DEV_PLASTICITY_JSON=" + report_json(), flush=True)

    def test_invalid_arms_and_mix_rejected(self):
        for bad in ("primary", "", None, 0):
            with self.assertRaises(ValueError):
                run(bad, "mapped")
            with self.assertRaises(ValueError):
                run("baseline", bad)
        with self.assertRaises(ValueError):
            mix_genomes(seeded_genome(17), seeded_genome(17), 0.75)
        with self.assertRaises(ValueError):
            mix_genomes(seeded_genome(17), seeded_genome(17), True)

if __name__ == "__main__":
    unittest.main()
