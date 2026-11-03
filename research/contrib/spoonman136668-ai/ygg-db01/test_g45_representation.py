"""G45 representation/procedure separation, no positive-score acceptance gate."""
import json
import unittest
from native_dg1a import DG1APrototype, GENOME_PARAMETER_COUNT
from g44_context import CUES, CONTEXTS, chosen_action
from g45_representation import (SCHEMA, ROUNDS, UPDATES_PER_PAIR,
                                witness_genome, joint_accuracy, supervised_fit,
                                build_report, report_json)

class G45SyntheticRepresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_constructive_capacity_witness_is_not_a_learned_result(self):
        model, genome = DG1APrototype(), witness_genome()
        self.assertEqual(genome.parameter_count, GENOME_PARAMETER_COUNT)
        self.assertEqual(joint_accuracy(model, genome, True), 1.0)
        self.assertEqual(joint_accuracy(model, genome, True, 0.5), 1.0)
        self.assertEqual(joint_accuracy(model, genome, False), 0.5)
        self.assertTrue(self.report["witness_is_hardcoded_not_learned"])
        for ctx in CONTEXTS:
            for cue in CUES:
                with self.subTest(ctx=ctx, cue=cue):
                    self.assertEqual(chosen_action(model, genome, cue, ctx, True),
                                     ctx * (1 if cue > 0 else -1))

    def test_frozen_balanced_supervised_probe(self):
        rows = self.report["rows"]
        self.assertEqual(len(rows), 4)
        self.assertEqual({(r["start"], r["context_mode"]) for r in rows},
                         {(start, mode) for start in ("seeded", "g38_pretrained")
                          for mode in ("visible", "masked")})
        for r in rows:
            with self.subTest(start=r["start"], mode=r["context_mode"]):
                self.assertEqual(r["updates"], ROUNDS * 4 * UPDATES_PER_PAIR)
                self.assertEqual(r["genome_parameters"], GENOME_PARAMETER_COUNT)
                for key in ("before", "after", "interpolation"):
                    self.assertIn(r[key], (0.0, 0.25, 0.5, 0.75, 1.0))
                if r["context_mode"] == "masked":
                    self.assertEqual(r["after"], 0.5)
                    self.assertEqual(r["interpolation"], 0.5)

    def test_fixed_source_control_and_deterministic_report(self):
        r = self.report
        self.assertEqual(r["schema"], SCHEMA)
        self.assertEqual(r["training_method"], "EXPLICIT_SYNTHETIC_SUPERVISED_TARGETS")
        self.assertEqual(r["reward_driven_learning"], "UNVERIFIED")
        self.assertEqual(r["scientific_acceptance"], "NO_GO")
        self.assertFalse(r["primary_execution_allowed"])
        self.assertEqual(json.loads(report_json()), r)
        print("YGG_G45_DEV_REPRESENTATION_JSON=" + report_json(), flush=True)

    def test_invalid_entry_points_fail_closed(self):
        for bad in ("protected", "", None, 0):
            with self.assertRaises(ValueError):
                supervised_fit(bad, "visible")
            with self.assertRaises(ValueError):
                supervised_fit("seeded", bad)
        with self.assertRaises(ValueError):
            joint_accuracy(DG1APrototype(), witness_genome(), 1)
        with self.assertRaises(ValueError):
            joint_accuracy(DG1APrototype(), witness_genome(), True, 0.25)

if __name__ == "__main__":
    unittest.main()
